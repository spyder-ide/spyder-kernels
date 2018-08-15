# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class LongListMagic(Magic):

    def line_long_list(self, arg=None):
        """%longlist | %ll
        List the whole source code for the current function or frame.
        """
        self.kernel.debugger.do_longlist(arg)
    line_ll = line_long_list


def register_magics(kernel):
    kernel.register_magics(LongListMagic)
