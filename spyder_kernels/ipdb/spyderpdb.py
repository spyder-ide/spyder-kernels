# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------
# Standard library import
import bdb
import pdb
import os.path as osp

# local library imports
from spyder_kernels.py3compat import PY2, PY3
from spyder_kernels.utils.misc import monkeypatch_method

# Use ipydb as the debugger to patch on IPython consoles
from IPython.core.debugger import Pdb as ipyPdb
from IPython import get_ipython
pdb.Pdb = ipyPdb


class SpyderPdb(pdb.Pdb):
    """
    Pdb custom Spyder class.
    """

    send_initial_notification = True
    starting = True

    # --- Methods overriden by us
    def preloop(self):
        """Ask Spyder for breakpoints before the first prompt is created."""
        if self.starting:
            get_ipython().kernel._ask_spyder_for_breakpoints()

    # --- Methods defined by us
    def set_spyder_breakpoints(self, breakpoints):
        self.clear_all_breaks()
        #------Really deleting all breakpoints:
        for bp in bdb.Breakpoint.bpbynumber:
            if bp:
                bp.deleteMe()
        bdb.Breakpoint.next = 1
        bdb.Breakpoint.bplist = {}
        bdb.Breakpoint.bpbynumber = [None]
        #------
        i = 0
        for fname, data in list(breakpoints.items()):
            if osp.isfile(fname):
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
            lineno = frame.f_lineno
            breaks = self.get_file_breaks(frame.f_code.co_filename)

            # Do 'continue' if the first breakpoint is *not* placed
            # where the debugger is going to land.
            # Fixes issue 4681
            if breaks and lineno != breaks[0] and osp.isfile(fname):
                get_ipython().kernel.pdb_continue()

    def notify_spyder(self, frame):
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
        try:            
            # Needed since basestring was removed in python 3
            basestring
        except NameError:
            basestring = str
        if isinstance(fname, basestring) and isinstance(lineno, int):
            if osp.isfile(fname):
                step = dict(fname=fname, lineno=lineno)

        # Publish Pdb state so we can update the Variable Explorer
        # and the Editor on the Spyder side
        kernel._pdb_step = step
        kernel.publish_pdb_state()


@monkeypatch_method(pdb.Pdb, 'Pdb')
def __init__(self, completekey='tab', stdin=None, stdout=None,
             skip=None, nosigint=False):
    self._old_Pdb___init__()


@monkeypatch_method(pdb.Pdb, 'Pdb')
def user_return(self, frame, return_value):
    """This function is called when a return trap is set here."""
    # This is useful when debugging in an active interpreter (otherwise,
    # the debugger will stop before reaching the target file)
    if self._wait_for_mainpyfile:
        if (self.mainpyfile != self.canonic(frame.f_code.co_filename)
            or frame.f_lineno<= 0):
            return
        self._wait_for_mainpyfile = 0
    self._old_Pdb_user_return(frame, return_value)


@monkeypatch_method(pdb.Pdb, 'Pdb')
def interaction(self, frame, traceback):
    if frame is not None and "spydercustomize.py" in frame.f_code.co_filename:
        self.run('exit')
    else:
        self.setup(frame, traceback)
        if self.send_initial_notification:
            self.notify_spyder(frame)
        self.print_stack_entry(self.stack[self.curindex])
        self._cmdloop()
        self.forget()


@monkeypatch_method(pdb.Pdb, 'Pdb')
def _cmdloop(self):
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


@monkeypatch_method(pdb.Pdb, 'Pdb')
def reset(self):
    self._old_Pdb_reset()
    kernel = get_ipython().kernel
    kernel._register_pdb_session(self)


#XXX: notify spyder on any pdb command (is that good or too lazy? i.e. is more
#     specific behaviour desired?)
@monkeypatch_method(pdb.Pdb, 'Pdb')
def postcmd(self, stop, line):
    if "_set_spyder_breakpoints" not in line:
        self.notify_spyder(self.curframe)
    return self._old_Pdb_postcmd(stop, line)


# Breakpoints don't work for files with non-ascii chars in Python 2
# Fixes Issue 1484
if PY2:
    @monkeypatch_method(pdb.Pdb, 'Pdb')
    def break_here(self, frame):
        from bdb import effective
        filename = self.canonic(frame.f_code.co_filename)
        try:
            filename = unicode(filename, "utf-8")
        except TypeError:
            pass
        if not filename in self.breaks:
            return False
        lineno = frame.f_lineno
        if not lineno in self.breaks[filename]:
            # The line itself has no breakpoint, but maybe the line is the
            # first line of a function with breakpoint set by function name.
            lineno = frame.f_code.co_firstlineno
            if not lineno in self.breaks[filename]:
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
