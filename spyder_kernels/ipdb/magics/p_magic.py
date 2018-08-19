# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class PMagic(Magic):

    def line_p(self, arg=None):
        """%p expression
        Print the value of the expression.
        """
        self.kernel.debugger.do_p(arg)


def register_magics(kernel):
    kernel.register_magics(PMagic)
