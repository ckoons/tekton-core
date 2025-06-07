#!/usr/bin/env python3
"""
Comprehensive test runner for Tekton A2A Protocol v0.2.1

Usage:
    ./run_all_tests.py              # Run all tests
    ./run_all_tests.py --unit       # Run only unit tests
    ./run_all_tests.py --integration # Run only integration tests
    ./run_all_tests.py --manual     # Run manual API tests
    ./run_all_tests.py -u           # Short form for --unit
    ./run_all_tests.py -i           # Short form for --integration
    ./run_all_tests.py -m           # Short form for --manual
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Test categories
UNIT_TESTS = {
    "Unit Tests - JSON-RPC": "tests/unit/a2a/test_jsonrpc_messages.py",
    "Unit Tests - Agent Cards": "tests/unit/a2a/test_agent_cards.py", 
    "Unit Tests - Task Lifecycle": "tests/unit/a2a/test_task_lifecycle.py",
    "Unit Tests - Discovery": "tests/unit/a2a/test_discovery.py",
}

INTEGRATION_TESTS = {
    "Integration Tests - Hermes A2A": "tests/integration/a2a/test_hermes_a2a.py"
}

MANUAL_TEST_SCRIPT = "tests/test_a2a_manual.sh"

def run_pytest_suite(suite_name: str, test_path: str) -> bool:
    """Run a pytest test suite and return success status"""
    print(f"\n{suite_name}")
    print("-" * len(suite_name))
    
    # Check if test file exists
    if not os.path.exists(test_path):
        print(f"❌ Test file not found: {test_path}")
        return False
    
    # Run pytest
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    # For integration tests, we need to set PYTHONPATH to include Hermes
    env = os.environ.copy()
    if "integration" in suite_name.lower():
        hermes_path = os.path.join(project_root, "Hermes")
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{hermes_path}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = hermes_path
    
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    if result.returncode == 0:
        print("✅ PASSED")
        return True
    else:
        print("❌ FAILED")
        
        # Extract and print summary
        lines = result.stdout.split('\n')
        for line in lines:
            if 'failed' in line and 'passed' in line:
                print(f"   {line.strip()}")
                break
        
        # Print errors if verbose
        if result.stderr and "ModuleNotFoundError" in result.stderr:
            print("   Note: Integration tests require Hermes to be importable")
        
        return False

def run_manual_tests() -> bool:
    """Run manual API tests"""
    print("\nManual API Tests")
    print("-" * 16)
    
    if not os.path.exists(MANUAL_TEST_SCRIPT):
        print(f"❌ Manual test script not found: {MANUAL_TEST_SCRIPT}")
        return False
    
    # Make sure script is executable
    subprocess.run(["chmod", "+x", MANUAL_TEST_SCRIPT], capture_output=True)
    
    # Run the script
    result = subprocess.run([MANUAL_TEST_SCRIPT], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ COMPLETED")
        # Check output for failures
        if "error" in result.stdout.lower() and "error handling" not in result.stdout.lower():
            print("   ⚠️  Some API calls returned errors")
        return True
    else:
        print("❌ FAILED TO RUN")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Run Tekton A2A Protocol tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "-u", "--unit",
        action="store_true",
        help="Run only unit tests"
    )
    
    parser.add_argument(
        "-i", "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    
    parser.add_argument(
        "-m", "--manual",
        action="store_true",
        help="Run only manual API tests"
    )
    
    args = parser.parse_args()
    
    # Determine which tests to run
    run_unit = True
    run_integration = True
    run_manual = True
    
    if args.unit or args.integration or args.manual:
        # If any specific flag is set, only run those
        run_unit = args.unit
        run_integration = args.integration
        run_manual = args.manual
    
    print("=" * 80)
    print("Tekton A2A Protocol v0.2.1 Test Runner")
    print("=" * 80)
    
    all_passed = True
    results = {}
    
    # Run unit tests
    if run_unit:
        print("\n📋 UNIT TESTS")
        print("=" * 40)
        for suite_name, test_path in UNIT_TESTS.items():
            passed = run_pytest_suite(suite_name, test_path)
            results[suite_name] = "PASSED" if passed else "FAILED"
            if not passed:
                all_passed = False
    
    # Run integration tests
    if run_integration:
        print("\n🔗 INTEGRATION TESTS")
        print("=" * 40)
        for suite_name, test_path in INTEGRATION_TESTS.items():
            passed = run_pytest_suite(suite_name, test_path)
            results[suite_name] = "PASSED" if passed else "FAILED"
            if not passed:
                all_passed = False
                # Add note about integration test requirements
                if "ModuleNotFoundError" in str(passed):
                    results[suite_name] += " (Requires Hermes module)"
    
    # Run manual tests
    if run_manual:
        print("\n🖱️  MANUAL API TESTS")
        print("=" * 40)
        passed = run_manual_tests()
        results["Manual API Tests"] = "COMPLETED" if passed else "FAILED"
        if not passed:
            all_passed = False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    # Group by test type
    if run_unit:
        print("\n📋 Unit Tests:")
        for suite, status in results.items():
            if "Unit" in suite:
                status_icon = "✅" if status == "PASSED" else "❌"
                print(f"  {status_icon} {suite}: {status}")
    
    if run_integration:
        print("\n🔗 Integration Tests:")
        for suite, status in results.items():
            if "Integration" in suite:
                status_icon = "✅" if status == "PASSED" else "❌"
                print(f"  {status_icon} {suite}: {status}")
    
    if run_manual:
        print("\n🖱️  Manual Tests:")
        for suite, status in results.items():
            if "Manual" in suite:
                status_icon = "✅" if status == "COMPLETED" else "❌"
                print(f"  {status_icon} {suite}: {status}")
    
    print("\n" + "=" * 80)
    
    # Overall status
    total_tests = len(results)
    passed_tests = sum(1 for status in results.values() if status in ["PASSED", "COMPLETED"])
    
    print(f"Total: {passed_tests}/{total_tests} test suites passed")
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
        
        # Provide helpful hints
        if any("Integration" in suite for suite in results if results[suite] == "FAILED"):
            print("\n💡 Hint: Integration tests require Hermes module to be importable.")
            print("   Consider running from Hermes directory or setting PYTHONPATH.")
        
        if any("Manual" in suite for suite in results):
            print("\n💡 Hint: Manual tests require Hermes to be running on port 8001.")
            print("   Start with: ./Hermes/run_hermes.sh")
    
    print("=" * 80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())