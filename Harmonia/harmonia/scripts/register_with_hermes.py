#!/usr/bin/env python3
"""
Register Harmonia with Hermes

This script registers the Harmonia component with the Hermes service registry,
allowing other components to discover and use its capabilities.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("harmonia.scripts.register_with_hermes")

# Add parent directory to path to allow importing Tekton core
script_dir = os.path.dirname(os.path.abspath(__file__))
harmonia_dir = os.path.abspath(os.path.join(script_dir, "../.."))
tekton_dir = os.path.abspath(os.path.join(harmonia_dir, ".."))
tekton_core_dir = os.path.join(tekton_dir, "tekton-core")

# Add to Python path
sys.path.insert(0, harmonia_dir)
sys.path.insert(0, tekton_dir)
sys.path.insert(0, tekton_core_dir)

# Determine if we're in a virtual environment
in_venv = sys.prefix != sys.base_prefix
if not in_venv:
    logger.warning("Not running in a virtual environment. Consider activating the Harmonia venv.")

# Try to import startup instructions
try:
    from tekton.core.component_registration import StartUpInstructions, ComponentRegistration
except ImportError:
    logger.error("Failed to import Tekton core modules. Make sure tekton-core is properly installed.")
    # Fallback to direct registration without StartUpInstructions
    HAS_STARTUP_INSTRUCTIONS = False
else:
    HAS_STARTUP_INSTRUCTIONS = True


async def register_with_hermes(instructions_file: Optional[str] = None, hermes_url: Optional[str] = None):
    """
    Register Harmonia with Hermes.
    
    Args:
        instructions_file: Path to StartUpInstructions JSON file
        hermes_url: URL of Hermes API
    """
    try:
        import aiohttp
        
        # Check for StartUpInstructions
        if HAS_STARTUP_INSTRUCTIONS and instructions_file and os.path.isfile(instructions_file):
            logger.info(f"Loading startup instructions from {instructions_file}")
            instructions = StartUpInstructions.from_file(instructions_file)
            capabilities = instructions.capabilities
            metadata = instructions.metadata
            hermes_url = instructions.hermes_url
            component_id = instructions.component_id
        else:
            # Use default values
            component_id = "harmonia.workflow"
            hermes_url = hermes_url or os.environ.get("HERMES_URL", "http://localhost:5000/api")
            
            # Define Harmonia capabilities
            capabilities = [
                {
                    "name": "create_workflow",
                    "description": "Create a new workflow definition",
                    "parameters": {
                        "name": "string",
                        "description": "string (optional)",
                        "tasks": "array",
                        "input": "object (optional)",
                        "output": "object (optional)"
                    }
                },
                {
                    "name": "execute_workflow",
                    "description": "Execute a workflow",
                    "parameters": {
                        "workflow_id": "string",
                        "input": "object (optional)"
                    }
                },
                {
                    "name": "get_workflow_status",
                    "description": "Get the status of a workflow execution",
                    "parameters": {
                        "execution_id": "string"
                    }
                },
                {
                    "name": "cancel_workflow",
                    "description": "Cancel a workflow execution",
                    "parameters": {
                        "execution_id": "string"
                    }
                }
            ]
            
            # Default metadata
            metadata = {
                "description": "Workflow orchestration engine",
                "version": "0.1.0",
                "dependencies": ["hermes.core.database"]
            }
        
        # Register with Hermes using ComponentRegistration if available
        if HAS_STARTUP_INSTRUCTIONS:
            registration = ComponentRegistration(
                component_id=component_id,
                component_name="Harmonia",
                hermes_url=hermes_url,
                capabilities=capabilities,
                metadata=metadata
            )
            
            result = await registration.register()
            if result:
                logger.info(f"Successfully registered Harmonia ({component_id}) with Hermes")
                return True
            else:
                logger.error(f"Failed to register Harmonia with Hermes")
                return False
        
        # Fallback to direct registration via API
        else:
            logger.info(f"Registering Harmonia with Hermes at {hermes_url}")
            
            # Define services
            services = [
                {
                    "service_id": component_id,
                    "name": "Harmonia Workflow Engine",
                    "version": "0.1.0",
                    "endpoint": "http://localhost:5006/api/workflows",
                    "capabilities": capabilities,
                    "metadata": metadata
                },
                {
                    "service_id": "harmonia.state",
                    "name": "Harmonia State Manager",
                    "version": "0.1.0",
                    "endpoint": "http://localhost:5006/api/state",
                    "capabilities": [
                        {
                            "name": "save_state",
                            "description": "Save workflow state",
                            "parameters": {
                                "execution_id": "string",
                                "state": "object"
                            }
                        },
                        {
                            "name": "load_state",
                            "description": "Load workflow state",
                            "parameters": {
                                "execution_id": "string"
                            }
                        },
                        {
                            "name": "create_checkpoint",
                            "description": "Create a checkpoint of workflow state",
                            "parameters": {
                                "execution_id": "string"
                            }
                        }
                    ],
                    "metadata": {
                        "description": "State management for workflow engine",
                        "version": "0.1.0",
                        "parent_component": "harmonia.workflow"
                    }
                }
            ]
            
            # Register each service
            async with aiohttp.ClientSession() as session:
                for service in services:
                    logger.info(f"Registering service: {service['service_id']}")
                    
                    async with session.post(
                        f"{hermes_url}/registration/register",
                        json=service
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"Successfully registered service {service['service_id']}: {data}")
                        else:
                            error = await response.text()
                            logger.error(f"Failed to register service {service['service_id']}: {error}")
                
                # Send heartbeat to indicate component is alive
                async with session.post(
                    f"{hermes_url}/registration/heartbeat",
                    json={"component": "harmonia", "status": "active"}
                ) as response:
                    if response.status == 200:
                        logger.info("Sent heartbeat to Hermes")
                    else:
                        logger.warning("Failed to send heartbeat to Hermes")
                    
    except Exception as e:
        logger.exception(f"Error registering services with Hermes: {e}")


async def main():
    """Main entry point."""
    logger.info("Registering Harmonia with Hermes...")
    
    # Check for StartUpInstructions file from environment
    instructions_file = os.environ.get("STARTUP_INSTRUCTIONS_FILE")
    hermes_url = os.environ.get("HERMES_URL", "http://localhost:5000/api")
    
    await register_with_hermes(instructions_file, hermes_url)
    
    logger.info("Registration complete. Harmonia services are now available to other components.")


if __name__ == "__main__":
    asyncio.run(main())