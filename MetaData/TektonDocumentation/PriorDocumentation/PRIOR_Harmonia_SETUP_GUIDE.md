# Harmonia Setup and Installation Guide

This guide provides step-by-step instructions for setting up and installing the Harmonia workflow orchestration engine in the Tekton ecosystem.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running Harmonia](#running-harmonia)
5. [Integration with Tekton](#integration-with-tekton)
6. [Troubleshooting](#troubleshooting)
7. [Development Setup](#development-setup)
8. [Upgrading](#upgrading)

## Prerequisites

Before installing Harmonia, ensure you have the following prerequisites:

- Python 3.9 or higher
- pip package manager
- Git (for cloning the repository)
- Access to the Tekton repository
- Optional: Docker for containerized deployment

## Installation

### Method 1: Standard Installation

1. Clone the Tekton repository if you haven't already:

```bash
git clone https://github.com/yourusername/Tekton.git
cd Tekton
```

2. Navigate to the Harmonia directory:

```bash
cd Harmonia
```

3. Run the setup script:

```bash
./setup.sh
```

This script will:
- Create a virtual environment
- Install dependencies
- Set up configuration files
- Initialize the state directory

### Method 2: Manual Installation

If the setup script doesn't work for your environment, follow these manual steps:

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Harmonia in development mode:

```bash
pip install -e .
```

4. Create necessary directories:

```bash
mkdir -p ~/.harmonia/state
```

### Method 3: Docker Installation

For containerized deployment:

1. Build the Docker image:

```bash
docker build -t harmonia .
```

2. Run the container:

```bash
docker run -p 8002:8002 -v ~/.harmonia:/root/.harmonia harmonia
```

## Configuration

### Environment Variables

Harmonia can be configured through environment variables:

```bash
# Core settings
export HARMONIA_PORT=8002
export HARMONIA_HOST=0.0.0.0
export HARMONIA_LOG_LEVEL=INFO

# Hermes integration
export HERMES_URL=http://localhost:5000/api
export HERMES_HEARTBEAT_INTERVAL=60

# State management
export HARMONIA_STATE_DIR=~/.harmonia/state
export HARMONIA_DATABASE_URL=  # Optional: Use a database instead of files

# Performance tuning
export HARMONIA_MAX_CONCURRENT_TASKS=10
export HARMONIA_CHECKPOINT_INTERVAL=60
```

### Configuration File

Alternatively, create a configuration file at `~/.harmonia/config.yaml`:

```yaml
# Core settings
server:
  port: 8002
  host: 0.0.0.0
  log_level: INFO

# Hermes integration
hermes:
  url: http://localhost:5000/api
  heartbeat_interval: 60

# State management
state:
  directory: ~/.harmonia/state
  database_url: null  # Optional: Use a database instead of files

# Performance tuning
performance:
  max_concurrent_tasks: 10
  checkpoint_interval: 60
```

### Advanced Configuration

For more advanced settings, edit the configuration file directly:

```yaml
# Add advanced configuration options
advanced:
  # Timeout settings (in seconds)
  timeouts:
    task_execution: 300
    workflow_execution: 3600
    api_request: 30
    
  # Event system configuration
  events:
    buffer_size: 1000
    flush_interval: 5
    
  # Security settings
  security:
    enable_authentication: true
    token_expiration: 3600
    allowed_origins: ["http://localhost:8080"]
```

## Running Harmonia

### Starting Harmonia

1. Activate the virtual environment if not already activated:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run Harmonia:

```bash
python -m harmonia
```

Or use the provided run script:

```bash
./run_harmonia.sh
```

### Command-Line Options

Harmonia supports various command-line options:

```bash
python -m harmonia --port 8002 --host 0.0.0.0 --log-level INFO
```

Available options:
- `--port`: Set the port (default: 8002)
- `--host`: Set the host (default: 0.0.0.0)
- `--log-level`: Set logging level (default: INFO)
- `--data-dir`: Set data directory (default: ~/.harmonia)
- `--config`: Path to config file (default: ~/.harmonia/config.yaml)
- `--no-hermes`: Run without Hermes integration
- `--debug`: Enable debug mode with verbose logging

### Running as a Service

To run Harmonia as a system service:

#### Systemd (Linux)

Create a systemd service file at `/etc/systemd/system/harmonia.service`:

```ini
[Unit]
Description=Harmonia Workflow Engine
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/Tekton/Harmonia
ExecStart=/path/to/Tekton/Harmonia/venv/bin/python -m harmonia
Restart=on-failure
Environment="HARMONIA_PORT=8002"
Environment="HERMES_URL=http://localhost:5000/api"

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable harmonia
sudo systemctl start harmonia
```

## Integration with Tekton

### Registration with Hermes

To register Harmonia with Hermes:

```bash
python register_with_hermes.py
```

This registers Harmonia's capabilities with the Hermes component registry, making them available to other components.

### Starting with Tekton Launch Script

To start Harmonia as part of the Tekton ecosystem:

```bash
cd /path/to/Tekton
./scripts/tekton-launch --components harmonia
```

### Verifying Integration

To verify Harmonia is properly integrated:

```bash
curl http://localhost:5000/api/registration/components

# Look for harmonia.workflow and harmonia.state in the response
```

## Troubleshooting

### Common Issues

1. **Can't connect to Harmonia API**

   - Check if Harmonia is running: `ps aux | grep harmonia`
   - Verify the port is open: `netstat -tuln | grep 8002`
   - Check for firewall issues: `curl -v http://localhost:8002/api/health`

2. **Registration with Hermes fails**

   - Check if Hermes is running: `curl http://localhost:5000/api/health`
   - Check network connectivity: `ping localhost`
   - Check logs for detailed error messages

3. **Workflow execution fails**

   - Check task-specific error messages in the execution response
   - Verify component dependencies are running
   - Check expression evaluation in task inputs

### Checking Logs

Harmonia logs are located at:

- Standard output (when running in the foreground)
- `~/.harmonia/logs/harmonia.log` (default log file)
- Systemd journal (when running as a service): `journalctl -u harmonia`

### Resetting State

If you need to reset Harmonia's state:

```bash
# Stop Harmonia first
rm -rf ~/.harmonia/state/*
```

## Development Setup

For development and testing:

1. Set up a development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/Tekton.git
cd Tekton/Harmonia

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt
pip install -e .
```

2. Run tests:

```bash
pytest
```

3. Run with hot reloading for development:

```bash
uvicorn harmonia.api.app:app --reload --port 8002
```

### Code Structure

- `harmonia/core/`: Core workflow engine functionality
- `harmonia/api/`: API layer (HTTP, WebSocket)
- `harmonia/models/`: Data models for workflows and executions
- `harmonia/scripts/`: Utility scripts
- `harmonia/client.py`: Client library

## Upgrading

### Upgrading from Previous Versions

1. Back up your data:

```bash
cp -r ~/.harmonia ~/.harmonia.backup-$(date +%Y%m%d)
```

2. Update the code:

```bash
cd /path/to/Tekton
git pull
cd Harmonia
```

3. Run the upgrade script:

```bash
./setup.sh --upgrade
```

4. Check for configuration changes:

```bash
diff ~/.harmonia/config.yaml.new ~/.harmonia/config.yaml
```

5. Apply any necessary configuration changes and restart Harmonia.

### Database Migrations

If you're using a database for state storage, run migrations:

```bash
python -m harmonia.scripts.migrate_db
```

### Post-upgrade Verification

After upgrading:

1. Check that Harmonia starts correctly
2. Verify registration with Hermes
3. Run a simple workflow to ensure functionality
4. Check logs for any warnings or errors