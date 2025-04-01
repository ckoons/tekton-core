"""
Tekton Core Module

This module provides the core functionality for the Tekton framework.
"""

from tekton.core.startup_instructions import StartUpInstructions
from tekton.core.startup_process import StartUpProcess, ComponentStatus
from tekton.core.startup_coordinator import StartUpCoordinator
from tekton.core.component_registration import ComponentRegistration
from tekton.core.component_discovery import ComponentDiscovery
from tekton.core.heartbeat_monitor import HeartbeatMonitor, ComponentHeartbeat
try:
    from tekton.core.latent_reasoning import LatentReasoningMixin
except ImportError:
    # Latent reasoning might not be available
    pass

__all__ = [
    'StartUpInstructions',
    'StartUpProcess',
    'StartUpCoordinator',
    'ComponentStatus',
    'ComponentRegistration',
    'ComponentDiscovery',
    'HeartbeatMonitor',
    'ComponentHeartbeat'
]