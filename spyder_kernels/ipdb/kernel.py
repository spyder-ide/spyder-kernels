# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the BSD 3 clause license

"""
IPython debugger kernel
"""

import functools
import sys

from IPython.core.completer import Completer
from IPython.core.inputsplitter import IPythonInputSplitter
from IPython.core.debugger import BdbQuit_excepthook, Pdb
from metakernel import MetaKernel

from spyder_kernels._version import __version__


class PhonyStdout(object):

    def __init__(self, write_func):
        self._write_func = write_func

    def flush(self):
        pass

    def write(self, s):
        self._write_func(s)

    def close(self):
        pass


class IPdbKernel(MetaKernel):
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

        # Instantiate IPython.core.debugger.Pdb here, pass it a phony
        # stdout that provides a dummy flush() method and a write() method
        # that internally sends data using a function so that it can
        # be initialized to use self.send_response()
        write_func = lambda s: self.send_response(self.iopub_socket,
                                                  'stream',
                                                  {'name': 'stdout',
                                                   'text': s})
        sys.excepthook = functools.partial(BdbQuit_excepthook,
                                           excepthook=sys.excepthook)
        self.debugger = Pdb(stdout=PhonyStdout(write_func))
        self.debugger.reset()
        self.debugger.setup(sys._getframe().f_back, None)

        self.completer = Completer()
        self.completer.limit_to__all__ = False

        self.input_transformer_manager = IPythonInputSplitter(
                                             line_input_checker=False)

    def do_execute_direct(self, code):
        """
        Execute code with the debugger.
        """
        # Process command:
        line = self.debugger.precmd(code)
        stop = self.debugger.onecmd(line)
        stop = self.debugger.postcmd(stop, line)
        if stop:
            self.debugger.postloop()

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

    def get_completions(self, info):
        """
        Get completions from kernel based on info dict.
        """
        code = info["code"]
        if code[-1] == ' ':
            return []

        self.completer.namespace = self.debugger.curframe.f_globals.copy()
        self.completer.namespace.update(self.debugger.curframe.f_locals)

        if "." in code:
            matches = self.completer.attr_matches(code)
        else:
            matches = self.completer.global_matches(code)

        return matches

    def get_usage(self):
        return self.debugger.do_help(None)
