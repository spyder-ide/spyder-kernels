# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class ClearMagic(Magic):

    def line_clear(self, arg=None):
        """%cl(ear) filename:lineno\n%cl(ear) [bpnumber [bpnumber...]]
        With a space separated list of breakpoint numbers, clear
        those breakpoints.  Without argument, clear all breaks (but
        first ask confirmation).  With a filename:lineno argument,
        clear all breaks at that line in that file.
        """
        self.kernel.debugger.do_clear(arg)
    line_cl = line_clear


def register_magics(kernel):
    kernel.register_magics(ClearMagic)
