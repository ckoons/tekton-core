#!/usr/bin/env python3
"""
Tekton Status Script - Python implementation

Provides comprehensive status of all Tekton components with enhanced reporting.
"""
import asyncio
import aiohttp
import argparse
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from tabulate import tabulate
import psutil

# Add parent directory to path to import tekton modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import centralized configuration
from tekton.utils.component_config import get_component_config, ComponentInfo
from tekton.utils.port_config import load_port_assignments


class ComponentStatus:
    """Represents the status of a single component"""
    
    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.status = "unknown"
        self.version = "unknown"
        self.registered = False
        self.response_time = None
        self.error = None
        self.details = {}
        self.process_info = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output"""
        return {
            "name": self.name,
            "port": self.port,
            "status": self.status,
            "version": self.version,
            "registered": self.registered,
            "response_time": self.response_time,
            "error": self.error,
            "details": self.details,
            "process": self.process_info
        }


async def check_component_health(session: aiohttp.ClientSession, name: str, port: int) -> ComponentStatus:
    """Check health of a single component"""
    component = ComponentStatus(name, port)
    
    # Check if process is running on the port
    component.process_info = check_port_process(port)
    
    if not component.process_info:
        component.status = "not_running"
        return component
    
    try:
        start_time = datetime.now()
        url = f"http://localhost:{port}/health"
        
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
            component.response_time = (datetime.now() - start_time).total_seconds()
            
            if resp.status == 200:
                data = await resp.json()
                
                # Parse standardized health response
                component.status = data.get("status", "healthy")
                component.version = data.get("version", "unknown")
                component.registered = data.get("registered_with_hermes", False)
                component.details = data.get("details", {})
            else:
                component.status = "unhealthy"
                component.error = f"HTTP {resp.status}"
                
    except asyncio.TimeoutError:
        component.status = "timeout"
        component.error = "Health check timed out"
    except aiohttp.ClientError as e:
        component.status = "unreachable"
        component.error = str(e)
    except Exception as e:
        component.status = "error"
        component.error = str(e)
        
    return component


def check_port_process(port: int) -> Optional[Dict[str, Any]]:
    """Check if a process is listening on the given port"""
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == 'LISTEN':
                try:
                    proc = psutil.Process(conn.pid)
                    return {
                        "pid": conn.pid,
                        "name": proc.name(),
                        "cmdline": " ".join(proc.cmdline()[:3]) + "..." if len(proc.cmdline()) > 3 else " ".join(proc.cmdline()),
                        "cpu_percent": proc.cpu_percent(),
                        "memory_mb": proc.memory_info().rss / 1024 / 1024
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    return {"pid": conn.pid, "name": "unknown"}
    except psutil.AccessDenied:
        # Try alternative method
        return {"error": "Access denied to process information"}
    return None


async def check_all_components() -> List[ComponentStatus]:
    """Check health of all components"""
    # Use centralized component configuration
    config = get_component_config()
    components = config.get_all_components()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for comp_id, comp_info in components.items():
            tasks.append(check_component_health(session, comp_id, comp_info.port))
        
        return await asyncio.gather(*tasks)


def format_table_output(components: List[ComponentStatus], verbose: bool = False) -> str:
    """Format component status as a table"""
    # Get component configuration for descriptions
    config = get_component_config()
    
    # Prepare data for table
    table_data = []
    for comp in components:
        status_symbol = {
            "healthy": "✅",
            "unhealthy": "❌",
            "not_running": "⭕",
            "timeout": "⏱️",
            "unreachable": "🔌",
            "error": "⚠️",
            "unknown": "❓"
        }.get(comp.status, "❓")
        
        registered_symbol = "✅" if comp.registered else "❌"
        
        response_str = f"{comp.response_time:.3f}s" if comp.response_time else "-"
        
        # Process info
        if comp.process_info and "pid" in comp.process_info:
            process_str = f"PID: {comp.process_info['pid']}"
            if "memory_mb" in comp.process_info:
                process_str += f" ({comp.process_info['memory_mb']:.1f}MB)"
        else:
            process_str = "-"
        
        # Get component info for name and description
        comp_info = config.get_component(comp.name)
        display_name = comp_info.name if comp_info else comp.name.upper()
        
        row = [
            display_name,
            comp.port,
            f"{status_symbol} {comp.status}",
            comp.version,
            f"{registered_symbol}",
            response_str
        ]
        
        if verbose:
            row.append(process_str)
            if comp_info:
                row.append(comp_info.description[:40] + "..." if len(comp_info.description) > 40 else comp_info.description)
        
        table_data.append(row)
    
    # Sort by port
    table_data.sort(key=lambda x: x[1])
    
    headers = ["Component", "Port", "Status", "Version", "Reg", "Response"]
    if verbose:
        headers.extend(["Process", "Description"])
    
    return tabulate(table_data, headers=headers, tablefmt="grid")


def calculate_system_stats(components: List[ComponentStatus]) -> Dict[str, Any]:
    """Calculate overall system statistics"""
    total = len(components)
    healthy = sum(1 for c in components if c.status == "healthy")
    registered = sum(1 for c in components if c.registered)
    running = sum(1 for c in components if c.status != "not_running")
    
    return {
        "total_components": total,
        "healthy_components": healthy,
        "running_components": running,
        "registered_components": registered,
        "health_percentage": (healthy / total * 100) if total > 0 else 0,
        "registration_percentage": (registered / total * 100) if total > 0 else 0
    }


def format_json_output(components: List[ComponentStatus]) -> str:
    """Format output as JSON"""
    stats = calculate_system_stats(components)
    
    output = {
        "timestamp": datetime.now().isoformat(),
        "system_stats": stats,
        "components": [c.to_dict() for c in components]
    }
    
    return json.dumps(output, indent=2)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Check status of Tekton components")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--component", help="Check specific component")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("🔍 Checking Tekton component status...\n")
    
    # Check components
    if args.component:
        # Use centralized component configuration
        config = get_component_config()
        component_name = args.component.lower().replace("-", "_")
        
        if not config.get_component(component_name):
            print(f"❌ Unknown component: {args.component}")
            print(f"Available components: {', '.join(sorted(config.get_all_components().keys()))}")
            sys.exit(1)
        
        components = await check_all_components()
        components = [c for c in components if c.name == component_name]
    else:
        components = await check_all_components()
    
    # Output results
    if args.json:
        print(format_json_output(components))
    else:
        print(format_table_output(components, verbose=args.verbose))
        
        # Print summary
        stats = calculate_system_stats(components)
        print(f"\n📊 System Summary:")
        print(f"   Total Components: {stats['total_components']}")
        print(f"   Running: {stats['running_components']} ({stats['running_components']/stats['total_components']*100:.0f}%)")
        print(f"   Healthy: {stats['healthy_components']} ({stats['health_percentage']:.0f}%)")
        print(f"   Registered: {stats['registered_components']} ({stats['registration_percentage']:.0f}%)")
        
        # Enhanced components
        enhanced = [c for c in components if c.name in ["rhetor", "sophia"] and c.status == "healthy"]
        if enhanced:
            print(f"\n🚀 Enhanced Components:")
            for comp in enhanced:
                comp_info = get_component_config().get_component(comp.name)
                name = comp_info.name if comp_info else comp.name.upper()
                print(f"   - {name} v{comp.version}")
        
        # Show categories if verbose
        if args.verbose:
            config = get_component_config()
            categories = {}
            for comp in components:
                comp_info = config.get_component(comp.name)
                if comp_info:
                    cat = comp_info.category
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(comp)
            
            print(f"\n📋 Components by Category:")
            for cat in sorted(categories.keys()):
                healthy = sum(1 for c in categories[cat] if c.status == "healthy")
                total = len(categories[cat])
                print(f"   {cat.title()}: {healthy}/{total} healthy")
        
        # Issues
        issues = [c for c in components if c.status not in ["healthy", "not_running"]]
        if issues:
            print(f"\n⚠️  Components with Issues:")
            for comp in issues:
                comp_info = get_component_config().get_component(comp.name)
                name = comp_info.name if comp_info else comp.name.upper()
                print(f"   - {name}: {comp.status}")
                if comp.error and args.verbose:
                    print(f"     Error: {comp.error}")


if __name__ == "__main__":
    asyncio.run(main())