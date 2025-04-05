"""
Core spectral analysis functionality for Tekton metrics.

This module provides the SpectralAnalyzer class that serves as the main interface
for all spectral and catastrophe theory analysis.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple

from .bifurcation import calculate_bifurcation_proximity
from .parameter_sensitivity import calculate_control_parameter_sensitivity
from .hysteresis import calculate_hysteresis_detection
from .catastrophe_points import identify_catastrophe_points
from .architectural_elasticity import find_architectural_elasticity
from ..utils import session_to_dict

logger = logging.getLogger(__name__)

class SpectralAnalyzer:
    """Analyzes metrics data to extract spectral insights."""
    
    def __init__(self, storage=None):
        """Initialize spectral analyzer.
        
        Args:
            storage: Optional metrics storage engine
        """
        self.storage = storage
    
    def analyze_session(self, session_data):
        """Analyze a single session.
        
        Args:
            session_data: SessionData object or dict
            
        Returns:
            Dict of analysis results
        """
        # Ensure we have dict format
        data = session_to_dict(session_data)
        
        results = {
            "session_id": data["id"],
            "processing_time": data.get("end_time", 0) - data.get("start_time", 0),
            "component_count": len(data.get("component_activations", {})),
            "propagation_steps": len(data.get("propagation_path", [])),
        }
        
        # Include spectral metrics if available
        if "spectral_metrics" in data:
            results["spectral"] = data["spectral_metrics"]
        else:
            # Calculate basic spectral metrics if not already present
            try:
                spectral = self._calculate_spectral_metrics(data)
                results["spectral"] = spectral
            except Exception as e:
                logger.error(f"Error calculating spectral metrics: {str(e)}")
                results["spectral"] = {}
        
        # Calculate additional insights
        results["insights"] = self._generate_insights(data, results)
        
        return results
    
    def analyze_sessions(self, sessions, group_by=None):
        """Analyze multiple sessions with optional grouping.
        
        Args:
            sessions: List of SessionData objects or dicts
            group_by: Optional field to group sessions by
            
        Returns:
            Dict of analysis results
        """
        if not sessions:
            return {"sessions": 0, "groups": {}}
        
        # Analyze each session
        session_results = [self.analyze_session(session) for session in sessions]
        
        # Calculate overall statistics
        overall = {
            "sessions": len(session_results),
            "avg_processing_time": np.mean([r["processing_time"] for r in session_results]),
            "avg_component_count": np.mean([r["component_count"] for r in session_results]),
            "avg_propagation_steps": np.mean([r["propagation_steps"] for r in session_results]),
        }
        
        # Calculate average spectral metrics
        spectral_keys = set()
        for result in session_results:
            spectral_keys.update(result.get("spectral", {}).keys())
        
        spectral_avgs = {}
        for key in spectral_keys:
            values = [r.get("spectral", {}).get(key, 0) for r in session_results]
            spectral_avgs[key] = np.mean(values)
        
        overall["spectral_avg"] = spectral_avgs
        
        # Group results if requested
        if group_by:
            groups = {}
            for result in session_results:
                # Get session data to extract group value
                session_id = result["session_id"]
                session = next((s for s in sessions if (s["id"] if isinstance(s, dict) else s.id) == session_id), None)
                
                if not session:
                    continue
                
                # Get group value
                if isinstance(session, dict):
                    group_val = session.get(group_by, "unknown")
                else:
                    group_val = getattr(session, group_by, "unknown")
                
                # Add to group
                if group_val not in groups:
                    groups[group_val] = []
                
                groups[group_val].append(result)
            
            # Calculate group statistics
            group_stats = {}
            for group_val, group_results in groups.items():
                group_stats[group_val] = self.analyze_sessions(group_results)
            
            overall["groups"] = group_stats
        
        return overall
    
    def find_architectural_elasticity(self, sessions):
        """Calculate architectural elasticity from session data."""
        return find_architectural_elasticity(sessions)
    
    def identify_catastrophe_points(self, sessions, window_size=5):
        """Identify potential catastrophe points in model behavior."""
        return identify_catastrophe_points(sessions, window_size)
        
    def calculate_bifurcation_proximity(self, sessions, num_recent=10):
        """Calculate the bifurcation proximity index for recent sessions."""
        return calculate_bifurcation_proximity(sessions, num_recent)
    
    def calculate_control_parameter_sensitivity(self, sessions, parameters=None):
        """Calculate sensitivity to different control parameters."""
        return calculate_control_parameter_sensitivity(sessions, parameters)
        
    def calculate_hysteresis_detection(self, sessions, parameter):
        """Calculate hysteresis in performance as a parameter changes."""
        return calculate_hysteresis_detection(sessions, parameter)
    
    def _calculate_spectral_metrics(self, session_data):
        """Calculate spectral metrics for a session."""
        metrics = {}
        
        # Calculate Depth Efficiency (DE)
        total_layers = sum(len(data.get("layers", {})) 
                         for data in session_data.get("parameter_usage", {}).values())
        if "accuracy" in session_data.get("performance", {}) and total_layers > 0:
            metrics["depth_efficiency"] = session_data["performance"]["accuracy"] / total_layers
        else:
            metrics["depth_efficiency"] = 0
            
        # Calculate Parametric Utilization (PU)
        total_params = sum(data.get("total", 0) for data in session_data.get("parameter_usage", {}).values())
        active_params = sum(data.get("active", 0) for data in session_data.get("parameter_usage", {}).values())
        
        if total_params > 0:
            metrics["parametric_utilization"] = active_params / total_params
        else:
            metrics["parametric_utilization"] = 0
            
        # Calculate Minimum Propagation Threshold (MPT)
        if session_data.get("propagation_path"):
            # Count unique components in the propagation path
            components = set()
            for step in session_data["propagation_path"]:
                components.add(step.get("source", ""))
                components.add(step.get("destination", ""))
            
            metrics["min_propagation_threshold"] = len(components)
        else:
            metrics["min_propagation_threshold"] = 0
            
        # Calculate Modularity Quotient (MQ)
        cross_module_flow = 0
        within_module_flow = 0
        
        for step in session_data.get("propagation_path", []):
            source = step.get("source", "")
            dest = step.get("destination", "")
            
            # If source and destination are in the same component family
            if source.split('.')[0] == dest.split('.')[0]:
                within_module_flow += step.get("info_content", 1)
            else:
                cross_module_flow += step.get("info_content", 1)
        
        total_flow = cross_module_flow + within_module_flow
        if total_flow > 0:
            metrics["modularity_quotient"] = 1 - (cross_module_flow / total_flow)
        else:
            metrics["modularity_quotient"] = 0
            
        return metrics
    
    def _generate_insights(self, session_data, analysis_results):
        """Generate insights from session data and analysis."""
        insights = {}
        
        # Get spectral metrics
        spectral = analysis_results.get("spectral", {})
        
        # Insight: Efficiency classification
        if "depth_efficiency" in spectral:
            de = spectral["depth_efficiency"]
            if de > 0.8:
                insights["depth_efficiency"] = "Excellent - very high efficiency per layer"
            elif de > 0.5:
                insights["depth_efficiency"] = "Good - efficient use of layers"
            elif de > 0.3:
                insights["depth_efficiency"] = "Moderate - some layer inefficiency"
            else:
                insights["depth_efficiency"] = "Poor - significant layer inefficiency"
        
        # Insight: Parameter utilization
        if "parametric_utilization" in spectral:
            pu = spectral["parametric_utilization"]
            if pu > 0.8:
                insights["parametric_utilization"] = "Excellent - very high parameter utilization"
            elif pu > 0.5:
                insights["parametric_utilization"] = "Good - effective parameter usage"
            elif pu > 0.3:
                insights["parametric_utilization"] = "Moderate - some parameter wastage"
            else:
                insights["parametric_utilization"] = "Poor - significant parameter wastage"
        
        # Insight: Propagation efficiency
        if "min_propagation_threshold" in spectral:
            mpt = spectral["min_propagation_threshold"]
            component_count = analysis_results.get("component_count", 0)
            
            if component_count > 0:
                propagation_ratio = mpt / component_count
                
                if propagation_ratio > 0.9:
                    insights["propagation"] = "Excessive - nearly all components involved"
                elif propagation_ratio > 0.7:
                    insights["propagation"] = "High - most components involved"
                elif propagation_ratio > 0.4:
                    insights["propagation"] = "Moderate - selective component usage"
                else:
                    insights["propagation"] = "Efficient - minimal component usage"
        
        # Insight: Modularity assessment
        if "modularity_quotient" in spectral:
            mq = spectral["modularity_quotient"]
            
            if mq > 0.8:
                insights["modularity"] = "Very High - clear module boundaries"
            elif mq > 0.6:
                insights["modularity"] = "High - good module separation"
            elif mq > 0.4:
                insights["modularity"] = "Moderate - some module overlap"
            else:
                insights["modularity"] = "Low - poor module separation"
        
        return insights
