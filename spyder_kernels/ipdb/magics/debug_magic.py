# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class DebugMagic(Magic):

    def line_debug(self, arg=None):
        """%debug
        Enter a recursive debugger that steps through the code
        argument (which is an arbitrary expression or statement to be
        executed in the current environment).
        """
        self.kernel.debugger.do_debug(arg)


def register_magics(kernel):
    kernel.register_magics(DebugMagic)
