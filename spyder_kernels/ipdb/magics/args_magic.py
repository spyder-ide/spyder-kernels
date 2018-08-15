# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class ArgsMagic(Magic):

    def line_args(self, arg=None):
        """%a(rgs)
        Print the argument list of the current function.
        """
        self.kernel.debugger.do_args(arg)
    line_a = line_args


def register_magics(kernel):
    kernel.register_magics(ArgsMagic)
