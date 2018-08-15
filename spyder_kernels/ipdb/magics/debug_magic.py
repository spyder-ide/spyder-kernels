# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class DebugMagic(Magic):

    def line_debug(self, arg=None):
        """%c(ont(inue))
        Continue execution, only stop when a breakpoint is encountered.
        """
        self.kernel.debugger.do_debug(arg)


def register_magics(kernel):
    kernel.register_magics(DebugMagic)
