# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class PpMagic(Magic):

    def line_pp(self, arg=None):
        """%pp expression
        Pretty-print the value of the expression.
        """
        self.kernel.debugger.do_pp(arg)


def register_magics(kernel):
    kernel.register_magics(PpMagic)
