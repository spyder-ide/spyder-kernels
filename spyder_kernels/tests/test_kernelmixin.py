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
from spyder_kernels.console.tests.test_console_kernel import (console_kernel
                                                              as ck)
from spyder_kernels.ipdb.tests.test_ipdb_kernel import ipdb_kernel as ik

from spyder_kernels.kernelmixin import PICKLE_PROTOCOL
from spyder_kernels.utils.iofuncs import iofunctions
from spyder_kernels.utils.test_utils import get_log_text

# Third-party imports
import cloudpickle

# =============================================================================
# Constants
# =============================================================================
FILES_PATH = os.path.dirname(os.path.realpath(__file__))
console__kernel = ck
ipdb_kernel = ik

# =============================================================================
# Tests
# =============================================================================
# --- For the Variable Explorer
def test_get_namespace_view(console_kernel, ipdb_kernel):
    """
    Test the namespace view of the kernel.
    """
    # Console kernel
    execute = console_kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    nsview = console_kernel.get_namespace_view()
    assert "'a':" in nsview
    assert "'type': 'int'" in nsview or "'type': u'int'" in nsview
    assert "'size': 1" in nsview
    assert "'color': '#0000ff'" in nsview
    assert "'view': '1'" in nsview

    # IPdb kernel    
    execute = ipdb_kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    nsview = ipdb_kernel.get_namespace_view()
    assert "'a':" in nsview
    assert "'type': 'int'" in nsview or "'type': u'int'" in nsview
    assert "'size': 1" in nsview
    assert "'color': '#0000ff'" in nsview
    assert "'view': '1'" in nsview


def test_get_var_properties(console_kernel, ipdb_kernel):
    """
    Test the properties fo the variables in the namespace.
    """
    # Console kernel
    execute = console_kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    var_properties = console_kernel.get_var_properties()
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

    # IPdb kernel
    execute = ipdb_kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    var_properties = ipdb_kernel.get_var_properties()
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
    


def test_send_spyder_msg(console_kernel, ipdb_kernel):
    """
    Test publishing custom messages to the Spyder frontend.
    """
    spyder_msg_type, content, data = 'TEST', None, None

    # Console kernel
    console_kernel.send_spyder_msg(spyder_msg_type, content, data)
    log_text = get_log_text(console_kernel)
    assert "{'spyder_msg_type': 'TEST'}" in log_text

    # IPdb kernel
    ipdb_kernel.send_spyder_msg(spyder_msg_type, content, data)
    log_text = get_log_text(ipdb_kernel)
    assert "{'spyder_msg_type': 'TEST'}" in log_text



