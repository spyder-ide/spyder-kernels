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

# Test imports
from ipykernel.tests.test_embed_kernel import setup_kernel
import IPython
import pytest


# Local imports
from spyder_kernels.py3compat import PY3, to_text_string
from spyder_kernels.console.kernel import PICKLE_PROTOCOL
from spyder_kernels.utils.iofuncs import iofunctions
from spyder_kernels.utils.test_utils import get_kernel, get_log_text

# Third-party imports
import cloudpickle
import IPython

# =============================================================================
# Constants
# =============================================================================
FILES_PATH = os.path.dirname(os.path.realpath(__file__))
TIMEOUT = 15

TKINTER_INSTALLED = False
try:
    import tkinter
    TKINTER_INSTALLED = True
except:
    pass

# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def kernel(request):
    """Console kernel fixture"""
    # Get kernel instance
    kernel = get_kernel()
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
    execute = kernel.do_execute('a = 1', True)

    nsview = kernel.get_namespace_view()
    assert "'a':" in nsview
    assert "'type': 'int'" in nsview or "'type': u'int'" in nsview
    assert "'size': 1" in nsview
    assert "'color': '#0000ff'" in nsview
    assert "'view': '1'" in nsview


def test_get_var_properties(kernel):
    """
    Test the properties fo the variables in the namespace.
    """
    execute = kernel.do_execute('a = 1', True)

    var_properties = kernel.get_var_properties()
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


def test_send_spyder_msg(kernel):
    """
    Test publishing custom messages to the Spyder frontend.
    """
    spyder_msg_type, content, data = 'TEST', None, None
    kernel.send_spyder_msg(spyder_msg_type, content, data)
    log_text = get_log_text(kernel)
    assert "{'spyder_msg_type': 'TEST'}" in log_text


def test_get_value(kernel):
    """Test getting the value of a variable."""
    name = 'a'
    execute = kernel.do_execute("a = 1", True)

    # Check data type send
    kernel.get_value(name)
    log_text = get_log_text(kernel)
    assert "{'spyder_msg_type': 'data'}" in log_text


def test_set_value(kernel):
    """Test setting the value of a variable."""
    name = 'a'
    execute = kernel.do_execute('a = 0', True)

    value = [cloudpickle.dumps(10, protocol=PICKLE_PROTOCOL)]
    PY2_frontend = False
    kernel.set_value(name, value, PY2_frontend)
    log_text = get_log_text(kernel)
    assert "'__builtin__': <module " in log_text
    assert "'__builtins__': <module " in log_text
    assert "'_ih': ['']" in log_text
    assert "'_oh': {}" in log_text
    assert "'a': 10" in log_text


def test_remove_value(kernel):
    """Test the removal of a variable."""
    name = 'a'
    execute = kernel.do_execute('a = 1', True)

    var_properties = kernel.get_var_properties()
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
    var_properties = kernel.get_var_properties()
    assert var_properties == '{}'


def test_copy_value(kernel):
    """Test the copy of a variable."""
    orig_name = 'a'
    new_name = 'b'
    execute = kernel.do_execute('a = 1', True)

    var_properties = kernel.get_var_properties()
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
    var_properties = kernel.get_var_properties()
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


def test_load_data(kernel):
    """Test loading data from filename."""
    namespace_file = osp.join(FILES_PATH, 'load_data.spydata')
    extention = '.spydata'
    kernel.load_data(namespace_file, extention)
    var_properties = kernel.get_var_properties()
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
    execute = kernel.do_execute('b = 1', True)

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

    # Without Wurlitzer there's not output generated
    # by the kernel
    reply = kernel.do_execute(code, True)
    captured = capsys.readouterr()
    assert captured.out == ''

    # With Wurlitzer we have the expected output
    kernel._load_wurlitzer()
    reply = kernel.do_execute(code, True)
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


