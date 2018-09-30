# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Kernelspec for IPdb kernels
"""

import sys

from IPython import get_ipython
from jupyter_client.kernelspec import KernelSpec

from spyder_kernels.py3compat import (PY2, iteritems, to_text_string,
                                      to_binary_string)


class IPdbKernelSpec(KernelSpec):
    """Kernelspec for IPdb kernels."""

    @property
    def argv(self):
        """Command to start the kernel."""

        # Command used to start kernels
        kernel_cmd = [
            sys.executable,
            '-m',
            'spyder_kernels.ipdb',
            '-f',
            '{connection_file}'
        ]

        return kernel_cmd

    @property
    def env(self):
        """Env vars for the kernel."""

        connection_file = get_ipython().kernel._get_connection_file()

        env_vars = {
            'SPY_CONSOLE_CONNECTION_FILE': connection_file
        }

        # Making all env_vars strings
        for key,var in iteritems(env_vars):
            if PY2:
                # Try to convert vars first to utf-8.
                try:
                    unicode_var = to_text_string(var)
                except UnicodeDecodeError:
                    # TODO: Fix this by moving to_unicode_from_fs
                    # from Spyder

                    # If that fails, try to use the file system
                    # encoding because one of our vars is our
                    # PYTHONPATH, and that contains file system
                    # directories
                    #try:
                    #    unicode_var = to_unicode_from_fs(var)
                    #except:
                        # If that also fails, make the var empty
                        # to be able to start Spyder.
                        # See https://stackoverflow.com/q/44506900/438386
                        # for details.
                    #    unicode_var = ''
                    pass
                env_vars[key] = to_binary_string(unicode_var,
                                                 encoding='utf-8')
            else:
                env_vars[key] = to_text_string(var)
        return env_vars
