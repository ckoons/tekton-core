#!/usr/bin/env python3
"""
Stress Test Utilities

Provides utility functions for the stress test.
"""

import time
import json
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger("tekton.stress_test.utils")


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate statistics for a list of values.
    
    Args:
        values: List of values
        
    Returns:
        Dictionary with statistics
    """
    if not values:
        return {
            "count": 0,
            "min": 0.0,
            "max": 0.0,
            "avg": 0.0,
            "p50": 0.0,
            "p95": 0.0,
            "p99": 0.0
        }
        
    sorted_values = sorted(values)
    count = len(sorted_values)
    
    # Calculate percentiles
    p50_index = int(count * 0.5)
    p95_index = int(count * 0.95)
    p99_index = int(count * 0.99)
    
    return {
        "count": count,
        "min": sorted_values[0],
        "max": sorted_values[-1],
        "avg": sum(sorted_values) / count,
        "p50": sorted_values[p50_index],
        "p95": sorted_values[p95_index] if p95_index < count else sorted_values[-1],
        "p99": sorted_values[p99_index] if p99_index < count else sorted_values[-1]
    }


def format_stats_summary(stats: Dict[str, Any]) -> str:
    """
    Format statistics summary for logging.
    
    Args:
        stats: Statistics dictionary
        
    Returns:
        Formatted summary string
    """
    return json.dumps(stats, indent=2)


def get_elapsed_time(start_time: float) -> Tuple[float, str]:
    """
    Get elapsed time and format it.
    
    Args:
        start_time: Start time
        
    Returns:
        Tuple of (elapsed seconds, formatted string)
    """
    elapsed = time.time() - start_time
    
    # Format as minutes and seconds
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    formatted = f"{minutes}m {seconds}s"
    
    return elapsed, formatted
