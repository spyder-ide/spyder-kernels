# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class ContinueMagic(Magic):

    def line_continue(self, arg=None):
        """%c(ont(inue))
        Continue execution, only stop when a breakpoint is encountered.
        """
        self.kernel.debugger.do_continue(arg)
    line_c = line_cont = line_continue


def register_magics(kernel):
    kernel.register_magics(ContinueMagic)
