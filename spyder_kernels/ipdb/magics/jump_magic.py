# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class JumpMagic(Magic):

    def line_jump(self, arg=None):
        """%j(ump) lineno
        Set the next line that will be executed.  Only available in
        the bottom-most frame.  This lets you jump back and execute
        code again, or jump forward to skip code that you don't want
        to run.

        It should be noted that not all jumps are allowed -- for
        instance it is not possible to jump into the middle of a
        for loop or out of a finally clause.
        """
        self.kernel.debugger.do_jump(arg)
    line_j = line_jump


def register_magics(kernel):
    kernel.register_magics(JumpMagic)
