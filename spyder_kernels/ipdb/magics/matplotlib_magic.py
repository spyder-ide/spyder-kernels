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
        Mosas
        """
        from ipykernel.eventloops import enable_gui
        from IPython.core.interactiveshell import InteractiveShell
        
        ipyshell = InteractiveShell()
        ipyshell.enable_gui = enable_gui
        ipyshell.enable_matplotlib(gui=gui)


def register_magics(kernel):
    kernel.register_magics(MatplotlibMagic)
