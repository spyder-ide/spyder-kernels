# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Spyder kernel for Jupyter
"""

# Standard library imports
import pickle

# Local imports
from spyder_kernels.kernelmixin import BaseKernelMixIn

# Third-party imports
from ipykernel.ipkernel import IPythonKernel


class ConsoleKernel(BaseKernelMixIn, IPythonKernel):
    """Spyder kernel for Jupyter"""

    def __init__(self, *args, **kwargs):
        super(ConsoleKernel, self).__init__(*args, **kwargs)

        self._pdb_obj = None
        self._pdb_step = None
        self._do_publish_pdb_state = True
        self._mpl_backend_error = None

    @property
    def _pdb_frame(self):
        """Return current Pdb frame if there is any"""
        if self._pdb_obj is not None and self._pdb_obj.curframe is not None:
            return self._pdb_obj.curframe

    @property
    def _pdb_locals(self):
        """
        Return current Pdb frame locals if available. Otherwise
        return an empty dictionary
        """
        if self._pdb_frame:
            return self._pdb_obj.curframe_locals
        else:
            return {}

    # --- For Pdb
    def publish_pdb_state(self):
        """
        Publish Variable Explorer state and Pdb step through
        send_spyder_msg.
        """
        if self._pdb_obj and self._do_publish_pdb_state:
            state = dict(namespace_view = self.get_namespace_view(),
                         var_properties = self.get_var_properties(),
                         step = self._pdb_step)
            self.send_spyder_msg('pdb_state', content={'pdb_state': state})
        self._do_publish_pdb_state = True

    def pdb_continue(self):
        """
        Tell the console to run 'continue' after entering a
        Pdb session to get to the first breakpoint.

        Fixes issue 2034
        """
        if self._pdb_obj:
            self.send_spyder_msg('pdb_continue')

    # --- Additional methods
    def close_all_mpl_figures(self):
        """Close all Matplotlib figures."""
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
            del plt
        except:
            pass

    # --- For Pdb
    def _register_pdb_session(self, pdb_obj):
        """Register Pdb session to use it later"""
        self._pdb_obj = pdb_obj

    def _set_spyder_breakpoints(self, breakpoints):
        """Set all Spyder breakpoints in an active pdb session"""
        if not self._pdb_obj:
            return

        # Breakpoints come serialized from Spyder. We send them
        # in a list of one element to be able to send them at all
        # in Python 2
        serialized_breakpoints = breakpoints[0]
        breakpoints = pickle.loads(serialized_breakpoints)

        self._pdb_obj.set_spyder_breakpoints(breakpoints)

    def _ask_spyder_for_breakpoints(self):
        if self._pdb_obj:
            self.send_spyder_msg('set_breakpoints')

    # --- For Matplotlib
    def _set_mpl_backend(self, backend, pylab=False):
        """
        Set a backend for Matplotlib.

        backend: A parameter that can be passed to %matplotlib
                 (e.g. inline or tk).
        """
        import traceback
        from IPython.core.getipython import get_ipython

        generic_error = ("\n"
                         "NOTE: The following error appeared when setting "
                         "your Matplotlib backend\n\n"
                         "{0}")

        magic = 'pylab' if pylab else 'matplotlib'

        error = None
        try:
            get_ipython().run_line_magic(magic, backend)
        except RuntimeError as err:
            # This catches errors generated by ipykernel when
            # trying to set a backend. See issue 5541
            if "GUI eventloops" in str(err):
                import matplotlib
                previous_backend = matplotlib.get_backend()
                error = ("\n"
                         "NOTE: Spyder *can't* set your selected Matplotlib "
                         "backend because there is a previous backend already "
                         "in use.\n\n"
                         "Your backend will be {0}".format(previous_backend))
                del matplotlib
            # This covers other RuntimeError's
            else:
                error = generic_error.format(traceback.format_exc())
        except Exception:
            error = generic_error.format(traceback.format_exc())

        self._mpl_backend_error = error

    def _show_mpl_backend_errors(self):
        """Show Matplotlib backend errors after the prompt is ready."""
        if self._mpl_backend_error is not None:
            print(self._mpl_backend_error)  # spyder: test-skip

    # --- Others
    def _load_autoreload_magic(self):
        """Load %autoreload magic."""
        from IPython.core.getipython import get_ipython
        get_ipython().run_line_magic('reload_ext', 'autoreload')
        get_ipython().run_line_magic('autoreload', '2')

    def _get_connection_file(self):
        """Get kernel's connection file."""
        from ipykernel import get_connection_file
        return get_connection_file()
