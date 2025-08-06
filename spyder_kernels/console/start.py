# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
File used to start kernels for the IPython Console
"""

# Standard library imports
import os
import os.path as osp
import sys
import site

# Third-party imports
from IPython.core import release as ipython_release
from packaging.version import parse as parse_version


# Remove current directory from sys.path to prevent kernel crashes when people
# name Python files or modules with the same name as standard library modules.
# See spyder-ide/spyder#8007
# Inject it back into sys.path after all imports in this module but
# before the kernel is initialized
while '' in sys.path:
    sys.path.remove('')

# Local imports
from spyder_kernels.console.kernelapp import SpyderKernelApp
from spyder_kernels.utils.misc import is_module_installed


def import_spydercustomize():
    """Import our customizations into the kernel."""
    here = osp.dirname(__file__)
    parent = osp.dirname(here)
    customize_dir = osp.join(parent, 'customize')

    # Import our customizations
    site.addsitedir(customize_dir)
    import spydercustomize  # noqa

    # Remove our customize path from sys.path
    try:
        sys.path.remove(customize_dir)
    except ValueError:
        pass


def kernel_config():
    """Create a config object with IPython kernel options."""
    from IPython.core.application import get_ipython_dir
    from traitlets.config.loader import Config, load_pyconfig_files

    # ---- IPython config ----
    try:
        profile_path = osp.join(get_ipython_dir(), 'profile_default')
        cfg = load_pyconfig_files(['ipython_config.py',
                                   'ipython_kernel_config.py'],
                                  profile_path)
    except:
        cfg = Config()

    # ---- Spyder config ----
    spy_cfg = Config()

    # Enable/disable certain features for testing
    testing = os.environ.get('SPY_TESTING') == 'True'
    if testing:
        # Don't load nor save history in our IPython consoles.
        spy_cfg.HistoryAccessor.enabled = False

    # Jedi completer.
    jedi_o = os.environ.get('SPY_JEDI_O') == 'True'
    spy_cfg.IPCompleter.use_jedi = jedi_o

    # Clear terminal arguments input.
    # This needs to be done before adding the exec_lines that come from
    # Spyder, to avoid deleting the sys module if users want to import
    # it through them.
    # See spyder-ide/spyder#15788
    clear_argv = "import sys; sys.argv = ['']; del sys"
    spy_cfg.IPKernelApp.exec_lines = [clear_argv]

    # Prevent other libraries to change the breakpoint builtin.
    # This started to be a problem since IPykernel 6.3.0.
    if sys.version_info[0:2] >= (3, 7):
        spy_cfg.IPKernelApp.exec_lines.append(
            "import sys; import pdb; "
            "sys.breakpointhook = pdb.set_trace; "
            "del sys; del pdb"
        )

    if is_module_installed('matplotlib'):
        spy_cfg.IPKernelApp.matplotlib = "inline"

    # Autocall
    autocall_o = os.environ.get('SPY_AUTOCALL_O')
    if autocall_o is not None:
        spy_cfg.ZMQInteractiveShell.autocall = int(autocall_o)

    # To handle the banner by ourselves
    spy_cfg.ZMQInteractiveShell.banner1 = ''

    # To disable tips (for the moment) that are only available in IPython 9.0+
    if parse_version(ipython_release.version) >= parse_version("9.0"):
        spy_cfg.ZMQInteractiveShell.enable_tip = False

    # Greedy completer
    greedy_o = os.environ.get('SPY_GREEDY_O') == 'True'
    spy_cfg.IPCompleter.greedy = greedy_o

    # Disable the new mechanism to capture and forward low-level output
    # in IPykernel 6. For that we have Wurlitzer.
    spy_cfg.IPKernelApp.capture_fd_output = False

    # Merge IPython and Spyder configs. Spyder prefs will have prevalence
    # over IPython ones
    cfg._merge(spy_cfg)
    return cfg


def varexp(line):
    """
    Spyder's variable explorer magic

    Used to generate plots, histograms and images of the variables displayed
    on it.
    """
    ip = get_ipython()       #analysis:ignore
    funcname, name = line.split()
    try:
        import guiqwt.pyplot as pyplot
    except:
        import matplotlib.pyplot as pyplot
    pyplot.figure();
    getattr(pyplot, funcname[2:])(ip._get_current_namespace()[name])
    pyplot.show()


def main():
    # Remove this module's path from sys.path:
    try:
        sys.path.remove(osp.dirname(__file__))
    except ValueError:
        pass

    try:
        locals().pop('__file__')
    except KeyError:
        pass
    __doc__ = ''
    __name__ = '__main__'

    # Import our customizations into the kernel
    import_spydercustomize()

    # Create a kernelapp instance
    kernelapp = SpyderKernelApp.instance()

    # Set config
    try:
        kernelapp.config = kernel_config()
    except Exception:
        pass

    # Re-add current working directory path into sys.path after all of the
    # import statements, but before initializing the kernel.
    if '' not in sys.path:
        sys.path.insert(0, '')

    # Init app
    kernelapp.initialize()

    # Set our own magics
    kernelapp.shell.register_magic_function(varexp)

    # Set Pdb class to be used by %debug and %pdb.
    # This makes IPython consoles to use the class defined in our
    # sitecustomize instead of their default one.
    import pdb
    kernelapp.shell.InteractiveTB.debugger_cls = pdb.Pdb

    # Start the (infinite) kernel event loop.
    kernelapp.start()


if __name__ == '__main__':
    main()
