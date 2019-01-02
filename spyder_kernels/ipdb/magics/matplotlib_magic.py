# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class MatplotlibMagic(Magic):

    def line_matplotlib(self, gui):
        """
        Matplotlib magic

        You can set all backends you can with the IPython %matplotlib
        magic.
        """
        self.kernel.debugger._enable_matplotlib(gui)


def register_magics(kernel):
    kernel.register_magics(MatplotlibMagic)
