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
import os
import os.path as osp

# Test imports
import pytest

# Local imports
from spyder_kernels.console.kernel import PICKLE_PROTOCOL
from spyder_kernels.utils.iofuncs import iofunctions
from spyder_kernels.utils.test_utils import get_kernel, get_log_text

# Third-party imports
import cloudpickle

# =============================================================================
# Constants
# =============================================================================
FILES_PATH = os.path.dirname(os.path.realpath(__file__))


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

    def shutdown_kernel():
        kernel.do_execute('reset -f', True)
    request.addfinalizer(shutdown_kernel)
    return kernel


# =============================================================================
# Tests
# =============================================================================
def test_magics(kernel):
    """Check available magics in the kernel."""
    line_magics = kernel.shell.magics_manager.magics['line']
    cell_magics = kernel.shell.magics_manager.magics['cell']
    for magic in ['alias', 'alias_magic', 'autocall', 'automagic', 'autosave',
                  'bookmark', 'cd', 'clear', 'cls', 'colors',
                  'config', 'connect_info', 'copy', 'ddir', 'debug',
                  'dhist', 'dirs', 'doctest_mode', 'echo', 'ed', 'edit', 'env',
                  'gui', 'hist', 'history', 'killbgscripts', 'ldir', 'less',
                  'load', 'load_ext', 'loadpy', 'logoff', 'logon', 'logstart',
                  'logstate', 'logstop', 'ls', 'lsmagic', 'macro', 'magic',
                  'matplotlib', 'mkdir', 'more', 'notebook', 'page',
                  'pastebin', 'pdb', 'pdef', 'pdoc', 'pfile', 'pinfo',
                  'pinfo2', 'popd', 'pprint', 'precision', 'profile', 'prun',
                  'psearch', 'psource', 'pushd', 'pwd', 'pycat', 'pylab',
                  'qtconsole', 'quickref', 'recall', 'rehashx', 'reload_ext',
                  'ren', 'rep', 'rerun', 'reset', 'reset_selective', 'rmdir',
                  'run', 'save', 'sc', 'set_env', 'sx', 'system',
                  'tb', 'time', 'timeit', 'unalias', 'unload_ext',
                  'who', 'who_ls', 'whos', 'xdel', 'xmode']:
        msg = "magic '%s' is not in line_magics" % magic
        assert magic in line_magics, msg

    for magic in ['!', 'HTML', 'SVG', 'bash', 'capture', 'cmd', 'debug',
                  'file', 'html', 'javascript', 'js', 'latex', 'markdown',
                  'perl', 'prun', 'pypy', 'python', 'python2', 'python3',
                  'ruby', 'script', 'sh', 'svg', 'sx', 'system', 'time',
                  'timeit', 'writefile']:
        assert magic in cell_magics


# --- For the Variable Explorer
def test_get_namespace_view(kernel):
    """
    Test the namespace view of the kernel.
    """
    execute = kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    nsview = kernel.get_namespace_view()
    assert nsview == ("{'a': {'type': 'int', 'size': 1, 'color': "
                      "'#0000ff', 'view': '1'}}")


def test_get_var_properties(kernel):
    """
    Test the properties fo the variables in the namespace.
    """
    execute = kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    var_properties = kernel.get_var_properties()
    assert var_properties == ("{'a': {'is_list': False, 'is_dict': False, "
                              "'len': None, 'is_array': False, "
                              "'is_image': False, 'is_data_frame': False, "
                              "'is_series': False, 'array_shape': None, "
                              "'array_ndim': None}}")


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
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    # Check data type send
    kernel.get_value(name)
    log_text = get_log_text(kernel)
    assert "{'spyder_msg_type': 'data'}" in log_text


