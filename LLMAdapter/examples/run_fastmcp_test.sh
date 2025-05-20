#!/bin/bash

# Test script for LLM Adapter FastMCP implementation
# This script runs the comprehensive test suite for LLM Adapter FastMCP

# Set the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPONENT_PATH="$(dirname "$SCRIPT_DIR")"

# Set Python path to include the component and tekton-core
export PYTHONPATH="$COMPONENT_PATH:${PYTHONPATH:-}"

# Set LLM Adapter configuration
export LLM_ADAPTER_LOG_LEVEL="${LLM_ADAPTER_LOG_LEVEL:-info}"
export LLM_ADAPTER_PORT="${LLM_ADAPTER_PORT:-8006}"

echo "========================================"
echo "LLM Adapter FastMCP Test Suite"
echo "========================================"
echo "Component Path: $COMPONENT_PATH"
echo "Log Level: $LLM_ADAPTER_LOG_LEVEL"
echo "Port: $LLM_ADAPTER_PORT"
echo "Python Path: $PYTHONPATH"
echo "========================================"

# Check if LLM Adapter server is running
LLM_ADAPTER_URL="${LLM_ADAPTER_URL:-http://localhost:8006}"
echo "Testing LLM Adapter server at: $LLM_ADAPTER_URL"

# Run the test script
cd "$COMPONENT_PATH"
python examples/test_fastmcp.py --url "$LLM_ADAPTER_URL" "$@"

echo "========================================"
echo "LLM Adapter FastMCP test completed"
echo "========================================"