# Hephaestus

Integrated GUI for the Tekton Multi-AI Engineering Platform.

## Overview

Hephaestus provides a unified graphical interface for all Tekton components, enabling visual management and interaction with the entire platform. Named after the Greek god of craftsmen and technology, Hephaestus brings together the various components of Tekton into a cohesive whole.

## Features

- Unified dashboard for all Tekton components
- Component-specific interfaces for specialized tasks
- Real-time status monitoring of the Tekton ecosystem
- Integration with Hermes for seamless communication
- Cross-component workflow visualization

## Project Status

🚧 **Early Development** 🚧

This component is currently in the planning and initial implementation phase.

## Component Integration

Hephaestus integrates with the following Tekton components:

- **Hermes**: For messaging and communication
- **Tekton Core**: For component lifecycle management
- **All Components**: Providing specialized UIs for each

## Development

### Prerequisites

- Python 3.9+
- Node.js 16+
- Tekton core components

### Setup

```bash
# Clone the repository
git clone https://github.com/cskoons/Hephaestus.git

# Install dependencies
cd Hephaestus
pip install -e .
npm install
```

### Running the GUI

```bash
# From the Tekton root directory
./hephaestus_launch

# Or, with the integrated launcher
./tekton_launch --gui
```

## Architecture

Hephaestus follows the Tekton architectural principles while adding a presentation layer:

- Component-based UI design
- Integration with the Hermes messaging system
- Decoupled from core functionality for optional use
- Extensible to accommodate new Tekton components