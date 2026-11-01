# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from pytest import fixture

@fixture(autouse=True)
def pylint_home():
	"""
	Fixture to isolate Pylint runs per test.

	Since Pylint checks PYLINTHOME at import time, for this to work Pylint must
	be imported dynamically within the test case.
	"""

	with (
		TemporaryDirectory() as temp_dir,
		patch.dict(os.environ, {"PYLINTHOME": temp_dir}),
	):
		yield temp_dir

@patch("spyder_kernels.customize.code_runner.frontend_request", autospec=True)
def test_pylint_magic_failing(frontend_request: MagicMock):
	from spyder_kernels.customize.code_runner import SpyderCodeRunner

	filename = str(Path(__file__).parent / "pylint_failing.py")

	code_runner = SpyderCodeRunner()
	code_runner.shell = MagicMock()
	code_runner.pylint(line=filename)

	frontend_request.assert_called_once_with(blocking=False)

	report_pylint = frontend_request.return_value.report_pylint
	report_pylint.assert_called_once()

	args, _ = report_pylint.call_args
	assert args[0] == filename
	assert len(args[1]["messages"]) == 2
	assert any(msg["messageId"] == "C0304" for msg in args[1]["messages"])
	assert any(msg["messageId"] == "C0114" for msg in args[1]["messages"])
	assert args[1]["statistics"]["score"] == 0
	assert args[1]["statistics"]["previousScore"] is None

@patch("spyder_kernels.customize.code_runner.frontend_request", autospec=True)
def test_pylint_magic_passing(frontend_request: MagicMock):
	from spyder_kernels.customize.code_runner import SpyderCodeRunner

	filename = str(Path(__file__).parent / "pylint_passing.py")

	code_runner = SpyderCodeRunner()
	code_runner.shell = MagicMock()
	code_runner.pylint(line=filename)

	frontend_request.assert_called_once_with(blocking=False)

	report_pylint = frontend_request.return_value.report_pylint
	report_pylint.assert_called_once()

	args, _ = report_pylint.call_args
	assert args[0] == filename
	assert len(args[1]["messages"]) == 0
	assert args[1]["statistics"]["score"] == 10
	assert args[1]["statistics"]["previousScore"] is None

@patch("spyder_kernels.customize.code_runner.frontend_request", autospec=True)
def test_pylint_magic_previous_score(frontend_request: MagicMock):
	from spyder_kernels.customize.code_runner import SpyderCodeRunner

	filename = str(Path(__file__).parent / "pylint_failing.py")

	code_runner = SpyderCodeRunner()
	code_runner.shell = MagicMock()
	code_runner.pylint(line=filename)
	code_runner.pylint(line=filename)

	assert len(frontend_request.call_args_list) == 2

	report_pylint = frontend_request.return_value.report_pylint
	args, _ = report_pylint.call_args
	assert args[1]["statistics"]["previousScore"] == 0
	assert args[1]["statistics"]["score"] == 0
