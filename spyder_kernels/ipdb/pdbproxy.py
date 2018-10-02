# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Proxy to execute Pdb commands in a Pdb instance running in a
different kernel.
"""

class PdbProxy(object):

    remote_pdb_obj = 'get_ipython().kernel._pdb_obj'

    def __init__(self, kernel_client):
        self.kernel_client = kernel_client

    def _execute(self, command, interactive=False):
        """Execute command in a remote Pdb instance."""
        if interactive:
            kc_exec = self.kernel_client.execute_interactive
        else:
            kc_exec = self.kernel_client.execute

        pdb_cmd = self.remote_pdb_obj + '.' + command
        if interactive:
            kc_exec(pdb_cmd, store_history=False)
        else:
            kc_exec(pdb_cmd, silent=True)

    def default(self, line):
        self._execute('default("{}")'.format(line), interactive=True)

    def postcmd(self, stop, line):
        self._execute('postcmd(None, "{}")'.format(line))

    def do_break(self, arg=None, temporary=0):
        if arg:
            self._execute('do_break("{}", {})'.format(arg, temporary),
                          interactive=True)
        else:
            self._execute('do_break(None, {})'.format(temporary),
                          interactive=True)
