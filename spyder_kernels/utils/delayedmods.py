# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Delayed modules classes.

They are useful to not import big modules until it's really necessary.

Notes:

* When accessing second level objects (e.g. numpy.ma.MaskedArray), you
  need to add them to the fake class that is returned in place of the
  missing module.
"""

# =============================================================================
# Class to use for missing objects
# =============================================================================
class FakeObject(object):
    """Fake class used in replacement of missing objects"""
    pass


# =============================================================================
# Numpy
# =============================================================================
class _DelayedNumpy(object):
    """Import Numpy only when one of its attributes is accessed."""

    def __getattribute__(self, name):
        try:
            import numpy
        except Exception:
            FakeNumpy = FakeObject
            FakeNumpy.MaskedArray = FakeObject
            return FakeNumpy

        return getattr(numpy, name)

numpy = _DelayedNumpy()


# =============================================================================
# Pandas
# =============================================================================
class _DelayedPandas(object):
    """Import Pandas only when one of its attributes is accessed."""

    def __getattribute__(self, name):
        try:
            import pandas
        except Exception:
            return FakeObject

        return getattr(pandas, name)

pandas = _DelayedPandas()


# =============================================================================
# Pillow
# =============================================================================
class _DelayedPIL(object):
    """Import Pillow only when one of its attributes is accessed."""

    def __getattribute__(self, name):
        try:
            import PIL.Image
        except Exception:
            FakePIL = FakeObject
            FakePIL.Image = FakeObject
            return FakePIL

        return getattr(PIL, name)

PIL = _DelayedPIL()


# =============================================================================
# BeautifulSoup
# =============================================================================
class _DelayedBs4(object):
    """Import bs4 only when one of its attributes is accessed."""

    def __getattribute__(self, name):
        try:
            import bs4
        except Exception:
            FakeBs4 = FakeObject
            FakeBs4.NavigableString = FakeObject
            return FakeBs4

        return getattr(bs4, name)

bs4 = _DelayedBs4()


# =============================================================================
# Scipy
# =============================================================================
class _DelayedScipy(object):
    """Import Scipy only when one of its attributes is accessed."""

    def __getattribute__(self, name):
        try:
            import scipy.io
        except Exception:
            return FakeObject

        return getattr(scipy, name)

scipy = _DelayedScipy()
