# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © 2018- Spyder Kernels Contributors
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Tests for the console kernel.
"""

# Standard library imports
import ast
import os

# Test imports
from ipykernel.tests.test_embed_kernel import setup_kernel
import IPython
import pytest

# Local imports
from spyder_kernels.console.kernel import ConsoleKernel
from spyder_kernels.utils.test_utils import get_kernel
from spyder_kernels.py3compat import PY3, to_text_string


# =============================================================================
# Constants
# =============================================================================
FILES_PATH = os.path.dirname(os.path.realpath(__file__))
TIMEOUT = 15


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def console_kernel(request):
    """Console kernel fixture"""
    # Get kernel instance
    kernel = get_kernel(kernel_class=ConsoleKernel)
    kernel.namespace_view_settings = {'check_all': False,
                                      'exclude_private': True,
                                      'exclude_uppercase': True,
                                      'exclude_capitalized': False,
                                      'exclude_unsupported': True,
                                      'excluded_names': ['nan', 'inf',
                                                         'infty',
                                                         'little_endian',
                                                         'colorbar_doc',
                                                         'typecodes',
                                                         '__builtins__',
                                                         '__main__',
                                                         '__doc__',
                                                         'NaN', 'Inf',
                                                         'Infinity',
                                                         'sctypes',
                                                         'rcParams',
                                                         'rcParamsDefault',
                                                         'sctypeNA', 'typeNA',
                                                         'False_', 'True_'],
                                      'minmax': False}
    # Teardown

    def reset_kernel():
        kernel.do_execute('reset -f', True)
    request.addfinalizer(reset_kernel)
    return kernel


# =============================================================================
# Tests
# =============================================================================
def test_magics(console_kernel):
    """Check available magics in the kernel."""
    line_magics = console_kernel.shell.magics_manager.magics['line']
    cell_magics = console_kernel.shell.magics_manager.magics['cell']
    for magic in ['alias', 'alias_magic', 'autocall', 'automagic', 'autosave',
                  'bookmark', 'cd', 'clear', 'colors',
                  'config', 'connect_info', 'debug',
                  'dhist', 'dirs', 'doctest_mode', 'ed', 'edit', 'env',
                  'gui', 'hist', 'history', 'killbgscripts', 'ldir', 'less',
                  'load', 'load_ext', 'loadpy', 'logoff', 'logon', 'logstart',
                  'logstate', 'logstop', 'ls', 'lsmagic', 'macro', 'magic',
                  'matplotlib', 'mkdir', 'more', 'notebook', 'page',
                  'pastebin', 'pdb', 'pdef', 'pdoc', 'pfile', 'pinfo',
                  'pinfo2', 'popd', 'pprint', 'precision', 'prun',
                  'psearch', 'psource', 'pushd', 'pwd', 'pycat', 'pylab',
                  'qtconsole', 'quickref', 'recall', 'rehashx', 'reload_ext',
                  'rep', 'rerun', 'reset', 'reset_selective', 'rmdir',
                  'run', 'save', 'sc', 'set_env', 'sx', 'system',
                  'tb', 'time', 'timeit', 'unalias', 'unload_ext',
                  'who', 'who_ls', 'whos', 'xdel', 'xmode']:
        msg = "magic '%s' is not in line_magics" % magic
        assert magic in line_magics, msg

    for magic in ['!', 'HTML', 'SVG', 'bash', 'capture', 'debug',
                  'file', 'html', 'javascript', 'js', 'latex', 'perl',
                  'prun', 'pypy', 'python', 'python2', 'python3',
                  'ruby', 'script', 'sh', 'svg', 'sx', 'system', 'time',
                  'timeit', 'writefile']:
        assert magic in cell_magics


# --- Other stuff
@pytest.mark.skipif(os.name == 'nt', reason="Doesn't work on Windows")
def test_output_from_c_libraries(console_kernel, capsys):
    """Test that the wurlitzer extension is working."""
    # This code was taken from the Wurlitzer demo
    code = """
import ctypes
libc = ctypes.CDLL(None)
libc.printf(('Hello from C\\n').encode('utf8'))
"""

    # Without Wurlitzer there's not output generated
    # by the kernel
    reply = console_kernel.do_execute(code, True)
    captured = capsys.readouterr()
    assert captured.out == ''

    # With Wurlitzer we have the expected output
    console_kernel._load_wurlitzer()
    reply = console_kernel.do_execute(code, True)
    captured = capsys.readouterr()
    assert captured.out == "Hello from C\n"


@pytest.mark.skipif(IPython.__version__ >= '7.2.0',
                    reason="This problem was fixed in IPython 7.2+")
def test_cwd_in_sys_path():
    """
    Test that cwd stays as the first element in sys.path after the
    kernel has started.
    """
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        msg_id = client.execute("import sys; sys_path = sys.path",
                                user_expressions={'output':'sys_path'})
        reply = client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Transform value obtained through user_expressions
        user_expressions = reply['content']['user_expressions']
        str_value = user_expressions['output']['data']['text/plain']
        value = ast.literal_eval(str_value)

        # Assert the first value of sys_path is an empty string
        assert value[0] == ''


@pytest.mark.skipif(not (os.name == 'nt' and PY3),
                    reason="Only meant for Windows and Python 3")
def test_multiprocessing(tmpdir):
    """
    Test that multiprocessing works on Windows and Python 3.
    """
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Remove all variables
        client.execute("%reset -f")
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Write multiprocessing code to a file
        code = """
from multiprocessing import Pool

def f(x):
    return x*x

if __name__ == '__main__':
    with Pool(5) as p:
        result = p.map(f, [1, 2, 3])
"""
        p = tmpdir.join("mp-test.py")
        p.write(code)

        # Run code
        client.execute("runfile(r'{}')".format(to_text_string(p)))
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Verify that the `result` variable is defined
        client.inspect('result')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']
        assert content['found']


def test_runcell(tmpdir):
    """Test the runcell command."""
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Write code with a cell to a file
        code = u"result = 10"
        p = tmpdir.join("cell-test.py")
        p.write(code)

        # Attach cell_code to the IPython shell instance to simulate
        # that the code was sent from Spyder's Editor
        client.execute(u"get_ipython().cell_code = '{}'".format(code))
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Execute runcell
        client.execute(u"runcell('', r'{}')".format(to_text_string(p)))
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Verify that the `result` variable is defined
        client.inspect('result')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        print(msg['content'])
        content = msg['content']
        assert content['found']


if __name__ == "__main__":
    pytest.main()
