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
import os.path as osp
from textwrap import dedent
from contextlib import contextmanager
import time
from subprocess import Popen, PIPE
import sys
import inspect

# Test imports
import ipykernel
import IPython
import pytest
from flaky import flaky
from jupyter_core import paths
from jupyter_client import BlockingKernelClient
import numpy as np

# Local imports
from spyder_kernels.py3compat import PY2, PY3, to_text_string
from spyder_kernels.utils.iofuncs import iofunctions
from spyder_kernels.utils.test_utils import get_kernel, get_log_text
from spyder_kernels.customize.spyderpdb import SpyderPdb

# For ipykernel 6
try:
    import asyncio
except ImportError:
    pass

# =============================================================================
# Constants
# =============================================================================
FILES_PATH = os.path.dirname(os.path.realpath(__file__))
IPYKERNEL_6 = ipykernel.__version__[0] >= '6'
TIMEOUT = 15
SETUP_TIMEOUT = 60


@contextmanager
def setup_kernel(cmd):
    """start an embedded kernel in a subprocess, and wait for it to be ready

    This function was taken from the ipykernel project.
    We plan to remove it when dropping support for python 2.

    Yields
    -------
    client: jupyter_client.BlockingKernelClient connected to the kernel
    """
    kernel = Popen([sys.executable, '-c', cmd], stdout=PIPE, stderr=PIPE)
    try:
        connection_file = os.path.join(
            paths.jupyter_runtime_dir(),
            'kernel-%i.json' % kernel.pid,
        )
        # wait for connection file to exist, timeout after 5s
        tic = time.time()
        while not os.path.exists(connection_file) \
            and kernel.poll() is None \
            and time.time() < tic + SETUP_TIMEOUT:
            time.sleep(0.1)

        if kernel.poll() is not None:
            o,e = kernel.communicate()
            if not PY3 and isinstance(e, bytes):
                e = e.decode()
            raise IOError("Kernel failed to start:\n%s" % e)

        if not os.path.exists(connection_file):
            if kernel.poll() is None:
                kernel.terminate()
            raise IOError("Connection file %r never arrived" % connection_file)

        client = BlockingKernelClient(connection_file=connection_file)
        client.load_connection_file()
        client.start_channels()
        client.wait_for_ready()
        try:
            yield client
        finally:
            client.stop_channels()
    finally:
        kernel.terminate()


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def kernel(request):
    """Console kernel fixture"""
    # Get kernel instance
    kernel = get_kernel()
    kernel.namespace_view_settings = {
        'check_all': False,
        'exclude_private': True,
        'exclude_uppercase': True,
        'exclude_capitalized': False,
        'exclude_unsupported': False,
        'exclude_callables_and_modules': True,
        'excluded_names': [
            'nan',
            'inf',
            'infty',
            'little_endian',
            'colorbar_doc',
            'typecodes',
            '__builtins__',
            '__main__',
            '__doc__',
            'NaN',
            'Inf',
            'Infinity',
            'sctypes',
            'rcParams',
            'rcParamsDefault',
            'sctypeNA',
            'typeNA',
            'False_',
            'True_'
        ],
        'minmax': False
    }

    # Teardown
    def reset_kernel():
        if IPYKERNEL_6:
            asyncio.run(kernel.do_execute('reset -f', True))
        else:
            kernel.do_execute('reset -f', True)
    request.addfinalizer(reset_kernel)

    return kernel


# =============================================================================
# Tests
# =============================================================================
def test_magics(kernel):
    """Check available magics in the kernel."""
    line_magics = kernel.shell.magics_manager.magics['line']
    cell_magics = kernel.shell.magics_manager.magics['cell']
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


# --- For the Variable Explorer
def test_get_namespace_view(kernel):
    """
    Test the namespace view of the kernel.
    """
    if IPYKERNEL_6:
        execute = asyncio.run(kernel.do_execute('a = 1', True))
    else:
        execute = kernel.do_execute('a = 1', True)

    nsview = repr(kernel.get_namespace_view())
    assert "'a':" in nsview
    assert "'type': 'int'" in nsview or "'type': u'int'" in nsview
    assert "'size': 1" in nsview
    assert "'view': '1'" in nsview
    assert "'numpy_type': 'Unknown'" in nsview

    if PY3:
        assert "'python_type': 'int'" in nsview
    else:
        assert "'python_type': u'int'" in nsview


