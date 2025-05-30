#!/bin/bash
# Script to install Tekton MCPs for Claude
# Installs Hermes as the central MCP that provides access to all Tekton components

# Main function
main() {
    echo "Installing Tekton MCP (via Hermes) for Claude..."
    
    # First, remove all existing Tekton MCPs
    echo "Removing existing Tekton MCPs..."
    claude mcp remove tekton 2>/dev/null || true
    
    # Use our Python-based proxy script that's similar to the successful "time" MCP
    echo "Installing Tekton MCP using Python proxy script..."
    claude mcp add tekton -s user -- python "/Users/cskoons/projects/github/Tekton/tekton_mcp_proxy.py"
    
    echo ""
    echo "Installation complete! Tekton MCP installed via Hermes."
    echo "All Tekton components registered with Hermes are now accessible to Claude."
}

# Run the main function
main