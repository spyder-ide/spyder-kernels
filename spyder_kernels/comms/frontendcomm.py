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

from spyder_kernels.comms.commbase import CommBase, CommError
from spyder_kernels.py3compat import TimeoutError, PY2


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

    def remote_call(self, comm_id=None, blocking=False, callback=None):
        """Get a handler for remote calls."""
        return super(FrontendComm, self).remote_call(
                blocking=blocking, comm_id=comm_id, callback=callback)

    # --- Private --------
    def _wait_reply(self, call_id, call_name, timeout):
        """Wait until the frontend replies to a request."""
        if call_id in self._reply_inbox:
            return

        # There is no get_ident in Py2
        if not PY2 and self._main_thread_id != threading.get_ident():
            # We can't call kernel.do_one_iteration from this thread.
            # And we have no reason to think the main thread is not busy.
            raise CommError(
                "Can't make blocking calls from non-main threads.")

        t_start = time.time()
        while call_id not in self._reply_inbox:
            if time.time() > t_start + timeout:
                raise TimeoutError(
                    "Timeout while waiting for '{}' reply".format(
                        call_name))
            priority = 0
            while priority is not None:
                priority = self.kernel.do_one_iteration()
                if priority is not None:
                    # For Python2
                    priority = priority.result()

    def _comm_open(self, comm, msg):
        """
        A new comm is open!
        """
        self.calling_comm_id = comm.comm_id
        self._register_comm(comm)
        self._set_pickle_protocol(msg['content']['data']['pickle_protocol'])
        self.remote_call()._set_pickle_protocol(pickle.HIGHEST_PROTOCOL)

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
