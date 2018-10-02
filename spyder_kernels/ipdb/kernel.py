# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
# Copyright (c) 2015, Lev Givon. All rights reserved.
# Licensed under the terms of the BSD 3 clause license
# -----------------------------------------------------------------------------

"""
IPython debugger kernel

This kernel is based in the ipbdkernel project of Lev Givon,
which is present in:

https://github.com/lebedov/ipdbkernel
"""

import functools
import os
import sys

from ipykernel.eventloops import enable_gui
from IPython.core.inputsplitter import IPythonInputSplitter
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.debugger import BdbQuit_excepthook
from IPython.utils.tokenutil import token_at_cursor
from jupyter_client.blocking.client import BlockingKernelClient
from metakernel import MetaKernel

from spyder_kernels._version import __version__
from spyder_kernels.ipdb import backend_inline
from spyder_kernels.ipdb.pdbproxy import PdbProxy
from spyder_kernels.kernelmixin import BaseKernelMixIn
from spyder_kernels.py3compat import builtins
from spyder_kernels.utils.module_completion import module_completion


class PhonyStdout(object):

    def __init__(self, write_func):
        self._write_func = write_func

    def flush(self):
        pass

    def write(self, s):
        self._write_func(s)

    def close(self):
        pass


class IPdbKernel(BaseKernelMixIn, MetaKernel):
    implementation = "IPdb Kernel"
    implementation_version = __version__
    language = "ipdb"
    language_version = __version__
    banner = "IPython debugger {}".format(__version__)

    language_info = {
        "mimetype": "text/x-python",
        "name": "ipython",
        "version": __version__,
        "help_links": MetaKernel.help_links,
    }

    kernel_json = {
        "argv": [sys.executable, "-m",
                 "spyder_kernels.ipdb", "-f", "{connection_file}"],
        "display_name": "IPdb",
        "language": "ipython",
        "mimetype": "text/x-python",
        "name": "ipdb_kernel",
    }

    def __init__(self, *args, **kwargs):
        super(IPdbKernel, self).__init__(*args, **kwargs)

        # Create Pdb proxy
        console_kernel_client = self._create_console_kernel_client()
        self.debugger = PdbProxy(console_kernel_client)

        # To detect if a line is complete
        self.input_transformer_manager = IPythonInputSplitter(
                                             line_input_checker=False)

        # For module_completion and do_inspect
        self.ipyshell = InteractiveShell().instance()
        self.ipyshell.enable_gui = enable_gui
        self.mpl_gui = None

        # Add _get_kernel_
        # TODO: Remove this?
        builtins._get_kernel_ = self._get_kernel_

        self._remove_unneeded_magics()

    # --- MetaKernel API
    def do_execute_direct(self, code):
        """
        Execute code with the debugger.
        """
        # Process command
        line = code.strip()
        self.debugger.default(line)
        self.debugger.postcmd(None, line)

        # Post command operations
        # TODO: Fix inline figures
        # self._show_inline_figures()

    def do_is_complete(self, code):
        """
        Given code as string, returns dictionary with 'status' representing
        whether code is ready to evaluate. Possible values for status are:

           'complete'   - ready to evaluate
           'incomplete' - not yet ready
           'invalid'    - invalid code
           'unknown'    - unknown; the default unless overridden

        Optionally, if 'status' is 'incomplete', you may indicate
        an indentation string.

        Example:

            return {'status' : 'incomplete',
                    'indent': ' ' * 4}
        """
        if self.parse_code(code)["magic"]:
            return {"status": "complete"}
        (status,
         indent_spaces) = self.input_transformer_manager.check_complete(code)
        r = {'status': status}
        if status == 'incomplete':
            r['indent'] = ' ' * indent_spaces
        return r

    def do_inspect(self, code, cursor_pos, detail_level=0):
        """
        Object instrospection.
        """
        name = token_at_cursor(code, cursor_pos)
        info = self.ipyshell.object_inspect(name)

        reply_content = {'status': 'ok'}
        reply_content['data'] = data = {}
        reply_content['metadata'] = {}
        reply_content['found'] = info['found']
        if info['found']:
            info_text = self.ipyshell.object_inspect_text(
                name,
                detail_level=detail_level,
            )
            data['text/plain'] = info_text
            self.log.debug(str(info_text))

        return reply_content

    def get_completions(self, info):
        """Get code completions."""
        code = info["code"]

        if code.startswith('import') or code.startswith('from'):
            matches = module_completion(code)
        else:
            # We need to ask for completions twice to get the
            # right completions through user_expressions
            for _ in range(2):
                matches = self.debugger._get_completions(code)

        return matches

    def get_usage(self):
        """General Pdb help."""
        return self.debugger.do_help(None)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        """Help for Pdb commands."""
        if none_on_fail:
            return None
        else:
            cmd = info['code'].strip()
            help_on = None
            try:
                try:
                    getattr(self.debugger, 'help_' + cmd)
                    help_on = self.debugger.do_help(cmd)
                except AttributeError:
                    getattr(self.debugger, 'do_' + cmd)
                    help_on = self.debugger.do_help(cmd)
            except AttributeError:
                response = self.do_inspect(info['code'], info['help_pos'])
                if 'data' in response:
                    if 'text/plain' in response['data']:
                        help_on = response['data']['text/plain']
                if not help_on:
                    self.debugger.error('No help for %r' % cmd)
        return help_on

    # --- Private API
    def _remove_unneeded_magics(self):
        """Remove unnecessary magics from MetaKernel."""
        line_magics = ['activity', 'conversation', 'dot', 'get', 'include',
                       'install', 'install_magic', 'jigsaw', 'kernel', 'kx',
                       'macro', 'parallel', 'plot', 'pmap', 'px', 'run',
                       'scheme', 'set']
        cell_magics = ['activity', 'brain', 'conversation', 'debug', 'dot',
                       'macro', 'processing', 'px', 'scheme', 'tutor']

        for lm in line_magics:
            try:
                self.line_magics.pop(lm)
            except KeyError:
                pass

        for cm in cell_magics:
            try:
                self.cell_magics.pop(cm)
            except:
                pass

    def _get_reference_namespace(self, name):
        """
        Return namespace where reference name is defined

        It returns the globals() if reference has not yet been defined
        """
        glbs = self._mglobals()
        if self.debugger.curframe is None:
            return glbs
        else:
            lcls = self.debugger.curframe.f_locals
            if name in lcls:
                return lcls
            else:
                return glbs

    def _mglobals(self):
        """Return current globals"""
        if self.debugger.curframe is not None:
            return self.debugger.curframe.f_globals
        else:
            return {}

    def _phony_stdout(self, text):
        self.log.debug(text)
        self.send_response(self.iopub_socket,
                           'stream',
                           {'name': 'stdout',
                            'text': text})

    def _show_inline_figures(self):
        """Show Matplotlib inline figures."""
        if self.mpl_gui == 'inline':
            backend_inline.show()

    def _get_kernel_(self):
        """To add _get_kernel_ function to builtins."""
        return self

    def _create_console_kernel_client(self):
        """Create a kernel client connected to a console kernel."""
        try:
            # Retrieve connection info from the environment
            shell_port = int(os.environ['SPY_CONSOLE_SHELL_PORT'])
            iopub_port = int(os.environ['SPY_CONSOLE_IOPUB_PORT'])
            stdin_port = int(os.environ['SPY_CONSOLE_STDIN_PORT'])
            control_port = int(os.environ['SPY_CONSOLE_CONTROL_PORT'])
            hb_port = int(os.environ['SPY_CONSOLE_HB_PORT'])
            ip = os.environ['SPY_CONSOLE_IP']
            key = os.environ['SPY_CONSOLE_KEY']
            transport = os.environ['SPY_CONSOLE_TRANSPORT']
            signature_scheme = os.environ['SPY_CONSOLE_SIGNATURE_SCHEME']

            # Create info dict
            info = dict(shell_port=shell_port,
                        iopub_port=iopub_port,
                        stdin_port=stdin_port,
                        control_port=control_port,
                        hb_port=hb_port,
                        ip=ip,
                        key=key,
                        transport=transport,
                        signature_scheme=signature_scheme)

            # Create kernel client
            kernel_client = BlockingKernelClient()
            kernel_client.load_connection_info(info)
            kernel_client.start_channels()
        except KeyError:
            # Create a console kernel to interact with, so this
            # kernel can stand on its own.
            # *Note*: This is useful for testing purposes only!
            from jupyter_client.manager import KernelManager
            kernel_manager = KernelManager(kernel_name='spyder_console')
            kernel_manager.start_kernel()
            kernel_client = kernel_manager.client()

            # Register a Pdb instance so that PdbProxy can work
            kernel_client.execute('import pdb; p=pdb.Pdb(); p.init()',
                                  silent=True)

        return kernel_client
