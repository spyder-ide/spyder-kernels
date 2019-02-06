# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""Tests for spydercustomize.py."""

# Stdlib imports
import sys

# Third party imports
import pytest

# Local imports
from spyder_kernels.customize.spydercustomize import UserModuleReloader
from spyder_kernels.py3compat import to_text_string


@pytest.fixture
def user_module(tmpdir):
    """Create a simple module in tmpdir as an example of a user module."""
    sys.path.append(to_text_string(tmpdir))
    modfile = tmpdir.mkdir('foo').join('bar.py')
    code = """
def square(x):
    return x**2
"""
    modfile.write(code)

    init_file = tmpdir.join('foo').join('__init__.py')
    init_file.write('#')


def test_umr_run(user_module):
    """Test that UMR's run method is working correctly."""
    umr = UserModuleReloader()

    from foo.bar import square
    umr.run(verbose=True)
    umr.modnames_to_reload == ['foo', 'foo.bar']


def test_umr_previous_modules():
    """Test that UMR's previos_modules is working as expected."""
    umr = UserModuleReloader()

    import scipy
    assert 'IPython' in umr.previous_modules
    assert 'scipy' not in umr.previous_modules


def test_umr_namelist():
    """Test that the UMR skips modules according to its name."""
    umr = UserModuleReloader()

    assert umr.is_module_in_namelist('tensorflow')
    assert umr.is_module_in_namelist('pytorch')
    assert umr.is_module_in_namelist('spyder_kernels')
    assert not umr.is_module_in_namelist('foo')


def test_umr_pathlist(user_module):
    """Test that the UMR skips modules according to its path."""
    umr = UserModuleReloader()

    # Don't reload stdlib modules
    import xml
    assert umr.is_module_in_pathlist(xml)

    # Don't reload third-party modules
    import numpy
    assert umr.is_module_in_pathlist(numpy)

    # Reload user modules
    import foo
    assert umr.is_module_in_pathlist(foo) == False
