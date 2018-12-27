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
# Spyder consoles sitecustomize
#

from distutils.version import LooseVersion
import io
import os
import pdb
import shlex
import sys
import time
import warnings

from IPython.core.getipython import get_ipython

from spyder_kernels.ipdb.spyderpdb import SpyderPdb

# We are in Python 2?
PY2 = sys.version[0] == '2'


#==============================================================================
# sys.argv can be missing when Python is embedded, taking care of it.
# Fixes Issue 1473 and other crazy crashes with IPython 0.13 trying to
# access it.
#==============================================================================
if not hasattr(sys, 'argv'):
    sys.argv = ['']


#==============================================================================
# Main constants
#==============================================================================
IS_EXT_INTERPRETER = os.environ.get('SPY_EXTERNAL_INTERPRETER') == "True"


#==============================================================================
# Important Note:
#
# We avoid importing spyder here, so we are handling Python 3 compatiblity
# by hand.
#==============================================================================
def _print(*objects, **options):
    end = options.get('end', '\n')
    file = options.get('file', sys.stdout)
    sep = options.get('sep', ' ')
    string = sep.join([str(obj) for obj in objects])
    if not PY2:
        # Python 3
        local_dict = {}
        exec('printf = print', local_dict) # to avoid syntax error in Python 2
        local_dict['printf'](string, file=file, end=end, sep=sep)
    else:
        # Python 2
        if end:
            print >>file, string
        else:
            print >>file, string,


#==============================================================================
# Execfile functions
#
# The definitions for Python 2 on Windows were taken from the IPython project
# Copyright (C) The IPython Development Team
# Distributed under the terms of the modified BSD license
#==============================================================================
try:
    # Python 2
    import __builtin__ as builtins
    if os.name == 'nt':
        def encode(u):
            return u.encode('utf8', 'replace')
        def execfile(fname, glob=None, loc=None):
            loc = loc if (loc is not None) else glob
            scripttext = builtins.open(fname).read()+ '\n'
            # compile converts unicode filename to str assuming
            # ascii. Let's do the conversion before calling compile
            if isinstance(fname, unicode):
                filename = encode(fname)
            else:
                filename = fname
            exec(compile(scripttext, filename, 'exec'), glob, loc)
    else:
        def execfile(fname, *where):
            if isinstance(fname, unicode):
                filename = fname.encode(sys.getfilesystemencoding())
            else:
                filename = fname
            builtins.execfile(filename, *where)
except ImportError:
    # Python 3
    import builtins
    basestring = (str,)
    def execfile(filename, namespace):
        # Open a source file correctly, whatever its encoding is
        with open(filename, 'rb') as f:
            exec(compile(f.read(), filename, 'exec'), namespace)


#==============================================================================
# Setting console encoding (otherwise Python does not recognize encoding)
# for Windows platforms
#==============================================================================
if os.name == 'nt' and PY2:
    try:
        import locale, ctypes
        _t, _cp = locale.getdefaultlocale('LANG')
        try:
            _cp = int(_cp[2:])
            ctypes.windll.kernel32.SetConsoleCP(_cp)
            ctypes.windll.kernel32.SetConsoleOutputCP(_cp)
        except (ValueError, TypeError):
            # Code page number in locale is not valid
            pass
    except:
        pass


#==============================================================================
# Cython support
#==============================================================================
RUN_CYTHON = os.environ.get("SPY_RUN_CYTHON") == "True"
HAS_CYTHON = False

if RUN_CYTHON:
    try:
        __import__('Cython')
        HAS_CYTHON = True
    except Exception:
        pass

    if HAS_CYTHON:
        # Import pyximport to enable Cython files support for
        # import statement
        import pyximport
        pyx_setup_args = {}

        # Add Numpy include dir to pyximport/distutils
        try:
            import numpy
            pyx_setup_args['include_dirs'] = numpy.get_include()
        except Exception:
            pass

        # Setup pyximport and enable Cython files reload
        pyximport.install(setup_args=pyx_setup_args, reload_support=True)


