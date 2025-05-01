# Tekton Register Implementation Plan

## Overview

This plan outlines the implementation of a standardized `tekton-register` utility that will replace all individual `register_with_hermes.py` scripts across Tekton components. This unified approach will eliminate code duplication, improve maintainability, and ensure consistent behavior across all components.

## Current State Analysis

Each Tekton component currently has its own `register_with_hermes.py` script:
- 13 separate registration scripts have been identified
- Code is largely duplicated across components
- Minor variations in implementation cause inconsistent behavior
- Maintenance requires changes in multiple places
- Newer components already attempt to use shared utilities with fallbacks

## Implementation Plan

### Phase 1: Core tekton-register Utility (Week 1)

1. **Create Core Registration Library in tekton-core**
   ```
   tekton-core/tekton/utils/registration/
   ├── __init__.py
   ├── cli.py               # Command-line interface
   ├── config.py            # Configuration loading
   ├── models.py            # Data models
   ├── registry.py          # Registration logic
   └── heartbeat.py         # Heartbeat handling
   ```

2. **Implement Component Capability Model**
   - Define a standardized schema for component capabilities
   - Create Pydantic models for validation
   - Support JSON/YAML serialization and deserialization
   - Include validation for required fields and data types

3. **Implement Registration Logic**
   - Create a HermesRegistrationClient class
   - Implement registration, heartbeat, and unregistration methods
   - Handle connection errors and retries
   - Implement proper signal handling for graceful shutdown

4. **Create Command-Line Interface**
   - Implement `tekton-register` script at `tekton-core/scripts/bin/tekton-register`
   - Support multiple commands (register, unregister, status)
   - Include options for component ID, config file path, and runtime parameters

### Phase 2: Component Configuration (Week 1-2)

1. **Define YAML Configuration Format**
   ```yaml
   # component.yaml format
   component:
     id: "component_id"
     name: "Component Name"
     version: "0.1.0"
     description: "Component description"
     port: 8000

   capabilities:
     - id: "capability_id"
       name: "Capability Name"
       description: "Capability description"
       methods:
         - id: "method_id"
           name: "Method Name"
           description: "Method description"
           parameters:
             - name: "param_name"
               type: "string"
               required: true
           returns:
             type: "object"
   ```

2. **Create Configuration Generator**
   - Create a utility to generate configuration templates
   - Include an interactive mode for guided setup
   - Implement auto-discovery of component properties when possible

3. **Create Component YAML Configurations**
   - Create a YAML configuration file for each component
   - Document all capabilities accurately
   - Place files in standardized locations within each component

### Phase 3: Component Migration (Week 2-3)

1. **Create Migration Strategy**
   - Document step-by-step migration process
   - Create test plans to validate registration
   - Determine order of component migration (simplest to most complex)

2. **Initial Component Migration**
   - Select two initial components for migration:
     - Telos (newer component with clean structure)
     - Rhetor (core component with multiple capabilities)
   - Create YAML configuration files for selected components
   - Update launch scripts to use `tekton-register` instead of the component-specific script
   - Test registration, heartbeat, and unregistration

3. **Batch Component Migration**
   - Create YAML configs for all remaining components
   - Update all launch scripts to use `tekton-register`
   - Test each component with the new registration system
   - Document any component-specific considerations

4. **Remove Legacy Scripts**
   - After successful migration and testing, remove all component-specific `register_with_hermes.py` scripts
   - Update documentation to reflect the new registration process

### Phase 4: Documentation and Integration (Week 3-4)

1. **Update Documentation**
   - Update `docs/COMPONENT_LIFECYCLE.md` with the new registration process
   - Update `docs/SHARED_COMPONENT_UTILITIES.md` with details about `tekton-register`
   - Create a comprehensive guide for adding new components with proper registration

2. **Integration with Component Startup**
   - Update `tekton-launch` to use the new registration utility
   - Integrate with the Single Port Architecture
   - Ensure proper shutdown and cleanup during component termination

3. **Validation and Testing**
   - Test all components with the new registration system
   - Verify heartbeat functionality
   - Test error handling and recovery
   - Ensure backward compatibility where needed

## Detailed Implementation: tekton-register CLI

The `tekton-register` CLI will be implemented as follows:

