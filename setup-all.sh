#!/bin/bash
# Setup all Tekton components with UV

set -e

# ANSI colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install UV system-wide if not present
if ! command -v uv &> /dev/null; then
    echo -e "${BLUE}Installing UV package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH if not already added by installer
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}Adding UV to PATH...${NC}"
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
fi

# First, setup tekton-core
echo -e "${BLUE}Setting up tekton-core...${NC}"
bash "$SCRIPT_DIR/component-setup.sh" tekton-core

# Components to setup
COMPONENTS=(Hermes Engram Athena Ergon Rhetor Telos Harmonia Sophia Synthesis)

# Setup each component
for component in "${COMPONENTS[@]}"; do
    echo -e "\n${BLUE}Setting up $component...${NC}"
    bash "$SCRIPT_DIR/component-setup.sh" "$component"
done

# Install Codex using its own setup
if [ -d "$SCRIPT_DIR/Codex" ]; then
    echo -e "\n${BLUE}Setting up Codex...${NC}"
    cd "$SCRIPT_DIR/Codex"
    uv pip install -e .
fi

echo -e "\n${GREEN}All Tekton components have been set up!${NC}"