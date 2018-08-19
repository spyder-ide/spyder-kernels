# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class Pinfo2Magic(Magic):

    def line_pinfo2(self, arg=None):
        """Provide detailed information about an object.

        The debugger interface to %pinfo2, i.e., obj?."""
        self.kernel.debugger.do_pinfo2(arg)


def register_magics(kernel):
    kernel.register_magics(Pinfo2Magic)