def test_get_var_properties(kernel):
    """
    Test the properties fo the variables in the namespace.
    """
    if IPYKERNEL_6:
        asyncio.run(kernel.do_execute('a = 1', True))
    else:
        kernel.do_execute('a = 1', True)

    var_properties = repr(kernel.get_var_properties())
    assert "'a'" in var_properties
    assert "'is_list': False" in var_properties
    assert "'is_dict': False" in var_properties
    assert "'len': None" in var_properties
    assert "'is_array': False" in var_properties
    assert "'is_image': False" in var_properties
    assert "'is_data_frame': False" in var_properties
    assert "'is_series': False" in var_properties
    assert "'array_shape': None" in var_properties
    assert "'array_ndim': None" in var_properties


def test_get_value(kernel):
    """Test getting the value of a variable."""
    name = 'a'
    if IPYKERNEL_6:
        asyncio.run(kernel.do_execute("a = 124", True))
    else:
        kernel.do_execute("a = 124", True)

    # Check data type send
    assert kernel.get_value(name) == 124


def test_set_value(kernel):
    """Test setting the value of a variable."""
    name = 'a'
    if IPYKERNEL_6:
         asyncio.run(kernel.do_execute('a = 0', True))
    else:
        kernel.do_execute('a = 0', True)
    value = 10
    kernel.set_value(name, value)
    log_text = get_log_text(kernel)
    assert "'__builtin__': <module " in log_text
    assert "'__builtins__': <module " in log_text
    assert "'_ih': ['']" in log_text
    assert "'_oh': {}" in log_text
    assert "'a': 10" in log_text


def test_remove_value(kernel):
    """Test the removal of a variable."""
    name = 'a'
    if IPYKERNEL_6:
        asyncio.run(kernel.do_execute('a = 1', True))
    else:
        kernel.do_execute('a = 1', True)

    var_properties = repr(kernel.get_var_properties())
    assert "'a'" in var_properties
    assert "'is_list': False" in var_properties
    assert "'is_dict': False" in var_properties
    assert "'len': None" in var_properties
    assert "'is_array': False" in var_properties
    assert "'is_image': False" in var_properties
    assert "'is_data_frame': False" in var_properties
    assert "'is_series': False" in var_properties
    assert "'array_shape': None" in var_properties
    assert "'array_ndim': None" in var_properties
    kernel.remove_value(name)
    var_properties = repr(kernel.get_var_properties())
    assert var_properties == '{}'


def test_copy_value(kernel):
    """Test the copy of a variable."""
    orig_name = 'a'
    new_name = 'b'
    if IPYKERNEL_6:
         asyncio.run(kernel.do_execute('a = 1', True))
    else:
        kernel.do_execute('a = 1', True)

    var_properties = repr(kernel.get_var_properties())
    assert "'a'" in var_properties
    assert "'is_list': False" in var_properties
    assert "'is_dict': False" in var_properties
    assert "'len': None" in var_properties
    assert "'is_array': False" in var_properties
    assert "'is_image': False" in var_properties
    assert "'is_data_frame': False" in var_properties
    assert "'is_series': False" in var_properties
    assert "'array_shape': None" in var_properties
    assert "'array_ndim': None" in var_properties
    kernel.copy_value(orig_name, new_name)
    var_properties = repr(kernel.get_var_properties())
    assert "'a'" in var_properties
    assert "'b'" in var_properties
    assert "'is_list': False" in var_properties
    assert "'is_dict': False" in var_properties
    assert "'len': None" in var_properties
    assert "'is_array': False" in var_properties
    assert "'is_image': False" in var_properties
    assert "'is_data_frame': False" in var_properties
    assert "'is_series': False" in var_properties
    assert "'array_shape': None" in var_properties
    assert "'array_ndim': None" in var_properties


@pytest.mark.parametrize(
    "load", [(True, "val1 = 0", {"val1": np.array(1)}),
             (False, "val1 = 0", {"val1": 0, "val1_000": np.array(1)})])
