#!/usr/bin/env python3
"""
Monitoring Dashboard Module

This module provides a centralized dashboard for monitoring Tekton components.
"""

# Re-export from dashboard package
from .dashboard import (
    HealthDashboard,
    MonitoringDashboard,
    get_dashboard
)

# Example usage
async def example():
    """Example of monitoring dashboard."""
    import asyncio
    from datetime import datetime
    
    # Create dashboard
    dashboard = get_dashboard()
    
    # Register alert hook
    def alert_hook(alert):
        print(f"ALERT: {alert.severity.value.upper()} - {alert.title}")
        print(f"  {alert.description}")
        print(f"  Component: {alert.component_id}")
        print(f"  Time: {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
    dashboard.register_alert_handler(alert_hook)
    
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
    import asyncio
    asyncio.run(example())