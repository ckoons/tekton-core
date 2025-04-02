# Tekton Orchestration System

<div align="center">
  <img src="images/icon.png" alt="Tekton Logo" width="800"/>
  <h3>Tekton<br>AI Driven Orchestration</h3>
</div>

Tekton is an intelligent orchestration system for AI-driven problem-solving. It coordinates multiple AI models, tools, and resources to efficiently tackle complex software engineering and knowledge work tasks.

## Overview

Tekton serves as the "builder" - the central coordinator between various AI models, tools, and workflows. It intelligently decomposes problems, routes tasks to the appropriate AI models or agents, and manages the execution flow for optimal outcomes.

### Key Features

- **Model Orchestration**: Coordinates between local and remote AI models
- **Task Routing**: Intelligently assigns tasks to the most appropriate models/agents
- **Problem Decomposition**: Breaks complex problems into manageable subtasks
- **Memory Integration**: Leverages Engram for persistent context across sessions
- **Agent Management**: Works with Agenteer for specialized agent creation and workflow
- **Resource Optimization**: Uses the right AI for each task based on complexity and requirements

## Architecture

Tekton uses a layered architecture:

```
┌─────────────────────────────────────────┐
│              Tekton Core                │
│  (Orchestration and Coordination Layer) │
└───────────────┬─────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼───────────┐   ┌───────▼─────────┐
│ Model Manager │   │ Workflow Engine │
└───────┬───────┘   └────────┬────────┘
        │                    │
┌───────▼───────┐   ┌────────▼────────┐
│ Local Models  │   │ Remote Services │
└───────────────┘   └─────────────────┘
```

## Integration

Tekton integrates with:

- **Codex**: For AI-assisted software engineering
- **Engram**: For persistent memory across sessions
- **Ergon**: For specialized agent creation and workflow management
- **Rhetor**: For AI communication, prompt engineering and context management
- **Sophia**: For Machine Learning, self improvement of Tekton and all component operations
- **Telos**: For User communication, requierments development & analysis, evaluation and goals
- **Local Models**: Deepseek Coder, CodeLlama, etc.
- **Remote APIs**: Claude, GPT, etc.

## Requirements

- Python 3.10+
- Linux or macOS

## Installation

Tekton uses the modern UV package manager for fast, reliable Python dependency management.

### Quick Install

```bash
# Install Tekton with UV
./tekton-install.sh
```

### Manual Installation

1. Install UV package manager:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create a Python environment:
   ```bash
   uv venv .venv --python=python3.10
   source .venv/bin/activate
   ```

3. Install Tekton Core:
   ```bash
   uv pip install -e tekton-core
   ```

### Setting Up Components

To set up individual Tekton components:

```bash
# Setup a specific component
./component-setup.sh Engram

# Setup all components
./setup-all.sh
```

## License

MIT License