def test_load_npz_data(kernel, load):
    """Test loading data from npz filename."""
    namespace_file = osp.join(FILES_PATH, 'load_data.npz')
    extention = '.npz'
    overwrite, execute, variables = load

    if IPYKERNEL_6:
        asyncio.run(kernel.do_execute(execute, True))
    else:
        kernel.do_execute(execute, True)

    kernel.load_data(namespace_file, extention, overwrite=overwrite)
    for var, value in variables.items():
        assert value == kernel.get_value(var)


def test_load_data(kernel):
    """Test loading data from filename."""
    namespace_file = osp.join(FILES_PATH, 'load_data.spydata')
    extention = '.spydata'
    kernel.load_data(namespace_file, extention)
    var_properties = repr(kernel.get_var_properties())
    assert "'a'" in var_properties
    assert "'is_list': False" in var_properties
    assert "'is_dict': False" in var_properties
    assert "'len': None" in var_properties
    assert "'is_array': False" in var_properties
    assert "'is_image': False" in var_properties
    assert "'is_data_frame': False" in var_properties
    assert "'is_series': False" in var_properties
    assert "'array_shape': None" in var_properties
    assert "'array_ndim': None" in var_properties


def test_save_namespace(kernel):
    """Test saving the namespace into filename."""
    namespace_file = osp.join(FILES_PATH, 'save_data.spydata')

    if IPYKERNEL_6:
        asyncio.run(kernel.do_execute('b = 1', True))
    else:
        kernel.do_execute('b = 1', True)

    kernel.save_namespace(namespace_file)
    assert osp.isfile(namespace_file)
    load_func = iofunctions.load_funcs['.spydata']
    data, error_message = load_func(namespace_file)
    assert data == {'b': 1}
    assert not error_message
    os.remove(namespace_file)
    assert not osp.isfile(namespace_file)


# --- For the Help plugin
def test_is_defined(kernel):
    """Test method to tell if object is defined."""
    obj = "debug"
    assert kernel.is_defined(obj)


def test_get_doc(kernel):
    """Test to get object documentation dictionary."""
    objtxt = 'help'
    assert ("Define the builtin 'help'" in kernel.get_doc(objtxt)['docstring'] or
            "Define the built-in 'help'" in kernel.get_doc(objtxt)['docstring'])

def test_get_source(kernel):
    """Test to get object source."""
    objtxt = 'help'
    assert 'class _Helper(object):' in kernel.get_source(objtxt)


# --- Other stuff
@pytest.mark.skipif(os.name == 'nt', reason="Doesn't work on Windows")
def test_output_from_c_libraries(kernel, capsys):
    """Test that the wurlitzer extension is working."""
    # This code was taken from the Wurlitzer demo
    code = """
import ctypes
libc = ctypes.CDLL(None)
libc.printf(('Hello from C\\n').encode('utf8'))
"""

    # With Wurlitzer we have the expected output
    kernel._load_wurlitzer()

    if IPYKERNEL_6:
        asyncio.run(kernel.do_execute(code, True))
    else:
        kernel.do_execute(code, True)
    captured = capsys.readouterr()
    assert captured.out == "Hello from C\n"


@flaky(max_runs=3)
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
        reply = client.get_shell_msg(timeout=TIMEOUT)

        # Transform value obtained through user_expressions
        user_expressions = reply['content']['user_expressions']
        str_value = user_expressions['output']['data']['text/plain']
        value = ast.literal_eval(str_value)

        # Assert the first value of sys_path is an empty string
        assert '' in value


@flaky(max_runs=3)
@pytest.mark.skipif(not PY3,
                    reason="Only meant for Python 3")
def test_multiprocessing(tmpdir):
    """
    Test that multiprocessing works on Python 3.
    """
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Remove all variables
        client.execute("%reset -f")
        client.get_shell_msg(timeout=TIMEOUT)

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
        client.get_shell_msg(timeout=TIMEOUT)

        # Verify that the `result` variable is defined
        client.inspect('result')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']
        assert content['found']


