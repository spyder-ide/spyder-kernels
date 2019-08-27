#
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)

import os
import sys

from IPython.core.getipython import get_ipython


def _get_globals():
    """Return current namespace"""
    ipython_shell = get_ipython()
    return ipython_shell.user_ns


class NamespaceManager(object):
    """
    Get a namespace and set __file__ to filename for this namespace.

    The namespace is either namespace, the current namespace if
    current_namespace is True, or a new namespace.
    """

    def __init__(self, filename, namespace=None, current_namespace=False):
        self.filename = filename
        self.namespace = namespace
        self.current_namespace = current_namespace
        self._previous_filename = None
        self._previous_main = None
        self._sys_path_0 = None
        self._reset_main = False

    def __enter__(self):
        """
        Prepare the namespace.
        """
        # Save previous __file__
        if self.namespace is None:
            if self.current_namespace:
                self.namespace = _get_globals()
            else:
                ipython_shell = get_ipython()
                main_mod = ipython_shell.new_main_mod(
                    self.filename, '__main__')
                self.namespace = main_mod.__dict__
                # Needed to allow pickle to reference main
                if '__main__' in sys.modules:
                    self._previous_main = sys.modules['__main__']
                sys.modules['__main__'] = main_mod
                self._reset_main = True
        if '__file__' in self.namespace:
            self._previous_filename = self.namespace['__file__']
        self.namespace['__file__'] = self.filename

        self._sys_path_0 = os.path.dirname(os.path.abspath(self.filename))
        sys.path.insert(0, self._sys_path_0)

        return self.namespace

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Reset the namespace.
        """
        if not self.current_namespace:
            get_ipython().user_ns.update(self.namespace)
        if self._previous_filename:
            self.namespace['__file__'] = self._previous_filename
        elif '__file__' in self.namespace:
            self.namespace.pop('__file__')
        if self._previous_main:
            sys.modules['__main__'] = self._previous_main
        elif '__main__' in sys.modules and self._reset_main:
            del sys.modules['__main__']
        if self._sys_path_0:
            # Pop the first entry if we were the ones that added it
            if sys.path[0] == self._sys_path_0:
                sys.path = sys.path[1:]
