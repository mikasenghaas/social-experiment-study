#!/bin/bash

# add poetry to path
export PATH="${HOME}/.local/bin:${PATH}"

# change to project dir
PROJECT_DIR=$(dirname "$(readlink -f "$0")")
cd ${PROJECT_DIR}

# install dependencies
poetry install

# run experiment
poetry run python main.py