@flaky(max_runs=3)
@pytest.mark.skipif(not PY3, reason="Only meant for Python 3")
def test_dask_multiprocessing(tmpdir):
    """
    Test that dask multiprocessing works on Python 3.
    """
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Remove all variables
        client.execute("%reset -f")
        client.get_shell_msg(timeout=TIMEOUT)

        # Write multiprocessing code to a file
        # Runs two times to verify that in the second case it doesn't break
        code = """
from dask.distributed import Client

if __name__=='__main__':
    client = Client()
    client.close()
    x = 'hello'
"""
        p = tmpdir.join("mp-test.py")
        p.write(code)

        # Run code two times
        client.execute("runfile(r'{}')".format(to_text_string(p)))
        client.get_shell_msg(timeout=TIMEOUT)

        client.execute("runfile(r'{}')".format(to_text_string(p)))
        client.get_shell_msg(timeout=TIMEOUT)

        # Verify that the `x` variable is defined
        client.inspect('x')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']
        assert content['found']


@flaky(max_runs=3)
def test_runfile(tmpdir):
    """
    Test that runfile uses the proper name space for execution.
    """
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Remove all variables
        client.execute("%reset -f")
        client.get_shell_msg(timeout=TIMEOUT)

        # Write defined variable code to a file
        code = u"result = 'hello world'; error # make an error"
        d = tmpdir.join("defined-test.py")
        d.write(code)

        # Write undefined variable code to a file
        code = dedent(u"""
        try:
            result3 = result
        except NameError:
            result2 = 'hello world'
        """)
        u = tmpdir.join("undefined-test.py")
        u.write(code)

        # Run code file `d` to define `result` even after an error
        client.execute("runfile(r'{}', current_namespace=False)"
                       .format(to_text_string(d)))
        client.get_shell_msg(timeout=TIMEOUT)

        # Verify that `result` is defined in the current namespace
        client.inspect('result')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']
        assert content['found']

        # Run code file `u` without current namespace
        client.execute("runfile(r'{}', current_namespace=False)"
                       .format(to_text_string(u)))
        client.get_shell_msg(timeout=TIMEOUT)

        # Verify that the variable `result2` is defined
        client.inspect('result2')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']
        assert content['found']

        # Run code file `u` with current namespace
        client.execute("runfile(r'{}', current_namespace=True)"
                       .format(to_text_string(u)))
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']

        # Verify that the variable `result3` is defined
        client.inspect('result3')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']
        assert content['found']

        # Verify that the variable `__file__` is undefined
        client.inspect('__file__')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']
        assert not content['found']


@flaky(max_runs=3)
def test_np_threshold(kernel):
    """Test that setting Numpy threshold doesn't make the Variable Explorer slow."""

    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:

        # Set Numpy threshold, suppress and formatter
        client.execute("""
import numpy as np;
np.set_printoptions(
    threshold=np.inf,
    suppress=True,
    formatter={'float_kind':'{:0.2f}'.format})
    """)
        client.get_shell_msg(timeout=TIMEOUT)

        # Create a big Numpy array and an array to check decimal format
        client.execute("""
x = np.random.rand(75000,5);
a = np.array([123412341234.123412341234])
""")
        client.get_shell_msg(timeout=TIMEOUT)

        # Assert that NumPy threshold, suppress and formatter
        # are the same as the ones set by the user
        client.execute("""
t = np.get_printoptions()['threshold'];
s = np.get_printoptions()['suppress'];
f = np.get_printoptions()['formatter']
""")
        client.get_shell_msg(timeout=TIMEOUT)

        # Check correct decimal format
        client.inspect('a')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']['data']['text/plain']
        assert "123412341234.12" in content

        # Check threshold value
        client.inspect('t')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']['data']['text/plain']
        assert "inf" in content

        # Check suppress value
        client.inspect('s')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']['data']['text/plain']
        assert "True" in content

        # Check formatter
        client.inspect('f')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']['data']['text/plain']
        assert "{'float_kind': <built-in method format of str object" in content


# We declare this constant immediately before the test, as determining
# that TURTLE_ACTIVE is True will briefly pop up a window, similar to the
# windows that will pop up during the test itself.
TURTLE_ACTIVE = False
try:
    import turtle
    turtle.Screen()
    turtle.bye()
    TURTLE_ACTIVE = True
