# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder_notebook/__init__.py for details)


"""
Spyder Kernels
==============

Provides Jupyter kernels for use with the consoles of Spyder, the Scientific
Python Development Environment. These can launched either through Spyder itself
or in an independent Python session, and allow for interactive or file-based
execution of Python code in different environments, all inside the IDE.
For more on Spyder, visit https://www.spyder-ide.org/

To learn about creating, connecting to and using Spyder's consoles, read:
https://docs.spyder-ide.org/ipythonconsole.html

For advice on managing packages and environments with Spyder-Kernels, see:
https://github.com/spyder-ide/spyder/wiki/Working-with-packages-and-environments-in-Spyder

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
    keywords='spyder jupyter kernel ipython console',
    url='https://github.com/spyder-ide/spyder-kernels',
    download_url="https://www.spyder-ide.org/#fh5co-download",
    license='MIT',
    author='Spyder Development Team',
    author_email="spyderlib@googlegroups.com",
    description="Jupyter kernels for Spyder's console",
    long_description="\n".join(DOCLINES[4:]),
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=REQUIREMENTS,
    include_package_data=True,
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Framework :: Jupyter',
                 'Framework :: IPython',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Topic :: Software Development :: Interpreters']
)
