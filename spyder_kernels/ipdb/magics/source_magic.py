# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class SourceMagic(Magic):

    def line_source(self, arg=None):
        """%source expression
        Try to get source code for the given object and display it.
        """
        self.kernel.debugger.do_source(arg)


def register_magics(kernel):
    kernel.register_magics(SourceMagic)
