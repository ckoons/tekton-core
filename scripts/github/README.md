# Tekton GitHub Utilities

## Overview

This directory contains utilities and tools for managing GitHub operations for the Tekton project. These utilities simplify branch management, status checking, and verification across multiple Tekton components.

## Directory Structure

- `lib/`: Shared library functions used by GitHub utilities
- `templates/`: Template files for GitHub operations
- `claude/`: Helper scripts designed for Claude Code sessions
- `examples/`: Example usage of GitHub utilities

## Available Utilities

- `tekton-branch-create`: Creates branches with consistent naming across all components
- `tekton-branch-status`: Checks branch status across all Tekton components
- `tekton-branch-verify`: Verifies branch correctness for Claude sessions

## Usage

See each utility's documentation and help text for specific usage instructions.

```bash
./scripts/github/tekton-branch-create --help
./scripts/github/tekton-branch-status --help
./scripts/github/tekton-branch-verify --help
```

## Common Workflows

### Starting a New Development Sprint

```bash
# Create a new sprint branch across all components
./scripts/github/tekton-branch-create sprint/feature-name-YYMMDD
```

### Checking Sprint Status

```bash
# Check status of a sprint branch across all components
./scripts/github/tekton-branch-status sprint/feature-name-YYMMDD
```

### Verifying Branch for Claude Sessions

```bash
# Verify the current branch for a Claude session
./scripts/github/tekton-branch-verify sprint/feature-name-YYMMDD
```