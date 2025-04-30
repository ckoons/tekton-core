# Tekton Development Sprint Process

## Overview

This document outlines the Development Sprint process for the Tekton project. Development Sprints provide a structured approach to implementing new features, addressing technical debt, and improving the Tekton ecosystem. Each sprint follows a defined process with clear roles, phases, and deliverables.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint process is designed to facilitate the continuous improvement of Tekton in a systematic and documented way.

## Roles and Responsibilities

### Casey (Human-in-the-Loop)

Casey is the project manager and human-in-the-loop who:
- Initiates Development Sprints based on project needs
- Reviews and approves transitions between sprint phases
- Provides feedback and guidance throughout the process
- Makes key decisions regarding sprint scope and direction
- Approves final deliverables and merges

### Architect Claude

The Architect Claude is an AI assistant responsible for:
- Creating high-level sprint plans and architectural designs
- Producing detailed implementation plans
- Documenting architectural decisions
- Defining sprint phases and deliverables
- Providing guidance to Working Claude sessions
- Answering architectural and design questions

### Working Claude

The Working Claude is an AI assistant (which may be different for each phase) responsible for:
- Implementing code according to the implementation plan
- Creating tests and ensuring code quality
- Updating documentation
- Producing status reports after each phase
- Creating retrospectives and identifying improvements
- Preparing instructions for subsequent Working Claude sessions

## Development Sprint Phases

### 1. Inception

- Casey discusses a potential sprint idea with Claude
- They evaluate the feasibility and value of the proposed work
- Casey decides whether to proceed with detailed planning or table the idea
- If proceeding, Casey requests Architect Claude to create a detailed plan

### 2. Planning and Architecture

- Architect Claude researches the requirements and current state
- Architect Claude creates a high-level plan document
- Architect Claude documents architectural decisions
- Architect Claude produces a detailed implementation plan
- Casey reviews and approves the plan, or requests changes
- Architect Claude creates the initial prompt for the Working Claude session

### 3. Implementation (potentially multiple phases)

- Working Claude reviews all sprint documentation
- Working Claude verifies they are working on the correct GitHub branch using `tekton-branch-verify`
- Working Claude asks any questions before beginning implementation
- Working Claude implements the code according to the plan
- Working Claude creates/updates tests
- Working Claude updates documentation
- Working Claude produces a status report after completing the phase

### 4. Continuation and Handoff (if needed)

- Working Claude prepares detailed instructions for the next phase
- Working Claude identifies remaining work and potential challenges
- Casey reviews the status and approves moving to the next phase
- A new Working Claude session continues implementation

### 5. Completion and Retrospective

- Working Claude finalizes all code changes
- Working Claude ensures all tests pass
- Working Claude completes all documentation updates
- Working Claude prepares a final status report
- Working Claude creates a retrospective document identifying improvements
- Working Claude identifies opportunities for shared code and further enhancements
- Casey reviews the final deliverables

### 6. Merge and Integration

- Casey approves the final changes
- Casey coordinates the merge into the main branch
- The improvements are integrated into the Tekton ecosystem

## Directory Structure

Each Development Sprint has its own directory under `MetaData/DevelopmentSprints/`:

```
MetaData/DevelopmentSprints/
├── README.md                         # This file explaining the overall process
├── Templates/                        # Templates for standard sprint documents
│   ├── SprintPlan.md
│   ├── ArchitecturalDecisions.md
│   ├── ImplementationPlan.md
│   ├── StatusReport.md
│   ├── Retrospective.md
│   └── PromptTemplate.md
└── [SprintName]/                     # One directory per sprint
    ├── README.md                     # Sprint-specific guidance
    ├── SprintPlan.md                 # High-level sprint plan
    ├── ArchitecturalDecisions.md     # Key architectural decisions
    ├── ImplementationPlan.md         # Detailed implementation plan
    ├── ClaudeCodePrompt.md           # Initial prompt for Working Claude
    ├── StatusReports/                # Directory for status reports
    │   ├── Phase1Status.md
    │   └── FinalStatus.md
    ├── Instructions/                 # Instructions for subsequent phases
    │   └── Phase2Instructions.md
    └── Retrospective.md              # Sprint retrospective
```

Each sprint directory may also contain additional documents specific to that sprint.

## GitHub Workflow

Tekton Development Sprints utilize a structured GitHub workflow to manage changes across components. The following utilities facilitate this workflow:

### Branch Management

- **tekton-branch-create**: Creates branches with consistent naming across all components
  ```bash
  scripts/github/tekton-branch-create sprint/feature-name-YYMMDD
  ```

- **tekton-branch-verify**: Verifies branch correctness before beginning work
  ```bash
  scripts/github/tekton-branch-verify sprint/feature-name-YYMMDD
  ```

- **tekton-branch-status**: Checks branch status across all Tekton components
  ```bash
  scripts/github/tekton-branch-status sprint/feature-name-YYMMDD
  ```

- **tekton-branch-sync**: Synchronizes changes between branches across components
  ```bash
  scripts/github/tekton-branch-sync source-branch target-branch
  ```

- **tekton-branch-cleanup**: Safely removes unused branches
  ```bash
  scripts/github/tekton-branch-cleanup --dry-run "sprint/*"
  ```

### Commit Management

- **tekton-commit**: Generates standardized commit messages using templates
  ```bash
  scripts/github/tekton-commit --title "Add new feature" feature
  ```

