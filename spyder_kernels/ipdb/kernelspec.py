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

        info = get_ipython().kernel._get_connection_info()

        env_vars = {
            'SPY_CONSOLE_SHELL_PORT': info['shell_port'],
            'SPY_CONSOLE_IOPUB_PORT': info['iopub_port'],
            'SPY_CONSOLE_STDIN_PORT': info['stdin_port'],
            'SPY_CONSOLE_CONTROL_PORT': info['control_port'],
            'SPY_CONSOLE_HB_PORT': info['hb_port'],
            'SPY_CONSOLE_IP': info['ip'],
            'SPY_CONSOLE_KEY': info['key'],
            'SPY_CONSOLE_TRANSPORT': info['transport'],
            'SPY_CONSOLE_SIGNATURE_SCHEME': info['signature_scheme'],
        }

        # Making all env_vars strings
        for key,var in iteritems(env_vars):
            if PY2:
                unicode_var = to_text_string(var)
                env_vars[key] = to_binary_string(unicode_var,
                                                 encoding='utf-8')
            else:
                env_vars[key] = to_text_string(var)
        return env_vars