except:
    pass

@flaky(max_runs=3)
@pytest.mark.skipif(not TURTLE_ACTIVE,
                    reason="Doesn't work on non-interactive settings or Python installations without Tk")
def test_turtle_launch(tmpdir):
    """Test turtle scripts running in the same kernel."""
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Remove all variables
        client.execute("%reset -f")
        client.get_shell_msg(timeout=TIMEOUT)

        # Write turtle code to a file
        code = """
import turtle
wn=turtle.Screen()
wn.bgcolor("lightgreen")
tess = turtle.Turtle() # Create tess and set some attributes
tess.color("hotpink")
tess.pensize(5)

tess.forward(80) # Make tess draw equilateral triangle
tess.left(120)
tess.forward(80)
tess.left(120)
tess.forward(80)
tess.left(120) # Complete the triangle

turtle.bye()
"""
        p = tmpdir.join("turtle-test.py")
        p.write(code)

        # Run code
        client.execute("runfile(r'{}')".format(to_text_string(p)))
        client.get_shell_msg(timeout=TIMEOUT)

        # Verify that the `tess` variable is defined
        client.inspect('tess')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']
        assert content['found']

        # Write turtle code to a file
        code = code + "a = 10"

        p = tmpdir.join("turtle-test1.py")
        p.write(code)

        # Run code again
        client.execute("runfile(r'{}')".format(to_text_string(p)))
        client.get_shell_msg(timeout=TIMEOUT)

        # Verify that the `a` variable is defined
        client.inspect('a')
        msg = client.get_shell_msg(timeout=TIMEOUT)
        content = msg['content']
        assert content['found']


@flaky(max_runs=3)
def test_matplotlib_inline(kernel):
    """Test that the default backend for our kernels is 'inline'."""
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Get current backend
        code = "import matplotlib; backend = matplotlib.get_backend()"
        client.execute(code, user_expressions={'output': 'backend'})
        reply = client.get_shell_msg(timeout=TIMEOUT)

        # Transform value obtained through user_expressions
        user_expressions = reply['content']['user_expressions']
        str_value = user_expressions['output']['data']['text/plain']
        value = ast.literal_eval(str_value)

        # Assert backend is inline
        assert 'inline' in value


def test_do_complete(kernel):
    """
    Check do complete works in normal and debugging mode.
    """
    if IPYKERNEL_6:
        asyncio.run(kernel.do_execute('abba = 1', True))
    else:
        kernel.do_execute('abba = 1', True)
    assert kernel.get_value('abba') == 1
    match = kernel.do_complete('ab', 2)
    assert 'abba' in match['matches']

    # test pdb
    pdb_obj = SpyderPdb()
    pdb_obj.curframe = inspect.currentframe()
    pdb_obj.completenames = lambda *ignore: ['baba']
    kernel.shell.pdb_session = pdb_obj
    match = kernel.do_complete('ba', 2)
    assert 'baba' in match['matches']
    pdb_obj.curframe = None


@pytest.mark.parametrize("exclude_callables_and_modules", [True, False])
@pytest.mark.parametrize("exclude_unsupported", [True, False])
def test_callables_and_modules(kernel, exclude_callables_and_modules,
                               exclude_unsupported):
    """
    Tests that callables and modules are in the namespace view only
    when the right options are passed to the kernel.
    """
    if IPYKERNEL_6:
        asyncio.run(kernel.do_execute('import numpy', True))
        asyncio.run(kernel.do_execute('a = 10', True))
        asyncio.run(kernel.do_execute('def f(x): return x', True))
    else:
        kernel.do_execute('import numpy', True)
        kernel.do_execute('a = 10', True)
        kernel.do_execute('def f(x): return x', True)

    settings = kernel.namespace_view_settings

    settings['exclude_callables_and_modules'] = exclude_callables_and_modules
    settings['exclude_unsupported'] = exclude_unsupported
    nsview = kernel.get_namespace_view()

    # Callables and modules should always be in nsview when the option
    # is active.
    if not exclude_callables_and_modules:
        assert 'numpy' in nsview.keys()
        assert 'f' in nsview.keys()
    else:
        assert 'numpy' not in nsview.keys()
        assert 'f' not in nsview.keys()

    # Other values should always be part of nsview
    assert 'a' in nsview.keys()

    # Restore settings for other tests
    settings['exclude_callables_and_modules'] = True
    settings['exclude_unsupported'] = False


