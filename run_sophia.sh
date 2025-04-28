#!/bin/bash

# Run Sophia API server
# This script starts the Sophia API server using the Single Port Architecture

# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set environment variables
export SOPHIA_PORT=${SOPHIA_PORT:-8006}
export SOPHIA_HOST=${SOPHIA_HOST:-localhost}
export TEKTON_LLM_URL=${TEKTON_LLM_URL:-http://localhost:8001}
export HERMES_URL=${HERMES_URL:-http://localhost:8000}
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/Sophia/logs"

# Check if virtual environment exists
VENV_DIR="$SCRIPT_DIR/Sophia/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running setup.sh first..."
    "$SCRIPT_DIR/Sophia/setup.sh"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Check if tekton-core package is available
if python -c "import tekton.utils.tekton_http" &> /dev/null; then
    echo "Tekton shared utilities found."
else
    echo "Warning: Tekton shared utilities not found. Using fallback implementations."
fi

# Check if tekton-llm-client package is available
if python -c "import tekton_llm_client" &> /dev/null; then
    echo "Tekton LLM client found."
else
    echo "Warning: Tekton LLM client not found. Some features may be limited."
fi

# Check for dependencies
if ! python -c "import fastapi, uvicorn, numpy, pandas, scikit-learn" &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r "$SCRIPT_DIR/Sophia/requirements.txt"
fi

# Run implementation status check if available
if [ -f "$SCRIPT_DIR/Sophia/scripts/check_impl_status.py" ]; then
    echo "Checking implementation status..."
    python "$SCRIPT_DIR/Sophia/scripts/check_impl_status.py"
fi

# Start the API server
echo "Starting Sophia API server on $SOPHIA_HOST:$SOPHIA_PORT..."
echo "LLM URL: $TEKTON_LLM_URL"
echo "Hermes URL: $HERMES_URL"

# Create log file with timestamp
LOG_FILE="$SCRIPT_DIR/Sophia/logs/sophia-$(date +'%Y%m%d-%H%M%S').log"

# Run the server with logging
uvicorn sophia.api.app:app --host "$SOPHIA_HOST" --port "$SOPHIA_PORT" --log-level info 2>&1 | tee "$LOG_FILE"

# Exit handling
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Sophia API server stopped with exit code $EXIT_CODE"
fi

# Deactivate virtual environment
deactivate

exit $EXIT_CODE