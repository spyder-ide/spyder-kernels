#!/bin/bash

export PATH="$HOME/miniconda/bin:$PATH"
source activate test
pytest -x -vv spyder_kernels
