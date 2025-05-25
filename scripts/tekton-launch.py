#!/usr/bin/env python3
"""
Tekton Component Launcher - Python implementation

Launches Tekton components with proper dependency management and parallel execution.
"""
import os
import sys
import asyncio
import subprocess
import argparse
import signal
import time
import psutil
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import platform

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tekton.utils.component_config import get_component_config
from tekton.utils.port_config import get_component_port


class ComponentLauncher:
    """Manages launching of Tekton components"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.config = get_component_config()
        self.launched_components = set()
        self.failed_components = set()
        
    def log(self, message: str, level: str = "info"):
        """Log a message with formatting"""
        symbols = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "launch": "🚀"
        }
        symbol = symbols.get(level, "•")
        print(f"{symbol} {message}")
        
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        import socket
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return True
        except OSError:
            # Port is in use
            return False
        
    def kill_port_process(self, port: int) -> bool:
        """Kill process listening on a port"""
        try:
            if platform.system() == "Darwin":  # macOS
                # Use lsof to find process
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
                            # Check if still running
                            try:
                                os.kill(int(pid), 0)  # Check if process exists
                                os.kill(int(pid), signal.SIGKILL)  # Force kill
                            except ProcessLookupError:
                                pass  # Already dead
                            return True
                        except Exception as e:
                            if self.verbose:
                                self.log(f"Error killing PID {pid}: {e}", "warning")
            else:
                # Try psutil for other platforms
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
        """Get the directory for a component"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Directory name mappings
        dir_mappings = {
            "tekton_core": "tekton-core",
            "llm_adapter": "LLMAdapter",
            # Most components follow the Title case pattern
        }
        
        if component_name in dir_mappings:
            return os.path.join(base_dir, dir_mappings[component_name])
        else:
            # Default: capitalize first letter
            dir_name = component_name.replace("_", "-")
            dir_name = dir_name[0].upper() + dir_name[1:] if dir_name else ""
            return os.path.join(base_dir, dir_name)
            
    def get_component_command(self, component_name: str) -> List[str]:
        """Get the launch command for a component"""
        # Get the component's directory
        component_dir = self.get_component_directory(component_name)
            
        # Check if component has a run script
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
            # Default to uvicorn
            port = get_component_port(component_name)
            
            # Determine the app module
            app_module = f"{component_name}.api.app:app"
            if component_name == "hermes":
                app_module = "hermes.api.app:app"
            elif component_name == "hephaestus":
                # Hephaestus uses a different server
                return [sys.executable, os.path.join(component_dir, "ui", "server", "server.py")]
                
            return [
                sys.executable, "-m", "uvicorn",
                app_module,
                "--host", "0.0.0.0",
                "--port", str(port),
                "--reload"
            ]
            
    def launch_component(self, component_name: str) -> Tuple[bool, str]:
        """Launch a single component"""
        try:
            comp_info = self.config.get_component(component_name)
            if not comp_info:
                return False, f"Unknown component: {component_name}"
                
            port = comp_info.port
            
            # Check if already running
            if not self.check_port_available(port):
                self.log(f"{comp_info.name} already running on port {port}", "warning")
                # Try to kill existing process
                if self.kill_port_process(port):
                    self.log(f"Killed existing process on port {port}", "info")
                    time.sleep(1)  # Give it a moment
                else:
                    return False, f"Could not free port {port}"
                    
            # Get launch command
            cmd = self.get_component_command(component_name)
            
            # Set environment variables
            env = os.environ.copy()
            env[f"{component_name.upper()}_PORT"] = str(port)
            
            # Change to component directory
            component_dir = self.get_component_directory(component_name)
                
            if not os.path.exists(component_dir):
                return False, f"Component directory not found: {component_dir}"
                
            # Launch the component
            if self.verbose:
                self.log(f"Launching {comp_info.name} with: {' '.join(cmd)}", "launch")
                
            # Use subprocess.Popen for non-blocking launch
            if platform.system() == "Windows":
                # Windows: Use CREATE_NEW_PROCESS_GROUP
                process = subprocess.Popen(
                    cmd,
                    cwd=component_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Unix: Use preexec_fn to detach from process group
                process = subprocess.Popen(
                    cmd,
                    cwd=component_dir,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid
                )
                
            # Check if process started successfully
            time.sleep(2)  # Give it time to start
            if process.poll() is not None:
                # Process already exited
                stdout, stderr = process.communicate()
                error_msg = stderr.decode() if stderr else stdout.decode()
                return False, f"Process exited immediately: {error_msg[:200]}"
                
            self.launched_components.add(component_name)
            return True, f"{comp_info.name} launched successfully on port {port}"
            
        except Exception as e:
            return False, f"Error launching {component_name}: {str(e)}"
            
    def get_launch_groups(self, components: List[str]) -> Dict[int, List[str]]:
        """Group components by startup priority"""
        groups = defaultdict(list)
        
        for comp_name in components:
            comp_info = self.config.get_component(comp_name)
            if comp_info:
                priority = comp_info.startup_priority
                groups[priority].append(comp_name)
                
        return dict(sorted(groups.items()))
        
    async def launch_components(self, components: List[str], parallel: bool = True):
        """Launch multiple components with dependency management"""
        if not components:
            self.log("No components to launch", "warning")
            return
            
        # Group by priority
        launch_groups = self.get_launch_groups(components)
        
        self.log(f"Launching {len(components)} components in {len(launch_groups)} groups", "info")
        
        # Launch each priority group
        for priority, group_components in launch_groups.items():
            self.log(f"\nPriority {priority}: {', '.join(group_components)}", "info")
            
            if parallel and len(group_components) > 1:
                # Launch in parallel within the group
                with ThreadPoolExecutor(max_workers=len(group_components)) as executor:
                    futures = {
                        executor.submit(self.launch_component, comp): comp
                        for comp in group_components
                    }
                    
                    for future in as_completed(futures):
                        comp_name = futures[future]
                        success, message = future.result()
                        
                        if success:
                            self.log(message, "success")
                        else:
                            self.log(message, "error")
                            self.failed_components.add(comp_name)
            else:
                # Launch sequentially
                for comp_name in group_components:
                    success, message = self.launch_component(comp_name)
                    
                    if success:
                        self.log(message, "success")
                    else:
                        self.log(message, "error")
                        self.failed_components.add(comp_name)
                        
            # Wait a bit between priority groups
            if priority < max(launch_groups.keys()):
                time.sleep(2)
                
    def select_components_interactive(self) -> List[str]:
        """Interactive component selection"""
        all_components = self.config.get_all_components()
        
        print("\nAvailable components:")
        sorted_components = sorted(all_components.items(), key=lambda x: x[1].startup_priority)
        
        for i, (comp_name, comp_info) in enumerate(sorted_components):
            print(f"  {i+1:2d}. {comp_info.name:20} - {comp_info.description}")
            
        print("\nEnter component numbers (comma-separated) or 'all' for all components:")
        selection = input("> ").strip()
        
        if selection.lower() == 'all':
            return list(all_components.keys())
            
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected = []
            for idx in indices:
                if 0 <= idx < len(sorted_components):
                    selected.append(sorted_components[idx][0])
            return selected
        except:
            print("Invalid selection")
            return []


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Launch Tekton components")
    parser.add_argument(
        "--components",
        help="Components to launch (comma-separated) or 'all'",
        default=None
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Don't prompt for component selection"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Launch components sequentially instead of in parallel"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    launcher = ComponentLauncher(verbose=args.verbose)
    
    # Determine which components to launch
    if args.components:
        if args.components.lower() == 'all':
            components = list(launcher.config.get_all_components().keys())
        else:
            components = [c.strip().lower().replace("-", "_") 
                         for c in args.components.split(",")]
    elif args.non_interactive:
        # Default to all components in non-interactive mode
        components = list(launcher.config.get_all_components().keys())
    else:
        # Interactive selection
        components = launcher.select_components_interactive()
        
    if not components:
        launcher.log("No components selected", "warning")
        return
        
    # Launch components
    start_time = time.time()
    await launcher.launch_components(components, parallel=not args.sequential)
    
    # Report results
    elapsed = time.time() - start_time
    successful = len(launcher.launched_components)
    failed = len(launcher.failed_components)
    
    print(f"\n{'='*60}")
    print(f"Launch completed in {elapsed:.1f} seconds")
    print(f"✅ Successful: {successful}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
        print(f"   Failed components: {', '.join(launcher.failed_components)}")
    
    # Exit with error code if any failed
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nLaunch cancelled by user")
        sys.exit(1)