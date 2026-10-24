# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

import os
from unittest.mock import MagicMock, patch

from spyder_kernels.customize.code_runner import SpyderCodeRunner


@patch("spyder_kernels.customize.code_runner.frontend_request", autospec=True)
def test_pylint_magic_failing(frontend_request: MagicMock):
	filename = os.path.dirname(__file__) + "/pylint_failing.py"

	code_runner = SpyderCodeRunner()
	code_runner.shell = MagicMock()
	code_runner.pylint(line=filename)

	frontend_request.assert_called_once_with(blocking=False)

	report_pylint = frontend_request.return_value.report_pylint
	report_pylint.assert_called_once()
	args, _ = report_pylint.call_args
	assert args[0] == filename
	assert len(args[1]) == 2
	assert any(msg["messageId"] == "C0304" for msg in args[1])
	assert any(msg["messageId"] == "C0114" for msg in args[1])

@patch("spyder_kernels.customize.code_runner.frontend_request", autospec=True)
def test_pylint_magic_passing(frontend_request: MagicMock):
	filename = os.path.dirname(__file__) + "/pylint_passing.py"

	code_runner = SpyderCodeRunner()
	code_runner.shell = MagicMock()
	code_runner.pylint(line=filename)

	frontend_request.assert_called_once_with(blocking=False)

	report_pylint = frontend_request.return_value.report_pylint
	report_pylint.assert_called_once_with(filename, [])
