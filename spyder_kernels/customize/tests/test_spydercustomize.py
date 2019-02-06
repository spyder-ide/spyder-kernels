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


def test_umr_namelist():
    """Test that the UMR skips modules according to its name."""
    umr = UserModuleReloader()

    assert umr.is_module_in_namelist('tensorflow')
    assert umr.is_module_in_namelist('pytorch')
    assert not umr.is_module_in_namelist('foo')


def test_umr_pathlist(tmpdir):
    """Test that the UMR skips modules according to its path."""
    umr = UserModuleReloader()

    # Don't reload stdlib modules
    import xml
    assert umr.is_module_in_pathlist(xml) == False

    # Don't reload third-party modules
    import numpy
    assert umr.is_module_in_pathlist(numpy) == False

    # Reload user modules
    sys.path.append(to_text_string(tmpdir))
    modfile = tmpdir.mkdir('foo').join('bar.py')
    code = """
def square(x):
    return x**2
"""
    modfile.write(code)

    init_file = tmpdir.join('foo').join('__init__.py')
    init_file.write('#')

    import foo
    assert umr.is_module_in_pathlist(foo)
