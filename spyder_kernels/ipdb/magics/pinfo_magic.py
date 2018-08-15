# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class PinfoMagic(Magic):

    def line_pinfo(self, arg=None):
        """Provide detailed information about an object.

        The debugger interface to %pinfo, i.e., obj?."""
        self.kernel.debugger.do_pinfo(arg)


def register_magics(kernel):
    kernel.register_magics(PinfoMagic)
