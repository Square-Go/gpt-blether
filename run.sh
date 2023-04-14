#!/bin/bash

# Set your desired venv directory name
VENV_DIR="venv"

if [ ! -d "$VENV_DIR" ]; then
   echo "Venv does not exist in $VENV_DIR. Did you run inital_setup.sh?"
    exit 1;
fi

echo "Activating virtual environment"
source "$VENV_DIR/bin/activate"
flask run;