```python
#!/usr/bin/env python3
"""
Tekton Component Registration Tool

Registers Tekton components with Hermes service registry.

Usage:
    tekton-register register --component COMPONENT_ID [--config CONFIG_FILE] [--hermes-url URL]
    tekton-register unregister --component COMPONENT_ID [--hermes-url URL]
    tekton-register status --component COMPONENT_ID [--hermes-url URL]
    tekton-register generate --component COMPONENT_ID [--output OUTPUT_FILE]
"""

import sys
import os
import argparse
import asyncio
import signal
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add tekton-core to path
script_dir = os.path.dirname(os.path.abspath(__file__))
tekton_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, tekton_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tekton.register")

# Import tekton-core utilities
try:
    from tekton.utils.registration.registry import register_component, unregister_component
    from tekton.utils.registration.config import load_component_config, find_component_config
    from tekton.utils.registration.models import ComponentConfig, validate_component_config
    REGISTRATION_UTILS_AVAILABLE = True
except ImportError:
    logger.warning("Tekton registration utilities not available. Falling back to direct implementation.")
    REGISTRATION_UTILS_AVAILABLE = False
    # Implement fallback registration logic here

async def register_command(args):
    """Register a component with Hermes."""
    # Load component configuration
    if args.config:
        config_path = args.config
    else:
        config_path = find_component_config(args.component)
        if not config_path:
            logger.error(f"No configuration found for component '{args.component}'")
            logger.error("Please specify a configuration file with --config")
            return 1
    
    # Load and validate configuration
    try:
        config = load_component_config(config_path)
        logger.info(f"Loaded configuration for {config.component.name} ({config.component.id})")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return 1
    
    # Register component
    try:
        client = await register_component(
            component_id=config.component.id,
            component_name=config.component.name,
            component_type=config.component.type,
            component_version=config.component.version,
            capabilities=config.capabilities,
            hermes_url=args.hermes_url,
            dependencies=config.dependencies,
            endpoint=args.endpoint or config.component.endpoint,
            additional_metadata=config.component.metadata
        )
        
        if client:
            logger.info(f"Successfully registered {config.component.name} with Hermes")
            
            # Set up signal handlers
            loop = asyncio.get_event_loop()
            stop_event = asyncio.Event()
            
            def handle_signal(sig):
                logger.info(f"Received signal {sig.name}, shutting down")
                asyncio.create_task(client.close())
                stop_event.set()
            
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
            
            logger.info("Registration active. Press Ctrl+C to unregister and exit...")
            try:
                await stop_event.wait()
            except Exception as e:
                logger.error(f"Error during registration: {e}")
                await client.close()
            
            return 0
        else:
            logger.error(f"Failed to register {config.component.name} with Hermes")
            return 1
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        return 1

async def unregister_command(args):
    """Unregister a component from Hermes."""
    try:
        success = await unregister_component(args.component, args.hermes_url)
        if success:
            logger.info(f"Successfully unregistered {args.component} from Hermes")
            return 0
        else:
            logger.error(f"Failed to unregister {args.component} from Hermes")
            return 1
    except Exception as e:
        logger.error(f"Error during unregistration: {e}")
        return 1

def generate_command(args):
    """Generate a component configuration template."""
    # Implementation details for generating component configuration
    pass

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Register Tekton components with Hermes service registry"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register a component with Hermes")
    register_parser.add_argument("--component", required=True, help="Component ID to register")
    register_parser.add_argument("--config", help="Path to component configuration file")
    register_parser.add_argument("--hermes-url", help="URL of the Hermes API",
                               default=os.environ.get("HERMES_URL", "http://localhost:8100/api"))
    register_parser.add_argument("--endpoint", help="API endpoint for the component")
    
    # Unregister command
    unregister_parser = subparsers.add_parser("unregister", help="Unregister a component from Hermes")
    unregister_parser.add_argument("--component", required=True, help="Component ID to unregister")
    unregister_parser.add_argument("--hermes-url", help="URL of the Hermes API",
                                 default=os.environ.get("HERMES_URL", "http://localhost:8100/api"))
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check component registration status")
    status_parser.add_argument("--component", required=True, help="Component ID to check")
    status_parser.add_argument("--hermes-url", help="URL of the Hermes API",
                             default=os.environ.get("HERMES_URL", "http://localhost:8100/api"))
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a component configuration template")
    generate_parser.add_argument("--component", required=True, help="Component ID to generate config for")
    generate_parser.add_argument("--output", help="Output file path")
    
    return parser.parse_args()

async def main():
    """Main entry point."""
    args = parse_arguments()
    
    if args.command == "register":
        return await register_command(args)
    elif args.command == "unregister":
        return await unregister_command(args)
    elif args.command == "status":
        # Implement status command
        pass
    elif args.command == "generate":
        return generate_command(args)
    else:
        logger.error("No command specified")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

## Migration Example for a Component

For each component, the migration will follow this pattern:

1. **Create YAML Configuration**
   ```yaml
   # telos.yaml
   component:
     id: "telos"
     name: "Telos Requirements Management"
     version: "0.1.0"
     description: "Requirements management and traceability system"
     port: 8800
     endpoint: "http://localhost:8800/api"
     
   capabilities:
     - id: "requirements_management"
       name: "Requirements Management"
       description: "Create and manage project requirements"
       methods:
         - id: "create_requirement"
           name: "Create Requirement"
           description: "Create a new requirement"
           parameters:
             - name: "name"
               type: "string"
               required: true
             - name: "description"
               type: "string"
               required: true
           returns:
             type: "object"
   ```

2. **Update Launch Script**
   Replace:
   ```bash
   python /path/to/telos/register_with_hermes.py
   ```
   
   With:
   ```bash
   tekton-register register --component telos
   ```

3. **After Migration**
   - Validate registration works correctly
   - Remove the original `register_with_hermes.py` script
   - Update any documentation references

## Deliverables

1. **tekton-register Utility**
   - Core registration library in tekton-core
   - Command-line interface
   - Configuration schema and validation

2. **Component Configuration Files**
   - YAML configuration files for all components
   - Standardized format and location

3. **Updated Documentation**
   - Registration process documentation
   - Migration guide
   - Component development guidelines

4. **Migration Results**
   - All components converted to use tekton-register
   - All individual register_with_hermes.py scripts removed
   - Consistent registration behavior across the platform

## Success Criteria

1. All components successfully register with Hermes using the shared utility
2. No individual register_with_hermes.py scripts remain in any component
3. Registration process is well-documented for future components
4. All component capabilities are correctly registered and discoverable

## Timeline

- **Week 1**: Core library and CLI implementation
- **Week 2**: Initial component migration (2-3 components)
- **Week 3**: Complete component migration (all remaining components)
- **Week 4**: Documentation, testing, and cleanup