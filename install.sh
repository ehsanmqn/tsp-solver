#!/bin/bash

# Remove any existing distribution files
rm -rf dist/

# Install latest versions of setuptools and pip
pip install --upgrade setuptools pip

# Build the wheel file
python setup.py sdist bdist_wheel
echo "tsp-solver packaged successfully"

# Install the wheel file
pip install dist/*.whl
echo "tsp-solver installed successfully"

# Run the TSP and VRP solver service
export MESSAGE_BROKER="localhost"

echo "Running tsp-solver"
python -m tsp_solver.service