def test_comprehensions_with_locals_in_pdb(kernel):
    """
    Test that evaluating comprehensions with locals works in Pdb.

    Also test that we use the right frame globals, in case the user
    wants to work with them.

    This is a regression test for spyder-ide/spyder#13909.
    """
    pdb_obj = SpyderPdb()
    pdb_obj.curframe = inspect.currentframe()
    pdb_obj.curframe_locals = pdb_obj.curframe.f_locals
    kernel.shell.pdb_session = pdb_obj

    # Create a local variable.
    kernel.shell.pdb_session.default('zz = 10')
    assert kernel.get_value('zz') == 10

    # Run a list comprehension with this variable.
    kernel.shell.pdb_session.default("compr = [zz * i for i in [1, 2, 3]]")
    assert kernel.get_value('compr') == [10, 20, 30]

    # Check that the variable is not reported as being part of globals.
    kernel.shell.pdb_session.default("in_globals = 'zz' in globals()")
    assert kernel.get_value('in_globals') == False

    pdb_obj.curframe = None
    pdb_obj.curframe_locals = None

def test_comprehensions_with_locals_in_pdb_2(kernel):
    """
    Test that evaluating comprehensions with locals works in Pdb.

    This is a regression test for spyder-ide/spyder#16790.
    """
    pdb_obj = SpyderPdb()
    pdb_obj.curframe = inspect.currentframe()
    pdb_obj.curframe_locals = pdb_obj.curframe.f_locals
    kernel.shell.pdb_session = pdb_obj

    # Create a local variable.
    kernel.shell.pdb_session.default('aa = [1, 2]')
    kernel.shell.pdb_session.default('bb = [3, 4]')
    kernel.shell.pdb_session.default('res = []')

    # Run a list comprehension with this variable.
    kernel.shell.pdb_session.default(
        "for c0 in aa: res.append([(c0, c1) for c1 in bb])")
    assert kernel.get_value('res') == [[(1, 3), (1, 4)], [(2, 3), (2, 4)]]

    pdb_obj.curframe = None
    pdb_obj.curframe_locals = None


def test_namespaces_in_pdb(kernel):
    """
    Test namespaces in pdb
    """
    # Define get_ipython for timeit
    get_ipython = lambda: kernel.shell
    kernel.shell.user_ns["test"] = 0
    pdb_obj = SpyderPdb()
    pdb_obj.curframe = inspect.currentframe()
    pdb_obj.curframe_locals = pdb_obj.curframe.f_locals
    kernel.shell.pdb_session = pdb_obj

    # Check adding something to globals works
    pdb_obj.default("globals()['test2'] = 0")
    assert pdb_obj.curframe.f_globals["test2"] == 0

    if PY2:
        # no error method in py2
        pdb_obj.curframe = None
        pdb_obj.curframe_locals = None
        return

    # Create wrapper to check for errors
    old_error = pdb_obj.error
    pdb_obj._error_occured = False
    def error_wrapper(*args, **kwargs):
        print(args, kwargs)
        pdb_obj._error_occured = True
        return old_error(*args, **kwargs)
    pdb_obj.error = error_wrapper

    # Test globals are visible
    pdb_obj.curframe.f_globals["test3"] = 0
    pdb_obj.default("%timeit test3")
    assert not pdb_obj._error_occured

    # Test locals are visible
    pdb_obj.curframe_locals["test4"] = 0
    pdb_obj.default("%timeit test4")
    assert not pdb_obj._error_occured

    # Test user namespace is not visible
    pdb_obj.default("%timeit test")
    assert pdb_obj._error_occured

    pdb_obj.curframe = None
    pdb_obj.curframe_locals = None


if __name__ == "__main__":
    pytest.main()
