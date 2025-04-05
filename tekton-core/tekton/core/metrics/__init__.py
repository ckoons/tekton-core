"""
Metrics collection and analysis for Tekton architecture.

This module provides tools for collecting, analyzing, and visualizing
performance metrics related to computational spectral analysis and catastrophe theory.
"""

from .collector import MetricsCollector, SessionData
from .storage.base import MetricsStorage
from .storage.sqlite import SQLiteMetricsStorage
from .storage.json_file import JSONFileMetricsStorage
from .analysis.spectral_analyzer import SpectralAnalyzer
from .integration import MetricsManager
from .utils import (
    session_to_dict,
    sessions_to_dicts,
    interpret_bifurcation_proximity,
    interpret_parameter_sensitivity,
    interpret_hysteresis
)

# Analysis specific imports for direct access
from .analysis.bifurcation import calculate_bifurcation_proximity
from .analysis.parameter_sensitivity import calculate_control_parameter_sensitivity
from .analysis.hysteresis import calculate_hysteresis_detection
from .analysis.catastrophe_points import identify_catastrophe_points
from .analysis.architectural_elasticity import find_architectural_elasticity

__all__ = [
    # Core classes
    "MetricsCollector",
    "SessionData",
    "MetricsStorage",
    "SQLiteMetricsStorage",
    "JSONFileMetricsStorage",
    "SpectralAnalyzer",
    "MetricsManager",
    
    # Utility functions
    "session_to_dict",
    "sessions_to_dicts",
    "interpret_bifurcation_proximity",
    "interpret_parameter_sensitivity",
    "interpret_hysteresis",
    
    # Analysis functions
    "calculate_bifurcation_proximity",
    "calculate_control_parameter_sensitivity",
    "calculate_hysteresis_detection",
    "identify_catastrophe_points",
    "find_architectural_elasticity"
]