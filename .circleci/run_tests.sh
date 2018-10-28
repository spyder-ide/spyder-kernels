#!/bin/bash

export PATH="$HOME/miniconda/bin:$PATH"
source activate test

pytest -x -vv --cov=spyder_kernels spyder_kernels

if [ $? -ne 0 ]; then
    exit 1
fi

codecov
