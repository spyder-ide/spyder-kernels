# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2018- Spyder Kernels Contributors
# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.
# -----------------------------------------------------------------------------

"""
Functions for our inline backend.

This is a simplified version of some functions present in
ipykernel/pylab/backend_inline.py
"""

from ipykernel.pylab.backend_inline import _fetch_figure_metadata
from IPython.display import Image
import matplotlib
from matplotlib._pylab_helpers import Gcf
from metakernel.display import display

from spyder_kernels.py3compat import io, PY2


def get_image(figure):
    """
    Get image display object from a Matplotlib figure.

    The idea to get png/svg from a figure was taken from
    https://stackoverflow.com/a/12145161/438386
    """
    if PY2:
        data = io.StringIO()
    else:
        data = io.BytesIO()

    figure.canvas.print_png(data)
    metadata=_fetch_figure_metadata(figure)

    # TODO: Passing metadata is making qtconsole crash
    img = Image(data=data.getvalue())
    return img


def show():
    """
    Show all figures as PNG payloads sent to the Jupyter clients.
    """
    try:
        for figure_manager in Gcf.get_all_fig_managers():
            display(get_image(figure_manager.canvas.figure))
    finally:
        if Gcf.get_all_fig_managers():
            matplotlib.pyplot.close('all')
