# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) The IPython Development Team.
# Copyright (c) 2009- Spyder Kernels Contributors
# Distributed under the terms of the BSD License.
# -----------------------------------------------------------------------------

"""
Module completion utilities

This code allows module completions out of an IPython session. It also
contains some improvements over the module_completions function present
in IPython.core.completerlib

It was developed for Spyder but now it has no use there.
"""

from IPython.core.completerlib import get_root_modules, try_import


def dot_completion(mod):
    if len(mod) < 2:
        return [x for x in get_root_modules() if x.startswith(mod[0])]
    completion_list = try_import('.'.join(mod[:-1]), True)
    completion_list = [x for x in completion_list if x.startswith(mod[-1])]
    completion_list = ['.'.join(mod[:-1] + [el]) for el in completion_list]
    return completion_list


def module_completion(line):
    """
    Returns a list containing the completion possibilities for an import line.

    The line looks like this :
    'import xml.d'
    'from xml.dom import'
    """

    words = line.split(' ')
    nwords = len(words)

    # from whatever <tab> -> 'import '
    if nwords == 3 and words[0] == 'from':
        if words[2].startswith('i') or words[2] == '':
            return ['import ']
        else:
            return []

    # 'import xy<tab> or import xy<tab>, '
    if words[0] == 'import':
        if nwords == 2 and words[1] == '':
            return get_root_modules()
        if ',' == words[-1][-1]:
            return [' ']
        mod = words[-1].split('.')
        return dot_completion(mod)

    # 'from xy<tab>'
    if nwords < 3 and (words[0] == 'from'):
        if nwords == 1:
            return get_root_modules()
        mod = words[1].split('.')
        return dot_completion(mod)

    # 'from xyz import abc<tab>'
    if nwords >= 3 and words[0] == 'from':
        mod = words[1]
        completion_list = try_import(mod)
        if words[2] == 'import' and words[3] != '':
            if '(' in words[-1]:
                words = words[:-2] + words[-1].split('(')
            if ',' in words[-1]:
                words = words[:-2] + words[-1].split(',')
            return [x for x in completion_list if x.startswith(words[-1])]
        else:
            return completion_list

    return []
