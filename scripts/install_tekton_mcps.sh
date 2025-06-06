#!/bin/bash
# Install Tekton MCP for Claude
# 
# This script installs Hermes as the central MCP aggregator for all Tekton components.
# Claude will connect to Hermes, which provides access to tools from all registered components.

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "  Tekton MCP Installation for Claude"
echo "=========================================="
echo ""

# Check if claude command exists
if ! command -v claude &> /dev/null; then
    echo -e "${RED}Error: 'claude' command not found${NC}"
    echo "Please ensure Claude Desktop is installed and the CLI is available in your PATH"
    exit 1
fi

# Remove any existing Tekton MCP installations
echo -e "${YELLOW}Removing any existing Tekton MCP installations...${NC}"
claude mcp remove tekton 2>/dev/null || true

# Install Hermes as the central MCP aggregator
echo -e "${YELLOW}Installing Hermes as the Tekton MCP aggregator...${NC}"
claude mcp add tekton -s user http://localhost:8001/api/mcp/v2

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo ""
    echo "Hermes is now installed as the central MCP endpoint for Tekton."
    echo "All Tekton components registered with Hermes will be accessible through Claude."
    echo ""
    echo "Endpoint: http://localhost:8001/api/mcp/v2"
    echo ""
    echo "To verify the installation:"
    echo "  1. Ensure Hermes is running: ./scripts/enhanced_tekton_launcher.py"
    echo "  2. Check Hermes health: curl http://localhost:8001/api/mcp/v2/health"
    echo "  3. List available tools: curl http://localhost:8001/api/mcp/v2/tools"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Installation failed${NC}"
    echo "Please check the error messages above and ensure:"
    echo "  - Claude Desktop is properly installed"
    echo "  - The 'claude' CLI command is available"
    echo "  - You have the necessary permissions"
    exit 1
fi