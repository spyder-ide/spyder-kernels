# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
# Based on the tests in the Metakernel package
# See test_metakernel.py at
# https://github.com/Calysto/metakernel/metakernel/tests
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Tests for spyder_kernels.ipdb.kernel.py
"""

# Standart library imports
import os
import os.path as osp
import sys

# Test library imports
import pytest

# Local imports
from spyder_kernels.ipdb.kernel import IPdbKernel
from spyder_kernels.py3compat import PY2
from spyder_kernels.utils.test_utils import get_kernel, get_log_text


# =============================================================================
# Skip on Linux/Windows and our CIs because these tests time out too frequently
# =============================================================================
if os.environ.get('CI', None) is not None and not sys.platform == 'darwin':
    pytestmark = pytest.mark.skip


# =============================================================================
# Constants
# =============================================================================
FILES_PATH = osp.dirname(osp.realpath(__file__))


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def ipdb_kernel():
    """IPdb kernel fixture"""
    # Get kernel instance
    kernel = get_kernel(kernel_class=IPdbKernel, testing=True)
    return kernel


# =============================================================================
# Tests
# =============================================================================
def test_available_magics(ipdb_kernel):
    """Check the magics available for the kernel."""
    kernel = ipdb_kernel
    for magic in ['EOF', 'a', 'alias', 'args', 'b', 'break',
                  'bt', 'c', 'cd', 'cl', 'clear', 'commands', 'connect_info',
                  'cont', 'continue', 'd', 'disable',
                  'display', 'down', 'download', 'edit', 'enable',
                  'exit', 'help', 'html', 'ignore',
                  'interact', 'j', 'javascript',
                  'jump', 'l', 'latex',  'list',
                  'll', 'load', 'long_list', 'ls', 'lsmagic', 'magic',
                  'matplotlib', 'n', 'next', 'p', 'pdef', 'pdoc',
                  'pfile', 'pinfo', 'pinfo2', 'pp', 'psource',
                  'python', 'q', 'quit', 'r', 'reload_magics', 'restart',
                  'return', 'retval', 'rv', 's',
                  'shell', 'source', 'step', 'tbreak', 'u', 'unalias',
                  'undisplay', 'unt', 'until', 'up', 'w', 'whatis', 'where']:
        msg = "magic '%s' is not in line_magics" % magic
        assert magic in kernel.line_magics, msg

    for magic in ['file', 'html', 'javascript', 'latex', 'shell', 'time']:
        assert magic in kernel.cell_magics


def test_shell_magic(ipdb_kernel):
    """Test %shell magic."""
    kernel = ipdb_kernel
    with open('TEST.txt', 'wb'):
        pass
    if os.name != 'nt':
        kernel.get_magic('%shell ls')
    else:
        kernel.get_magic('%shell dir')
    log_text = get_log_text(kernel)
    assert 'TEST.txt' in log_text
    os.remove('TEST.txt')


@pytest.mark.skipif(os.name == 'nt',
                    reason="It's failing on Windows")
def test_break_magic(ipdb_kernel):
    """Test %break magic."""
    kernel = ipdb_kernel
    script_path = osp.join(FILES_PATH, 'script.py')
    if os.name == 'nt':
        script_path = osp.normcase(script_path)

    kernel.get_magic('%b ' + script_path + ':2')
    log_text = get_log_text(kernel)
    assert 'Blank or comment' in log_text

    kernel.get_magic('%break ' + script_path + ':9')
    log_text = get_log_text(kernel)
    assert 'Breakpoint 1 at' in log_text
    assert script_path in log_text


def test_down_magic(ipdb_kernel):
    """Test %down magic."""
    kernel = ipdb_kernel

    kernel.get_magic('%d')
    log_text = get_log_text(kernel)
    assert 'Newest frame' in log_text

    kernel.get_magic('%d')
    log_text = get_log_text(kernel)
    assert 'Newest frame' in log_text


def test_help(ipdb_kernel):
    """Check availability of help information."""
    kernel = ipdb_kernel
    resp = kernel.get_help_on('%shell', 0)
    assert 'run the line as a shell command' in resp

    resp = kernel.do_execute('%cd?', False)
    assert 'change current directory of session' in resp[
        'payload'][0]['data']['text/plain']

    resp = kernel.do_execute('range?', False)
    assert 'range(stop)' in resp[
        'payload'][0]['data']['text/plain']

    resp = kernel.get_help_on('what', 0)
    assert resp == None


def test_complete(ipdb_kernel):
    """Check completion."""
    kernel = ipdb_kernel

    # Line magics
    comp = kernel.do_complete('%connect_', len('%connect_'))
    assert comp['matches'] == ['%connect_info'], str(comp['matches'])

    # Cell magics
    comp = kernel.do_complete('%%fil', len('%%fil'))
    assert comp['matches'] == ['%%file'], str(comp['matches'])

    comp = kernel.do_complete('%%', len('%%'))
    assert '%%file' in comp['matches']
    assert '%%html' in comp['matches']

    # Regular completions
    comp = kernel.do_complete('imp', len('imp'))
    assert comp['matches'] == ['import'], str(comp['matches'])

    # Module completions
    comp = kernel.do_complete('import xm', len('import xm'))
    assert 'xml' in comp['matches']

    comp = kernel.do_complete('from numpy.linalg import ',
                              len('from numpy.linalg import '))
    assert 'norm' in comp['matches']

    # Assignment completions
    comp = kernel.do_complete('x = ran', len('x = ran'))
    assert 'range' in comp['matches']

    # Pdb commands should not be completed
    comp = kernel.do_complete('retv', len('retv'))
    assert comp['matches'] == []

    # Completion of function args
    comp = kernel.do_complete('display(', len('display('))
    kwargs = []
    for c in comp['matches']:
        if c.endswith('='):
            kwargs.append(c)
    if PY2:
        # display doesn't have named args in PY2
        assert kwargs == []
    else:
        assert kwargs != []


def test_inspect(ipdb_kernel):
    """Check inspect."""
    kernel = ipdb_kernel
    kernel.do_inspect('%lsmagic', len('%lsmagic'))
    log_text = get_log_text(kernel)
    assert "List currently available magic functions" in log_text

    kernel.do_inspect('%lsmagic ', len('%lsmagic') + 1)


def test_path_complete(ipdb_kernel):
    kernel = ipdb_kernel
    comp = kernel.do_complete('~/.ipytho', len('~/.ipytho'))
    if os.name != 'nt':
        assert 'ipython/' in comp['matches']
    else:
        assert comp['matches'] == ['"ipython\\"']

    paths = [p for p in os.listdir(os.getcwd())
             if not p.startswith('.') and '-' not in p]

    for path in paths:
        comp = kernel.do_complete(path, len(path) - 1)

        if osp.isdir(path):
            path = path.split()[-1]
            if os.name != 'nt':
                assert path + os.sep in comp['matches']
            else:
                assert '"' + path + os.sep + '"' in comp['matches']
        else:
            path = path.split()[-1]
            if os.name != 'nt':
                assert path in comp['matches'], (comp['matches'], path)
            else:
                assert '"' + path + '"' in comp['matches'], (comp['matches'],
                                                             path)


def test_ls_path_complete(ipdb_kernel):
    kernel = ipdb_kernel
    if os.name != 'nt':
        comp = kernel.do_complete('! ls ~/.ipytho', len('! ls ~/.ipytho'))
        assert comp['matches'] == ['ipython/'], comp
    else:
        comp = kernel.do_complete('! dir ~/.ipytho', len('! dir ~/.ipytho'))
        assert comp['matches'] == ['"ipython\\"'], comp


@pytest.mark.skipif(not sys.platform.startswith('linux'),
                    reason="Only for linux")
def test_not_get_completions_path(ipdb_kernel):
    kernel = ipdb_kernel
    comp = kernel.do_complete('/tm', len('/tm'))
    assert len(comp['matches']) == 1


def test_history(ipdb_kernel):
    kernel = ipdb_kernel
    if os.name != 'nt':
        kernel.do_execute('!ls', False)
    else:
        kernel.do_execute('!dir', False)
    kernel.do_execute('%cd ~', False)
    kernel.do_shutdown(False)

    with open(kernel.hist_file, 'rb') as fid:
        text = fid.read().decode('utf-8', 'replace')

    if os.name != 'nt':
        assert '!ls' in text
    else:
        assert '!dir' in text
    assert '%cd' in text

    kernel = ipdb_kernel
    kernel.do_history(None, None, None)
    if os.name != 'nt':
        assert '!ls' in ''.join(kernel.hist_cache)
    else:
        assert '!dir' in ''.join(kernel.hist_cache)
    assert '%cd ~'


def test_sticky_magics(ipdb_kernel):
    kernel = ipdb_kernel
    kernel.do_execute('%%%html\nhello', None)
    text = get_log_text(kernel)

    assert 'html added to session magics' in text
    kernel.do_execute('<b>hello</b>', None)
    kernel.do_execute('%%%html', None)
    text = get_log_text(kernel)
    assert text.count('Display Data') == 2
    assert 'html removed from session magics' in text


@pytest.mark.skipif(os.environ.get('CI', None) is None,
                    reason="It's not meant to be run outside of CIs")
def test_shell_partial_quote(ipdb_kernel):
    kernel = ipdb_kernel
    if os.name != 'nt':
        kernel.do_execute('%cd "/home/', False)
        text = get_log_text(kernel)
        assert """No such file or directory: '"/home/'""" in text, text
    else:
        kernel.do_execute('%cd "/home/', False)
        text = get_log_text(kernel)
        assert """[WinError 123] The filename, directory name,"""
        """ or volume label syntax is incorrect: '"/home/'""" in text, text


if __name__ == "__main__":
    pytest.main()
