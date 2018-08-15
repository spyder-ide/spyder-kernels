# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class DisplayMagic(Magic):

    def line_display(self, arg=None):
        """%display [expression]

        Display the value of the expression if it changed, each time execution
        stops in the current frame.

        Without expression, list all display expressions for the current frame.
        """
        self.kernel.debugger.do_display(arg)


def register_magics(kernel):
    kernel.register_magics(DisplayMagic)
