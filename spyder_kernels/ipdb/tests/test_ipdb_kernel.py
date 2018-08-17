# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
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

# Test library imports
import pytest

# Local imports
from spyder_kernels.ipdb.kernel import IPdbKernel

# Third party imports
from metakernel.tests.utils import get_kernel, get_log_text


def test_available_magics():
    """Check the magics available for the kernel."""
    kernel = get_kernel(kernel_class=IPdbKernel)
    for magic in ['EOF', 'a', 'activity', 'alias', 'args', 'b', 'break',
                  'bt', 'c', 'cd', 'cl', 'clear', 'commands', 'connect_info',
                  'cont', 'continue', 'conversation', 'd', 'disable',
                  'display', 'dot', 'down', 'download', 'edit', 'enable',
                  'exit', 'get', 'help', 'html', 'ignore', 'include',
                  'install', 'install_magic', 'interact', 'j', 'javascript',
                  'jigsaw', 'jump', 'kernel', 'kx', 'l', 'latex',  'list',
                  'll', 'load', 'long_list', 'ls', 'lsmagic', 'macro', 'magic',
                  'matplotlib', 'n', 'next', 'p', 'parallel', 'pdef', 'pdoc',
                  'pfile', 'pinfo', 'pinfo2', 'plot', 'pmap', 'pp', 'psource',
                  'px', 'python', 'q', 'quit', 'r', 'reload_magics', 'restart',
                  'return', 'retval', 'run', 'rv', 's', 'scheme', 'set',
                  'shell', 'source', 'step', 'tbreak', 'u', 'unalias',
                  'undisplay', 'unt', 'until', 'up', 'w', 'whatis', 'where']:
        msg = "magic '%s' is not in line_magics" % magic
        assert magic in kernel.line_magics, msg

    for magic in ['file', 'html', 'javascript', 'latex', 'shell', 'time']:
        assert magic in kernel.cell_magics


def test_shell_magic():
    """Test %shell magic."""
    kernel = get_kernel(kernel_class=IPdbKernel)
    with open('TEST.txt', 'wb'):
        pass
    if os.name != 'nt':
        kernel.get_magic('%shell ls')
    else:
        kernel.get_magic('%shell dir')
    log_text = get_log_text(kernel)
    assert 'TEST.txt' in log_text
    os.remove('TEST.txt')


def test_help():
    """Check availability of help information."""
    kernel = get_kernel(kernel_class=IPdbKernel)
    resp = kernel.get_help_on('%shell', 0)
    assert 'run the line as a shell command' in resp

    resp = kernel.do_execute('%cd?', False)
    assert 'change current directory of session' in resp[
        'payload'][0]['data']['text/plain']

    resp = kernel.get_help_on('what', 0)
    assert resp == ("Sorry, no help is available"
                    " on 'what'.", ("response was actually %s" % resp))


def test_complete():
    """Check completion."""
    kernel = get_kernel(kernel_class=IPdbKernel)
    comp = kernel.do_complete('%connect_', len('%connect_'))
    assert comp['matches'] == ['%connect_info'], str(comp['matches'])

    comp = kernel.do_complete('%%fil', len('%%fil'))
    assert comp['matches'] == ['%%file'], str(comp['matches'])

    comp = kernel.do_complete('%%', len('%%'))
    assert '%%file' in comp['matches']
    assert '%%html' in comp['matches']


def test_inspect():
    """Check inspect."""
    kernel = get_kernel(kernel_class=IPdbKernel)
    kernel.do_inspect('%lsmagic', len('%lsmagic'))
    log_text = get_log_text(kernel)
    assert "list the current line and cell magics" in log_text

    kernel.do_inspect('%lsmagic ', len('%lsmagic') + 1)


def test_path_complete():
    kernel = get_kernel(kernel_class=IPdbKernel)
    comp = kernel.do_complete('~/.ipytho', len('~/.ipytho'))
    if os.name != 'nt':
        assert comp['matches'] == ['ipython/']
    else:
        assert comp['matches'] == ['ipython\\']

    paths = [p for p in os.listdir(os.getcwd())
             if not p.startswith('.') and '-' not in p]

    for path in paths:
        comp = kernel.do_complete(path, len(path) - 1)

        if os.path.isdir(path):
            path = path.split()[-1]
            assert path + os.sep in comp['matches']
        else:
            path = path.split()[-1]
            assert path in comp['matches'], (comp['matches'], path)


def test_ls_path_complete():
    kernel = get_kernel(kernel_class=IPdbKernel)
    if os.name != 'nt':
        comp = kernel.do_complete('! ls ~/.ipytho', len('! ls ~/.ipytho'))
        assert comp['matches'] == ['ipython/'], comp
    else:
        comp = kernel.do_complete('! dir ~/.ipytho', len('! dir ~/.ipytho'))
        assert comp['matches'] == ['ipython\\'], comp


def test_history():
    kernel = get_kernel(kernel_class=IPdbKernel)
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

    kernel = get_kernel(kernel_class=IPdbKernel)
    kernel.do_history(None, None, None)
    if os.name != 'nt':
        assert '!ls' in ''.join(kernel.hist_cache)
    else:
        assert '!dir' in ''.join(kernel.hist_cache)
    assert '%cd ~'


def test_sticky_magics():
    kernel = get_kernel(kernel_class=IPdbKernel)
    kernel.do_execute('%%%html\nhello', None)
    text = get_log_text(kernel)

    assert 'html added to session magics' in text
    kernel.do_execute('<b>hello</b>', None)
    kernel.do_execute('%%%html', None)
    text = get_log_text(kernel)
    assert text.count('Display Data') == 2
    assert 'html removed from session magics' in text


def test_shell_partial_quote():
    kernel = get_kernel(kernel_class=IPdbKernel)
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
