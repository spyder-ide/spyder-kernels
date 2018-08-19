# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class EOFMagic(Magic):

    def line_EOF(self, arg=None):
        """%EOF
        Handles the receipt of EOF as a command.
        """
        self.kernel.debugger.do_EOF(arg)


def register_magics(kernel):
    kernel.register_magics(EOFMagic)