#==============================================================================
# Prevent subprocess.Popen calls to create visible console windows on Windows.
# See issue #4932
#==============================================================================
if os.name == 'nt':
    import subprocess
    creation_flag = 0x08000000  # CREATE_NO_WINDOW

    class SubprocessPopen(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            kwargs['creationflags'] = creation_flag
            super(SubprocessPopen, self).__init__(*args, **kwargs)

    subprocess.Popen = SubprocessPopen

#==============================================================================
# Importing user's sitecustomize
#==============================================================================
try:
    import sitecustomize  #analysis:ignore
except:
    pass


#==============================================================================
# Add default filesystem encoding on Linux to avoid an error with
# Matplotlib 1.5 in Python 2 (Fixes Issue 2793)
#==============================================================================
if PY2 and sys.platform.startswith('linux'):
    def _getfilesystemencoding_wrapper():
        return 'utf-8'

    sys.getfilesystemencoding = _getfilesystemencoding_wrapper


#==============================================================================
# Set PyQt API to #2
#==============================================================================
if os.environ.get("QT_API") == 'pyqt':
    try:
        import sip
        for qtype in ('QString', 'QVariant', 'QDate', 'QDateTime',
                      'QTextStream', 'QTime', 'QUrl'):
            sip.setapi(qtype, 2)
    except:
        pass
else:
    try:
        os.environ.pop('QT_API')
    except KeyError:
        pass


#==============================================================================
# IPython kernel adjustments
#==============================================================================
# Patch unittest.main so that errors are printed directly in the console.
# See http://comments.gmane.org/gmane.comp.python.ipython.devel/10557
# Fixes Issue 1370
import unittest
from unittest import TestProgram
class IPyTesProgram(TestProgram):
    def __init__(self, *args, **kwargs):
        test_runner = unittest.TextTestRunner(stream=sys.stderr)
        kwargs['testRunner'] = kwargs.pop('testRunner', test_runner)
        kwargs['exit'] = False
        TestProgram.__init__(self, *args, **kwargs)
unittest.main = IPyTesProgram

# Ignore some IPython/ipykernel warnings
try:
    warnings.filterwarnings(action='ignore', category=DeprecationWarning,
                            module='ipykernel.ipkernel')
except:
    pass


#==============================================================================
# Pandas adjustments
#==============================================================================
try:
    import pandas as pd

    # Set Pandas output encoding
    pd.options.display.encoding = 'utf-8'

    # Filter warning that appears for DataFrames with np.nan values
    # Example:
    # >>> import pandas as pd, numpy as np
    # >>> pd.Series([np.nan,np.nan,np.nan],index=[1,2,3])
    # Fixes Issue 2991
    # For 0.18-
    warnings.filterwarnings(action='ignore', category=RuntimeWarning,
                            module='pandas.core.format',
                            message=".*invalid value encountered in.*")
    # For 0.18.1+
    warnings.filterwarnings(action='ignore', category=RuntimeWarning,
                            module='pandas.formats.format',
                            message=".*invalid value encountered in.*")
except:
    pass


# =============================================================================
# Numpy adjustments
# =============================================================================
try:
    # Filter warning that appears when users have 'Show max/min'
    # turned on and Numpy arrays contain a nan value.
    # Fixes Issue 7063
    # Note: It only happens in Numpy 1.14+
    warnings.filterwarnings(action='ignore', category=RuntimeWarning,
                            module='numpy.core._methods',
                            message=".*invalid value encountered in.*")
except:
    pass


# =============================================================================
# Multiprocessing adjustments
# =============================================================================
# This patch is only needed on Windows and Python 3
if os.name == 'nt' and not PY2:
    # This could fail with changes in Python itself, so we protect it
    # with a try/except
    try:
        import multiprocessing.spawn
        _old_preparation_data = multiprocessing.spawn.get_preparation_data

        def _patched_preparation_data(name):
            """
            Patched get_preparation_data to work when all variables are
            removed before execution.
            """
            try:
                return _old_preparation_data(name)
            except AttributeError:
                main_module = sys.modules['__main__']
                # Any string for __spec__ does the job
                main_module.__spec__ = ''
                return _old_preparation_data(name)

        multiprocessing.spawn.get_preparation_data = _patched_preparation_data
    except Exception:
        pass


#==============================================================================
# Pdb adjustments
#==============================================================================
pdb.Pdb = SpyderPdb


#==============================================================================
# User module reloader
#==============================================================================
class UserModuleReloader(object):
    """
    User Module Reloader (UMR) aims at deleting user modules
    to force Python to deeply reload them during import

    pathlist [list]: blacklist in terms of module path
    namelist [list]: blacklist in terms of module name
    """
    def __init__(self, namelist=None, pathlist=None):
        if namelist is None:
            namelist = []
        spy_modules = ['sitecustomize', 'spyder', 'spyderplugins']
        mpl_modules = ['matplotlib', 'tkinter', 'Tkinter']
        # Add other, necessary modules to the UMR blacklist
        # astropy: see issue 6962
        # pytorch: see issue 7041
        # fastmat: see issue 7190
        # pythoncom: see issue 7190
        other_modules = ['pytorch', 'pythoncom']
        if PY2:
            py2_modules = ['astropy', 'fastmat']
            other_modules = other_modules + py2_modules
        self.namelist = namelist + spy_modules + mpl_modules + other_modules

        if pathlist is None:
            pathlist = []
        self.pathlist = pathlist
        self.previous_modules = list(sys.modules.keys())

    def is_module_blacklisted(self, modname, modpath):
        if HAS_CYTHON:
            # Don't return cached inline compiled .PYX files
            return True
        for path in [sys.prefix]+self.pathlist:
            if modpath.startswith(path):
                return True
        else:
            return set(modname.split('.')) & set(self.namelist)

    def run(self, verbose=False):
        """
        Del user modules to force Python to deeply reload them

        Do not del modules which are considered as system modules, i.e.
        modules installed in subdirectories of Python interpreter's binary
        Do not del C modules
        """
        log = []
        for modname, module in list(sys.modules.items()):
            if modname not in self.previous_modules:
                modpath = getattr(module, '__file__', None)
                if modpath is None:
                    # *module* is a C module that is statically linked into the
                    # interpreter. There is no way to know its path, so we
                    # choose to ignore it.
                    continue
                if not self.is_module_blacklisted(modname, modpath):
                    log.append(modname)
                    del sys.modules[modname]
        if verbose and log:
            _print("\x1b[4;33m%s\x1b[24m%s\x1b[0m"\
                   % ("Reloaded modules", ": "+", ".join(log)))

__umr__ = None


#==============================================================================
# Handle Post Mortem Debugging and Traceback Linkage to Spyder
#==============================================================================
def clear_post_mortem():
    """
    Remove the post mortem excepthook and replace with a standard one.
    """
    ipython_shell = get_ipython()
    ipython_shell.set_custom_exc((), None)


def post_mortem_excepthook(type, value, tb):
    """
    For post mortem exception handling, print a banner and enable post
    mortem debugging.
    """
    clear_post_mortem()
    ipython_shell = get_ipython()
    ipython_shell.showtraceback((type, value, tb))
    p = pdb.Pdb(ipython_shell.colors)

    if not type == SyntaxError:
        # wait for stderr to print (stderr.flush does not work in this case)
        time.sleep(0.1)
        _print('*' * 40)
        _print('Entering post mortem debugging...')
        _print('*' * 40)
        #  add ability to move between frames
        p.send_initial_notification = False
        p.reset()
        frame = tb.tb_frame
        prev = frame
        while frame.f_back:
            prev = frame
            frame = frame.f_back
        frame = prev
        # wait for stdout to print
        time.sleep(0.1)
        p.interaction(frame, tb)


def set_post_mortem():
    """
    Enable the post mortem debugging excepthook.
    """
    def ipython_post_mortem_debug(shell, etype, evalue, tb,
               tb_offset=None):
        post_mortem_excepthook(etype, evalue, tb)
    ipython_shell = get_ipython()
    ipython_shell.set_custom_exc((Exception,), ipython_post_mortem_debug)

# Add post mortem debugging if requested and in a dedicated interpreter
# existing interpreters use "runfile" below
if "SPYDER_EXCEPTHOOK" in os.environ:
    set_post_mortem()


# ==============================================================================
# runfile and debugfile commands
# ==============================================================================
def _get_globals():
    """Return current namespace"""
    ipython_shell = get_ipython()
    return ipython_shell.user_ns


def run_umr():
    """Run the user module reloader."""
    global __umr__
    if os.environ.get("SPY_UMR_ENABLED", "").lower() == "true":
        if __umr__ is None:
            namelist = os.environ.get("SPY_UMR_NAMELIST", None)
            if namelist is not None:
                namelist = namelist.split(',')
            __umr__ = UserModuleReloader(namelist=namelist)
        else:
            verbose = os.environ.get("SPY_UMR_VERBOSE", "").lower() == "true"
            __umr__.run(verbose=verbose)


def runfile(filename, args=None, wdir=None, namespace=None, post_mortem=False):
    """
    Run filename
    args: command line arguments (string)
    wdir: working directory
    post_mortem: boolean, whether to enter post-mortem mode on error
    """
    try:
        filename = filename.decode('utf-8')
    except (UnicodeError, TypeError, AttributeError):
        # UnicodeError, TypeError --> eventually raised in Python 2
        # AttributeError --> systematically raised in Python 3
        pass
    run_umr()
    if args is not None and not isinstance(args, basestring):
        raise TypeError("expected a character buffer object")
    if namespace is None:
        namespace = _get_globals()
    namespace['__file__'] = filename
    sys.argv = [filename]
    if args is not None:
        for arg in shlex.split(args):
            sys.argv.append(arg)
    if wdir is not None:
        try:
            wdir = wdir.decode('utf-8')
        except (UnicodeError, TypeError, AttributeError):
            # UnicodeError, TypeError --> eventually raised in Python 2
            # AttributeError --> systematically raised in Python 3
            pass
        os.chdir(wdir)
    if post_mortem:
        set_post_mortem()
    if HAS_CYTHON:
        # Cython files
        with io.open(filename, encoding='utf-8') as f:
            ipython_shell = get_ipython()
            ipython_shell.run_cell_magic('cython', '', f.read())
    else:
        execfile(filename, namespace)

    clear_post_mortem()
    sys.argv = ['']
    namespace.pop('__file__')


builtins.runfile = runfile


def runcell(cellname, filename):
    """
    Run a code cell from an editor as a file.

    Currently looks for code in an `ipython` property called `cell_code`.
    This property must be set by the editor prior to calling this function.
    This function deletes the contents of `cell_code` upon completion.

    Parameters
    ----------
    cellname : str
        Used as a reference in the history log of which
        cell was run with the fuction. This variable is not used.
    filename : str
        Needed to allow for proper traceback links.
    """
    try:
        filename = filename.decode('utf-8')
    except (UnicodeError, TypeError, AttributeError):
        # UnicodeError, TypeError --> eventually raised in Python 2
        # AttributeError --> systematically raised in Python 3
        pass
    run_umr()
    ipython_shell = get_ipython()
    try:
        cell_code = ipython_shell.cell_code
    except AttributeError:
        _print("--Run Cell Error--\n"
               "Please use only through Spyder's Editor; "
               "shouldn't be called manually from the console")
        return

    # Trigger `post_execute` to exit the additional pre-execution.
    # See Spyder PR #7310.
    ipython_shell.events.trigger('post_execute')

    ipython_shell.run_cell(cell_code)
    del ipython_shell.cell_code


builtins.runcell = runcell


def debugfile(filename, args=None, wdir=None, post_mortem=False):
    """
    Debug filename
    args: command line arguments (string)
    wdir: working directory
    post_mortem: boolean, included for compatiblity with runfile
    """
    debugger = pdb.Pdb()
    filename = debugger.canonic(filename)
    debugger._wait_for_mainpyfile = 1
    debugger.mainpyfile = filename
    debugger._user_requested_quit = 0
    if os.name == 'nt':
        filename = filename.replace('\\', '/')
    debugger.run("runfile(%r, args=%r, wdir=%r)" % (filename, args, wdir))


builtins.debugfile = debugfile


#==============================================================================
# Add a _get_kernel_ function to builtins to get the current kernel
#==============================================================================
def _get_kernel_():
    return get_ipython().kernel

builtins._get_kernel_ = _get_kernel_


#==============================================================================
# Restoring original PYTHONPATH
#==============================================================================
try:
    os.environ['PYTHONPATH'] = os.environ['OLD_PYTHONPATH']
    del os.environ['OLD_PYTHONPATH']
except KeyError:
    pass
