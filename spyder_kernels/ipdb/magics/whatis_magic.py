# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class WhatisMagic(Magic):

    def line_whatis(self, arg=None):
        """%whatis arg
        Print the type of the argument.
        """
        self.kernel.debugger.do_whatis(arg)


def register_magics(kernel):
    kernel.register_magics(WhatisMagic)
