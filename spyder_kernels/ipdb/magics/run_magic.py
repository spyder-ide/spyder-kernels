# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from metakernel import Magic


class RunMagic(Magic):

    def line_run(self, arg=None):
        """%run [args...]
        Restart the debugged python program. If a string is supplied
        it is split with "shlex", and the result is used as the new
        sys.argv.  History, breakpoints, actions and debugger options
        are preserved.  "restart" is an alias for "run".
        """
        self.kernel.debugger.do_run(arg)
    line_restart = line_run


def register_magics(kernel):
    kernel.register_magics(RunMagic)
