#!/usr/bin/env python3
"""
Wrapper script to register Sophia with Hermes.

This script is a wrapper around sophia/scripts/register_with_hermes.py.
"""

import os
import sys
import subprocess

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the actual registration script
registration_script = os.path.join(script_dir, "Sophia", "sophia", "scripts", "register_with_hermes.py")

def main():
    """Main entry point."""
    # Make sure the registration script exists
    if not os.path.exists(registration_script):
        print(f"Error: Registration script not found at {registration_script}", file=sys.stderr)
        sys.exit(1)
    
    # Make sure the script is executable
    if not os.access(registration_script, os.X_OK):
        os.chmod(registration_script, 0o755)
    
    # Run the registration script with the same arguments
    try:
        result = subprocess.run([registration_script] + sys.argv[1:], check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Error executing registration script: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()