### Claude Code Integration

Special utilities are provided for Claude Code sessions:

- **scripts/github/claude/branch-validator.sh**: Validates branch for Claude sessions
- **scripts/github/claude/prepare-session.sh**: Prepares environment for Claude sessions
- **scripts/github/claude/generate-commit.sh**: Generates commit message templates

### Setup and Configuration

Working Claude sessions must use these utilities to ensure consistency across all Development Sprints. To verify the correct setup, Working Claude should run:

```bash
scripts/github/claude/prepare-session.sh -c -p sprint/your-sprint-name-YYMMDD
```

## Branch Management

Every Development Sprint must work in isolation on a dedicated branch to prevent conflicts between sprints. The branch naming convention is:

```
sprint/[sprint-name]-[date]
```

For example: `sprint/shared-code-042825`

Working Claude sessions must verify they are on the correct branch before making any changes. This is done using the `tekton-branch-verify` utility:

```bash
scripts/github/tekton-branch-verify sprint/your-sprint-name-YYMMDD
```

For detailed branch management guidelines, see [Branch Management Guide](/MetaData/DevelopmentSprints/Templates/BranchManagement.md).

## Commit Messages

Commit messages should be descriptive and specific to the changes being made. They should also be formatted according to the [Conventional Commits specification](https://www.conventionalcommits.org/en/v1.0.0/) and should always include the following lines to credit both Claude Code and Casey Koons.

```
🤖 Generated with [Claude Code](https://claude.ai/code)
Design & Engineering Guidance by Casey Koons <cskoons@gmail.com>
Co-Authored-By: Casey Koons <cskoons@gmail.com> & Claude <noreply@anthropic.com>
```

To ensure consistent commit messages, use the `tekton-commit` utility:

```bash
scripts/github/tekton-commit --title "Your commit title" feature|fix|docs|refactor|test|chore
```

## Documentation Requirements

Documentation updates are a critical part of every Development Sprint. Three categories of documentation have been defined:

1. **MUST Update**: Documentation that must be updated as part of the sprint
   - Component-specific documentation for modified components
   - API references for changed APIs
   - User guides for new features

2. **CAN Update**: Documentation that can be updated if relevant
   - Development guides
   - Best practices
   - Examples and tutorials

3. **CANNOT Update without Approval**: Documentation requiring approval
   - Architecture overview
   - Project roadmap
   - Core design principles

Each Implementation Plan will specify which documentation falls into each category for that sprint.

## AI-Centric Development Paradigm

Tekton represents a paradigm shift from traditional human-driven development to a collaborative multi-AI engineering platform. This approach influences how Development Sprints are conducted and evaluated.

### Core AI-Centric Principles

1. **Composable, Single-Purpose Tools**: Following the UNIX philosophy, create small, well-defined utilities that can be composed rather than monolithic systems.

2. **Protocol-First Development**: Define interfaces and contracts before implementation, enabling parallel development by different AI systems.

3. **Declarative Over Imperative**: Specify desired outcomes rather than step-by-step procedures, allowing AIs to determine optimal implementation paths.

4. **Evolutionary Architecture**: Build systems that expect and facilitate their own evolution through experimental branches and feedback loops.

5. **Knowledge Transfer Between AI Instances**: Create structured ways for AI insights to be persisted and shared between Claude sessions and across sprints.

6. **Contextual Memory and Progressive Reasoning**: Design systems where context is preserved across AI invocations through mechanisms like Engram.

7. **Meta-Programming Capabilities**: Provide frameworks where AIs can define and test abstractions, generating tools to improve their own workflows.

8. **Self-Discovery and Registration**: Components should register their capabilities, making them discoverable without human guidance.

For detailed information on these principles and their implementation, see [AI-Centric Development Principles](/MetaData/DevelopmentSprints/Templates/AICentricDevelopment.md).

### Self-Improvement Cycle

Each Development Sprint should include dedicated time and resources for self-improvement:

- AI systems should analyze their own performance and suggest improvements
- Successful patterns should be extracted and formalized
- Meta-level improvements to the development process itself should be prioritized
- Opportunities for shared libraries and utilities should be identified
- New insights should be documented for future sprints

This self-improvement cycle ensures that Tekton evolves not just through planned features but through discoveries made during the development process itself.

## Continuous Improvement

The Development Sprint process itself is subject to continuous improvement. Each retrospective should not only address the specific sprint but also identify ways to improve the sprint process itself. These improvements will be incorporated into future sprints.

Sprint retrospectives should specifically address:

1. **Process Improvements**: How can the Development Sprint workflow be enhanced?
2. **Tool Enhancements**: What new tools or improvements to existing tools would streamline development?
3. **Communication Patterns**: How can AI collaboration be made more effective?
4. **Knowledge Persistence**: How can insights from this sprint be better preserved for future work?
5. **Meta-Programming Opportunities**: What repetitive tasks could be automated through new utilities?

## Getting Started

To initiate a Development Sprint:

1. Casey discusses the idea with Claude
2. If approved, Casey requests a detailed plan from Architect Claude
3. Architect Claude creates the initial sprint documentation
4. A dedicated branch is created for the sprint using the `tekton-branch-create` utility
5. The Working Claude session begins implementation, first verifying the branch with `tekton-branch-verify`
6. Status is tracked throughout the process
7. The sprint is completed with a retrospective

For detailed information on a specific sprint, refer to the README.md in that sprint's directory.