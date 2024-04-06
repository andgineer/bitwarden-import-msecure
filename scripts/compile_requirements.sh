#!/usr/bin/env bash
#
# Obsolete - use invoke tasks instead.
#
# Pin current dependencies versions.
#
unset CONDA_PREFIX  # if conda is installed, it will mess with the virtual env

START_TIME=$(date +%s)

uv pip compile requirements.in --output-file=requirements.txt
REQS_TIME=$(date +%s)

uv pip compile requirements.dev.in --output-file=requirements.dev.txt

END_TIME=$(date +%s)

echo "Req‘s compilation time: $((REQS_TIME - $START_TIME)) seconds"
echo "Req‘s dev compilation time: $((END_TIME - REQS_TIME)) seconds"
echo "Total execution time: $((END_TIME - $START_TIME)) seconds"

# do not pin dependencies in the package
scripts/include_pyproject_requirements.py requirements.in
