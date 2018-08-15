# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class PdefMagic(Magic):

    def line_pdef(self, arg=None):
        """Print the call signature for any callable object.

        The debugger interface to %pdef"""
        self.kernel.debugger.do_pdef(arg)


def register_magics(kernel):
    kernel.register_magics(PdefMagic)
