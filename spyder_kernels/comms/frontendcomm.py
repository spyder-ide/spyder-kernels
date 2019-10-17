# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
In addition to the remote_call mechanism implemented in CommBase:
 - Implements _wait_reply, so blocking calls can be made.
"""
import time
import threading
import pickle
import zmq
import sys
import socket
from jupyter_client.localinterfaces import localhost
from tornado import ioloop

from spyder_kernels.comms.commbase import CommBase
from spyder_kernels.py3compat import TimeoutError, PY2


def get_port():
    sock = socket.socket()
    # struct.pack('ii', (0,0)) is 8 null bytes
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b'\0' * 8)
    sock.bind((localhost(), 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


class FrontendComm(CommBase):
    """Mixin to implement the spyder_shell_api"""

    def __init__(self, kernel):
        super(FrontendComm, self).__init__()

        # Comms
        self.kernel = kernel
        self.kernel.comm_manager.register_target(
            self._comm_name, self._comm_open)

        if not PY2:
            self._main_thread_id = threading.get_ident()

        if self.kernel.parent:
            # self.kernel.parent is IPKernelApp unless we are in tests
            # Create a new socket
            context = zmq.Context()
            self.comm_socket = context.socket(zmq.ROUTER)
            self.comm_socket.linger = 1000

            self.comm_port = get_port()

            self.comm_port = self.kernel.parent._bind_socket(
                self.comm_socket, self.comm_port)
            if hasattr(zmq, 'ROUTER_HANDOVER'):
                # set router-handover to workaround zeromq reconnect problems
                # in certain rare circumstances
                # see ipython/ipykernel#270 and zeromq/libzmq#2892
                self.comm_socket.router_handover = 1

            self.comm_socket_thread = threading.Thread(target=self.poll_thread)
            self.comm_socket_thread.start()

            # patch parent.close
            self.comm_thread_close = threading.Event()
            super_close = self.kernel.parent.close

            def close():
                """Close comm_socket_thread."""
                self.comm_thread_close.set()
                context.term()
                self.comm_socket_thread.join()
                super_close()

            self.kernel.parent.close = close

    def poll_thread(self):
        """Recieve messages from comm socket"""
        if not PY2:
            # Create an event loop to handle some messages
            ioloop.IOLoop().initialize()
        while not self.comm_thread_close.is_set():
            out_stream = None
            if self.kernel.shell_streams:
                out_stream = self.kernel.shell_streams[0]
            try:
                ident, msg = self.kernel.session.recv(self.comm_socket, 0)
            except Exception:
                self.kernel.log.warning("Invalid Message:", exc_info=True)
            msg_type = msg['header']['msg_type']

            handler = self.kernel.shell_handlers.get(msg_type, None)
            if handler is None:
                self.kernel.log.warning("Unknown message type: %r", msg_type)
            else:
                try:
                    # shell_streams[0] handles replies
                    handler(out_stream, ident, msg)
                except Exception:
                    self.kernel.log.error("Exception in message handler:",
                                          exc_info=True)

            sys.stdout.flush()
            sys.stderr.flush()
            # flush to ensure reply is sent
            if out_stream:
                out_stream.flush(zmq.POLLOUT)

    def remote_call(self, comm_id=None, blocking=False, callback=None):
        """Get a handler for remote calls."""
        return super(FrontendComm, self).remote_call(
                blocking=blocking, comm_id=comm_id, callback=callback)

    # --- Private --------
    def _wait_reply(self, call_id, call_name, timeout):
        """Wait until the frontend replies to a request."""
        if call_id in self._reply_inbox:
            return

        t_start = time.time()
        while call_id not in self._reply_inbox:
            if time.time() > t_start + timeout:
                raise TimeoutError(
                    "Timeout while waiting for '{}' reply".format(
                        call_name))
            # Wait 10ms for a reply
            time.sleep(0.01)

    def _comm_open(self, comm, msg):
        """
        A new comm is open!
        """
        self.calling_comm_id = comm.comm_id
        self._register_comm(comm)
        self._set_pickle_protocol(msg['content']['data']['pickle_protocol'])
        self.remote_call()._set_pickle_protocol(pickle.HIGHEST_PROTOCOL)
        self.remote_call()._set_comm_port(self.comm_port)

    def _comm_close(self, msg):
        """Close comm."""
        comm_id = msg['content']['comm_id']
        comm = self._comms[comm_id]['comm']
        # Pretend it is already closed to avoid problems when closing
        comm._closed = True
        del self._comms[comm_id]

    def _async_error(self, error_wrapper):
        """
        Send an async error back to the frontend to be displayed.
        """
        self.remote_call()._async_error(error_wrapper)

    def _register_comm(self, comm):
        """
        Remove side effect ipykernel has.
        """
        def handle_msg(msg):
            """Handle a comm_msg message"""
            if comm._msg_callback:
                comm._msg_callback(msg)
        comm.handle_msg = handle_msg
        super(FrontendComm, self)._register_comm(comm)
