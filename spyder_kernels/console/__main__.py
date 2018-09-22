# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

import sys

if __name__ == '__main__':
    if sys.argv[-1] == 'install':
        from spyder_kernels.console import install
        install.main()
    else:
        from spyder_kernels.console import start
        start.main()
