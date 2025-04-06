#!/usr/bin/env python3
"""
Stress Test Configuration

Defines configuration parameters for the stress test.
"""

import os

# Core configuration
NUM_SERVICES = int(os.environ.get("TEKTON_STRESS_SERVICES", "5"))
NUM_DATABASES = int(os.environ.get("TEKTON_STRESS_DATABASES", "2"))
NUM_CLIENTS = int(os.environ.get("TEKTON_STRESS_CLIENTS", "10"))
TEST_DURATION = int(os.environ.get("TEKTON_STRESS_DURATION", "60"))  # seconds

# Failure configuration
FAILURE_PROBABILITY = float(os.environ.get("TEKTON_STRESS_FAILURE_PROB", "0.2"))  # 20% chance of service failure during test
RECOVERY_PROBABILITY = float(os.environ.get("TEKTON_STRESS_RECOVERY_PROB", "0.7"))  # 70% chance of recovery after failure

# Database configuration
DB_ERROR_RATE = float(os.environ.get("TEKTON_STRESS_DB_ERROR_RATE", "0.05"))  # 5% chance of database query failure

# Performance configuration 
BASE_REQUEST_RATE = float(os.environ.get("TEKTON_STRESS_BASE_RATE", "2.0"))  # Base requests per second

# Directories
DATA_DIR = os.environ.get("TEKTON_STRESS_DATA_DIR", "/tmp/tekton_stress_test")
