# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
# Taken from the tests utils in the Metakernel package
# See utils.py at https://github.com/Calysto/metakernel/metakernel/tests
# Licensed under the terms of the BSD License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

try:
    from jupyter_client import session as ss
except ImportError:
    from IPython.kernel.zmq import session as ss
import zmq
import logging

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from spyder_kernels.console.kernel import SpyderKernel


def get_kernel(kernel_class=SpyderKernel):
    """Get an instance of a kernel with the kernel class given."""
    log = logging.getLogger('test')
    log.setLevel(logging.DEBUG)

    for hdlr in log.handlers:
        log.removeHandler(hdlr)

    hdlr = logging.StreamHandler(StringIO())
    hdlr.setLevel(logging.DEBUG)
    log.addHandler(hdlr)

    context = zmq.Context.instance()
    iopub_socket = context.socket(zmq.PUB)

    kernel = kernel_class(session=ss.Session(), iopub_socket=iopub_socket,
                          log=log)
    return kernel


def get_log_text(kernel):
    """Get the log of the given kernel."""
    return kernel.log.handlers[0].stream.getvalue()


class dummyComm():
    def __init__(self):
        self.other = None
        self.message_callback = None
        self.close_callback = None

    def close(self):
        self.other.close_callback({'content': None})

    def send(self, msg_dict, buffers=None):
        msg = {
            'buffers': buffers,
            'content': {'data': msg_dict},
            }
        self.other.message_callback(msg)

    def on_msg(self, callback):
        self.message_callback = callback

    def on_close(self, callback):
        self.close_callback = callback