def test_set_value(kernel):
    """Test setting the value of a variable."""
    name = 'a'
    execute = kernel.do_execute('a = 0', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    value = [cloudpickle.dumps(10, protocol=PICKLE_PROTOCOL)]
    PY2_frontend = False
    kernel.set_value(name, value, PY2_frontend)
    log_text = get_log_text(kernel)
    assert ("'__builtin__': <module "
            "'builtins' (built-in)>, '__builtins__': <module 'builtins' "
            "(built-in)>, '_ih': [''], '_oh': {}") in log_text
    assert "'a': 10" in log_text


def test_remove_value(kernel):
    """Test the removal of a variable."""
    name = 'a'
    execute = kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    var_properties = kernel.get_var_properties()
    assert var_properties == ("{'a': {'is_list': False, 'is_dict': False, "
                              "'len': None, 'is_array': False, "
                              "'is_image': False, 'is_data_frame': False, "
                              "'is_series': False, 'array_shape': None, "
                              "'array_ndim': None}}")
    kernel.remove_value(name)
    var_properties = kernel.get_var_properties()
    assert var_properties == '{}'


def test_copy_value(kernel):
    """Test the copy of a variable."""
    orig_name = 'a'
    new_name = 'b'
    execute = kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    var_properties = kernel.get_var_properties()
    assert var_properties == ("{'a': {'is_list': False, 'is_dict': False, "
                              "'len': None, 'is_array': False, "
                              "'is_image': False, 'is_data_frame': False, "
                              "'is_series': False, 'array_shape': None, "
                              "'array_ndim': None}}")
    kernel.copy_value(orig_name, new_name)
    var_properties = kernel.get_var_properties()
    assert var_properties == ("{'a': {'is_list': False, 'is_dict': False, "
                              "'len': None, 'is_array': False, "
                              "'is_image': False, 'is_data_frame': False, "
                              "'is_series': False, 'array_shape': None, "
                              "'array_ndim': None}, "
                              "'b': {'is_list': False, 'is_dict': False, "
                              "'len': None, 'is_array': False, "
                              "'is_image': False, 'is_data_frame': False, "
                              "'is_series': False, 'array_shape': None, "
                              "'array_ndim': None}}")


def test_load_data(kernel):
    """Test loading data from filename."""
    namespace_file = osp.join(FILES_PATH, 'load_data.spydata')
    extention = '.spydata'
    kernel.load_data(namespace_file, extention)
    var_properties = kernel.get_var_properties()
    assert var_properties == ("{'a': {'is_list': False, 'is_dict': False, "
                              "'len': None, 'is_array': False, "
                              "'is_image': False, 'is_data_frame': False, "
                              "'is_series': False, 'array_shape': None, "
                              "'array_ndim': None}}")


def test_save_namespace(kernel):
    """Test saving the namespace into filename."""
    namespace_file = osp.join(FILES_PATH, 'save_data.spydata')
    execute = kernel.do_execute('b = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    kernel.save_namespace(namespace_file)
    assert osp.isfile(namespace_file)
    load_func = iofunctions.load_funcs['.spydata']
    data, error_message = load_func(namespace_file)
    assert data == {'b': 1}
    assert not error_message
    os.remove(namespace_file)
    assert not osp.isfile(namespace_file)


# --- For Pdb
def test_publish_pdb_state(kernel):
    """
    Test publishing Variable Explorer state and Pdb step through
    send_spyder_msg.
    """
    # TODO: initialize _obj_pdb
    pass


def test_pdb_continue(kernel):
    """Test pdb 'continue' message."""
    # TODO: initialize _obj_pdb
    pass


# --- For the Help plugin
def test_is_defined(kernel):
    """Test method to tell if object is defined."""
    obj = "debug"
    assert kernel.is_defined(obj)


def test_get_doc(kernel):
    """Test to get object documentation dictionary."""
    objtxt = 'help'
    assert "Define the builtin 'help'" in kernel.get_doc(objtxt)['docstring']


def test_get_source(kernel):
    """Test to get object source."""
    objtxt = 'help'
    assert 'class _Helper(object):' in kernel.get_source(objtxt)


if __name__ == "__main__":
    pytest.main()
