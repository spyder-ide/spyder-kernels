#!/bin/bash

export PATH="$HOME/miniconda/bin:$PATH"
source activate test

pytest -x -vv --cov=spyder_kernels --cov-report=term-missing spyder_kernels

codecov
