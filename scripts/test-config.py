#!/usr/bin/env python3
"""Test script to demonstrate centralized configuration"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tekton.utils.component_config import get_component_config
from tekton.utils.port_config import load_port_assignments

def main():
    print("🔍 Testing Centralized Configuration\n")
    
    # Test component configuration
    config = get_component_config()
    
    print("📦 All Components:")
    components = config.get_all_components()
    for comp_id, comp in sorted(components.items(), key=lambda x: x[1].port):
        print(f"  {comp.name:20} (port {comp.port:5}) - {comp.category:12} - {comp.description}")
    
    print(f"\n📊 Total Components: {len(components)}")
    
    # Test port configuration
    print("\n🔌 Port Configuration (from port_config.py):")
    ports = load_port_assignments()
    print(f"  Loaded {len(ports)} port assignments")
    
    # Test startup order
    print("\n🚀 Startup Order:")
    startup_groups = config.get_startup_order()
    for i, group in enumerate(startup_groups):
        print(f"  Priority {i}: {', '.join(group)}")
    
    # Test validation
    print("\n✅ Dependency Validation:")
    errors = config.validate_dependencies()
    if errors:
        for error in errors:
            print(f"  ❌ {error}")
    else:
        print("  All dependencies are valid!")
    
    # Test categories
    print("\n📂 Components by Category:")
    for cat in ['infrastructure', 'memory', 'ai', 'planning', 'workflow', 'execution', 'resources', 'ui']:
        comps = config.get_components_by_category(cat)
        if comps:
            print(f"  {cat.title()}: {', '.join(c.id for c in comps)}")

if __name__ == "__main__":
    main()