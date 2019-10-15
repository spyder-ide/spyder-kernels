#
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)

import sys
import linecache

from IPython.core.getipython import get_ipython

from spyder_kernels.py3compat import PY2


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

    def __init__(self, filename, namespace=None, current_namespace=False,
                 file_code=None):
        self.filename = filename
        self.namespace = namespace
        self.current_namespace = current_namespace
        self._previous_filename = None
        self._previous_main = None
        self._reset_main = False
        self._file_code = file_code

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
        if (self._file_code is not None
                and not PY2
                and isinstance(self._file_code, bytes)):
            try:
                self._file_code = self._file_code.decode()
            except UnicodeDecodeError:
                # Setting the cache is not supported for non utf-8 files
                self._file_code = None
        if self._file_code is not None:
            # '\n' is used instead of the native line endings. (see linecache)
            # mtime is set to None to avoid a cache update.
            linecache.cache[self.filename] = (
                len(self._file_code), None,
                [line + '\n' for line in self._file_code.splitlines()],
                self.filename)
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
        if self.filename in linecache.cache:
            linecache.cache.pop(self.filename)
