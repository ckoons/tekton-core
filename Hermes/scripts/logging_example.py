#!/usr/bin/env python3
"""
Centralized Logging System Example - Demonstrates logging capabilities.

This script demonstrates how Tekton components can use the Centralized
Logging System for structured, schema-versioned logging.
"""

import os
import sys
import logging
import time
import argparse
import datetime
import traceback
import random
from typing import Dict, Any, Optional, List

# Add project root to Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hermes.core.logging import LogLevel, init_logging, get_logger
from hermes.utils.logging_helper import (
    setup_logging, intercept_python_logging, patch_stdout_stderr,
    create_correlation_context
)


def demonstrate_basic_logging(component_name: str) -> None:
    """
    Demonstrate basic logging capabilities.
    
    Args:
        component_name: Component name to use for logs
    """
    print("\n=== Basic Logging ===\n")
    
    # Set up logging
    logger = setup_logging(component_name)
    
    # Log at different levels
    logger.fatal("This is a fatal error message", code="FATAL001")
    logger.error("This is an error message", code="ERROR001")
    logger.warn("This is a warning message", code="WARN001")
    logger.info("This is an info message", code="INFO001")
    logger.normal("Component started successfully", code="NORMAL001")
    logger.debug("This is a debug message", code="DEBUG001")
    logger.trace("This is a trace message", code="TRACE001")
    
    # Log with context
    logger.info(
        "This is a message with context",
        code="INFO002",
        context={
            "user_id": "user123",
            "action": "login",
            "ip_address": "192.168.1.1"
        }
    )
    
    # Log with effective timestamp
    past_time = time.time() - 3600  # 1 hour ago
    logger.info(
        "This event actually happened an hour ago",
        code="INFO003",
        context={"retroactive": True},
        effective_timestamp=past_time
    )
    
    # Log errors with stack traces
    try:
        # Generate an exception
        result = 1 / 0
    except Exception as e:
        logger.error(
            f"An error occurred: {e}",
            code="ERROR002",
            context={"operation": "division"},
            stack_trace=traceback.format_exc()
        )


def demonstrate_logger_extensions(component_name: str) -> None:
    """
    Demonstrate logger extension capabilities.
    
    Args:
        component_name: Component name to use for logs
    """
    print("\n=== Logger Extensions ===\n")
    
    # Set up logging
    logger = setup_logging(component_name)
    
    # Create logger with context
    user_logger = logger.with_context({
        "user_id": "user456",
        "session_id": "session789"
    })
    
    # Log with extended context
    user_logger.info("User logged in", code="USER001")
    user_logger.info(
        "User performed action",
        code="USER002",
        context={"action": "update_profile"}  # This will be merged with default context
    )
    
    # Create logger with correlation ID
    correlation_id = create_correlation_context()
    correlation_logger = logger.with_correlation(correlation_id)
    
    # Log correlated events
    correlation_logger.info("Operation started", code="OP001")
    correlation_logger.info("Step 1 completed", code="OP002")
    correlation_logger.info("Step 2 completed", code="OP003")
    correlation_logger.info("Operation completed", code="OP004")
    
    print(f"All those events share correlation ID: {correlation_id}")


def demonstrate_query_capabilities(component_name: str) -> None:
    """
    Demonstrate log query capabilities.
    
    Args:
        component_name: Component name to use for logs
    """
    print("\n=== Query Capabilities ===\n")
    
    # Set up logging
    logger = setup_logging(component_name)
    
    # Generate some logs with different levels
    for i in range(10):
        level = random.choice([
            LogLevel.ERROR,
            LogLevel.WARN,
            LogLevel.INFO,
            LogLevel.DEBUG
        ])
        
        # Log the message
        if level == LogLevel.ERROR:
            logger.error(f"Error message {i}", code=f"ERROR{i}")
        elif level == LogLevel.WARN:
            logger.warn(f"Warning message {i}", code=f"WARN{i}")
        elif level == LogLevel.INFO:
            logger.info(f"Info message {i}", code=f"INFO{i}")
        else:
            logger.debug(f"Debug message {i}", code=f"DEBUG{i}")
    
    # Query logs
    from hermes.core.logging import _global_log_manager
    
    # Get logs for the component
    logs = _global_log_manager.query(
        components=[component_name],
        limit=5  # Get latest 5 logs
    )
    
    print(f"Latest 5 logs for {component_name}:")
    for log in logs:
        print(f"[{log.level.name}] {log.message} (Code: {log.code})")
    
    # Get error logs only
    error_logs = _global_log_manager.query(
        components=[component_name],
        levels=[LogLevel.ERROR],
        limit=5
    )
    
    print(f"\nLatest error logs for {component_name}:")
    for log in error_logs:
        print(f"[{log.level.name}] {log.message} (Code: {log.code})")


def demonstrate_python_logging_integration(component_name: str) -> None:
    """
    Demonstrate integration with Python's logging system.
    
    Args:
        component_name: Component name to use for logs
    """
    print("\n=== Python Logging Integration ===\n")
    
    # Set up logging
    logger = setup_logging(component_name)
    
    # Intercept Python logging
    intercept_python_logging(component_name)
    
    # Create Python logger
    py_logger = logging.getLogger("example.python")
    py_logger.setLevel(logging.DEBUG)
    
    # Log using Python's logging system
    py_logger.critical("This is a critical message from Python logging")
    py_logger.error("This is an error message from Python logging")
    py_logger.warning("This is a warning message from Python logging")
    py_logger.info("This is an info message from Python logging")
    py_logger.debug("This is a debug message from Python logging")
    
    # Log an exception
    try:
        # Generate an exception
        result = 1 / 0
    except Exception as e:
        py_logger.exception("An exception occurred")


def demonstrate_stdout_stderr_redirection(component_name: str) -> None:
    """
    Demonstrate redirection of stdout and stderr to logging system.
    
    Args:
        component_name: Component name to use for logs
    """
    print("\n=== Stdout/Stderr Redirection ===\n")
    
    # Set up logging
    logger = setup_logging(component_name)
    
    # Save original stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        # Patch stdout and stderr
        patch_stdout_stderr(component_name)
        
        # Print to stdout (will be redirected to logging system)
        print("This message goes to stdout but is also logged")
        
        # Print to stderr (will be redirected to logging system)
        print("This message goes to stderr but is also logged", file=sys.stderr)
        
    finally:
        # Restore original stdout/stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def main() -> None:
    """Main function to parse arguments and run examples."""
    parser = argparse.ArgumentParser(description="Centralized Logging System Example")
    
    parser.add_argument(
        "--component",
        type=str,
        default="example.logging",
        help="Component name to use for logs"
    )
    
    parser.add_argument(
        "--storage-path",
        type=str,
        default=None,
        help="Path to store log files (default: ~/.tekton/logs)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["FATAL", "ERROR", "WARN", "INFO", "NORMAL", "DEBUG", "TRACE"],
        default="TRACE",
        help="Minimum log level for console output"
    )
    
    args = parser.parse_args()
    
    # Initialize logging system
    init_logging(
        storage_path=args.storage_path,
        console_level=args.log_level
    )
    
    # Run demonstrations
    demonstrate_basic_logging(args.component)
    demonstrate_logger_extensions(args.component)
    demonstrate_query_capabilities(args.component)
    demonstrate_python_logging_integration(args.component)
    demonstrate_stdout_stderr_redirection(args.component)
    
    print("\nAll demonstrations completed. Check log files in:")
    print(f"  {os.path.expanduser('~/.tekton/logs')}" if args.storage_path is None else f"  {args.storage_path}")


if __name__ == "__main__":
    main()