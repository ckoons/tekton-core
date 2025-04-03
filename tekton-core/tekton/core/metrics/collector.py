"""
Core metrics collection for Tekton architecture.

This module provides tools for collecting performance and
architectural metrics during system operation.
"""

import time
import uuid
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)

@dataclass
class SessionData:
    """Data structure for storing metrics from a processing session."""
    
    id: str
    prompt: str
    config: Dict[str, Any]
    start_time: float
    
    # Runtime data
    component_activations: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    propagation_path: List[Dict[str, Any]] = field(default_factory=list)
    parameter_usage: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Results
    end_time: Optional[float] = None
    response: Optional[str] = None
    performance: Dict[str, Any] = field(default_factory=dict)
    
    # Derived metrics
    spectral_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON for storage."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SessionData':
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


class MetricsCollector:
    """Collects metrics during system operation."""
    
    def __init__(self, storage_engine=None):
        """Initialize metrics collector.
        
        Args:
            storage_engine: Optional storage engine for metrics
        """
        self.storage = storage_engine
        self.current_session = None
        self.active = True
    
    def start_session(self, prompt: str, config: Dict[str, Any]) -> str:
        """Start a new metrics collection session.
        
        Args:
            prompt: The input prompt text
            config: Configuration of components used
            
        Returns:
            Session ID
        """
        if not self.active:
            logger.info("Metrics collection disabled")
            return "disabled"
            
        session_id = str(uuid.uuid4())
        self.current_session = SessionData(
            id=session_id,
            prompt=prompt,
            config=config,
            start_time=time.time()
        )
        
        logger.debug(f"Started metrics session {session_id}")
        return session_id
    
    def record_component_activation(self, 
                                   component_id: str, 
                                   activation_data: Dict[str, Any]):
        """Record activation metrics for a component.
        
        Args:
            component_id: ID of the activated component
            activation_data: Data about the activation
        """
        if not self.active or not self.current_session:
            return
            
        if component_id not in self.current_session.component_activations:
            self.current_session.component_activations[component_id] = []
            
        activation_record = {
            "timestamp": time.time(),
            **activation_data
        }
        
        self.current_session.component_activations[component_id].append(activation_record)
    
    def record_propagation_step(self, 
                               source: str, 
                               destination: str, 
                               info_content: float,
                               data: Optional[Dict[str, Any]] = None):
        """Record data propagation between components.
        
        Args:
            source: Source component ID
            destination: Destination component ID
            info_content: Measured information content
            data: Additional data about the propagation
        """
        if not self.active or not self.current_session:
            return
            
        step_data = {
            "timestamp": time.time(),
            "source": source,
            "destination": destination,
            "info_content": info_content
        }
        
        if data:
            step_data.update(data)
            
        self.current_session.propagation_path.append(step_data)
    
    def record_parameter_usage(self,
                              component_id: str,
                              total_params: int,
                              active_params: int,
                              layer_data: Optional[Dict[str, Any]] = None):
        """Record parameter usage metrics.
        
        Args:
            component_id: ID of the component
            total_params: Total parameters available
            active_params: Number of active parameters
            layer_data: Optional layer-specific data
        """
        if not self.active or not self.current_session:
            return
            
        usage_data = {
            "timestamp": time.time(),
            "total": total_params,
            "active": active_params,
            "utilization": active_params / total_params if total_params > 0 else 0
        }
        
        if layer_data:
            usage_data["layers"] = layer_data
            
        self.current_session.parameter_usage[component_id] = usage_data
    
    def complete_session(self, 
                        response: str, 
                        performance_metrics: Dict[str, Any],
                        calculate_spectral: bool = True):
        """Complete the metrics collection session.
        
        Args:
            response: Response text generated
            performance_metrics: Performance metrics
            calculate_spectral: Whether to calculate spectral metrics
        """
        if not self.active or not self.current_session:
            return
            
        self.current_session.end_time = time.time()
        self.current_session.response = response
        self.current_session.performance = performance_metrics
        
        # Calculate spectral metrics
        if calculate_spectral:
            self._calculate_spectral_metrics()
        
        # Save to storage if available
        if self.storage:
            try:
                self.storage.store_session(self.current_session)
                logger.debug(f"Stored metrics for session {self.current_session.id}")
            except Exception as e:
                logger.error(f"Failed to store metrics: {str(e)}")
        
        session_data = self.current_session
        self.current_session = None
        return session_data
    
    def _calculate_spectral_metrics(self):
        """Calculate spectral analysis metrics from collected data."""
        if not self.current_session:
            return
            
        metrics = {}
        
        # Calculate Depth Efficiency (DE)
        # DE = performance / layer count
        try:
            total_layers = sum(len(data.get("layers", {})) 
                             for data in self.current_session.parameter_usage.values())
            if "accuracy" in self.current_session.performance and total_layers > 0:
                metrics["depth_efficiency"] = self.current_session.performance["accuracy"] / total_layers
        except (KeyError, ZeroDivisionError):
            metrics["depth_efficiency"] = 0
            
        # Calculate Parametric Utilization (PU)
        # PU = active parameters / total parameters
        try:
            total_params = sum(data["total"] for data in self.current_session.parameter_usage.values())
            active_params = sum(data["active"] for data in self.current_session.parameter_usage.values())
            
            if total_params > 0:
                metrics["parametric_utilization"] = active_params / total_params
            else:
                metrics["parametric_utilization"] = 0
        except (KeyError, ZeroDivisionError):
            metrics["parametric_utilization"] = 0
            
        # Calculate Minimum Propagation Threshold (MPT)
        # MPT = shortest successful path through components
        try:
            if self.current_session.propagation_path:
                # Count unique components in the propagation path
                components = set()
                for step in self.current_session.propagation_path:
                    components.add(step["source"])
                    components.add(step["destination"])
                
                metrics["min_propagation_threshold"] = len(components)
            else:
                metrics["min_propagation_threshold"] = 0
        except Exception:
            metrics["min_propagation_threshold"] = 0
            
        # Calculate Modularity Quotient (MQ)
        # MQ = 1 - (cross-module info flow / within-module info flow)
        try:
            cross_module_flow = 0
            within_module_flow = 0
            
            for step in self.current_session.propagation_path:
                # If source and destination are in the same component family
                if step["source"].split('.')[0] == step["destination"].split('.')[0]:
                    within_module_flow += step.get("info_content", 1)
                else:
                    cross_module_flow += step.get("info_content", 1)
            
            total_flow = cross_module_flow + within_module_flow
            if total_flow > 0:
                metrics["modularity_quotient"] = 1 - (cross_module_flow / total_flow)
            else:
                metrics["modularity_quotient"] = 0
        except Exception:
            metrics["modularity_quotient"] = 0
            
        # Store the calculated metrics
        self.current_session.spectral_metrics = metrics