# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from qtconsole.qtconsoleapp import JupyterQtConsoleApp
import pytest


SHELL_TIMEOUT = 20000


@pytest.fixture
def qtconsole(qtbot):
    """Qtconsole fixture."""
    # Create a console with the ipdb kernel
    console = JupyterQtConsoleApp()
    console.initialize(argv=['--kernel', 'spyder_console'])

    qtbot.addWidget(console.window)
    console.window.confirm_exit = False
    console.window.show()
    return console


def test_builtins(qtconsole, qtbot):
    """
    Test that our additions to builtins are in the kernel's namespace.
    """
    window = qtconsole.window
    shell = window.active_frontend

    # Wait until the console is fully up
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    # Set qt backend
    for builtin in ['runfile', 'debugfile', '_get_kernel_']:
        with qtbot.waitSignal(shell.executed):
            shell.execute(builtin)
        assert 'NameError' not in shell._control.toPlainText()
        assert builtin in shell._control.toPlainText()


if __name__ == "__main__":
    pytest.main()
