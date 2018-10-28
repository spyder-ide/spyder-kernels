# Jupyter kernels for the Spyder console

[![CircleCI](https://circleci.com/gh/spyder-ide/spyder-kernels.svg?style=shield)](https://circleci.com/gh/spyder-ide/spyder-kernels)
[![AppVeyor](https://ci.appveyor.com/api/projects/status/pd0etf64xyiyd3qb/branch/master?svg=true)](https://ci.appveyor.com/project/spyder-ide/spyder-kernels/branch/master)
[![codecov](https://codecov.io/gh/spyder-ide/spyder-kernels/branch/master/graph/badge.svg)](https://codecov.io/gh/spyder-ide/spyder-kernels)

Package that provides the kernels used by Spyder on its IPython console.

## Installation

To install this package, you can use either the ``pip`` or ``conda`` package
managers, as follows:

Using conda (the recommended way!):

```
conda install spyder-kernels
```

Using pip:

```
pip install spyder-kernels
```

## Dependencies

This project depends on:

* [ipykernel](https://github.com/ipython/ipykernel/)
* [cloudpickle](https://github.com/cloudpipe/cloudpickle)
* [wurlitzer](https://github.com/minrk/wurlitzer)


## Changelog

Visit our [CHANGELOG](CHANGELOG.md) file to know more about our new features
and improvements.

## Development and contribution

To start contributing to this project you can execute

```
pip install -e .
```

in your git clone and then test your changes in Spyder. We follow PEP8 and
PEP257 style guidelines.
