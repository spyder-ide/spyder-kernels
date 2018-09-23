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
import sys

from ipykernel.eventloops import enable_gui
from IPython.core.completer import IPCompleter
from IPython.core.inputsplitter import IPythonInputSplitter
from IPython.core.interactiveshell import InteractiveShell
from IPython.core.debugger import BdbQuit_excepthook
from IPython.utils.tokenutil import token_at_cursor
from metakernel import MetaKernel

from spyder_kernels._version import __version__
from spyder_kernels.ipdb import backend_inline
from spyder_kernels.ipdb.spyderpdb import SpyderPdb
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


class DummyShell(object):
    """Dummy shell to pass to IPCompleter."""

    @property
    def magics_manager(self):
        """
        Create a dummy magics manager with the interface
        expected by IPCompleter.
        """
        class DummyMagicsManager(object):
            def lsmagic(self):
                return {'line': {}, 'cell': {}}

        return DummyMagicsManager()


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

        # Instantiate spyder_kernels.ipdb.spyderpdb.SpyderPdb here,
        # pass it a phony stdout that provides a dummy
        # flush() method and a write() method
        # that internally sends data using a function so that it can
        # be initialized to use self.send_response()
        sys.excepthook = functools.partial(BdbQuit_excepthook,
                                           excepthook=sys.excepthook)
        self.debugger = SpyderPdb(stdout=PhonyStdout(self._phony_stdout))
        self.debugger.reset()
        self.debugger.setup(sys._getframe().f_back, None)

        # Completer
        self.completer = IPCompleter(
                shell=DummyShell(),
                namespace=self._get_current_namespace()
        )
        self.completer.limit_to__all__ = False

        # To detect if a line is complete
        self.input_transformer_manager = IPythonInputSplitter(
                                             line_input_checker=False)

        # For the %matplotlib magic
        self.ipyshell = InteractiveShell()
        self.ipyshell.enable_gui = enable_gui
        self.mpl_gui = None

        # Add _get_kernel_
        builtins._get_kernel_ = self._get_kernel_

        self._remove_unneeded_magics()

    # --- MetaKernel API
    def do_execute_direct(self, code):
        """
        Execute code with the debugger.
        """
        # Process command:
        line = self.debugger.precmd(code)
        stop = self.debugger.default(line)
        stop = self.debugger.postcmd(stop, line)
        if stop:
            self.debugger.postloop()

        self._show_inline_figures()

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
        """
        Get completions from kernel based on info dict.
        """
        code = info["code"]
        # Update completer namespace before performing the
        # completion
        self.completer.namespace = self._get_current_namespace()

        if code.startswith('import') or code.startswith('from'):
            matches = module_completion(code)
        else:
            matches = self.completer.complete(text=None, line_buffer=code)[1]

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
            return self.debugger.do_help(cmd)

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

    def _get_current_namespace(self, with_magics=False):
        """Get current namespace."""
        glbs = self.debugger.curframe.f_globals
        lcls = self.debugger.curframe.f_locals
        ns = {}

        if glbs == lcls:
            ns = glbs
        else:
            ns = glbs.copy()
            ns.update(lcls)
        
        # Add magics to ns so we can show help about them on the Help
        # plugin
        if with_magics:
            line_magics = self.line_magics
            cell_magics = self.cell_magics
            ns.update(line_magics)
            ns.update(cell_magics)
        
        return ns

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
