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

from spyder_kernels.comms.commbase import CommBase, CommError
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
        self._wait_list = {}

        if not PY2:
            self._main_thread_id = threading.get_ident()

    def remote_call(self, blocking=False):
        """Get a handler for remote calls."""
        return super(FrontendComm, self).remote_call(blocking=blocking)

    # --- Private --------
    def _wait_reply(self, call_id, call_name, timeout):
        """Wait until the frontend replies to a request."""
        if call_id in self._call_reply_dict:
            return

        # There is no get_ident in Py2
        if not PY2 and self._main_thread_id != threading.get_ident():
            # We can't call kernel.do_one_iteration from this thread.
            # And we have no reason to think the main thread is not busy.
            raise CommError(
                "Can't make blocking calls from non main threads.")
        t_start = time.time()
        self._wait_list[call_id] = call_name
        while call_id not in self._call_reply_dict:
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
        self._wait_list.pop(call_id)

    def _comm_open(self, comm, msg):
        """
        A new comm is open!
        """
        self._register_comm(comm)
