#!/usr/bin/env python3
"""
Monitoring Dashboard Module

This module provides a centralized dashboard for monitoring Tekton components.
"""

import os
import time
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Callable

from ..logging_integration import get_logger, LogCategory
from ..component_lifecycle import ComponentState
from ..metrics_integration import get_metrics_manager
from .health import HealthStatus, ComponentHealth, SystemHealth, state_to_health_status
from .alerts import Alert, AlertSeverity, AlertManager
from .detector import IssueDetector

# Configure logger
logger = get_logger("tekton.monitoring.dashboard")


class MonitoringDashboard:
    """Dashboard for monitoring Tekton components."""
    
    def __init__(self, 
                hermes_url: Optional[str] = None,
                update_interval: float = 10.0,
                alert_retention_days: int = 7):
        """
        Initialize monitoring dashboard.
        
        Args:
            hermes_url: Optional URL of Hermes service
            update_interval: Interval in seconds for updating health status
            alert_retention_days: Number of days to retain resolved alerts
        """
        self.hermes_url = hermes_url
        self.update_interval = update_interval
        self.alert_retention_days = alert_retention_days
        self.system_health = SystemHealth()
        self.alert_manager = AlertManager(alert_retention_days)
        self.issue_detector = IssueDetector(self.alert_manager)
        self.update_task = None
        self.running = False
        
        # Setup system health to use alerts from alert manager
        self.system_health.alerts = self.alert_manager.alerts
        
        # Get logger
        self.logger = get_logger("tekton.monitoring")
        
        # Create metrics
        self.metrics = get_metrics_manager("tekton.monitoring")
        
    async def start(self) -> None:
        """Start monitoring dashboard."""
        if self.running:
            return
            
        self.running = True
        
        # Start metrics
        await self.metrics.start()
        
        # Start update task
        self.update_task = asyncio.create_task(self._update_loop())
        self.logger.info("Started monitoring dashboard", category=LogCategory.SYSTEM)
        
    async def stop(self) -> None:
        """Stop monitoring dashboard."""
        if not self.running:
            return
            
        self.running = False
        
        # Stop metrics
        await self.metrics.stop()
        
        # Cancel update task
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
            self.update_task = None
            
        self.logger.info("Stopped monitoring dashboard", category=LogCategory.SYSTEM)
        
    async def _update_loop(self) -> None:
        """Update loop for monitoring."""
        try:
            while self.running:
                try:
                    # Update health status
                    await self._update_health_status()
                    
                    # Clean up old alerts
                    self.alert_manager.clean_up_alerts()
                    
                    # Update metrics
                    self._update_metrics()
                    
                except Exception as e:
                    self.logger.error(
                        f"Failed to update health status: {e}",
                        category=LogCategory.SYSTEM,
                        exception=e
                    )
                    
                # Wait for next update
                await asyncio.sleep(self.update_interval)
                
        except asyncio.CancelledError:
            self.logger.info("Monitoring update loop cancelled", category=LogCategory.SYSTEM)
            
    async def _update_health_status(self) -> None:
        """Update health status for all components."""
        if self.hermes_url:
            try:
                # Fetch component status from Hermes
                await self._fetch_component_status()
            except Exception as e:
                self.logger.error(
                    f"Failed to fetch component status from Hermes: {e}",
                    category=LogCategory.SYSTEM,
                    exception=e
                )
        else:
            # Use mock data for example
            self._update_mock_data()
            
    async def _fetch_component_status(self) -> None:
        """Fetch component status from Hermes."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.hermes_url}/api/components") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process component data
                        for component_data in data.get("components", []):
                            component_id = component_data.get("component_id")
                            if not component_id:
                                continue
                                
                            # Determine health status
                            state = component_data.get("state")
                            status = state_to_health_status(state)
                            
                            # Get or create component
                            component = self.system_health.get_component(component_id)
                            if component:
                                # Update existing component
                                component.update_status(
                                    status=status,
                                    state=state,
                                    last_heartbeat=component_data.get("last_heartbeat"),
                                    metrics=component_data.get("metrics")
                                )
                            else:
                                # Create new component
                                component = ComponentHealth(
                                    component_id=component_id,
                                    component_name=component_data.get("component_name", component_id),
                                    component_type=component_data.get("component_type", "unknown"),
                                    status=status,
                                    state=state,
                                    last_heartbeat=component_data.get("last_heartbeat"),
                                    metrics=component_data.get("metrics"),
                                    dependencies=component_data.get("dependencies", [])
                                )
                                self.system_health.add_component(component)
                                
                            # Check for issues
                            self.issue_detector.check_component(component)
                    else:
                        self.logger.warning(
                            f"Failed to fetch component status: {response.status}",
                            category=LogCategory.SYSTEM
                        )
            except Exception as e:
                self.logger.error(
                    f"Error fetching component status: {e}",
                    category=LogCategory.SYSTEM,
                    exception=e
                )
                
    def _update_mock_data(self) -> None:
        """Update mock data for example."""
        # Add mock components if none exist
        if not self.system_health.components:
            # Mock component 1
            component1 = ComponentHealth(
                component_id="example.service1",
                component_name="Example Service 1",
                component_type="service",
                status=HealthStatus.HEALTHY,
                last_heartbeat=time.time(),
                state=ComponentState.READY.value,
                metrics={
                    "cpu_usage": 0.2,
                    "memory_usage": 100 * 1024 * 1024,
                    "request_count": 1000,
                    "error_count": 5
                },
                dependencies=["example.database"]
            )
            self.system_health.add_component(component1)
            
            # Mock component 2
            component2 = ComponentHealth(
                component_id="example.service2",
                component_name="Example Service 2",
                component_type="service",
                status=HealthStatus.DEGRADED,
                last_heartbeat=time.time(),
                state=ComponentState.DEGRADED.value,
                metrics={
                    "cpu_usage": 0.8,
                    "memory_usage": 800 * 1024 * 1024,
                    "request_count": 500,
                    "error_count": 50
                },
                dependencies=["example.database"]
            )
            self.system_health.add_component(component2)
            
            # Mock component 3
            component3 = ComponentHealth(
                component_id="example.database",
                component_name="Example Database",
                component_type="database",
                status=HealthStatus.HEALTHY,
                last_heartbeat=time.time(),
                state=ComponentState.READY.value,
                metrics={
                    "cpu_usage": 0.4,
                    "memory_usage": 500 * 1024 * 1024,
                    "connection_count": 20,
                    "query_count": 5000
                }
            )
            self.system_health.add_component(component3)
            
            # Add mock alert
            alert = Alert(
                severity=AlertSeverity.WARNING,
                title="High CPU Usage",
                description="Component example.service2 has high CPU usage (80%)",
                component_id="example.service2"
            )
            self.alert_manager.add_alert(alert)
        else:
            # Update mock data
            import random
            
            # Update each component
            for component in self.system_health.components.values():
                # Randomly update metrics
                if "cpu_usage" in component.metrics:
                    component.metrics["cpu_usage"] += (random.random() - 0.5) * 0.1
                    component.metrics["cpu_usage"] = max(0.0, min(1.0, component.metrics["cpu_usage"]))
                    
                if "memory_usage" in component.metrics:
                    component.metrics["memory_usage"] += (random.random() - 0.5) * 50 * 1024 * 1024
                    component.metrics["memory_usage"] = max(0, component.metrics["memory_usage"])
                    
                # Update status based on CPU usage
                if "cpu_usage" in component.metrics:
                    cpu_usage = component.metrics["cpu_usage"]
                    if cpu_usage > 0.9:
                        component.update_status(HealthStatus.UNHEALTHY, state=ComponentState.ERROR.value)
                    elif cpu_usage > 0.7:
                        component.update_status(HealthStatus.DEGRADED, state=ComponentState.DEGRADED.value)
                    else:
                        component.update_status(HealthStatus.HEALTHY, state=ComponentState.READY.value)
                        
                # Update last heartbeat
                component.last_heartbeat = time.time()
                
                # Check for issues
                self.issue_detector.check_component(component)
                
    def _update_metrics(self) -> None:
        """Update metrics from system health."""
        registry = self.metrics.get_registry()
        
        # Update component count metrics
        counts = registry.get("component_count")
        if not counts:
            counts = registry.create_gauge(
                name="component_count",
                description="Count of components by status",
                labels={"status": "total"}
            )
        counts.set(self.system_health.metrics["total_components"])
        
        # Update by status
        for status in ["healthy", "degraded", "unhealthy"]:
            status_counts = registry.get("component_count", {"status": status})
            if not status_counts:
                status_counts = registry.create_gauge(
                    name="component_count",
                    description="Count of components by status",
                    labels={"status": status}
                )
            status_counts.set(self.system_health.metrics[f"{status}_components"])
            
        # Update alert count
        alerts = registry.get("alert_count")
        if not alerts:
            alerts = registry.create_gauge(
                name="alert_count",
                description="Count of active alerts"
            )
        alerts.set(self.system_health.metrics["active_alerts"])
            
    def get_system_health(self) -> SystemHealth:
        """
        Get system health.
        
        Returns:
            System health
        """
        return self.system_health
        
    def get_component_health(self, component_id: str) -> Optional[ComponentHealth]:
        """
        Get health for a specific component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component health or None if not found
        """
        return self.system_health.get_component(component_id)
        
    def get_alerts(self, 
                component_id: Optional[str] = None,
                include_resolved: bool = False) -> List[Alert]:
        """
        Get alerts, optionally filtered by component.
        
        Args:
            component_id: Optional component ID
            include_resolved: Whether to include resolved alerts
            
        Returns:
            List of alerts
        """
        return self.alert_manager.get_alerts(component_id, include_resolved)
        
    def register_alert_hook(self, hook: Callable[[Alert], None]) -> None:
        """
        Register a hook to be called when an alert is created.
        
        Args:
            hook: Function to call with the alert
        """
        self.alert_manager.register_alert_hook(hook)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert dashboard to dictionary."""
        return self.system_health.to_dict()
        
    def to_json(self) -> str:
        """Convert dashboard to JSON."""
        return json.dumps(self.to_dict())


