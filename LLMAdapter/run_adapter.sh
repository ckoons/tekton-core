#!/bin/bash
# Simple script to run the LLM Adapter

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

# Find script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found${RESET}"
    exit 1
fi

# Check for required Python packages
echo -e "${BLUE}Checking for required Python packages...${RESET}"
if ! python3 -c "import anthropic" &> /dev/null || ! python3 -c "import fastapi" &> /dev/null || ! python3 -c "import websockets" &> /dev/null; then
    echo -e "${YELLOW}Installing required packages...${RESET}"
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Warning: ANTHROPIC_API_KEY is not set. LLM responses will be simulated.${RESET}"
    echo -e "${YELLOW}Set the ANTHROPIC_API_KEY environment variable to enable Claude integration.${RESET}"
else
    echo -e "${GREEN}ANTHROPIC_API_KEY is set. Claude integration is enabled.${RESET}"
fi

# Run the adapter
echo -e "${GREEN}${BOLD}Starting Tekton LLM Adapter${RESET}"
echo -e "${GREEN}HTTP Server: http://localhost:8300${RESET}"
echo -e "${GREEN}WebSocket Server: ws://localhost:8301${RESET}"

# Start the adapter
cd "$SCRIPT_DIR"
python3 -m llm_adapter.server