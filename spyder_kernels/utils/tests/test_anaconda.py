# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Tests for anaconda.py.
"""
# Standard library imports
import os

# Local library imports
import spyder_kernels.utils.anaconda as anaconda

# Third-party library imports
import pytest


# =============================================================================
# ---- Tests
# =============================================================================
def test_get_conda_rootpath():
    """
    Test to get the root path of the anaconda installation.
    """
    # Check if running with anaconda
    if anaconda.is_anaconda():
        conda_root_path = anaconda.get_conda_rootpath()
        if os.name == 'nt':
            assert conda_root_path == "C:\\conda"
        else:
            assert conda_root_path == "/home/circleci/miniconda"


def test_get_win_conda_envpath():
    """
    Test to get the conda environment base path.
    """
    # Check if running with anaconda in Windows
    if anaconda.is_anaconda() and os.name == 'nt':
        conda_envpath = anaconda.get_win_conda_envpath()
        if os.name == 'nt':
            expected_conda_envpath = (
                """C:\\conda\\envs\\test\\Library\\mingw-w64\\bin;"""
                """C:\\conda\\envs\\test\\Library\\usr\\bin;"""
                """C:\\conda\\envs\\test\\Library\\bin;"""
                """C:\\conda\\envs\\test\\Scripts;"""
                """C:\\conda\\envs\\test\\bin;"""
                """C:\\conda;"""
                """C:\\conda\\Scripts;"""
                """C:\\conda\\bin;""")
            assert conda_envpath == expected_conda_envpath


if __name__ == "__main__":
    pytest.main()
