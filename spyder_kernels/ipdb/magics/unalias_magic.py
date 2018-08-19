# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class UnaliasMagic(Magic):

    def line_unalias(self, arg=None):
        """%unalias name
        Delete the specified alias.
        """
        self.kernel.debugger.do_unalias(arg)


def register_magics(kernel):
    kernel.register_magics(UnaliasMagic)
