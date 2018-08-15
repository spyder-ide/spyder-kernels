# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class NextMagic(Magic):

    def line_next(self, arg=None):
        """%n(ext)
        Continue execution until the next line in the current function
        is reached or it returns.
        """
        self.kernel.debugger.do_next(arg)
    line_n = line_next


def register_magics(kernel):
    kernel.register_magics(NextMagic)
