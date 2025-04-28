#!/bin/bash

# Run Sophia API server
# This script starts the Sophia API server

# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set environment variables
export SOPHIA_PORT=${SOPHIA_PORT:-8006}
export SOPHIA_HOST=${SOPHIA_HOST:-localhost}
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Check if virtual environment exists
VENV_DIR="$SCRIPT_DIR/Sophia/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running setup.sh first..."
    "$SCRIPT_DIR/Sophia/setup.sh"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "uvicorn not found. Installing..."
    pip install uvicorn[standard]
fi

# Run the API server
echo "Starting Sophia API server on $SOPHIA_HOST:$SOPHIA_PORT..."
uvicorn sophia.api.app:app --host "$SOPHIA_HOST" --port "$SOPHIA_PORT" --reload

# Deactivate virtual environment
deactivate