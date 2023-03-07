#!/bin/sh

PYTHON='python3'
README_FILE='README.md'
TEMPLATE_FILE='README_template.md'
VENV_DIR='.venvREADME'

# Deactivate if already in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then deactivate; fi

# Create the venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR"
    $PYTHON -m venv "$VENV_DIR"
fi

# Activate the virtual environment
echo "Activating virtual environment in $VENV_DIR"
source "$VENV_DIR/bin/activate"

# Update/install pip and required packages
echo "Updating pip and installing required packages"
$PYTHON -m pip -U pip setuptools wheel
$PYTHON -m pip install -U -r requirements-dev.txt

# Generate the readme file to doc/README.md
echo "Generating README.md"
cd doc
$PYTHON render_readme.py
cd ..

# Move the generated readme file to the root directory
mv doc/README.md README.md

# Add the updated readme file and the formatted source code to the index, ready for commit
git add "$README_FILE"

# Deactivate the virtual environment
if [ -n "$VIRTUAL_ENV" ]; then deactivate; fi
