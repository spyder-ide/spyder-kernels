# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class PsourceMagic(Magic):

    def line_psource(self, arg=None):
        """%psource object
        Print (or run through pager) the source code for an object."""
        self.kernel.debugger.do_psource(arg)


def register_magics(kernel):
    kernel.register_magics(PsourceMagic)
