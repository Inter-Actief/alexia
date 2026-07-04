#!/bin/bash

# Print some debugging information about the environment
# ------------------------------------------------------
# Python version
echo "Python version:"
python3 -V
# Path to the python binary being used
echo "Python binary:"
which python
# uv version
echo "uv version:"
uv --version
# Installed package list
echo "Installed packages:"
uv pip list

# Configure Django and run the tests
# ----------------------------------
# Copy the test settings to local.py
echo "Copying test settings to local.py"
cp ./alexia/conf/settings/test.py ./alexia/conf/settings/local.py

# Run Django initial checks
echo "Checking if Django can run..."
python3 manage.py check

# Make sure staticfiles are collected into the static volume
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Make sure database is migrated
echo "Executing Django migrations..."
python3 manage.py migrate

# Run Django tests
echo "Running Alexia tests..."
python3 manage.py test --keepdb
