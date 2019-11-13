#
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------
#
# IMPORTANT NOTE: Don't add a coding line here! It's not necessary for
# site files
#
# Spyder debugger
#
import bdb
import os
import pdb
import re
import sys
import sysconfig
import logging
import traceback

from IPython.core.getipython import get_ipython
from IPython.core.debugger import Pdb as ipyPdb

from spyder_kernels.py3compat import TimeoutError, PY2, _print, isidentifier
from spyder_kernels.comms.frontendcomm import CommError, _frontend_request

if not PY2:
    from IPython.core.inputtransformer2 import TransformerManager
    basestring = (str,)
else:
    from IPython.core.inputsplitter import IPythonInputSplitter as\
        TransformerManager


logger = logging.getLogger(__name__)


def create_pathlist():
    """
    Create list of Python library paths to be skipped from module
    reloading and Pdb steps.
    """
    # Get standard installation paths
    try:
        paths = sysconfig.get_paths()
        standard_paths = [paths['stdlib'],
                          paths['purelib'],
                          paths['scripts'],
                          paths['data']]
    except Exception:
        standard_paths = []

    # Get user installation path
    # See spyder-ide/spyder#8776
    try:
        import site
        if getattr(site, 'getusersitepackages', False):
            # Virtualenvs don't have this function but
            # conda envs do
            user_path = [site.getusersitepackages()]
        elif getattr(site, 'USER_SITE', False):
            # However, it seems virtualenvs have this
            # constant
            user_path = [site.USER_SITE]
        else:
            user_path = []
    except Exception:
        user_path = []

    return standard_paths + user_path


def path_is_library(path, initial_pathlist=None):
    """Decide if a path is in user code or a library according to its path."""
    # Compute DEFAULT_PATHLIST only once and make it global to reuse it
    # in any future call of this function.
    if 'DEFAULT_PATHLIST' not in globals():
        global DEFAULT_PATHLIST
        DEFAULT_PATHLIST = create_pathlist()

    if initial_pathlist is None:
        initial_pathlist = []

    pathlist = initial_pathlist + DEFAULT_PATHLIST

    if path is None:
        # Path probably comes from a C module that is statically linked
        # into the interpreter. There is no way to know its path, so we
        # choose to ignore it.
        return True
    elif any([p in path for p in pathlist]):
        # We don't want to consider paths that belong to the standard
        # library or installed to site-packages.
        return True
    elif not os.name == 'nt':
        # Paths containing the strings below can be part of the default
        # Linux installation, Homebrew or the user site-packages in a
        # virtualenv.
        patterns = [
            r'^/usr/lib.*',
            r'^/usr/local/lib.*',
            r'^/usr/.*/dist-packages/.*',
            r'^/home/.*/.local/lib.*',
            r'^/Library/.*',
            r'^/Users/.*/Library/.*',
            r'^/Users/.*/.local/.*',
        ]

        if [p for p in patterns if re.search(p, path)]:
            return True
        else:
            return False
    else:
        return False


