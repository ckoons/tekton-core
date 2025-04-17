#!/usr/bin/env python3
"""
Test script to check Hermes API functionality
"""

import os
import sys
import logging
import subprocess
import time
import requests
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("hermes_test")

# Add Hermes path to Python path
hermes_path = os.path.join(os.path.dirname(__file__), "Hermes")
sys.path.insert(0, hermes_path)

def start_hermes_api():
    """Start the Hermes API server directly"""
    logger.info("Starting Hermes API server...")
    
    # Create data and log directories
    os.makedirs(f"{os.environ['HOME']}/.tekton/data/hermes", exist_ok=True)
    os.makedirs(f"{os.environ['HOME']}/.tekton/logs", exist_ok=True)
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{hermes_path}:{env.get('PYTHONPATH', '')}"
    env["PORT"] = "8100"  # Use port 8100 for the API
    env["HOST"] = "127.0.0.1"
    env["HERMES_DATA_DIR"] = f"{os.environ['HOME']}/.tekton/data/hermes"
    env["DB_MCP_PORT"] = "8101"
    env["DB_MCP_HOST"] = "127.0.0.1"
    env["DEBUG"] = "True"
    
    # Start the Hermes API server
    api_path = os.path.join(hermes_path, "hermes", "api", "app.py")
    
    if os.path.exists(api_path):
        command = [sys.executable, api_path]
        
        process = subprocess.Popen(
            command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait to see if process starts
        time.sleep(2)
        if process.poll() is not None:
            return_code = process.poll()
            stdout, stderr = process.communicate()
            logger.error(f"Server exited with code {return_code}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        logger.info(f"Hermes API server started with PID: {process.pid}")
        return process
    else:
        logger.error(f"Hermes API server script not found at {api_path}")
        return None

def check_api_endpoint(url, timeout=30):
    """Check if an API endpoint is responding"""
    logger.info(f"Waiting for {url} to be available (timeout: {timeout}s)...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            logger.info(f"Response status: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"API is available! Response: {response.text}")
                return True
            else:
                logger.warning(f"API responded with status {response.status_code}")
        except requests.RequestException as e:
            logger.debug(f"Request failed: {e}")
        
        # Wait before trying again
        time.sleep(1)
        sys.stdout.write(".")
        sys.stdout.flush()
    
    logger.error(f"API not available after {timeout} seconds")
    return False

def stop_process(process):
    """Stop a running process"""
    if process is None:
        return
    
    logger.info(f"Stopping process (PID: {process.pid})...")
    try:
        process.terminate()
        time.sleep(2)
        
        if process.poll() is None:
            # Force kill if still running
            logger.warning("Process did not terminate, sending SIGKILL")
            process.kill()
            time.sleep(1)
        
        stdout, stderr = process.communicate()
        logger.info(f"Process output: {stdout}")
        if stderr:
            logger.warning(f"Process error output: {stderr}")
        
        logger.info("Process stopped")
    except Exception as e:
        logger.error(f"Error stopping process: {e}")

if __name__ == "__main__":
    print("Testing Hermes API server...\n")
    
    try:
        api_process = start_hermes_api()
        
        if api_process:
            # Check API endpoints
            root_ok = check_api_endpoint("http://localhost:8100/")
            health_ok = check_api_endpoint("http://localhost:8100/api/health")
            
            if root_ok and health_ok:
                print("\n✅ Hermes API server is running properly!")
            else:
                print("\n❌ Hermes API server is not responding correctly")
        else:
            print("\n❌ Failed to start Hermes API server")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        # Clean up processes
        if 'api_process' in locals() and api_process:
            stop_process(api_process)