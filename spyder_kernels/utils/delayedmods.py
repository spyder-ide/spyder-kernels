# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Delayed modules classes.

They are useful to not import big modules until it's really
necessary.
"""

class FakeObject(object):
    """Fake class used in replacement of missing objects"""
    pass


class _DelayedNumpy(object):
    """Import Numpy only when one of its attributes is accessed."""

    def __getattribute__(self, name):
        try:
            import numpy
        except Exception:
            return FakeObject

        return getattr(numpy, name)

numpy = _DelayedNumpy()


class _DelayedPandas(object):
    """Import Pandas only when one of its attributes is accessed."""

    def __getattribute__(self, name):
        try:
            import pandas
        except Exception:
            return FakeObject

        return getattr(pandas, name)

pandas = _DelayedPandas()


class _DelayedPIL(object):
    """Import Pillow only when one of its attributes is accessed."""

    def __getattribute__(self, name):
        try:
            import PIL
        except Exception:
            return FakeObject

        return getattr(PIL, name)

PIL = _DelayedPIL()


class _DelayedBs4(object):
    """Import bs4 only when one of its attributes is accessed."""

    def __getattribute__(self, name):
        try:
            import bs4
        except Exception:
            return FakeObject

        return getattr(bs4, name)

bs4 = _DelayedBs4()