# =============================================================================
# Pdb adjustments
# =============================================================================
class SpyderPdb(ipyPdb, object):  # Inherits `object` to call super() in PY2
    """
    Extends Pdb to add features:

     - Process ipython magic.
     - Accepts multiline input.
     - Option to process 'pre_execute' and 'post_execute' events.
     - Better interrupt signal handling.
     - Option to skip libraries while stepping.
     - Break into threads.
     - Add completion to non-command code.
    """

    send_initial_notification = True
    starting = True

    def __init__(self, completekey='tab', stdin=None, stdout=None,
                 skip=None, nosigint=False):
        """Init Pdb."""
        # Only set to true when calling debugfile
        self.continue_if_has_breakpoints = False
        self.pdb_ignore_lib = False
        self.pdb_execute_events = False
        super(SpyderPdb, self).__init__()
        self._pdb_breaking = False

    # --- Methods overriden for code execution
    def default(self, line):
        """
        Default way of running pdb statment.

        The only difference with Pdb.default is that if line contains multiple
        statments, the code will be compiled with 'exec'. It will not print the
        result but will run without failing.
        """
        execute_events = self.pdb_execute_events
        if line[:1] == '!':
            line = line[1:]
        locals = self.curframe_locals
        globals = self.curframe.f_globals
        try:
            line = TransformerManager().transform_cell(line)
            try:
                code = compile(line + '\n', '<stdin>', 'single')
            except SyntaxError:
                # support multiline statments
                code = compile(line + '\n', '<stdin>', 'exec')
            save_stdout = sys.stdout
            save_stdin = sys.stdin
            save_displayhook = sys.displayhook
            try:
                sys.stdin = self.stdin
                sys.stdout = self.stdout
                sys.displayhook = self.displayhook
                if execute_events:
                     get_ipython().events.trigger('pre_execute')
                exec(code, globals, locals)
                if execute_events:
                     get_ipython().events.trigger('post_execute')
            finally:
                sys.stdout = save_stdout
                sys.stdin = save_stdin
                sys.displayhook = save_displayhook
        except BaseException:
            if PY2:
                t, v = sys.exc_info()[:2]
                if type(t) == type(''):
                    exc_type_name = t
                else: exc_type_name = t.__name__
                print >>self.stdout, '***', exc_type_name + ':', v
            else:
                exc_info = sys.exc_info()[:2]
                self.error(
                    traceback.format_exception_only(*exc_info)[-1].strip())

    # --- Methods overriden for signal handling
    def sigint_handler(self, signum, frame):
        """
        Handle a sigint signal. Break on the frame above this one.

        This method is not present in python2 so this won't be called there.
        """
        if self.allow_kbdint:
            raise KeyboardInterrupt
        self.message("\nProgram interrupted. (Use 'cont' to resume).")
        # avoid stopping in set_trace
        sys.settrace(None)
        self._pdb_breaking = True
        self.set_step()
        self.set_trace(sys._getframe())

    def interaction(self, frame, traceback):
        """
        Called when a user interaction is required.

        If this is from sigint, break on the upper frame.
        If the frame is in spydercustomize.py, quit.
        Notifies spyder and print current code.

        """
        if self._pdb_breaking:
            self._pdb_breaking = False
            if frame and frame.f_back:
                return self.interaction(frame.f_back, traceback)
        if (frame is not None
                and "spydercustomize.py" in frame.f_code.co_filename):
            self.onecmd('exit')
        else:
            self.setup(frame, traceback)
            if self.send_initial_notification:
                self.notify_spyder(frame)
            if get_ipython().kernel._pdb_print_code:
                self.print_stack_entry(self.stack[self.curindex])
            self._cmdloop()
            self.forget()

    # --- Methods overriden for skipping libraries
    def stop_here(self, frame):
        """Check if pdb should stop here."""
        if not super(SpyderPdb, self).stop_here(frame):
            return False
        filename = frame.f_code.co_filename
        if filename.startswith('<'):
            # This is not a file
            return True
        if self.pdb_ignore_lib and path_is_library(filename):
            return False
        return True

    # --- Methods reimplemented for text complete
    def completenames(self, text, line, begidx, endidx):
        """
        Try to complete with command names, otherwise goes to default.
        """
        matched_names = super(SpyderPdb, self).completenames(
            text, line, begidx, endidx)
        matched_default = self.completedefault(text, line, begidx, endidx)
        return matched_names + matched_default

    def completedefault(self, text, line, begidx, endidx):
        """
        Default completion.
        """
        return self._complete_expression(text, line, begidx, endidx)

    # --- Method defined by us to respond to ipython complete protocol
    def do_complete(self, code, cursor_pos):
        """
        Respond to a complete request.
        """
        if cursor_pos is None:
            cursor_pos = len(code)

        # Get text to complete
        text = code[:cursor_pos].split(' ')[-1]
        # Choose pdb function to complete, based on cmd.py
        origline = code
        line = origline.lstrip()
        if not line:
            return
        stripped = len(origline) - len(line)
        begidx = cursor_pos - len(text) - stripped
        endidx = cursor_pos - stripped
        if begidx > 0:
            cmd, args, _ = self.parseline(line)
            if cmd == '':
                compfunc = self.completedefault
            else:
                try:
                    compfunc = getattr(self, 'complete_' + cmd)
                except AttributeError:
                    compfunc = self.completedefault
        elif line[0] != '!':
            compfunc = self.completenames
        else:
            compfunc = self.completedefault

        def is_name_or_composed(text):
            if not text or text[0] == '.':
                return False
            # We want to keep value.subvalue
            return isidentifier(text.replace('.', ''))

        while text and not is_name_or_composed(text):
            text = text[1:]
            begidx += 1

        matches = compfunc(text, line, begidx, endidx)

        return {'matches': matches,
                'cursor_end': cursor_pos,
                'cursor_start': cursor_pos - len(text),
                'metadata': {},
                'status': 'ok'}

    # --- Methods overriden by us for Spyder integration
    def preloop(self):
        """Ask Spyder for breakpoints before the first prompt is created."""
        try:
            _frontend_request(blocking=True).set_debug_state(True)
            pdb_settings = _frontend_request().get_pdb_settings()
            self.pdb_ignore_lib = pdb_settings['pdb_ignore_lib']
            self.pdb_execute_events = pdb_settings['pdb_execute_events']
            if self.starting:
                self.set_spyder_breakpoints(pdb_settings['breakpoints'])
        except (CommError, TimeoutError):
            logger.debug("Could not get breakpoints from the frontend.")

    def postloop(self):
        """Notifies spyder that the loop has ended."""
        try:
            _frontend_request(blocking=True).set_debug_state(False)
        except (CommError, TimeoutError):
            logger.debug("Could not send debugging state to the frontend.")
        super(SpyderPdb, self).postloop()

    def set_continue(self):
        """
        Stop only at breakpoints or when finished.

        Reimplemented to avoid stepping out of debugging if there are no
        breakpoints. We could add more later.
        """
        # Don't stop except at breakpoints or when finished
        self._set_stopinfo(self.botframe, None, -1)

    def reset(self):
        """
        Register Pdb session after reset.
        """
        super(SpyderPdb, self).reset()
        kernel = get_ipython().kernel
        kernel._register_pdb_session(self)

    def user_return(self, frame, return_value):
        """This function is called when a return trap is set here."""
        # This is useful when debugging in an active interpreter (otherwise,
        # the debugger will stop before reaching the target file)
        if self._wait_for_mainpyfile:
            if (self.mainpyfile != self.canonic(frame.f_code.co_filename)
                    or frame.f_lineno <= 0):
                return
            self._wait_for_mainpyfile = 0
        super(SpyderPdb, self).user_return(frame, return_value)

    def _cmdloop(self):
        """Modifies the error text."""
        while True:
            try:
                # keyboard interrupts allow for an easy way to cancel
                # the current command, so allow them during interactive input
                self.allow_kbdint = True
                self.cmdloop()
                self.allow_kbdint = False
                break
            except KeyboardInterrupt:
                _print("--KeyboardInterrupt--\n"
                       "For copying text while debugging, use Ctrl+Shift+C",
                       file=self.stdout)

    def postcmd(self, stop, line):
        """
        Notify spyder on any pdb command.

        Is that good or too lazy? i.e. is more specific behaviour desired?
        """
        if '!get_ipython().kernel' not in line:
            self.notify_spyder(self.curframe)
        return super(SpyderPdb, self).postcmd(stop, line)

    if PY2:
        def break_here(self, frame):
            """
            Breakpoints don't work for files with non-ascii chars in Python 2

            Fixes Issue 1484
            """
            from bdb import effective
            filename = self.canonic(frame.f_code.co_filename)
            try:
                filename = unicode(filename, "utf-8")
            except TypeError:
                pass
            if filename not in self.breaks:
                return False
            lineno = frame.f_lineno
            if lineno not in self.breaks[filename]:
                # The line itself has no breakpoint, but maybe the line is the
                # first line of a function with breakpoint set by function name
                lineno = frame.f_code.co_firstlineno
                if lineno not in self.breaks[filename]:
                    return False

            # flag says ok to delete temp. bp
            (bp, flag) = effective(filename, lineno, frame)
            if bp:
                self.currentbp = bp.number
                if (flag and bp.temporary):
                    self.do_clear(str(bp.number))
                return True
            else:
                return False

    # --- Methods defined by us for Spyder integration
    def set_spyder_breakpoints(self, breakpoints):
        """Set Spyder breakpoints."""
        self.clear_all_breaks()
        # -----Really deleting all breakpoints:
        for bp in bdb.Breakpoint.bpbynumber:
            if bp:
                bp.deleteMe()
        bdb.Breakpoint.next = 1
        bdb.Breakpoint.bplist = {}
        bdb.Breakpoint.bpbynumber = [None]
        # -----
        i = 0
        for fname, data in list(breakpoints.items()):
            for linenumber, condition in data:
                i += 1
                self.set_break(self.canonic(fname), linenumber,
                               cond=condition)

        # Jump to first breakpoint.
        # Fixes issue 2034
        if self.starting:
            # Only run this after a Pdb session is created
            self.starting = False

            # Get all breakpoints for the file we're going to debug
            frame = self.curframe
            if not frame:
                # We are not debugging, return. Solves #10290
                return
            lineno = frame.f_lineno
            breaks = self.get_file_breaks(frame.f_code.co_filename)

            # Do 'continue' if the first breakpoint is *not* placed
            # where the debugger is going to land.
            # Fixes issue 4681
            if (self.continue_if_has_breakpoints and
                    breaks and
                    lineno < breaks[0]):
                try:
                    get_ipython().kernel.pdb_continue()
                except (CommError, TimeoutError):
                    logger.debug(
                        "Could not send a Pdb continue call to the frontend.")

    def notify_spyder(self, frame):
        """Send kernel state to the frontend."""
        if not frame:
            return

        kernel = get_ipython().kernel

        # Get filename and line number of the current frame
        fname = self.canonic(frame.f_code.co_filename)
        if PY2:
            try:
                fname = unicode(fname, "utf-8")
            except TypeError:
                pass
        lineno = frame.f_lineno

        # Set step of the current frame (if any)
        step = {}
        if isinstance(fname, basestring) and isinstance(lineno, int):
            step = dict(fname=fname, lineno=lineno)

        # Publish Pdb state so we can update the Variable Explorer
        # and the Editor on the Spyder side
        kernel._pdb_step = step
        try:
            kernel.publish_pdb_state()
        except (CommError, TimeoutError):
            logger.debug("Could not send Pdb state to the frontend.")


pdb.Pdb = SpyderPdb
