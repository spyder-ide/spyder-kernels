# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder_notebook/__init__.py for details)


"""
Spyder Kernels
==============

Provides Jupyter kernels for use with the Spyder IDE's IPython consoles,
launched either through Spyder itself or in an independent Python session.
These allow for interactive or file-based execution of Python code in
different environments inside of Spyder.

Spyder is a powerful scientific environment written in Python, for Python,
and designed by and for scientists, engineers and data analysts.
It features a unique combination of the advanced editing, analysis, debugging
and profiling functionality of a comprehensive development tool with the data
exploration, interactive execution, deep inspection and beautiful visualization
capabilities of a scientific package.

To launch a Spyder IPython console and run code in a different environment
(virtualenv/venv or conda), Python installation or machine from Spyder itself,
just install this package there and either change Spyder's Python interpreter
to point to it (under Tools -> Preferences -> Python interpreter) or launch an
independent kernel on the host (via python -m spyder_kernels.console) and
connect to it via the Console -> Connect to existing kernel dialog in Spyder.

For further advice on managing packages and environments with Spyder, see:
https://github.com/spyder-ide/spyder/wiki/Working-with-packages-and-environments-in-Spyder

To learn more about creating, connecting and using Spyder's consoles, read:
https://docs.spyder-ide.org/ipythonconsole.html

"""

# Standard library imports
import ast
import os

# Third party imports
from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))
DOCLINES = __doc__.split('\n')


def get_version(module='spyder_kernels'):
    """Get version."""
    with open(os.path.join(HERE, module, '_version.py'), 'r') as f:
        data = f.read()
    lines = data.split('\n')
    for line in lines:
        if line.startswith('VERSION_INFO'):
            version_tuple = ast.literal_eval(line.split('=')[-1].strip())
            version = '.'.join(map(str, version_tuple))
            break
    return version


REQUIREMENTS = ['ipykernel>=4.8.2',
                'pyzmq>=17',
                'jupyter-client>=5.2.3',
                'cloudpickle']


setup(
    name='spyder-kernels',
    version=get_version(),
    keywords='spyder jupyter kernel ipython console shell',
    url='https://github.com/spyder-ide/spyder-kernels',
    license='MIT',
    author='Spyder Development Team',
    description="Jupyter kernels for the Spyder IDE's IPython consoles.",
    long_description="\n".join(DOCLINES[4:]),
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    platforms=["any"],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Framework :: Jupyter',
                 'Framework :: IPython',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Software Development :: Interpreters']
)
