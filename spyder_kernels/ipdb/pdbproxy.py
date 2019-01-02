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

from __future__ import print_function
import ast
import sys

from spyder_kernels.py3compat import to_text_string


class PdbProxy(object):

    remote_pdb_obj = u'get_ipython().kernel._pdb_obj'

    def __init__(self, parent, kernel_client):
        self.parent = parent
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
            kc_exec(pdb_cmd, store_history=False,
                    output_hook=self._output_hook,
                    allow_stdin=False)
        else:
            kc_exec(pdb_cmd, silent=True, allow_stdin=False)

    def _silent_exec_method(self, method, args=None):
        """
        Silently execute a method of our remote Pdb instance and get its
        response.

        Parameters
        ----------
        method: string
            Method name
        args: string
            Args to be passed to the method (optional)
        """
        method = to_text_string(method)

        # Pass args to the method call, if any
        if args is not None:
            args = to_text_string(args)
            method_call = method + u'("{}")'.format(args)
        else:
            method_call = method + u'()'

        # Ask the remote instance to execute the method call
        cmd = (u'__dbg_response__ = ' + self.remote_pdb_obj + u'.' +
               method_call)
        msg_id = self.kernel_client.execute(cmd,
                    silent=True,
                    user_expressions={'output':'__dbg_response__'})

        # Get response
        reply = self.kernel_client.get_shell_msg(msg_id)
        user_expressions = reply['content']['user_expressions']
        try:
            return user_expressions['output']['data']['text/plain']
        except KeyError:
            return None

    def _get_completions(self, code):
        """
        Get code completions from our Pdb instance.

        Parameters
        ----------
        code: string
            Code to get completions for.
        """
        response = self._silent_exec_method('_get_completions', code)
        if response is None:
            return []
        else:
            try:
                return ast.literal_eval(response)
            except Exception:
                return []

    def _is_ready(self):
        """
        Check if the remote Pdb instance is ready to start debugging.
        """
        response = self._silent_exec_method('_is_ready')
        if response is None:
            return False
        else:
            try:
                return ast.literal_eval(response)
            except Exception:
                return False

    def _enable_matplotlib(self, gui):
        """Set Matplotlib backend in the remote kernel."""
        self.kernel_client.execute(u"%matplotlib {}".format(gui),
                                   silent=True)

    def _output_hook(self, msg):
        """Output hook for execute_interactive."""
        msg_type = msg['header']['msg_type']
        content = msg['content']
        if msg_type == 'stream':
            stream = getattr(sys, content['name'])
            stream.write(content['text'])
        elif msg_type in ('display_data', 'execute_result'):
            self.parent.send_response(
                self.parent.iopub_socket,
                msg_type,
                content
            )
        elif msg_type == 'error':
            print('\n'.join(content['traceback']), file=sys.stderr)

    def _reset_namespace(self, arg):
        if arg:
            self.kernel_client.execute_interactive(
                u"%reset {}".format(arg),
                store_history=False)
        else:
            print("We can't ask for confirmation in this kernel.\n"
                  "Please use '%reset -f' to reset your namespace.")

    def _do_command(self, command, arg):
        """
        Method to execute a given Pdb comand with its respective arg.

        Note: This is useful because almost all Pdb commands have a
        single arg.
        """
        self._execute(u'{}({})'.format(command, arg), interactive=True)

    # --- Pdb API
    def default(self, line):
        self._execute(u'default("{}")'.format(line), interactive=True)

    def postcmd(self, stop, line):
        self._execute(u'postcmd(None, "{}")'.format(line))

    def error(self, msg):
        self._execute(u'error("{}")'.format(msg), interactive=True)

    # --- Pdb commands
    def do_break(self, arg=None, temporary=0):
        if arg:
            self._execute(u'do_break("{}", {})'.format(arg, temporary),
                          interactive=True)
        else:
            self._execute(u'do_break(None, {})'.format(temporary),
                          interactive=True)
