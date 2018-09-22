# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.
#
# get_kernel_dict and write_kernel_spec are modified versions from
# ipykernel/kernelspec.py
# -----------------------------------------------------------------------------

"""
Functions to install the console kernelspec.

Note: For testing purposes only
"""

import json
import os
import os.path as osp
import sys
import tempfile

from jupyter_client.kernelspec import install_kernel_spec


def get_kernel_dict():
    """Construct dict for kernel.json"""
    return {
        'argv': [sys.executable, '-m', 'spyder_kernels.console', '-f',
                 '{connection_file}'],
        'display_name': 'Spyder Python %i' % sys.version_info[0],
        'language': 'python',
    }


def write_kernel_spec():
    """
    Write a kernel spec directory to `path`

    The path to the kernelspec is always returned.
    """
    # Create path
    path = osp.join(tempfile.mkdtemp(suffix='_kernel'), 'console')
    os.makedirs(path)

    # write kernel.json
    kernel_dict = get_kernel_dict()
    with open(osp.join(path, 'kernel.json'), 'w') as f:
        json.dump(kernel_dict, f, indent=1)

    return path


def main():
    """Install kernelspec."""
    path = write_kernel_spec()
    return install_kernel_spec(path, kernel_name='spyder_console', user=True)


if __name__ == '__main__':
    main()
