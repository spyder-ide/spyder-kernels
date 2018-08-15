# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class PdocMagic(Magic):

    def line_pdoc(self, arg=None):
        """Print the docstring for an object.

        The debugger interface to %pdoc."""
        self.kernel.debugger.do_pdoc(arg)


def register_magics(kernel):
    kernel.register_magics(PdocMagic)
