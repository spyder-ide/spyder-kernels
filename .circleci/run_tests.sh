#!/bin/bash

export PATH="$HOME/miniconda/bin:$PATH"
source activate test

# Install ipdb_kernel spec
pip install -e .
python spyder_kernels/ipdb install --user

# Run tests
pytest -x -vv --cov=spyder_kernels spyder_kernels

if [ $? -ne 0 ]; then
    exit 1
fi

codecov
