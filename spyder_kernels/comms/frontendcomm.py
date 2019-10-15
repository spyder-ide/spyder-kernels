# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
In addition to the remote_call mechanism implemented in CommBase:
 - Implements _wait_reply, so blocking calls can be made.
"""
import os
import time
import threading
import pickle
from tornado import ioloop

from spyder_kernels.comms.commbase import CommBase
from spyder_kernels.py3compat import TimeoutError, PY2


class FrontendComm(CommBase):
    """Mixin to implement the spyder_shell_api"""

    def __init__(self, kernel):
        super(FrontendComm, self).__init__()

        # Comms
        self._pid = os.getpid()
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
        if self.kernel.lock.locked():
            # This can cause problems with messages ordering.
            raise RuntimeError('Recursive call to _wait_reply.')
        if call_id in self._reply_inbox:
            return

        # There is no get_ident in Py2
        if not PY2 and self._main_thread_id != threading.get_ident():
            # A new event loop is needed to call do_one_iteration
            try:
                ioloop.IOLoop.current()
            except RuntimeError:
                ioloop.IOLoop().initialize()

        t_start = time.time()
        while call_id not in self._reply_inbox:
            if time.time() > t_start + timeout:
                raise TimeoutError(
                    "Timeout while waiting for '{}' reply".format(
                        call_name))
            priority = 0
            while priority is not None:
                with self.kernel.lock:
                    priority = self.kernel.do_one_iteration()
                if priority is not None:
                    # For Python2
                    priority = priority.result()

    def _comm_open(self, comm, msg):
        """
        A new comm is open!
        """
        self._register_comm(comm)
        self._set_pickle_protocol(msg['content']['data']['pickle_protocol'])
        self.remote_call()._set_pickle_protocol(pickle.HIGHEST_PROTOCOL)

    def _comm_close(self, msg):
        """Close comm."""
        comm_id = msg['content']['comm_id']
        comm = self._comms[comm_id]
        # Pretend it is already closed to avoid problems when closing
        comm._closed = True
        del self._comms[comm_id]

    def _async_error(self, error_wrapper):
        """
        Send an async error back to the frontend to be displayed.
        """
        self.remote_call()._async_error(error_wrapper)
