#!/bin/bash

export TRAVIS_OS_NAME="linux"
export CONDA_DEPENDENCIES_FLAGS="--quiet"
export CONDA_DEPENDENCIES="ipykernel cloudpickle nomkl numpy pandas scipy \
                           pexpect matplotlib qtconsole pytest pytest-cov"
export PIP_DEPENDENCIES_FLAGS="-q"
export PIP_DEPENDENCIES="codecov pytest-qt"

echo -e "PYTHON = $PYTHON_VERSION \n============"
git clone git://github.com/astropy/ci-helpers.git > /dev/null
source ci-helpers/travis/setup_conda_$TRAVIS_OS_NAME.sh
source $HOME/miniconda/etc/profile.d/conda.sh
conda activate test

# Install metakernel from master to verify that it doesn't break us
pip install -q --no-deps git+https://github.com/Calysto/metakernel.git
