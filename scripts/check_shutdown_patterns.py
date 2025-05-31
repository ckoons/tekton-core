#!/usr/bin/env python3
"""
Check shutdown patterns across all Tekton components to identify potential port binding issues.
"""

import os
import re
from pathlib import Path

# Components to check
components = [
    "Apollo", "Athena", "Budget", "Engram", "Ergon", 
    "Harmonia", "Hermes", "Metis", "Prometheus", 
    "Rhetor", "Sophia", "Synthesis", "Telos", "Terma"
]

# Patterns to look for
patterns = {
    "shutdown_handler": r'@app\.on_event\(["\'"]shutdown["\']',
    "socket_reuse": r'SO_REUSEADDR|SO_REUSEPORT',
    "graceful_shutdown": r'signal\.|SIGTERM|SIGINT',
    "cleanup_method": r'cleanup|close|disconnect|shutdown',
    "uvicorn_config": r'uvicorn\.run.*workers',
    "async_cleanup": r'async def.*shutdown|async def.*cleanup'
}

def check_component(component_path):
    """Check a component for shutdown patterns."""
    results = {pattern: False for pattern in patterns}
    files_checked = []
    
    # Look for main app files
    app_files = [
        f"{component_path}/{component_path.split('/')[-1].lower()}/api/app.py",
        f"{component_path}/{component_path.split('/')[-1].lower()}/app.py",
        f"{component_path}/{component_path.split('/')[-1].lower()}/main.py",
        f"{component_path}/{component_path.split('/')[-1].lower()}/__main__.py"
    ]
    
    for app_file in app_files:
        if os.path.exists(app_file):
            files_checked.append(app_file)
            with open(app_file, 'r') as f:
                content = f.read()
                
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, content):
                    results[pattern_name] = True
    
    return results, files_checked

def main():
    """Main function to check all components."""
    tekton_root = Path(__file__).parent.parent
    
    print("Checking shutdown patterns across Tekton components...")
    print("=" * 80)
    
    component_results = {}
    
    for component in components:
        component_path = tekton_root / component
        if component_path.exists():
            results, files = check_component(str(component_path))
            component_results[component] = results
            
            print(f"\n{component}:")
            print(f"  Files checked: {len(files)}")
            for pattern, found in results.items():
                status = "✓" if found else "✗"
                print(f"  {status} {pattern}")
    
    # Summary of potential issues
    print("\n" + "=" * 80)
    print("\nPotential issues (components missing shutdown handlers):")
    for component, results in component_results.items():
        if not results.get("shutdown_handler"):
            print(f"  - {component}: No shutdown handler found")
    
    print("\nComponents without socket reuse options:")
    for component, results in component_results.items():
        if not results.get("socket_reuse"):
            print(f"  - {component}: No socket reuse options")

if __name__ == "__main__":
    main()