# Singleton dashboard instance
_dashboard: Optional[MonitoringDashboard] = None

def get_dashboard() -> MonitoringDashboard:
    """
    Get the monitoring dashboard singleton.
    
    Returns:
        Monitoring dashboard
    """
    global _dashboard
    if _dashboard is None:
        _dashboard = MonitoringDashboard()
    return _dashboard


# Example usage
async def example():
    """Example of monitoring dashboard."""
    from datetime import datetime
    
    # Create dashboard
    dashboard = get_dashboard()
    
    # Register alert hook
    def alert_hook(alert: Alert):
        print(f"ALERT: {alert.severity.value.upper()} - {alert.title}")
        print(f"  {alert.description}")
        print(f"  Component: {alert.component_id}")
        print(f"  Time: {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
    dashboard.register_alert_hook(alert_hook)
    
    # Start dashboard
    await dashboard.start()
    
    try:
        # Wait a bit for dashboard to update
        for _ in range(3):
            await asyncio.sleep(5)
            
            # Print current status
            health = dashboard.get_system_health()
            print(f"System Status: {health.overall_status.value}")
            print(f"Components: {health.metrics['total_components']} total, "
                f"{health.metrics['healthy_components']} healthy, "
                f"{health.metrics['degraded_components']} degraded, "
                f"{health.metrics['unhealthy_components']} unhealthy")
            print(f"Active Alerts: {health.metrics['active_alerts']}")
            print()
            
            # Print component details
            for component in health.components.values():
                print(f"Component: {component.component_name} ({component.component_id})")
                print(f"  Status: {component.status.value}")
                print(f"  Type: {component.component_type}")
                print(f"  State: {component.state}")
                if component.metrics:
                    print("  Metrics:")
                    for key, value in component.metrics.items():
                        print(f"    {key}: {value}")
                print()
                
    finally:
        # Stop dashboard
        await dashboard.stop()


if __name__ == "__main__":
    asyncio.run(example())