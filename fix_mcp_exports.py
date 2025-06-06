#!/usr/bin/env python3
"""Fix MCP __init__.py exports for all components."""

import os

COMPONENTS = ["Ergon", "Rhetor", "Synthesis", "Telos", "Engram"]

def fix_mcp_init(component):
    """Add get_all_tools to MCP __init__.py exports."""
    init_path = f"{component}/{component.lower()}/core/mcp/__init__.py"
    
    if not os.path.exists(init_path):
        print(f"✗ {init_path} not found")
        return
        
    with open(init_path, 'r') as f:
        content = f.read()
    
    # Check if get_all_tools is already imported
    if 'get_all_tools' in content and 'from' in content:
        print(f"✓ {component} already imports get_all_tools")
        return
        
    # Add import
    if component == "Synthesis":
        # Synthesis needs different handling
        if 'from .tools import' not in content:
            # Add import section
            import_line = "\n# Import tools\nfrom .tools import get_all_tools\n"
            # Find a good place to insert
            if '__all__' in content:
                content = content.replace('__all__', import_line + '\n__all__')
            else:
                content += import_line
    else:
        # For other components, add to existing import
        import_section = f"from {component.lower()}.core.mcp.tools import"
        if import_section in content:
            # Find the import and add get_all_tools
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if import_section in line and ')' not in line:
                    # Multi-line import, find the closing parenthesis
                    j = i + 1
                    while j < len(lines) and ')' not in lines[j]:
                        j += 1
                    if j < len(lines):
                        lines[j] = lines[j].replace(')', ',\n    get_all_tools\n)')
                    break
            content = '\n'.join(lines)
    
    # Add to __all__ if not present
    if '"get_all_tools"' not in content and '__all__' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '__all__' in line and ']' not in line:
                # Multi-line __all__, find the closing bracket
                j = i + 1
                while j < len(lines) and ']' not in lines[j]:
                    j += 1
                if j < len(lines):
                    lines[j] = lines[j].replace(']', ',\n    "get_all_tools"\n]')
                break
        content = '\n'.join(lines)
    
    with open(init_path, 'w') as f:
        f.write(content)
        
    print(f"✓ Fixed {component} MCP __init__.py")

if __name__ == "__main__":
    os.chdir("/Users/cskoons/projects/github/Tekton")
    
    for component in COMPONENTS:
        print(f"Fixing {component}...")
        fix_mcp_init(component)