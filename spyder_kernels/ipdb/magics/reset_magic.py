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

# Local imports
from spyder_kernels.utils.test_utils import running_under_pytest


class ResetMagic(Magic):

    def line_reset(self, arg=None):
        """
        %reset

        Reset the global namespace.
        """
        if self.kernel.debugger:
            self.kernel.debugger.reset()
            self.kernel.debugger.setup(sys._getframe().f_back, None)


def register_magics(kernel):
    # This is only useful for our tests
    if running_under_pytest():
        kernel.register_magics(ResetMagic)
    else:
        pass
