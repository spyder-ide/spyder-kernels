# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class ReturnMagic(Magic):

    def line_return(self, arg=None):
        """%r(eturn)
        Continue execution until the current function returns.
        """
        self.kernel.debugger.do_run(arg)
    line_r = line_return


def register_magics(kernel):
    kernel.register_magics(ReturnMagic)
