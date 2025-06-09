#!/usr/bin/env python3
"""
Fix MCP tool names in shutdown methods of hermes_bridge.py files.

This script replaces the dot separator in tool names with underscores
in the shutdown methods to match the registration changes.
"""

import os
import re
from pathlib import Path


def fix_shutdown_methods(file_path):
    """Fix tool name formatting in shutdown methods."""
    print(f"Processing shutdown methods in: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Patterns to fix shutdown method tool names
    patterns = [
        # Fix tool names in shutdown that use dots
        (r'f"{self\.component_name}\.health_check"', r'f"{self.component_name}_health_check"'),
        (r'f"{self\.component_name}\.component_info"', r'f"{self.component_name}_component_info"'),
        (r'f"{self\.component_name}\.{(.+?)}"', r'f"{self.component_name}_{\1}"'),
        (r"f'{self\.component_name}\.{(.+?)}'", r"f'{self.component_name}_{\1}'"),
        # Also fix string concatenation patterns
        (r'self\.component_name \+ "\."\s*\+ tool', r'self.component_name + "_" + tool'),
        (r"self\.component_name \+ '\.'\s*\+ tool", r"self.component_name + '_' + tool"),
    ]
    
    changes_made = False
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            changes_made = True
            content = new_content
    
    if changes_made:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  ✓ Fixed shutdown method tool names")
        return True
    else:
        print(f"  - No shutdown method changes needed")
        return False


def find_hermes_bridge_files(root_dir):
    """Find all hermes_bridge.py files in the project."""
    hermes_bridge_files = []
    
    for component_dir in Path(root_dir).iterdir():
        if component_dir.is_dir() and component_dir.name not in ['.git', '__pycache__', 'venv', 'node_modules']:
            # Look for hermes_bridge.py in various possible locations
            possible_paths = [
                component_dir / 'hermes_bridge.py',
                component_dir / component_dir.name.lower() / 'hermes_bridge.py',
                component_dir / component_dir.name.lower() / 'core' / 'hermes_bridge.py',
                component_dir / component_dir.name.lower() / 'core' / 'mcp' / 'hermes_bridge.py',
                component_dir / component_dir.name.lower() / 'api' / 'hermes_bridge.py',
            ]
            
            for path in possible_paths:
                if path.exists():
                    hermes_bridge_files.append(path)
    
    return hermes_bridge_files


def main():
    """Main function to fix shutdown methods in all hermes_bridge.py files."""
    print("MCP Shutdown Method Fixer")
    print("=========================")
    print("This script will fix tool names in shutdown methods.")
    print()
    
    # Get the Tekton root directory
    script_dir = Path(__file__).parent
    tekton_root = script_dir.parent
    
    print(f"Tekton root: {tekton_root}")
    print()
    
    # Find all hermes_bridge.py files
    bridge_files = find_hermes_bridge_files(tekton_root)
    
    if not bridge_files:
        print("No hermes_bridge.py files found!")
        return
    
    print(f"Found {len(bridge_files)} hermes_bridge.py files")
    print()
    
    # Process each file
    files_modified = 0
    for file_path in bridge_files:
        if fix_shutdown_methods(file_path):
            files_modified += 1
    
    print()
    print(f"Summary: Modified {files_modified} out of {len(bridge_files)} files")


if __name__ == "__main__":
    main()