def test_runfile(tmpdir):
    """
    Test that runfile uses the proper name space for execution.
    """
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Remove all variables
        client.execute("%reset -f")
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Write defined variable code to a file
        code = u"result = 'hello world'"
        d = tmpdir.join("defined-test.py")
        d.write(code)

        # Write undefined variable code to a file
        code = dedent(u"""
        try:
            result3 = result
        except:
            result2 = 'hello world'
        """)
        u = tmpdir.join("undefined-test.py")
        u.write(code)

        # Run code
        client.execute("runfile(r'{}', current_namespace=False)"
                       .format(to_text_string(d)))
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Verify that the `result` variable is defined
        client.inspect('result')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']
        assert content['found']

        # Run code
        client.execute("runfile(r'{}', current_namespace=False)"
                       .format(to_text_string(u)))
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Verify that the `result2` variable is defined
        client.inspect('result2')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']
        assert content['found']

        # Run code
        client.execute("runfile(r'{}', current_namespace=True)"
                       .format(to_text_string(u)))
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']
        print(content)

        # Verify that the `result3` variable is defined
        client.inspect('result3')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']
        assert content['found']


def test_runcell(tmpdir):
    """Test the runcell command."""
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Write code with a cell to a file
        code = u"result = 10; fname = __file__"
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
        content = msg['content']
        assert content['found']

        # Verify that the `fname` variable is `cell-test.py`
        client.inspect('fname')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']
        assert "cell-test.py" in content['data']['text/plain']

        # Verify that the `__file__` variable is undefined
        client.inspect('__file__')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']
        assert not content['found']


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
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Create a big Numpy array and an array to check decimal format
        client.execute("""
x = np.random.rand(75000,5);
a = np.array([123412341234.123412341234])
""")
        client.get_shell_msg(block=True, timeout=TIMEOUT)
        
        # Assert that NumPy threshold, suppress and formatter
        # are the same as the ones set by the user
        client.execute("""
t = np.get_printoptions()['threshold'];
s = np.get_printoptions()['suppress'];
f = np.get_printoptions()['formatter']
""")
        client.get_shell_msg(block=True, timeout=TIMEOUT)
        
        # Check correct decimal format
        client.inspect('a')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']['data']['text/plain']
        assert "123412341234.12" in content

        # Check threshold value
        client.inspect('t')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']['data']['text/plain']
        assert "inf" in content

        # Check suppress value
        client.inspect('s')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']['data']['text/plain']
        assert "True" in content

        # Check formatter
        client.inspect('f')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']['data']['text/plain']
        assert "{'float_kind': <built-in method format of str object" in content

@pytest.mark.skipif(not TKINTER_INSTALLED,
                    reason="Doesn't work on Python installations without Tk")
def test_turtle_launch(tmpdir):
    """Test turtle scripts running in the same kernel."""
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Remove all variables
        client.execute("%reset -f")
        client.get_shell_msg(block=True, timeout=TIMEOUT)

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
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Verify that the `tess` variable is defined
        client.inspect('tess')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']
        assert content['found']

        # Write turtle code to a file
        code = code + "a = 10"

        p = tmpdir.join("turtle-test1.py")
        p.write(code)

        # Run code again
        client.execute("runfile(r'{}')".format(to_text_string(p)))
        client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Verify that the `a` variable is defined
        client.inspect('a')
        msg = client.get_shell_msg(block=True, timeout=TIMEOUT)
        content = msg['content']
        assert content['found']


def test_matplotlib_inline(kernel):
    """Test that the default backend for our kernels is 'inline'."""
    # Command to start the kernel
    cmd = "from spyder_kernels.console import start; start.main()"

    with setup_kernel(cmd) as client:
        # Get current backend
        code = "import matplotlib; backend = matplotlib.get_backend()"
        client.execute(code, user_expressions={'output': 'backend'})
        reply = client.get_shell_msg(block=True, timeout=TIMEOUT)

        # Transform value obtained through user_expressions
        user_expressions = reply['content']['user_expressions']
        str_value = user_expressions['output']['data']['text/plain']
        value = ast.literal_eval(str_value)

        # Assert backend is inline
        assert 'inline' in value


if __name__ == "__main__":
    pytest.main()
