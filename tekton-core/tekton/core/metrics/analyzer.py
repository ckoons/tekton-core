"""
Spectral analysis tools for Tekton metrics.

This module provides tools for analyzing metrics data
and generating spectral insights.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

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
        data = session_data.to_dict() if hasattr(session_data, 'to_dict') else session_data
        
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
        """Calculate architectural elasticity from session data.
        
        Architectural Elasticity (AE) = Δ(performance) / Δ(architectural_complexity)
        
        Args:
            sessions: List of session data objects
            
        Returns:
            Dict of elasticity metrics
        """
        if len(sessions) < 2:
            return {"error": "Need at least 2 sessions to calculate elasticity"}
        
        # Convert to list of dicts
        session_dicts = []
        for session in sessions:
            if hasattr(session, 'to_dict'):
                session_dicts.append(session.to_dict())
            else:
                session_dicts.append(session)
        
        # Sort by start time
        session_dicts.sort(key=lambda x: x.get('start_time', 0))
        
        # Calculate changes between consecutive sessions
        elasticity_points = []
        
        for i in range(1, len(session_dicts)):
            prev = session_dicts[i-1]
            curr = session_dicts[i]
            
            # Extract performance metric (accuracy, success rate, etc.)
            prev_perf = prev.get('performance', {}).get('accuracy', 0)
            curr_perf = curr.get('performance', {}).get('accuracy', 0)
            
            # Extract complexity metrics
            prev_complexity = self._calculate_complexity(prev)
            curr_complexity = self._calculate_complexity(curr)
            
            # Calculate elasticity if complexity changed
            if abs(curr_complexity - prev_complexity) > 0.001:
                elasticity = (curr_perf - prev_perf) / (curr_complexity - prev_complexity)
                
                elasticity_points.append({
                    "from_session": prev['id'],
                    "to_session": curr['id'],
                    "performance_delta": curr_perf - prev_perf,
                    "complexity_delta": curr_complexity - prev_complexity,
                    "elasticity": elasticity
                })
        
        # Calculate overall elasticity
        if elasticity_points:
            avg_elasticity = np.mean([p["elasticity"] for p in elasticity_points])
            max_elasticity = max([p["elasticity"] for p in elasticity_points])
            min_elasticity = min([p["elasticity"] for p in elasticity_points])
        else:
            avg_elasticity = 0
            max_elasticity = 0
            min_elasticity = 0
        
        return {
            "points": elasticity_points,
            "average": avg_elasticity,
            "maximum": max_elasticity,
            "minimum": min_elasticity
        }
    
    def identify_catastrophe_points(self, sessions, window_size=5):
        """Identify potential catastrophe points in model behavior.
        
        Args:
            sessions: List of session data
            window_size: Window size for detecting sudden changes
            
        Returns:
            List of potential catastrophe points
        """
        if len(sessions) < window_size * 2:
            return {"error": f"Need at least {window_size*2} sessions to identify catastrophe points"}
        
        # Convert to list of dicts
        session_dicts = []
        for session in sessions:
            if hasattr(session, 'to_dict'):
                session_dicts.append(session.to_dict())
            else:
                session_dicts.append(session)
        
        # Sort by start time
        session_dicts.sort(key=lambda x: x.get('start_time', 0))
        
        # Extract metrics series
        times = [s.get('start_time', 0) for s in session_dicts]
        accuracies = [s.get('performance', {}).get('accuracy', 0) for s in session_dicts]
        de_values = [s.get('spectral_metrics', {}).get('depth_efficiency', 0) for s in session_dicts]
        pu_values = [s.get('spectral_metrics', {}).get('parametric_utilization', 0) for s in session_dicts]
        mq_values = [s.get('spectral_metrics', {}).get('modularity_quotient', 0) for s in session_dicts]
        
        # Detect sudden changes in metrics
        catastrophe_points = []
        
        for i in range(window_size, len(session_dicts) - window_size):
            # Calculate before/after averages
            before_acc = np.mean(accuracies[i-window_size:i])
            after_acc = np.mean(accuracies[i:i+window_size])
            acc_change = after_acc - before_acc
            
            before_de = np.mean(de_values[i-window_size:i])
            after_de = np.mean(de_values[i:i+window_size])
            de_change = after_de - before_de
            
            before_pu = np.mean(pu_values[i-window_size:i])
            after_pu = np.mean(pu_values[i:i+window_size])
            pu_change = after_pu - before_pu
            
            before_mq = np.mean(mq_values[i-window_size:i])
            after_mq = np.mean(mq_values[i:i+window_size])
            mq_change = after_mq - before_mq
            
            # Calculate change magnitudes
            acc_magnitude = abs(acc_change) / max(before_acc, 0.001)
            de_magnitude = abs(de_change) / max(before_de, 0.001)
            pu_magnitude = abs(pu_change) / max(before_pu, 0.001)
            mq_magnitude = abs(mq_change) / max(before_mq, 0.001)
            
            # Check for significant changes
            significant_changes = []
            
            if acc_magnitude > 0.2:  # 20% change threshold
                significant_changes.append(("accuracy", acc_change, acc_magnitude))
            
            if de_magnitude > 0.2:
                significant_changes.append(("depth_efficiency", de_change, de_magnitude))
            
            if pu_magnitude > 0.2:
                significant_changes.append(("parametric_utilization", pu_change, pu_magnitude))
            
            if mq_magnitude > 0.2:
                significant_changes.append(("modularity_quotient", mq_change, mq_magnitude))
            
            if significant_changes:
                catastrophe_points.append({
                    "session_id": session_dicts[i]['id'],
                    "time": times[i],
                    "changes": significant_changes,
                    "magnitude": max(c[2] for c in significant_changes)
                })
        
        # Sort by magnitude (descending)
        catastrophe_points.sort(key=lambda x: x["magnitude"], reverse=True)
        
        return catastrophe_points
    
    def _calculate_complexity(self, session_data):
        """Calculate architectural complexity metric.
        
        Args:
            session_data: Session data dict
            
        Returns:
            Complexity score
        """
        # Count components
        component_count = len(session_data.get('component_activations', {}))
        
        # Count total parameters
        total_params = sum(data.get('total', 0) for data in session_data.get('parameter_usage', {}).values())
        
        # Count propagation steps
        prop_steps = len(session_data.get('propagation_path', []))
        
        # Calculate modularity
        mq = session_data.get('spectral_metrics', {}).get('modularity_quotient', 0.5)
        
        # Combine into complexity score
        # Higher complexity for more components, more parameters, more propagation steps, lower modularity
        complexity = (
            component_count * 0.3 + 
            np.log1p(total_params) * 0.3 + 
            prop_steps * 0.2 + 
            (1 - mq) * 0.2
        )
        
        return complexity
    
    def _calculate_spectral_metrics(self, session_data):
        """Calculate spectral metrics for a session.
        
        Args:
            session_data: Session data dict
            
        Returns:
            Dict of spectral metrics
        """
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
        """Generate insights from session data and analysis.
        
        Args:
            session_data: Session data dict
            analysis_results: Analysis results dict
            
        Returns:
            Dict of insights
        """
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