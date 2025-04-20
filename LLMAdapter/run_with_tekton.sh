#!/bin/bash
# Script to run the LLM Adapter and Tekton system together

# ANSI color codes for terminal output
BLUE="\033[94m"
GREEN="\033[92m"
YELLOW="\033[93m"
RED="\033[91m"
BOLD="\033[1m"
RESET="\033[0m"

# Find script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEKTON_DIR="$(dirname "$SCRIPT_DIR")"

# Check if log directory exists
mkdir -p "$HOME/.tekton/logs"

# Start the LLM Adapter in the background
echo -e "${GREEN}${BOLD}Starting Tekton LLM Adapter...${RESET}"
cd "$SCRIPT_DIR"
nohup python3 -m llm_adapter.server > "$HOME/.tekton/logs/llm_adapter.log" 2>&1 &
LLM_ADAPTER_PID=$!
echo -e "${GREEN}LLM Adapter started with PID: ${LLM_ADAPTER_PID}${RESET}"
echo -e "${GREEN}HTTP Server: http://localhost:8300${RESET}"
echo -e "${GREEN}WebSocket Server: ws://localhost:8301${RESET}"

# Give the adapter a moment to start up
sleep 2

# Now start Tekton
echo -e "${BLUE}${BOLD}Launching Tekton system...${RESET}"
cd "$TEKTON_DIR"
tekton-launch

# When Tekton is stopped, also stop the LLM Adapter
echo -e "${YELLOW}Tekton system stopped. Stopping LLM Adapter...${RESET}"
kill $LLM_ADAPTER_PID
echo -e "${GREEN}LLM Adapter stopped.${RESET}"