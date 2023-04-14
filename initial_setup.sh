#!/bin/bash

# Set your desired venv directory name
VENV_DIR="venv"

if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found. Exiting."
    exit 1
fi

# Check if the venv directory exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment in $VENV_DIR"
    python3 -m venv "$VENV_DIR"
else
    echo "Python virtual environment $VENV_DIR already exists"
fi

# Activate the venv
echo "Activating virtual environment"
source "$VENV_DIR/bin/activate"

source venv/bin/activate
echo "Installing dependencies" 
pip3 install -r requirements.txt --no-cache-dir --upgrade
[ $? -eq 0 ] && { echo "Dependencies installed succesfully!"; } || { deactivate; echo "Failed to install dependencies"; exit 1; }
echo "Copying config.json.example to config.json"
cp config.json.example config.json

# Prompt the user for their OpenAI API key
echo "Please enter your OpenAI API key to update the config file:"
read -rs openai_key


# Replace <your_openai_key> in config.json with the user's key
sed -i -E "s/<your_openai_key>/$openai_key/g" config.json

[ $? -eq 0 ] && { echo "OpenAI API key set in config.json!"; } || { echo "Failed to set openaikey in config.json. You can set this yourself, the rest of setup is complete."; }

# Display a confirmation message

export FLASK_APP=bot

echo "Everything is ready! Run './run.sh' to start the webapp."
deactivate;