def test_get_value(console_kernel, ipdb_kernel):
    """Test getting the value of a variable."""
    name = 'a'

    # Console kernel
    execute = console_kernel.do_execute("a = 1", True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    # Check data type send
    console_kernel.get_value(name)
    log_text = get_log_text(console_kernel)
    assert "{'spyder_msg_type': 'data'}" in log_text

    # IPdb kernel
    execute = ipdb_kernel.do_execute("a = 1", True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    # Check data type send
    console_kernel.get_value(name)
    log_text = get_log_text(ipdb_kernel)
    assert "{'spyder_msg_type': 'data'}" in log_text


def test_set_value(console_kernel, ipdb_kernel):
    """Test setting the value of a variable."""
    name = 'a'

    # Console kernel
    execute = console_kernel.do_execute('a = 0', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    value = [cloudpickle.dumps(10, protocol=PICKLE_PROTOCOL)]
    PY2_frontend = False
    console_kernel.set_value(name, value, PY2_frontend)
    log_text = get_log_text(console_kernel)
    assert "'__builtin__': <module " in log_text
    assert "'__builtins__': <module " in log_text
    assert "'_ih': ['']" in log_text
    assert "'_oh': {}" in log_text
    assert "'a': 10" in log_text

    # IPdb kernel
    execute = ipdb_kernel.do_execute('a = 0', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    value = [cloudpickle.dumps(10, protocol=PICKLE_PROTOCOL)]
    PY2_frontend = False
    console_kernel.set_value(name, value, PY2_frontend)
    log_text = get_log_text(ipdb_kernel)
    assert "'__builtin__': <module " in log_text
    assert "'__builtins__': <module " in log_text
    assert "'_ih': ['']" in log_text
    assert "'_oh': {}" in log_text
    assert "'a': 10" in log_text


def test_remove_value(console_kernel, ipdb_kernel):
    """Test the removal of a variable."""
    name = 'a'

    # Console kernel
    execute = console_kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    var_properties = console_kernel.get_var_properties()
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
    console_kernel.remove_value(name)
    var_properties = console_kernel.get_var_properties()
    assert var_properties == '{}'

    # IPdb kernel
    execute = ipdb_kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    var_properties = ipdb_kernel.get_var_properties()
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
    ipdb_kernel.remove_value(name)
    var_properties = ipdb_kernel.get_var_properties()
    assert var_properties == '{}'


def test_copy_value(console_kernel, ipdb_kernel):
    """Test the copy of a variable."""
    orig_name = 'a'
    new_name = 'b'

    # Console kernel
    execute = console_kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    var_properties = console_kernel.get_var_properties()
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
    console_kernel.copy_value(orig_name, new_name)
    var_properties = console_kernel.get_var_properties()
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

    # IPdb kernel
    execute = ipdb_kernel.do_execute('a = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    var_properties = ipdb_kernel.get_var_properties()
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
    ipdb_kernel.copy_value(orig_name, new_name)
    var_properties = ipdb_kernel.get_var_properties()
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


def test_load_data(console_kernel, ipdb_kernel):
    """Test loading data from filename."""
    namespace_file = osp.join(FILES_PATH, 'load_data.spydata')
    extention = '.spydata'

    # Console kernel
    console_kernel.load_data(namespace_file, extention)
    var_properties = console_kernel.get_var_properties()
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

    # Console IPdb
    ipdb_kernel.load_data(namespace_file, extention)
    var_properties = ipdb_kernel.get_var_properties()
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



def test_save_namespace(console_kernel, ipdb_kernel):
    """Test saving the namespace into filename."""
    namespace_file = osp.join(FILES_PATH, 'save_data.spydata')

    # Console kernel
    execute = console_kernel.do_execute('b = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    console_kernel.save_namespace(namespace_file)
    assert osp.isfile(namespace_file)
    load_func = iofunctions.load_funcs['.spydata']
    data, error_message = load_func(namespace_file)
    assert data == {'b': 1}
    assert not error_message
    os.remove(namespace_file)
    assert not osp.isfile(namespace_file)

    # IPkernel kernel
    execute = ipdb_kernel.do_execute('b = 1', True)
    assert execute == {'execution_count': 0, 'payload': [], 'status': 'ok',
                       'user_expressions': {}}
    ipdb_kernel.save_namespace(namespace_file)
    assert osp.isfile(namespace_file)
    load_func = iofunctions.load_funcs['.spydata']
    data, error_message = load_func(namespace_file)
    assert data == {'b': 1}
    assert not error_message
    os.remove(namespace_file)
    assert not osp.isfile(namespace_file)



# --- For the Help plugin
def test_is_defined(console_kernel, ipdb_kernel):
    """Test method to tell if object is defined."""
    obj = "debug"

    # Console kernel
    assert console_kernel.is_defined(obj)

    # IPdb kernel
    assert ipdb_kernel.is_defined(obj)



def test_get_doc(console_kernel, ipdb_kernel):
    """Test to get object documentation dictionary."""
    objtxt = 'help'

    # Console kernel
    assert "Define the builtin 'help'" in console_kernel.get_doc(
                                                        objtxt)['docstring']

    # IPdb kernel
    assert "Define the builtin 'help'" in ipdb_kernel.get_doc(
                                                        objtxt)['docstring']


def test_get_source(console_kernel, ipdb_kernel):
    """Test to get object source."""
    objtxt = 'help'

    # Console kernel
    assert 'class _Helper(object):' in console_kernel.get_source(objtxt)

    # IPdb kernel
    assert 'class _Helper(object):' in ipdb_kernel.get_source(objtxt)



if __name__ == "__main__":
    pytest.main()
