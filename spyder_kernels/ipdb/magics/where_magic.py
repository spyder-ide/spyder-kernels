# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class WhereMagic(Magic):

    def line_where(self, arg=None):
        """%w(here)
        Print a stack trace, with the most recent frame at the bottom.
        An arrow indicates the "current frame", which determines the
        context of most commands.  'bt' is an alias for this command.
        """
        self.kernel.debugger.do_where(arg)
    line_w = line_bt = line_where


def register_magics(kernel):
    kernel.register_magics(WhereMagic)
