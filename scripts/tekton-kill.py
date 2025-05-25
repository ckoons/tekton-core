#!/usr/bin/env python3
"""
Tekton Component Killer - Python implementation

Gracefully shuts down Tekton components with proper cleanup.
"""
import os
import sys
import asyncio
import psutil
import signal
import time
import argparse
import aiohttp
import subprocess
from typing import List, Dict, Optional, Tuple
import platform

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tekton.utils.component_config import get_component_config
from tekton.utils.port_config import get_component_port


class ComponentKiller:
    """Manages graceful shutdown of Tekton components"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.config = get_component_config()
        self.killed_components = set()
        self.failed_components = set()
        
    def log(self, message: str, level: str = "info"):
        """Log a message with formatting"""
        symbols = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "stop": "🛑"
        }
        symbol = symbols.get(level, "•")
        print(f"{symbol} {message}")
        
    def find_process_on_port(self, port: int) -> Optional[psutil.Process]:
        """Find process listening on a specific port"""
        if platform.system() == "Darwin":  # macOS
            try:
                # Use lsof to find process
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    pid = int(result.stdout.strip().split('\n')[0])
                    try:
                        return psutil.Process(pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except Exception as e:
                if self.verbose:
                    self.log(f"Error finding process on port {port}: {e}", "warning")
        else:
            # Use psutil for other platforms
            try:
                for conn in psutil.net_connections(kind='inet'):
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        try:
                            return psutil.Process(conn.pid)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
            except psutil.AccessDenied:
                if self.verbose:
                    self.log(f"Access denied checking port {port}", "warning")
        return None
        
    async def send_shutdown_signal(self, component_name: str, port: int) -> bool:
        """Send shutdown signal via HTTP to component"""
        try:
            # Try to send graceful shutdown via API
            async with aiohttp.ClientSession() as session:
                shutdown_url = f"http://localhost:{port}/shutdown"
                
                try:
                    async with session.post(
                        shutdown_url,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        if resp.status in [200, 204]:
                            if self.verbose:
                                self.log(f"Sent shutdown signal to {component_name}", "info")
                            return True
                except:
                    # Shutdown endpoint might not exist, that's OK
                    pass
                    
        except Exception as e:
            if self.verbose:
                self.log(f"Could not send shutdown signal to {component_name}: {e}", "warning")
        
        return False
        
    def kill_process(self, process: psutil.Process, component_name: str) -> Tuple[bool, str]:
        """Kill a process gracefully, then forcefully if needed"""
        try:
            # Get process info before killing
            pid = process.pid
            
            # First try graceful termination
            if platform.system() == "Windows":
                # Windows: Send CTRL_BREAK_EVENT
                process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                # Unix: Send SIGTERM
                process.terminate()
                
            if self.verbose:
                self.log(f"Sent termination signal to {component_name} (PID: {pid})", "info")
                
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                return True, f"{component_name} terminated gracefully"
            except psutil.TimeoutExpired:
                # Process didn't terminate, force kill
                if self.verbose:
                    self.log(f"{component_name} didn't terminate gracefully, forcing...", "warning")
                    
                process.kill()
                process.wait(timeout=2)
                return True, f"{component_name} force killed"
                
        except psutil.NoSuchProcess:
            return True, f"{component_name} already terminated"
        except psutil.AccessDenied:
            return False, f"Access denied killing {component_name}"
        except Exception as e:
            return False, f"Error killing {component_name}: {str(e)}"
            
    async def kill_component(self, component_name: str) -> Tuple[bool, str]:
        """Kill a single component"""
        try:
            comp_info = self.config.get_component(component_name)
            if not comp_info:
                return False, f"Unknown component: {component_name}"
                
            port = comp_info.port
            
            # Find process on port
            process = self.find_process_on_port(port)
            if not process:
                return True, f"{comp_info.name} not running on port {port}"
                
            # Try graceful shutdown first
            await self.send_shutdown_signal(component_name, port)
            
            # Give it a moment to shutdown gracefully
            time.sleep(1)
            
            # Check if still running
            process = self.find_process_on_port(port)
            if process:
                # Still running, kill it
                success, message = self.kill_process(process, comp_info.name)
                if success:
                    self.killed_components.add(component_name)
                else:
                    self.failed_components.add(component_name)
                return success, message
            else:
                self.killed_components.add(component_name)
                return True, f"{comp_info.name} shutdown gracefully"
                
        except Exception as e:
            self.failed_components.add(component_name)
            return False, f"Error killing {component_name}: {str(e)}"
            
    def kill_all_on_ports(self) -> int:
        """Kill all processes on Tekton ports"""
        killed_count = 0
        all_components = self.config.get_all_components()
        
        for comp_name, comp_info in all_components.items():
            process = self.find_process_on_port(comp_info.port)
            if process:
                try:
                    process_name = process.name()
                    success, message = self.kill_process(process, f"Process on port {comp_info.port}")
                    if success:
                        killed_count += 1
                        self.log(f"Killed {process_name} on port {comp_info.port}", "success")
                    else:
                        self.log(message, "error")
                except Exception as e:
                    self.log(f"Error killing process on port {comp_info.port}: {e}", "error")
                    
        return killed_count
        
    async def kill_components(self, components: List[str]):
        """Kill multiple components"""
        if not components:
            self.log("No components to kill", "warning")
            return
            
        self.log(f"Shutting down {len(components)} components", "info")
        
        # Kill components in reverse startup order (highest priority first)
        sorted_components = sorted(
            components,
            key=lambda c: self.config.get_component(c).startup_priority if self.config.get_component(c) else 0,
            reverse=True
        )
        
        for comp_name in sorted_components:
            success, message = await self.kill_component(comp_name)
            
            if success:
                self.log(message, "success")
            else:
                self.log(message, "error")
                
    def get_running_components(self) -> List[str]:
        """Get list of currently running components"""
        running = []
        all_components = self.config.get_all_components()
        
        for comp_name, comp_info in all_components.items():
            if self.find_process_on_port(comp_info.port):
                running.append(comp_name)
                
        return running


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Kill Tekton components")
    parser.add_argument(
        "--components",
        help="Components to kill (comma-separated) or 'all'",
        default=None
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force kill without graceful shutdown"
    )
    parser.add_argument(
        "--all-ports",
        action="store_true",
        help="Kill all processes on Tekton ports (including non-Tekton processes)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    killer = ComponentKiller(verbose=args.verbose)
    
    # Handle --all-ports flag
    if args.all_ports:
        killer.log("Killing all processes on Tekton ports", "warning")
        killed = killer.kill_all_on_ports()
        killer.log(f"Killed {killed} processes", "info")
        return
        
    # Determine which components to kill
    if args.components:
        if args.components.lower() == 'all':
            components = killer.get_running_components()
        else:
            components = [c.strip().lower().replace("-", "_") 
                         for c in args.components.split(",")]
    else:
        # Default to all running components
        components = killer.get_running_components()
        
    if not components:
        killer.log("No running components found", "info")
        return
        
    # Show what we're about to kill
    killer.log(f"Found {len(components)} running components:", "info")
    for comp in components:
        comp_info = killer.config.get_component(comp)
        if comp_info:
            print(f"  • {comp_info.name} (port {comp_info.port})")
            
    # Kill components
    start_time = time.time()
    await killer.kill_components(components)
    
    # Report results
    elapsed = time.time() - start_time
    successful = len(killer.killed_components)
    failed = len(killer.failed_components)
    
    print(f"\n{'='*60}")
    print(f"Shutdown completed in {elapsed:.1f} seconds")
    print(f"✅ Successful: {successful}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
        print(f"   Failed components: {', '.join(killer.failed_components)}")
    
    # Exit with error code if any failed
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nKill operation cancelled by user")
        sys.exit(1)