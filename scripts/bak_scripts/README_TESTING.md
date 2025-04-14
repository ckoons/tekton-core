# Tekton Testing Guide

This document provides instructions for testing the Tekton startup process.

## Testing the Startup Sequence

The `test_startup_sequence.py` script is designed to validate the complete Tekton startup sequence, including:

1. Component dependency resolution
2. Registration with Hermes
3. Heartbeat monitoring and reconnection after Hermes restarts
4. Virtual environment isolation

### Prerequisites

Before running the test script, make sure you have:

1. Installed all required dependencies for both Tekton core and individual components
2. Built and configured Hermes (required for registration tests)
3. Set up virtual environments for each component if testing isolation

### Running the Test

To run the complete test suite:

```bash
cd /Users/cskoons/projects/github/Tekton
./scripts/test_startup_sequence.py
```

This will test the startup sequence for the default components (Synthesis, Harmonia, Athena, Sophia).

### Test Options

The test script supports several options:

- `--components`: Comma-separated list of components to test (default: Synthesis,Harmonia,Athena,Sophia)
- `--hermes-url`: URL of the Hermes API (default: http://localhost:5000/api)
- `--no-restart-test`: Skip the Hermes restart test
- `--verbose`: Enable verbose logging

Example:

```bash
./scripts/test_startup_sequence.py --components Synthesis,Harmonia --no-restart-test --verbose
```

### Test Phases

The test runs through four phases:

1. **Dependency Resolution**: Verifies that component dependencies are properly resolved and components start in the correct order.
2. **Virtual Environment Isolation**: Checks that each component has its own virtual environment with the required dependencies.
3. **Startup Sequence**: Tests the full startup sequence using the launcher script.
4. **Hermes Restart Handling**: Simulates a Hermes restart and verifies that components can reconnect automatically.

## Interpreting Results

The test outputs a summary of results for each phase:

```
=== Test Results ===
dependency_resolution: PASSED
venv_isolation: PASSED
startup_sequence: PASSED
hermes_restart: PASSED

Overall Status: PASSED
```

If any tests fail, examine the log output to understand the cause of the failure.

## Troubleshooting

If tests fail, check the following:

1. **Dependency Resolution Failure**: Ensure there are no circular dependencies between components.
2. **Virtual Environment Isolation Failure**: Verify that each component has a properly set up virtual environment with the required dependencies.
3. **Startup Sequence Failure**: Check the launcher logs for component-specific errors.
4. **Hermes Restart Failure**: Ensure the heartbeat monitoring system is properly configured and components have the correct registration code.

For more detailed diagnostics, run the test with the `--verbose` flag.