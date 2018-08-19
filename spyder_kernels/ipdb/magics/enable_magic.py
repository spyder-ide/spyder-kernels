# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class EnableMagic(Magic):

    def line_enable(self, arg=None):
        """%enable bpnumber [bpnumber ...]
        Enables the breakpoints given as a space separated list of
        breakpoint numbers.
        """
        self.kernel.debugger.do_enable(arg)


def register_magics(kernel):
    kernel.register_magics(EnableMagic)
