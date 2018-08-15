# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class UpMagic(Magic):

    def line_up(self, arg=None):
        """%u(p) [count]
        Move the current frame count (default one) levels up in the
        stack trace (to an older frame).
        """
        self.kernel.debugger.do_up(arg)
    line_u = line_up


def register_magics(kernel):
    kernel.register_magics(UpMagic)
