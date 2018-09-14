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
    console.initialize(argv=['--kernel', 'ipdb_kernel'])

    qtbot.addWidget(console.window)
    console.window.confirm_exit = False
    console.window.show()
    return console


def test_matplotlib_inline(qtconsole, qtbot):
    """Test that %matplotlib inline is working."""
    window = qtconsole.window
    shell = window.active_frontend

    # Wait until the console is fully up
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    # Set inline backend
    with qtbot.waitSignal(shell.executed):
        shell.execute("%matplotlib inline")

    # Make a plot
    with qtbot.waitSignal(shell.executed):
        shell.execute("import matplotlib.pyplot as plt; plt.plot(range(10))")

    # Assert that there's a plot in the console
    assert shell._control.toHtml().count('img src') == 1