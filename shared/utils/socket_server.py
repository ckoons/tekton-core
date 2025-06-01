"""
Socket reuse utility for uvicorn servers.

Provides a wrapper to enable SO_REUSEADDR for uvicorn servers,
fixing the port binding issues during rapid restarts.
"""
import os
import sys
import socket
import signal
import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server


def run_with_socket_reuse(app_str: str, host: str = "0.0.0.0", port: int = 8000, **kwargs):
    """
    Run uvicorn with socket reuse enabled.
    
    This fixes the "Address already in use" error during rapid restarts.
    
    Args:
        app_str: App import string (e.g., "myapp.main:app")
        host: Host to bind to
        port: Port to bind to
        **kwargs: Additional uvicorn.run arguments
    """
    # Create socket with SO_REUSEADDR
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((host, port))
        sock.listen(5)
        
        # Update kwargs to use the socket
        kwargs.update({
            "host": None,  # Don't bind again
            "port": None,  # Don't bind again
            "fd": sock.fileno()
        })
        
        # Run uvicorn with the pre-bound socket
        uvicorn.run(app_str, **kwargs)
        
    finally:
        sock.close()


class ReuseAddressServer(Server):
    """Uvicorn server with SO_REUSEADDR enabled."""
    
    async def startup(self, sockets=None):
        """Override startup to set socket options."""
        await super().startup(sockets)
        
        # Set SO_REUSEADDR on all server sockets
        for server in self.servers:
            for sock in server.sockets:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def run_component_server(
    component_name: str,
    app_module: str,
    default_port: int,
    reload: bool = True
):
    """
    Run a Tekton component server with proper socket reuse.
    
    Args:
        component_name: Name of the component (e.g., "budget", "telos")
        app_module: Module path to the app (e.g., "budget.api.app")
        default_port: Default port if not in environment
        reload: Whether to enable auto-reload
    """
    # Get port from environment
    port_env = f"{component_name.upper()}_PORT"
    port = int(os.environ.get(port_env, str(default_port)))
    
    print(f"Starting {component_name.capitalize()} on port {port}...")
    
    # Run with socket reuse
    run_with_socket_reuse(
        f"{app_module}:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        reload_dirs=[component_name] if reload else None,
        timeout_graceful_shutdown=5,
        server_header=False,
        access_log=False,
        use_colors=True
    )