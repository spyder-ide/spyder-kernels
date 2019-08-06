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
import os
import sys

# Third-party imports
from ipykernel.ipkernel import IPythonKernel
from spyder_kernels.comms.frontendcomm import FrontendComm


PY2 = sys.version[0] == '2'

# Excluded variables from the Variable Explorer (i.e. they are not
# shown at all there)
EXCLUDED_NAMES = ['In', 'Out', 'exit', 'get_ipython', 'quit']


class SpyderKernel(IPythonKernel):
    """Spyder kernel for Jupyter"""

    def __init__(self, *args, **kwargs):
        super(SpyderKernel, self).__init__(*args, **kwargs)

        self.frontend_comm = FrontendComm(self)

        # All functions that can be called through the comm
        handlers = {
            'set_breakpoints': self.set_spyder_breakpoints,
            'get_value': self.get_value,
            'load_data': self.load_data,
            'save_namespace': self.save_namespace,
            'is_defined': self.is_defined,
            'get_doc': self.get_doc,
            'get_source': self.get_source,
            'set_value': self.set_value,
            'remove_value': self.remove_value,
            'copy_value': self.copy_value,
            'set_cwd': self.set_cwd,
            'get_cwd': self.get_cwd,
            'update_cwd': self.update_cwd,
            'get_syspath': self.get_syspath,
            'get_env': self.get_env,
            'close_all_mpl_figures': self.close_all_mpl_figures,
            'show_mpl_backend_errors': self.show_mpl_backend_errors,
            'update_namespace_view': self.update_namespace_view,
            'set_namespace_view_settings': self.set_namespace_view_settings,
            'update_var_properties': self.update_var_properties,
            }
        for call_id in handlers:
            self.frontend_comm.register_call_handler(
                call_id, handlers[call_id])

        self.namespace_view_settings = {}

        self._pdb_obj = None
        self._pdb_step = None
        self._do_publish_pdb_state = True
        self._mpl_backend_error = None

    def frontend_call(self, blocking=False, broadcast=True):
        """Call the frontend."""
        # If not broadcast, send only to the calling comm
        if broadcast:
            comm_id = None
        else:
            comm_id = self.frontend_comm.calling_comm_id

        return self.frontend_comm.remote_call(
            blocking=blocking, comm_id=comm_id)

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

    def set_spyder_breakpoints(self, breakpoints):
        """
        Handle a message from the frontend
        """
        if self._pdb_obj:
            self._pdb_obj.set_spyder_breakpoints(breakpoints)

    # -- Public API ---------------------------------------------------
    # --- For the Variable Explorer
    def set_namespace_view_settings(self, settings):
        """Set namespace_view_settings."""
        self.namespace_view_settings = settings

    def get_namespace_view(self):
        """
        Return the namespace view

        This is a dictionary with the following structure

        {'a': {'color': '#800000', 'size': 1, 'type': 'str', 'view': '1'}}

        Here:
        * 'a' is the variable name
        * 'color' is the color used to show it
        * 'size' and 'type' are self-evident
        * and'view' is its value or the text shown in the last column
        """
        from spyder_kernels.utils.nsview import make_remote_view

        settings = self.namespace_view_settings
        if settings:
            ns = self._get_current_namespace()
            view = make_remote_view(ns, settings, EXCLUDED_NAMES)
            return view
        else:
            return None

    def update_namespace_view(self):
        """Send updated namespace view."""
        view = self.get_namespace_view()
        self.frontend_call().set_namespace_view(view)

    def get_var_properties(self):
        """
        Get some properties of the variables in the current
        namespace
        """
        from spyder_kernels.utils.nsview import get_remote_data

        settings = self.namespace_view_settings
        if settings:
            ns = self._get_current_namespace()
            data = get_remote_data(ns, settings, mode='editable',
                                   more_excluded_names=EXCLUDED_NAMES)

            properties = {}
            for name, value in list(data.items()):
                properties[name] = {
                    'is_list':  isinstance(value, (tuple, list)),
                    'is_dict':  isinstance(value, dict),
                    'is_set': isinstance(value, set),
                    'len': self._get_len(value),
                    'is_array': self._is_array(value),
                    'is_image': self._is_image(value),
                    'is_data_frame': self._is_data_frame(value),
                    'is_series': self._is_series(value),
                    'array_shape': self._get_array_shape(value),
                    'array_ndim': self._get_array_ndim(value)
                }

            return properties
        else:
            return None

    def update_var_properties(self):
        """Send updated var properties."""
        properties = self.get_var_properties()
        self.frontend_call().set_var_properties(properties)

    def get_value(self, name):
        """Get the value of a variable"""
        ns = self._get_current_namespace()
        self._do_publish_pdb_state = False
        return ns[name]

    def set_value(self, name, value):
        """Set the value of a variable"""
        ns = self._get_reference_namespace(name)
        ns[name] = value
        self.log.debug(ns)

    def remove_value(self, name):
        """Remove a variable"""
        ns = self._get_reference_namespace(name)
        ns.pop(name)

    def copy_value(self, orig_name, new_name):
        """Copy a variable"""
        ns = self._get_reference_namespace(orig_name)
        ns[new_name] = ns[orig_name]

    def load_data(self, filename, ext):
        """Load data from filename"""
        from spyder_kernels.utils.iofuncs import iofunctions
        from spyder_kernels.utils.misc import fix_reference_name

        glbs = self._mglobals()

        load_func = iofunctions.load_funcs[ext]
        data, error_message = load_func(filename)

        if error_message:
            return error_message

        for key in list(data.keys()):
            new_key = fix_reference_name(key, blacklist=list(glbs.keys()))
            if new_key != key:
                data[new_key] = data.pop(key)

        try:
            glbs.update(data)
        except Exception as error:
            return str(error)

        return None

    def save_namespace(self, filename):
        """Save namespace into filename"""
        from spyder_kernels.utils.nsview import get_remote_data
        from spyder_kernels.utils.iofuncs import iofunctions

        ns = self._get_current_namespace()
        settings = self.namespace_view_settings
        data = get_remote_data(ns, settings, mode='picklable',
                               more_excluded_names=EXCLUDED_NAMES).copy()
        return iofunctions.save(data, filename)

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
            self.frontend_call(blocking=False).pdb_state(state)
        self._do_publish_pdb_state = True

    def pdb_continue(self):
        """
        Tell the console to run 'continue' after entering a
        Pdb session to get to the first breakpoint.

        Fixes issue 2034
        """
        if self._pdb_obj:
            self.frontend_call(blocking=False).pdb_continue()

    # --- For the Help plugin
    def is_defined(self, obj, force_import=False):
        """Return True if object is defined in current namespace"""
        from spyder_kernels.utils.dochelpers import isdefined

        ns = self._get_current_namespace(with_magics=True)
        return isdefined(obj, force_import=force_import, namespace=ns)

    def get_doc(self, objtxt):
        """Get object documentation dictionary"""
        try:
            import matplotlib
            matplotlib.rcParams['docstring.hardcopy'] = True
        except:
            pass
        from spyder_kernels.utils.dochelpers import getdoc

        obj, valid = self._eval(objtxt)
        if valid:
            return getdoc(obj)

    def get_source(self, objtxt):
        """Get object source"""
        from spyder_kernels.utils.dochelpers import getsource

        obj, valid = self._eval(objtxt)
        if valid:
            return getsource(obj)

    # --- Additional methods
    def set_cwd(self, dirname):
        """Set current working directory."""
        os.chdir(dirname)

    def get_cwd(self):
        """Get current working directory."""
        return os.getcwd()

    def update_cwd(self):
        """Send updated working directory."""
        cwd = self.get_cwd()
        self.frontend_call().remote_set_cwd(cwd)

    def get_syspath(self):
        """Return sys.path contents."""
        return sys.path[:]

    def get_env(self):
        """Get environment variables."""
        return os.environ.copy()

    def close_all_mpl_figures(self):
        """Close all Matplotlib figures."""
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
            del plt
        except:
            pass

    # -- Private API ---------------------------------------------------
    # --- For the Variable Explorer
    def _get_current_namespace(self, with_magics=False):
        """
        Return current namespace

        This is globals() if not debugging, or a dictionary containing
        both locals() and globals() for current frame when debugging
        """
        ns = {}
        glbs = self._mglobals()

        if self._pdb_frame is None:
            ns.update(glbs)
        else:
            ns.update(glbs)
            ns.update(self._pdb_locals)

        # Add magics to ns so we can show help about them on the Help
        # plugin
        if with_magics:
            line_magics = self.shell.magics_manager.magics['line']
            cell_magics = self.shell.magics_manager.magics['cell']
            ns.update(line_magics)
            ns.update(cell_magics)

        return ns

    def _get_reference_namespace(self, name):
        """
        Return namespace where reference name is defined

        It returns the globals() if reference has not yet been defined
        """
        glbs = self._mglobals()
        if self._pdb_frame is None:
            return glbs
        else:
            lcls = self._pdb_locals
            if name in lcls:
                return lcls
            else:
                return glbs

    def _mglobals(self):
        """Return current globals -- handles Pdb frames"""
        if self._pdb_frame is not None:
            return self._pdb_frame.f_globals
        else:
            return self.shell.user_ns

    def _get_len(self, var):
        """Return sequence length"""
        try:
            return len(var)
        except:
            return None

    def _is_array(self, var):
        """Return True if variable is a NumPy array"""
        try:
            import numpy
            return isinstance(var, numpy.ndarray)
        except:
            return False

    def _is_image(self, var):
        """Return True if variable is a PIL.Image image"""
        try:
            from PIL import Image
            return isinstance(var, Image.Image)
        except:
            return False

    def _is_data_frame(self, var):
        """Return True if variable is a DataFrame"""
        try:
            from pandas import DataFrame
            return isinstance(var, DataFrame)
        except:
            return False

    def _is_series(self, var):
        """Return True if variable is a Series"""
        try:
            from pandas import Series
            return isinstance(var, Series)
        except:
            return False

    def _get_array_shape(self, var):
        """Return array's shape"""
        try:
            if self._is_array(var):
                return var.shape
            else:
                return None
        except:
            return None

    def _get_array_ndim(self, var):
        """Return array's ndim"""
        try:
            if self._is_array(var):
                return var.ndim
            else:
                return None
        except:
            return None

    # --- For Pdb
    def _register_pdb_session(self, pdb_obj):
        """Register Pdb session to use it later"""
        self._pdb_obj = pdb_obj

    # --- For the Help plugin
    def _eval(self, text):
        """
        Evaluate text and return (obj, valid)
        where *obj* is the object represented by *text*
        and *valid* is True if object evaluation did not raise any exception
        """
        from spyder_kernels.py3compat import is_text_string

        assert is_text_string(text)
        ns = self._get_current_namespace(with_magics=True)
        try:
            return eval(text, ns), True
        except:
            return None, False

    # --- For Matplotlib
    def _set_mpl_backend(self, backend, pylab=False):
        """
        Set a backend for Matplotlib.

        backend: A parameter that can be passed to %matplotlib
                 (e.g. 'inline' or 'tk').
        """
        import traceback
        from IPython.core.getipython import get_ipython

        generic_error = (
            "\n" + "="*73 + "\n"
            "NOTE: The following error appeared when setting "
            "your Matplotlib backend!!\n" + "="*73 + "\n\n"
            "{0}"
        )

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
                if not backend in previous_backend.lower():
                    # Only inform about an error if the user selected backend
                    # and the one set by Matplotlib are different. Else this
                    # message is very confusing.
                    error = (
                        "\n"
                        "NOTE: Spyder *can't* set your selected Matplotlib "
                        "backend because there is a previous backend already "
                        "in use.\n\n"
                        "Your backend will be {0}".format(previous_backend)
                    )
                del matplotlib
            # This covers other RuntimeError's
            else:
                error = generic_error.format(traceback.format_exc())
        except Exception:
            error = generic_error.format(traceback.format_exc())

        self._mpl_backend_error = error

    def show_mpl_backend_errors(self):
        """Show Matplotlib backend errors after the prompt is ready."""
        if self._mpl_backend_error is not None:
            print(self._mpl_backend_error)  # spyder: test-skip

    # --- Others
    def _load_autoreload_magic(self):
        """Load %autoreload magic."""
        from IPython.core.getipython import get_ipython
        try:
            get_ipython().run_line_magic('reload_ext', 'autoreload')
            get_ipython().run_line_magic('autoreload', '2')
        except Exception:
            pass

    def _load_wurlitzer(self):
        """Load wurlitzer extension."""
        # Wurlitzer has no effect on Windows
        if not os.name == 'nt':
            from IPython.core.getipython import get_ipython
            # Enclose this in a try/except because if it fails the
            # console will be totally unusable.
            # Fixes spyder-ide/spyder#8668
            try:
                get_ipython().run_line_magic('reload_ext', 'wurlitzer')
            except Exception:
                pass
