# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Spyder kernel application.
"""

# Third-party imports
from ipykernel.kernelapp import IPKernelApp
from traitlets import DottedObjectName

# Local imports
from spyder_kernels.console.kernel import SpyderKernel


class SpyderKernelApp(IPKernelApp):

    outstream_class = DottedObjectName(
        'spyder_kernels.console.outstream.TTYOutStream'
    )

    kernel_class = SpyderKernel

    def init_pdb(self):
        """
        This method was added in IPykernel 5.3.1 and it replaces
        the debugger used by the kernel with a new class
        introduced in IPython 7.15 during kernel's initialization.
        Therefore, it doesn't allow us to use our debugger.
        """
        pass

    def close(self):
        """Close the loopback socket."""
        socket = self.kernel.loopback_socket
        if socket and not socket.closed:
            socket.close()
        return super().close()
