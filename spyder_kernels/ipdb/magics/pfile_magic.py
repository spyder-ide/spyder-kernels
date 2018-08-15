# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class PfileMagic(Magic):

    def line_pfile(self, arg=None):
        """Print (or run through pager) the file where an object is defined.

        The debugger interface to %pfile.
        """
        self.kernel.debugger.do_pfile(arg)


def register_magics(kernel):
    kernel.register_magics(PfileMagic)
