# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

from flaky import flaky
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


@flaky(max_runs=3)
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
    with qtbot.waitSignal(shell.executed, timeout=5000):
        shell.execute("import matplotlib.pyplot as plt; plt.plot(range(10))")

    # Assert that there's a plot in the console
    assert shell._control.toHtml().count('img src') == 1


@flaky(max_runs=3)
def test_matplotlib_qt(qtconsole, qtbot):
    """Test that %matplotlib qt is working."""
    window = qtconsole.window
    shell = window.active_frontend

    # Wait until the console is fully up
    qtbot.waitUntil(lambda: shell._prompt_html is not None,
                    timeout=SHELL_TIMEOUT)

    # Set qt backend
    with qtbot.waitSignal(shell.executed):
        shell.execute("%matplotlib qt")

    # Make a plot
    with qtbot.waitSignal(shell.executed, timeout=5000):
        shell.execute("import matplotlib.pyplot as plt; plt.plot(range(10))")

    # Assert we have three prompts in the console, meaning that the
    # previous plot command was non-blocking
    assert '3' in shell._prompt_html

    # Running QApplication.instance() should return a QApplication
    # object because "%matplotlib qt" creates one
    with qtbot.waitSignal(shell.executed):
        shell.execute("from PyQt5.QtWidgets import QApplication; QApplication.instance()")

    # Assert the previous command returns the object
    assert 'PyQt5.QtWidgets.QApplication object' in shell._control.toPlainText()


if __name__ == "__main__":
    pytest.main()
