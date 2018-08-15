# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class RetvalMagic(Magic):

    def line_retval(self, arg=None):
        """%retval
        Print the return value for the last return of a function.
        """
        self.kernel.debugger.do_retval(arg)
    line_rv = line_retval


def register_magics(kernel):
    kernel.register_magics(RetvalMagic)
