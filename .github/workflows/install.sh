#!/bin/bash

# Install dependencies
conda install --file requirements/posix.txt -y -q

# Install test dependencies
conda install nomkl -y -q
conda install --file requirements/tests.txt -y -q

# Install codecov
pip install codecov -q
