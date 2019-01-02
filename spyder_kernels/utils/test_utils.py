# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
# Taken from the tests utils in the Metakernel package
# See utils.py at https://github.com/Calysto/metakernel/metakernel/tests
# Licensed under the terms of the BSD License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

import os

from jupyter_client import session as ss
import zmq
import logging

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def get_kernel(kernel_class, testing=False):
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

    kernel = kernel_class(session=ss.Session(),
                          iopub_socket=iopub_socket,
                          log=log, testing=testing)
    return kernel


def get_log_text(kernel):
    """Get the log of the given kernel."""
    return kernel.log.handlers[0].stream.getvalue()


def running_under_pytest():
    """
    Return True if currently running under pytest.
    """
    return bool(os.environ.get('SPYDER_KERNELS_PYTEST'))
