# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class QuitMagic(Magic):

    def line_quit(self, arg=None):
        """%q(uit)\nexit
        Quit from the debugger. The program being executed is aborted.
        """
        self.kernel.debugger.do_quit(arg)
    line_exit = line_q = line_quit


def register_magics(kernel):
    kernel.register_magics(QuitMagic)
