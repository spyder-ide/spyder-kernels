# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""Utilities for conda environtment handling."""

# Standard imports
import json
import os
import os.path as osp
from subprocess import check_output
import sys

# Local library imports
from spyder_kernels.py3compat import to_text_string


def is_anaconda():
    """
    Detect if we are running under Anaconda.

    Taken from https://stackoverflow.com/a/47610844/438386
    """
    is_conda = osp.exists(osp.join(sys.prefix, 'conda-meta'))
    return is_conda


def get_conda_rootpath():
    """Get conda root path using 'conda info --json'."""
    try:
        conda_info = check_output('conda info --json')
        conda_info_json = json.loads(conda_info)
        return to_text_string(conda_info_json['env_vars']['CONDA_ROOT'])
    except Exception:
        return None


def get_win_conda_envpath():
    """Get directories to add to PATH for conda envs on Windows."""
    env_python_exec = sys.executable
    conda_root_path = get_conda_rootpath()

    # Environment PATH elements
    env_path = ''
    if env_python_exec:
        env_root_path = osp.dirname(to_text_string(env_python_exec))
        env_path = env_root_path + os.pathsep
        env_path += osp.join(env_root_path, u'Library', u'mingw-w64',
                             u'bin' + os.pathsep)
        env_path += osp.join(env_root_path, u'Library', u'usr',
                             u'bin' + os.pathsep)
        env_path += osp.join(env_root_path, u'Library', u'bin' + os.pathsep)
        env_path += osp.join(env_root_path, u'Scripts' + os.pathsep)
        env_path += osp.join(env_root_path, u'bin' + os.pathsep)

    # Root environment PATH elements
    root_path = ''
    if conda_root_path is not None:
        root_path = conda_root_path + os.pathsep
        root_path += osp.join(conda_root_path, u'Scripts' + os.pathsep)
        root_path += osp.join(conda_root_path, u'bin' + os.pathsep)

    return env_path + root_path
