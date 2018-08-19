# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class StepMagic(Magic):

    def line_step(self, arg=None):
        """%s(tep)
        Execute the current line, stop at the first possible occasion
        (either in a function that is called or in the current
        function).
        """
        self.kernel.debugger.do_step(arg)
    line_s = line_step


def register_magics(kernel):
    kernel.register_magics(StepMagic)
