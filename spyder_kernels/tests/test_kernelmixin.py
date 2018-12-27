# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © 2018- Spyder Kernels Contributors
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Tests for the kernel mixin.
"""

# Standard library imports
import os
import os.path as osp

# Test imports
import pytest

# Local imports
from spyder_kernels.console.kernel import ConsoleKernel
from spyder_kernels.ipdb.kernel import IPdbKernel
from spyder_kernels.kernelmixin import PICKLE_PROTOCOL
from spyder_kernels.utils.iofuncs import iofunctions
from spyder_kernels.utils.test_utils import get_kernel, get_log_text
from spyder_kernels.py3compat import PY2

# Third-party imports
import cloudpickle

# =============================================================================
# Constants
# =============================================================================
FILES_PATH = os.path.dirname(os.path.realpath(__file__))


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture(scope="module",
                params=[IPdbKernel,
                        ConsoleKernel])
def kernel(request):
    """Kernel fixture"""
    # Get kernel instance
    kernel = get_kernel(kernel_class=request.param)
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
        if request.param == ConsoleKernel:
            kernel.do_execute('reset -f', True)
        else:
            kernel.do_execute('%reset', True)

    request.addfinalizer(reset_kernel)
    return kernel


# =============================================================================
# Tests
# =============================================================================
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
    if osp.isfile(namespace_file):
        os.remove(namespace_file)
        assert not osp.isfile(namespace_file)
    execute = kernel.do_execute('b = 1', True)
    kernel.save_namespace(namespace_file)
    assert osp.isfile(namespace_file)
    load_func = iofunctions.load_funcs['.spydata']
    data, error_message = load_func(namespace_file)
    assert data['b'] == 1
    assert not error_message
    os.remove(namespace_file)
    assert not osp.isfile(namespace_file)


# --- For the Help plugin
def test_is_defined(kernel):
    """Test method to tell if object is defined."""
    obj = "eval"
    assert kernel.is_defined(obj)


def test_get_doc(kernel):
    """Test to get object documentation dictionary."""
    objtxt = 'eval'
    if PY2:
        assert "Evaluate the source" in kernel.get_doc(objtxt)['docstring']
    else:
        assert "Evaluate the given source" in kernel.get_doc(
                                                        objtxt)['docstring']


def test_get_source(kernel):
    """Test to get object source."""
    objtxt = 'help'
    if isinstance(kernel, ConsoleKernel):
        assert 'class _Helper(object):' in kernel.get_source(objtxt)
    else:
        assert 'class HelpMagic(Magic):' in kernel.get_source(objtxt)


if __name__ == "__main__":
    pytest.main()
