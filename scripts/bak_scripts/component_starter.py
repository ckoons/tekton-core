#!/usr/bin/env python3
"""
Component Starter - Functions for starting Tekton components

This module provides functions for starting and managing Tekton components.
"""

import os
import sys
import logging
import subprocess
from typing import Dict, List, Any, Optional, Set, Union
import asyncio
import shutil

# Configure logging
logger = logging.getLogger("tekton_launcher.starter")

# Get Tekton directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEKTON_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# Import Tekton modules
try:
    from tekton.core.startup_instructions import StartUpInstructions
    from tekton.core.component_registration import ComponentRegistration
except ImportError:
    logger.error("Failed to import Tekton core modules. Make sure tekton-core is properly installed.")
    raise

    
async def create_virtual_environment(component_name: str, component_dir: str) -> bool:
    """
    Create or update a virtual environment for a component.
    
    Args:
        component_name: Name of the component
        component_dir: Directory of the component
        
    Returns:
        Success status
    """
    logger.info(f"Creating virtual environment for {component_name}")
    
    # Check if Python is available
    python_path = shutil.which("python3") or shutil.which("python")
    if not python_path:
        logger.error("Python executable not found")
        return False
    
    # Check if we can create virtual environments
    venv_module = subprocess.run(
        [python_path, "-m", "venv", "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if venv_module.returncode != 0:
        logger.error("Python venv module not available")
        return False
    
    # Set up virtual environment
    venv_dir = os.path.join(component_dir, "venv")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        logger.info(f"Creating new virtual environment in {venv_dir}")
        try:
            subprocess.run(
                [python_path, "-m", "venv", venv_dir],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to create virtual environment: {e}")
            return False
    
    # Get pip executable for the virtual environment
    if os.name == "nt":  # Windows
        pip_executable = os.path.join(venv_dir, "Scripts", "pip")
    else:  # Unix/Linux/Mac
        pip_executable = os.path.join(venv_dir, "bin", "pip")
    
    # Check if pip exists
    if not os.path.exists(pip_executable):
        logger.error(f"Pip not found in virtual environment: {pip_executable}")
        return False
    
    # Upgrade pip
    logger.info("Upgrading pip in virtual environment")
    try:
        subprocess.run(
            [pip_executable, "install", "--upgrade", "pip"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.SubprocessError as e:
        logger.warning(f"Failed to upgrade pip: {e}")
        
    # Install requirements if requirements.txt exists
    requirements_file = os.path.join(component_dir, "requirements.txt")
    if os.path.exists(requirements_file):
        logger.info(f"Installing requirements from {requirements_file}")
        try:
            subprocess.run(
                [pip_executable, "install", "-r", requirements_file],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to install requirements: {e}")
            return False
    
    # Install in development mode
    setup_py = os.path.join(component_dir, "setup.py")
    if os.path.exists(setup_py):
        logger.info(f"Installing component in development mode from {setup_py}")
        try:
            subprocess.run(
                [pip_executable, "install", "-e", component_dir],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to install component in development mode: {e}")
            return False
    
    logger.info(f"Virtual environment for {component_name} created successfully")
    return True


async def start_component(component_name: str, instructions: StartUpInstructions, use_subprocess: bool = True) -> bool:
    """
    Start a component with the given instructions.
    
    Args:
        component_name: Name of the component to start
        instructions: Startup instructions
        use_subprocess: Whether to start in a subprocess for isolation
        
    Returns:
        Success status
    """
    logger.info(f"Starting component: {component_name}")
    
    # Check if component directory exists
    component_dir = os.path.join(TEKTON_DIR, component_name)
    if not os.path.isdir(component_dir):
        logger.error(f"Component directory not found: {component_dir}")
        return False
    
    # Create data directories
    os.makedirs(instructions.data_directory, exist_ok=True)
    
    # Save instructions to a file
    instructions_file = os.path.join(
        os.path.expanduser("~/.tekton/data"),
        f"{component_name.lower()}_instructions.json"
    )
    instructions.save_to_file(instructions_file)
    
    # Find the register_with_hermes.py script
    register_script = None
    scripts_dir = os.path.join(component_dir, component_name.lower(), "scripts")
    if os.path.isdir(scripts_dir):
        register_script = os.path.join(scripts_dir, "register_with_hermes.py")
    
    # Check if script exists and is executable
    if register_script and os.path.isfile(register_script):
        logger.info(f"Found registration script: {register_script}")
        
        try:
            # Make script executable if it isn't already
            if not os.access(register_script, os.X_OK):
                os.chmod(register_script, 0o755)
                logger.info(f"Made script executable: {register_script}")
            
            # Set up environment for the script
            env = os.environ.copy()
            env["STARTUP_INSTRUCTIONS_FILE"] = instructions_file
            env["HERMES_URL"] = instructions.hermes_url
            env["PYTHONPATH"] = f"{component_dir}:{TEKTON_DIR}:{os.path.join(TEKTON_DIR, 'tekton-core')}:{env.get('PYTHONPATH', '')}"
            
            if use_subprocess:
                # Launch in a subprocess
                logger.info(f"Launching {component_name} in a subprocess with registration script")
                
                # Use the component's virtual environment if available
                python_executable = sys.executable
                venv_dir = os.path.join(component_dir, "venv")
                if os.path.isdir(venv_dir):
                    venv_python = os.path.join(venv_dir, "bin", "python")
                    if os.path.isfile(venv_python):
                        python_executable = venv_python
                        logger.info(f"Using virtual environment: {venv_dir}")
                
                # Start the process
                process = subprocess.Popen(
                    [python_executable, register_script],
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                
                # Log the process ID
                logger.info(f"Started {component_name} with PID: {process.pid}")
                
                # Return success
                return True
                
            else:
                # Import and run the module directly
                logger.info(f"Importing and running {component_name} registration module")
                
                # Add component to Python path
                if component_dir not in sys.path:
                    sys.path.insert(0, component_dir)
                
                # Import and run the module
                module_name = f"{component_name.lower()}.scripts.register_with_hermes"
                try:
                    __import__(module_name)
                    logger.info(f"Successfully imported {module_name}")
                    return True
                except ImportError as e:
                    logger.error(f"Failed to import {module_name}: {e}")
                    return False
                
        except Exception as e:
            logger.exception(f"Error starting component {component_name}: {e}")
            return False
    else:
        # No registration script found, attempt to register directly
        logger.warning(f"No registration script found for {component_name}, attempting direct registration")
        
        try:
            # Create a generic registration
            registration = ComponentRegistration(
                component_id=instructions.component_id,
                component_name=component_name,
                version=instructions.metadata.get("version", "0.1.0"),
                hermes_url=instructions.hermes_url,
                capabilities=instructions.capabilities,
                metadata=instructions.metadata
            )
            
            # Register with Hermes
            result = await registration.register()
            if result:
                logger.info(f"Successfully registered {component_name} with Hermes")
                return True
            else:
                logger.error(f"Failed to register {component_name} with Hermes")
                return False
                
        except Exception as e:
            logger.exception(f"Error registering component {component_name}: {e}")
            return False