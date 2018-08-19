# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class UndisplayMagic(Magic):

    def line_undisplay(self, arg=None):
        """%undisplay [expression]

        Do not display the expression any more in the current frame.

        Without expression, clear all display expressions for the current frame
        """
        self.kernel.debugger.do_undisplay(arg)


def register_magics(kernel):
    kernel.register_magics(UndisplayMagic)
