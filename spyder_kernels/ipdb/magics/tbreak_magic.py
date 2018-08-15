# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class TbreakMagic(Magic):

    def line_tbreak(self, arg=None):
        """%tbreak [ ([filename:]lineno | function) [, condition] ]
        Same arguments as break, but sets a temporary breakpoint: it
        is automatically deleted when first hit.
        """
        self.kernel.debugger.do_tbreak(arg)


def register_magics(kernel):
    kernel.register_magics(TbreakMagic)
