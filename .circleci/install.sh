#!/bin/bash

# Install Miniconda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
source $HOME/miniconda/etc/profile.d/conda.sh

# Make new conda environment with required Python version
conda create -y -n test python=$PYTHON_VERSION
conda activate test

# Install dependencies
conda install -y -q --file requirements.txt

# Install test dependencies
conda install -y -q nomkl numpy pandas scipy pytest pytest-cov mock

# Install codecov
pip install -q codecov
