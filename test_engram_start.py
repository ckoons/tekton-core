#!/usr/bin/env python3
"""
Test script to start the Engram server directly
"""

import os
import sys
import logging
import subprocess
import time
import requests
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("engram_test")

# Add Engram path to Python path
engram_path = os.path.join(os.path.dirname(__file__), "Engram")
sys.path.insert(0, engram_path)

def start_engram_server():
    """Start the Engram server as a subprocess"""
    logger.info("Starting Engram server directly...")
    
    # Create data and log directories
    os.makedirs(f"{os.environ['HOME']}/.tekton/data", exist_ok=True)
    os.makedirs(f"{os.environ['HOME']}/.tekton/logs", exist_ok=True)
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{engram_path}:{env.get('PYTHONPATH', '')}"
    env["ENGRAM_USE_FALLBACK"] = "1"  # Force fallback mode to avoid vector DB issues
    
    try:
        # First try direct module import and serve
        from engram.api.consolidated_server import app, main
        
        logger.info("Successfully imported consolidated_server, can launch API directly...")
        logger.info("Starting Engram standalone server...")
        
        # Start Engram server as a process
        command = [
            "python", "-m", "engram.api.consolidated_server",
            "--data-dir", f"{os.environ['HOME']}/.tekton/data",
            "--port", "8000", 
            "--host", "127.0.0.1"
        ]
        
        process = subprocess.Popen(
            command,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait to see if the process starts
        time.sleep(2)
        if process.poll() is not None:
            return_code = process.poll()
            stdout, stderr = process.communicate()
            logger.error(f"Server exited with code {return_code}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        logger.info(f"Engram server started with PID: {process.pid}")
        return process
        
    except ImportError as e:
        logger.error(f"Failed to import consolidated_server: {e}")
        logger.info("Trying script-based approach...")
        
        # Try script-based approach
        script_path = os.path.join(engram_path, "core", "engram_consolidated")
        if not os.path.exists(script_path):
            logger.error(f"Server script not found at {script_path}")
            return None
        
        # Run the consolidated script
        process = subprocess.Popen(
            [script_path, "--data-dir", f"{os.environ['HOME']}/.tekton/data", "--debug"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait to see if the process starts
        time.sleep(2)
        if process.poll() is not None:
            return_code = process.poll()
            stdout, stderr = process.communicate()
            logger.error(f"Server exited with code {return_code}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return None
        
        logger.info(f"Engram server started with PID: {process.pid}")
        return process

def check_health_endpoint(timeout=60):
    """Check if the health endpoint is responding"""
    logger.info(f"Waiting for health endpoint to be available (timeout: {timeout}s)...")
    
    url = "http://127.0.0.1:8000/health"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                logger.info("Health endpoint is available!")
                logger.info(f"Response: {response.json()}")
                return True
        except Exception:
            pass
        
        # Wait a second before trying again
        time.sleep(1)
        sys.stdout.write(".")
        sys.stdout.flush()
    
    logger.error(f"Health endpoint not available after {timeout} seconds")
    return False

def stop_process(process):
    """Stop the Engram server process"""
    if process is None:
        logger.warning("No process to stop")
        return
    
    logger.info(f"Stopping Engram server (PID: {process.pid})...")
    try:
        # Try graceful shutdown first
        process.terminate()
        time.sleep(2)
        
        # If still running, force kill
        if process.poll() is None:
            logger.warning("Server did not respond to terminate, using kill signal")
            os.kill(process.pid, signal.SIGKILL)
            time.sleep(1)
        
        # Get any output
        stdout, stderr = process.communicate()
        logger.info(f"Server output: {stdout}")
        if stderr:
            logger.warning(f"Server error output: {stderr}")
        
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Error stopping server: {e}")

if __name__ == "__main__":
    print("Testing Engram direct start...\n")
    
    try:
        # Start the server
        process = start_engram_server()
        
        if process is not None:
            # Check if the health endpoint is available
            health_ok = check_health_endpoint(timeout=30)
            
            if health_ok:
                print("\n✅ Engram server started successfully and health endpoint is responding!")
            else:
                print("\n❌ Engram server started but health endpoint is not responding")
        else:
            print("\n❌ Failed to start Engram server")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        # Always try to stop the server
        if 'process' in locals() and process is not None:
            stop_process(process)