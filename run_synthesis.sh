#!/bin/bash
# Run the Synthesis execution engine

set -e

# Define directories
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SYNTH_DIR="$SCRIPT_DIR/Synthesis"

# Function to check if a process is running on a port
function check_port() {
    if command -v lsof >/dev/null 2>&1; then
        lsof -i:$1 >/dev/null 2>&1
        return $?
    else
        netstat -tuln 2>/dev/null | grep ":$1 " >/dev/null 2>&1
        return $?
    fi
}

# Check for Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "$SYNTH_DIR/venv" ]; then
    echo "Setting up Synthesis environment..."
    cd "$SYNTH_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .
    pip install fastapi uvicorn aiohttp pydantic
else
    source "$SYNTH_DIR/venv/bin/activate"
fi

# Check if Hermes is running
HERMES_PORT=${HERMES_PORT:-8001}
if ! check_port $HERMES_PORT; then
    echo "Warning: Hermes does not appear to be running on port $HERMES_PORT."
    echo "You can start Hermes first or continue without Hermes registration."
    read -p "Continue without Hermes? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Set Synthesis port
export SYNTHESIS_PORT=${SYNTHESIS_PORT:-8009}

# Check if the port is already in use
if check_port $SYNTHESIS_PORT; then
    echo "Error: Port $SYNTHESIS_PORT is already in use."
    echo "Either stop the process using that port or set a different port with SYNTHESIS_PORT env variable."
    exit 1
fi

# Run Synthesis API server
echo "Starting Synthesis on port $SYNTHESIS_PORT..."
cd "$SYNTH_DIR"
python3 -m synthesis.api.app &
SYNTHESIS_PID=$!

# Sleep briefly to ensure the server has started
sleep 2

# Check if the server started successfully
if ! ps -p $SYNTHESIS_PID > /dev/null; then
    echo "Error: Failed to start Synthesis API server."
    exit 1
fi

# Register with Hermes if it's running
if check_port $HERMES_PORT; then
    echo "Registering Synthesis with Hermes..."
    python3 -m synthesis.scripts.register_with_hermes &
    REGISTER_PID=$!
    echo "Hermes registration process running with PID $REGISTER_PID"
fi

echo "Synthesis is running on port $SYNTHESIS_PORT (PID: $SYNTHESIS_PID)"
echo "API URL: http://localhost:$SYNTHESIS_PORT/api/"
echo "WebSocket URL: ws://localhost:$SYNTHESIS_PORT/ws"
echo "Press Ctrl+C to stop"

# Trap keyboard interrupt to gracefully shut down
trap "kill $SYNTHESIS_PID 2>/dev/null; [ -z \${REGISTER_PID+x} ] || kill $REGISTER_PID 2>/dev/null; echo 'Synthesis stopped.'; exit 0" INT TERM

# Wait for the process to finish
wait $SYNTHESIS_PID