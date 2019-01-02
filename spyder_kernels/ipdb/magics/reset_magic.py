# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

# Standard library imports
import sys

# Metakernel imports
from metakernel import Magic


class ResetMagic(Magic):

    def line_reset(self, arg=None):
        """
        %reset

        Reset the global namespace.
        """
        if self.kernel.debugger:
            self.kernel.debugger._reset_namespace(arg)


def register_magics(kernel):
    kernel.register_magics(ResetMagic)
