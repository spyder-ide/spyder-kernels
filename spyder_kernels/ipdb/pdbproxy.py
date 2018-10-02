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

import ast

class PdbProxy(object):

    remote_pdb_obj = u'get_ipython().kernel._pdb_obj'

    def __init__(self, kernel_client):
        self.kernel_client = kernel_client

    # --- Custom API
    def _execute(self, command, interactive=False):
        """Execute command in a remote Pdb instance."""
        if interactive:
            kc_exec = self.kernel_client.execute_interactive
        else:
            kc_exec = self.kernel_client.execute

        pdb_cmd = self.remote_pdb_obj + u'.' + command
        if interactive:
            kc_exec(pdb_cmd, store_history=False)
        else:
            kc_exec(pdb_cmd, silent=True)

    def _get_completions(self, code):
        """Get code completions from our Pdb instance."""
        # Ask for completions to the debugger
        cmd = (u'__spy_matches__ = ' + self.remote_pdb_obj + u'.' +
               u'_get_completions("{}")'.format(code))
        msg_id = self.kernel_client.execute(cmd,
                    silent=True,
                    user_expressions={'output':'__spy_matches__'})

        # Get completions from the reply
        reply = self.kernel_client.get_shell_msg(msg_id)
        user_expressions = reply['content']['user_expressions']
        try:
            str_matches = user_expressions['output']['data']['text/plain']
            try:
                return ast.literal_eval(str_matches)
            except Exception:
                return []
        except KeyError:
            return []

    # --- Pdb API
    def default(self, line):
        self._execute(u'default("{}")'.format(line), interactive=True)

    def postcmd(self, stop, line):
        self._execute(u'postcmd(None, "{}")'.format(line))

    def do_break(self, arg=None, temporary=0):
        if arg:
            self._execute(u'do_break("{}", {})'.format(arg, temporary),
                          interactive=True)
        else:
            self._execute(u'do_break(None, {})'.format(temporary),
                          interactive=True)

    def do_down(self, arg):
        if arg:
            self._execute(u'do_down("{}")'.format(arg), interactive=True)
        else:
            self._execute(u'do_down(None)', interactive=True)

    def error(self, msg):
        self._execute(u'error("{}")'.format(msg), interactive=True)
