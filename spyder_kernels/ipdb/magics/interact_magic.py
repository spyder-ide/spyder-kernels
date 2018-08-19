# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class InteractMagic(Magic):

    def line_interact(self, arg=None):
        """%interact

        Start an interactive interpreter whose global namespace
        contains all the (global and local) names found in the current scope.
        """
        self.kernel.debugger.do_interact(arg)


def register_magics(kernel):
    kernel.register_magics(InteractMagic)
