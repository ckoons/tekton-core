#!/usr/bin/env python3
"""
Enhanced Tekton Component Launcher - Next Generation

Advanced launcher with health monitoring, auto-recovery, and improved reliability.
"""
import os
import sys
import asyncio
import subprocess
import argparse
import signal
import time
import psutil
import aiohttp
import json
from typing import List, Dict, Optional, Set, Tuple, Any
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from enum import Enum
import platform
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tekton.utils.component_config import get_component_config
from tekton.utils.port_config import get_component_port


class ComponentState(Enum):
    """Component state enumeration"""
    NOT_RUNNING = "not_running"
    STARTING = "starting"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class LaunchResult:
    """Result of a component launch operation"""
    component_name: str
    success: bool
    state: ComponentState
    pid: Optional[int] = None
    port: Optional[int] = None
    message: str = ""
    startup_time: float = 0.0
    health_check_time: Optional[float] = None
    error: Optional[str] = None


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    component_name: str
    healthy: bool
    response_time: float
    status_code: Optional[int] = None
    version: Optional[str] = None
    details: Dict[str, Any] = None
    error: Optional[str] = None
    endpoint: Optional[str] = None


class EnhancedComponentLauncher:
    """Advanced component launcher with monitoring and recovery"""
    
    def __init__(self, verbose: bool = False, health_check_retries: int = 3):
        self.verbose = verbose
        self.health_check_retries = health_check_retries
        self.config = get_component_config()
        self.launched_components: Dict[str, LaunchResult] = {}
        self.health_monitor_task: Optional[asyncio.Task] = None
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            connector=aiohttp.TCPConnector(limit=50)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        if self.health_monitor_task:
            self.health_monitor_task.cancel()
            
    def log(self, message: str, level: str = "info", component: str = None):
        """Enhanced logging with component context"""
        symbols = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "launch": "🚀",
            "health": "🏥",
            "monitor": "👁️"
        }
        symbol = symbols.get(level, "•")
        timestamp = datetime.now().strftime("%H:%M:%S")
        comp_prefix = f"[{component}] " if component else ""
        print(f"{symbol} {timestamp} {comp_prefix}{message}")
        
    async def enhanced_health_check(self, component_name: str, port: int) -> HealthCheckResult:
        """Enhanced health check with multiple endpoints and retries"""
        start_time = time.time()

        # Try multiple health endpoints in order of preference
        health_endpoints = ["/health", "/api/health", "/status", "/api/status", "/"]

        for attempt in range(self.health_check_retries):
            # Try each endpoint until one works
            for endpoint in health_endpoints:
                try:
                    url = f"http://localhost:{port}{endpoint}"

                    async with self.session.get(url) as resp:
                        response_time = time.time() - start_time

                        if resp.status == 200:
                            try:
                                data = await resp.json()
                                return HealthCheckResult(
                                    component_name=component_name,
                                    healthy=True,
                                    response_time=response_time,
                                    status_code=resp.status,
                                    version=data.get("version", "unknown"),
                                    details=data,
                                    endpoint=endpoint
                                )
                            except json.JSONDecodeError:
                                # Health endpoint returns non-JSON but is responsive
                                return HealthCheckResult(
                                    component_name=component_name,
                                    healthy=True,
                                    response_time=response_time,
                                    status_code=resp.status,
                                    endpoint=endpoint
                                )
                        elif resp.status in [404, 405]:
                            # Try next endpoint
                            continue
                        else:
                            # Bad status, but only return error on last attempt/endpoint
                            if attempt == self.health_check_retries - 1 and endpoint == health_endpoints[-1]:
                                return HealthCheckResult(
                                    component_name=component_name,
                                    healthy=False,
                                    response_time=response_time,
                                    status_code=resp.status,
                                    error=f"HTTP {resp.status}",
                                    endpoint=endpoint
                                )

                except (aiohttp.ClientConnectorError, ConnectionRefusedError):
                    # Connection refused - try next endpoint or retry
                    continue
                except asyncio.TimeoutError:
                    # Timeout - try next endpoint
                    continue
                except Exception as e:
                    # Other error - try next endpoint
                    continue

            # If we're here, no endpoint worked this attempt
            if attempt == self.health_check_retries - 1:
                return HealthCheckResult(
                    component_name=component_name,
                    healthy=False,
                    response_time=time.time() - start_time,
                    error=f"No working endpoint found among {health_endpoints}"
                )

            # Wait before retry
            if attempt < self.health_check_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

        # Should never reach here, but just in case
        return HealthCheckResult(
            component_name=component_name,
            healthy=False,
            response_time=time.time() - start_time,
            error="All retries failed"
        )
        
    async def wait_for_healthy(self, component_name: str, port: int, timeout: int = 10) -> bool:
        """Wait for component to become healthy with progress updates"""
        start_time = time.time()
        last_update = 0

        # Start with shorter intervals for faster feedback
        check_interval = 0.5  # Check every 500ms initially

        while time.time() - start_time < timeout:
            health = await self.enhanced_health_check(component_name, port)

            if health.healthy:
                self.log(
                    f"Health check passed in {health.response_time:.3f}s",
                    "health",
                    component_name
                )
                return True

            # Progress update every 3 seconds (faster feedback)
            elapsed = time.time() - start_time
            if elapsed - last_update >= 3:
                remaining = max(0, timeout - elapsed)  # Don't show negative time
                if remaining > 0:
                    self.log(
                        f"Waiting for health check ({remaining:.0f}s remaining)...",
                        "info",
                        component_name
                    )
                else:
                    self.log(
                        f"Waiting for health check (timeout imminent)...",
                        "warning",
                        component_name
                    )
                last_update = elapsed

            await asyncio.sleep(check_interval)

        return False
        
    async def enhanced_launch_component(self, component_name: str) -> LaunchResult:
        """Enhanced component launch with detailed monitoring"""
        launch_start = time.time()
        
        try:
            comp_info = self.config.get_component(component_name)
            if not comp_info:
                return LaunchResult(
                    component_name=component_name,
                    success=False,
                    state=ComponentState.FAILED,
                    message=f"Unknown component: {component_name}",
                    startup_time=time.time() - launch_start
                )
                
            port = comp_info.port
            
            # Check if already running and healthy
            if not self.check_port_available(port):
                health = await self.enhanced_health_check(component_name, port)
                if health.healthy:
                    self.log(f"Already running and healthy", "success", component_name)
                    return LaunchResult(
                        component_name=component_name,
                        success=True,
                        state=ComponentState.HEALTHY,
                        port=port,
                        message=f"Already running on port {port}",
                        startup_time=0,
                        health_check_time=health.response_time
                    )
                else:
                    # Kill unhealthy process
                    self.log(f"Killing unhealthy process on port {port}", "warning", component_name)
                    if not self.kill_port_process(port):
                        return LaunchResult(
                            component_name=component_name,
                            success=False,
                            state=ComponentState.FAILED,
                            message=f"Could not free port {port}",
                            startup_time=time.time() - launch_start
                        )
                    await asyncio.sleep(2)
                    
            # Launch the component
            result = await self.launch_component_process(component_name)
            if not result.success:
                return result
                
            # Wait for component to become healthy (reduced timeout)
            self.log(f"Waiting for health check...", "info", component_name)
            health_start = time.time()

            # Use component-specific timeouts - be more aggressive
            timeout = 8 if component_name in ["hermes", "engram", "rhetor"] else 5

            if await self.wait_for_healthy(component_name, port, timeout=timeout):
                final_health = await self.enhanced_health_check(component_name, port)
                result.state = ComponentState.HEALTHY
                result.health_check_time = time.time() - health_start
                result.message = f"Successfully launched and healthy on port {port}"
                
                # Register with monitoring
                self.launched_components[component_name] = result
                
                self.log(
                    f"Launch completed in {result.startup_time:.1f}s, health in {result.health_check_time:.1f}s",
                    "success",
                    component_name
                )
            else:
                result.state = ComponentState.UNHEALTHY
                result.message = f"Launched but failed health check within 30s"
                result.error = "Health check timeout"
                
                self.log(result.message, "warning", component_name)
                
            result.startup_time = time.time() - launch_start
            return result
            
        except Exception as e:
            return LaunchResult(
                component_name=component_name,
                success=False,
                state=ComponentState.FAILED,
                message=f"Launch failed: {str(e)}",
                error=str(e),
                startup_time=time.time() - launch_start
            )
            
    async def launch_component_process(self, component_name: str) -> LaunchResult:
        """Launch the actual component process (sync version of original logic)"""
        try:
            comp_info = self.config.get_component(component_name)
            port = comp_info.port
            
            # Get launch command (using original logic)
            cmd = self.get_component_command(component_name)
            
            # Set environment variables
            env = os.environ.copy()
            env[f"{component_name.upper()}_PORT"] = str(port)
            
            # Change to component directory
            component_dir = self.get_component_directory(component_name)
                
            if not os.path.exists(component_dir):
                return LaunchResult(
                    component_name=component_name,
                    success=False,
                    state=ComponentState.FAILED,
                    message=f"Component directory not found: {component_dir}"
                )
                
            # Launch the component
            if self.verbose:
                self.log(f"Executing: {' '.join(cmd)}", "launch", component_name)
                
            # Use subprocess.Popen for non-blocking launch
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    cmd,
                    cwd=component_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    cwd=component_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid
                )
                
            # Check if process started successfully (faster check)
            await asyncio.sleep(1)  # Reduced from 2s to 1s
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                error_msg = stderr.decode() if stderr else stdout.decode()

                # Try to extract meaningful error from output
                if "ModuleNotFoundError" in error_msg:
                    clean_error = "Missing Python dependencies"
                elif "Permission denied" in error_msg:
                    clean_error = "Permission denied"
                elif "Address already in use" in error_msg:
                    clean_error = "Port already in use"
                elif "ImportError" in error_msg:
                    clean_error = "Import error - check dependencies"
                else:
                    clean_error = error_msg[:200] if error_msg.strip() else "Process exited without output"

                return LaunchResult(
                    component_name=component_name,
                    success=False,
                    state=ComponentState.FAILED,
                    message=f"Process exited immediately: {clean_error}",
                    error=error_msg[:500]
                )
                
            return LaunchResult(
                component_name=component_name,
                success=True,
                state=ComponentState.STARTING,
                pid=process.pid,
                port=port,
                message=f"Process started with PID {process.pid}"
            )
            
        except Exception as e:
            return LaunchResult(
                component_name=component_name,
                success=False,
                state=ComponentState.FAILED,
                message=f"Failed to start process: {str(e)}",
                error=str(e)
            )
    
    # Include original helper methods
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available (original logic)"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            return False
        
    def kill_port_process(self, port: int) -> bool:
        """Kill process listening on a port (original logic)"""
        try:
            if platform.system() == "Darwin":
                result = subprocess.run(
                    ["lsof", "-ti", f":{port}"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            time.sleep(1)
                            try:
                                os.kill(int(pid), 0)
                                os.kill(int(pid), signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                            return True
                        except Exception as e:
                            if self.verbose:
                                self.log(f"Error killing PID {pid}: {e}", "warning")
            else:
                for conn in psutil.net_connections(kind='inet'):
                    if conn.laddr.port == port and conn.status == 'LISTEN':
                        try:
                            proc = psutil.Process(conn.pid)
                            proc.terminate()
                            proc.wait(timeout=3)
                            return True
                        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                            try:
                                proc.kill()
                                return True
                            except:
                                pass
        except Exception as e:
            if self.verbose:
                self.log(f"Error killing process on port {port}: {e}", "warning")
        return False
    
    def get_component_directory(self, component_name: str) -> str:
        """Get the directory for a component (original logic)"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        dir_mappings = {
            "tekton_core": "tekton-core",
            # "llm_adapter": "LLMAdapter", # Removed - use Rhetor with tekton-llm-client
        }
        
        if component_name in dir_mappings:
            return os.path.join(base_dir, dir_mappings[component_name])
        else:
            dir_name = component_name.replace("_", "-")
            dir_name = dir_name[0].upper() + dir_name[1:] if dir_name else ""
            return os.path.join(base_dir, dir_name)
            
    def get_component_command(self, component_name: str) -> List[str]:
        """Get the launch command for a component (original logic)"""
        component_dir = self.get_component_directory(component_name)
            
        run_script = None
        for script_name in [f"run_{component_name}.sh", f"run_{component_name}.py"]:
            script_path = os.path.join(component_dir, script_name)
            if os.path.exists(script_path):
                run_script = script_path
                break
                
        if run_script and run_script.endswith('.sh'):
            return ["bash", run_script]
        elif run_script and run_script.endswith('.py'):
            return [sys.executable, run_script]
        else:
            port = get_component_port(component_name)
            
            app_module = f"{component_name}.api.app:app"
            if component_name == "hermes":
                app_module = "hermes.api.app:app"
            elif component_name == "hephaestus":
                return [sys.executable, os.path.join(component_dir, "ui", "server", "server.py")]
                
            return [
                sys.executable, "-m", "uvicorn",
                app_module,
                "--host", "0.0.0.0",
                "--port", str(port),
                "--reload"
            ]
    
    async def launch_with_monitoring(self, components: List[str], enable_monitoring: bool = True):
        """Launch components with optional continuous monitoring"""
        if not components:
            self.log("No components to launch", "warning")
            return
            
        # Group by priority
        launch_groups = self.get_launch_groups(components)
        
        self.log(f"Launching {len(components)} components in {len(launch_groups)} groups", "info")
        
        # Launch each priority group
        for priority, group_components in launch_groups.items():
            self.log(f"Priority {priority}: {', '.join(group_components)}", "info")
            
            # Launch in parallel within the group
            tasks = [
                self.enhanced_launch_component(comp)
                for comp in group_components
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Process results
            for result in results:
                if result.success:
                    self.log(result.message, "success", result.component_name)
                else:
                    self.log(result.message, "error", result.component_name)
                    
            # Wait a bit between priority groups
            if priority < max(launch_groups.keys()):
                await asyncio.sleep(2)
                
        # Start health monitoring if requested
        if enable_monitoring:
            self.start_health_monitoring()
            
    def get_launch_groups(self, components: List[str]) -> Dict[int, List[str]]:
        """Group components by startup priority (original logic)"""
        groups = defaultdict(list)
        
        for comp_name in components:
            comp_info = self.config.get_component(comp_name)
            if comp_info:
                priority = comp_info.startup_priority
                groups[priority].append(comp_name)
                
        return dict(sorted(groups.items()))
    
    def start_health_monitoring(self, interval: int = 30):
        """Start continuous health monitoring"""
        async def monitor():
            while True:
                try:
                    await asyncio.sleep(interval)
                    
                    # Check health of all launched components
                    for comp_name in list(self.launched_components.keys()):
                        result = self.launched_components[comp_name]
                        if result.state == ComponentState.HEALTHY:
                            health = await self.enhanced_health_check(comp_name, result.port)
                            
                            if not health.healthy:
                                self.log(
                                    f"Component became unhealthy: {health.error}",
                                    "warning",
                                    comp_name
                                )
                                # Could implement auto-restart here
                                
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.log(f"Health monitoring error: {e}", "error")
                    
        self.health_monitor_task = asyncio.create_task(monitor())
        self.log("Health monitoring started", "monitor")


async def main():
    """Enhanced main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced Tekton component launcher")
    parser.add_argument(
        "--components",
        help="Components to launch (comma-separated) or 'all'",
        default=None
    )
    parser.add_argument(
        "--launch-all",
        action="store_true",
        help="Launch all available components"
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Enable continuous health monitoring"
    )
    parser.add_argument(
        "--health-retries",
        type=int,
        default=3,
        help="Number of health check retries"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    async with EnhancedComponentLauncher(
        verbose=args.verbose,
        health_check_retries=args.health_retries
    ) as launcher:
        
        # Determine components to launch
        if args.launch_all:
            components = list(launcher.config.get_all_components().keys())
        elif args.components:
            if args.components.lower() == 'all':
                components = list(launcher.config.get_all_components().keys())
            else:
                components = [c.strip().lower().replace("-", "_")
                             for c in args.components.split(",")]
        else:
            components = list(launcher.config.get_all_components().keys())
            
        if not components:
            launcher.log("No components selected", "warning")
            return
            
        # Launch components
        start_time = time.time()
        await launcher.launch_with_monitoring(components, enable_monitoring=args.monitor)
        
        # Report results
        elapsed = time.time() - start_time
        successful = len([r for r in launcher.launched_components.values() if r.success])
        failed = len([r for r in launcher.launched_components.values() if not r.success])
        
        print(f"\n{'='*60}")
        print(f"Launch completed in {elapsed:.1f} seconds")
        print(f"✅ Successful: {successful}")
        if failed > 0:
            print(f"❌ Failed: {failed}")
            
        # Keep monitoring if requested
        if args.monitor and launcher.health_monitor_task:
            launcher.log("Monitoring active. Press Ctrl+C to stop.", "info")
            try:
                await launcher.health_monitor_task
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nLauncher stopped by user")
        sys.exit(0)