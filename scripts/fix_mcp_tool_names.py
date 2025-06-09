#!/usr/bin/env python3
"""
Fix MCP tool names in all hermes_bridge.py files.

This script replaces the dot separator in tool names with underscores
to comply with MCP naming requirements (^[a-zA-Z0-9_-]{1,64}$).
"""

import os
import re
from pathlib import Path


def fix_hermes_bridge_file(file_path):
    """Fix tool name formatting in a hermes_bridge.py file."""
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to find tool name construction with dots
    # Matches: tool_name = f"{self.component_name}.{...}"
    patterns = [
        (r'tool_name = f"{self\.component_name}_{{(.+?)}}"', r'tool_name = f"{self.component_name}_{\1}"'),
        (r"tool_name = f'{self\.component_name}_{{(.+?)}}'", r"tool_name = f'{self.component_name}_{\1}'"),
        # Also handle any direct string concatenation
        (r'tool_name = self\.component_name \+ "\."\s*\+', r'tool_name = self.component_name + "_" +'),
        (r"tool_name = self\.component_name \+ '\.'\s*\+", r"tool_name = self.component_name + '_' +"),
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
        print(f"  ✓ Fixed tool name formatting")
        return True
    else:
        print(f"  - No changes needed")
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
    """Main function to fix all hermes_bridge.py files."""
    print("MCP Tool Name Fixer")
    print("===================")
    print("This script will fix tool names to comply with MCP naming requirements.")
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
    
    print(f"Found {len(bridge_files)} hermes_bridge.py files:")
    for f in bridge_files:
        print(f"  - {f.relative_to(tekton_root)}")
    print()
    
    # Process each file
    files_modified = 0
    for file_path in bridge_files:
        if fix_hermes_bridge_file(file_path):
            files_modified += 1
    
    print()
    print(f"Summary: Modified {files_modified} out of {len(bridge_files)} files")
    
    if files_modified > 0:
        print()
        print("Next steps:")
        print("1. Review the changes with: git diff")
        print("2. Test the MCP functionality (see testing instructions)")
        print("3. Commit the changes if everything works")


if __name__ == "__main__":
    main()