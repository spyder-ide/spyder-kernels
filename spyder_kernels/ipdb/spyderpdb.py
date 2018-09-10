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
from spyder_kernels.py3compat import PY2

# Use ipydb as the debugger to patch on IPython consoles
from IPython.core.debugger import Pdb as ipyPdb
pdb.Pdb = ipyPdb

"""
Pdb custom Spyder class.
"""
class SpyderPdb(pdb.Pdb):

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
        if isinstance(fname, basestring) and isinstance(lineno, int):
            if osp.isfile(fname):
                step = dict(fname=fname, lineno=lineno)

        # Publish Pdb state so we can update the Variable Explorer
        # and the Editor on the Spyder side
        kernel._pdb_step = step
        kernel.publish_pdb_state()
