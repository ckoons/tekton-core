#!/bin/bash
# Tekton Installation with UV

set -e

# ANSI colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
HOME_BIN="$HOME/bin"
UV_VERSION="0.5.9"  # Update as needed

echo -e "${BLUE}Tekton Installation${NC}"

# Ensure ~/bin exists and is in PATH
if [ ! -d "$HOME_BIN" ]; then
    echo -e "${YELLOW}Creating $HOME_BIN directory...${NC}"
    mkdir -p "$HOME_BIN"
    
    # Add to PATH if needed
    if [[ ":$PATH:" != *":$HOME_BIN:"* ]]; then
        # Detect shell profile
        if [ -f "$HOME/.zshrc" ]; then
            PROFILE="$HOME/.zshrc"
        elif [ -f "$HOME/.bashrc" ]; then
            PROFILE="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            PROFILE="$HOME/.bash_profile"
        else
            PROFILE="$HOME/.profile"
        fi
        
        echo -e "${YELLOW}Adding $HOME_BIN to PATH in $PROFILE${NC}"
        echo 'export PATH="$HOME/bin:$PATH"' >> "$PROFILE"
    fi
fi

# Install UV if not present
if ! command -v uv &> /dev/null; then
    echo -e "${BLUE}Installing UV package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH if not already added by installer
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}Adding UV to PATH...${NC}"
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
fi

# Setup Python environment
echo -e "${BLUE}Setting up Tekton Python environment...${NC}"
uv venv "$SCRIPT_DIR/.venv" --python=python3.10

# Install dependencies
echo -e "${BLUE}Installing Tekton dependencies...${NC}"
source "$SCRIPT_DIR/.venv/bin/activate"
uv pip install -e "$SCRIPT_DIR/tekton-core"

# Create tekton command
echo -e "${BLUE}Creating tekton command...${NC}"
ln -sf "$SCRIPT_DIR/scripts/tekton_launcher.py" "$HOME_BIN/tekton"
chmod +x "$HOME_BIN/tekton"

# Create symbolic links for component scripts
echo -e "${BLUE}Setting up component commands...${NC}"
ln -sf "$SCRIPT_DIR/scripts/tekton-launch" "$HOME_BIN/tekton-launch"
ln -sf "$SCRIPT_DIR/scripts/tekton-status" "$HOME_BIN/tekton-status"
ln -sf "$SCRIPT_DIR/scripts/tekton-kill" "$HOME_BIN/tekton-kill"
chmod +x "$SCRIPT_DIR/scripts/tekton-launch"
chmod +x "$SCRIPT_DIR/scripts/tekton-status"
chmod +x "$SCRIPT_DIR/scripts/tekton-kill"

echo -e "${GREEN}Tekton installation complete!${NC}"
echo -e "Run 'tekton --help' to get started"