#!/usr/bin/env python3
"""
Test script to verify socket reuse functionality
"""
import os
import sys
import time
import subprocess
import signal

# Add Tekton root to path
tekton_root = os.path.abspath(os.path.dirname(__file__))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

def test_component_restart(component_name, port):
    """Test rapid restart of a component"""
    print(f"\n=== Testing {component_name} on port {port} ===")
    
    # Set the port environment variable
    env = os.environ.copy()
    env[f"{component_name.upper()}_PORT"] = str(port)
    
    # Start the component
    print(f"Starting {component_name}...")
    proc = subprocess.Popen(
        [sys.executable, "-m", component_name],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a bit for it to start
    time.sleep(2)
    
    # Kill it
    print(f"Killing {component_name} (PID: {proc.pid})...")
    proc.send_signal(signal.SIGTERM)
    proc.wait(timeout=5)
    
    # Try to restart immediately
    print(f"Restarting {component_name} immediately...")
    proc2 = subprocess.Popen(
        [sys.executable, "-m", component_name],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a bit
    time.sleep(2)
    
    # Check if it's still running
    if proc2.poll() is None:
        print(f"✅ {component_name} restarted successfully!")
        proc2.send_signal(signal.SIGTERM)
        proc2.wait(timeout=5)
        return True
    else:
        # Get error output
        _, stderr = proc2.communicate()
        print(f"❌ {component_name} failed to restart!")
        print(f"Error: {stderr.decode()}")
        return False

def main():
    """Test socket reuse for various components"""
    # Test components with their ports
    test_cases = [
        ("rhetor", 8003),
        ("apollo", 8000),
        ("budget", 8001),
        ("hermes", 8005),
    ]
    
    results = []
    for component, port in test_cases:
        try:
            success = test_component_restart(component, port)
            results.append((component, success))
        except Exception as e:
            print(f"Error testing {component}: {e}")
            results.append((component, False))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for component, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{component}: {status}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)