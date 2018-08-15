# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class DownMagic(Magic):

    def line_down(self, arg=None):
        """%d(own) [count]
        Move the current frame count (default one) levels down in the
        stack trace (to a newer frame).
        """
        self.kernel.debugger.do_down(arg)
    line_d = line_down


def register_magics(kernel):
    kernel.register_magics(DownMagic)
