# Clean Slate Sprint - Claude Code Implementation Guide for Telos

## Context

You are assisting with the Clean Slate Sprint for the Tekton project. This sprint focuses on rebuilding the UI component architecture to address persistent issues in previous implementations. The goal is to establish a reliable, standardized approach to UI components with proper isolation and clear patterns.

The project has made excellent progress. So far, we have:
1. Implemented the Athena component with BEM naming and proper isolation
2. Implemented the Ergon component following the same patterns
3. Implemented the Hermes component following the same patterns
4. Implemented the Engram component following the same patterns
5. Implemented the Rhetor component following the same patterns
6. Created a comprehensive debug instrumentation system for both frontend and backend
7. Added debug instrumentation to all implemented components
8. Currently implementing the Prometheus component following the same patterns

**IMPORTANT UPDATE (May 11, 2025):** The next major task (after Prometheus) is to implement the Telos component (requirements management system) using the same patterns established for other components, with Athena as the gold standard reference model.

## Your Role

As the AI assistant for this sprint, your role is to implement the Telos component following a methodical, restrained approach that prioritizes reliability over feature richness. You should:

1. Follow the implementation plan exactly, using Athena as the reference
2. Focus on creating simple, reliable solutions with clear patterns
3. Test each step before proceeding to the next
4. Maintain strict component isolation to prevent interference
5. Document your work clearly for future reference

## Key Principles to Follow

### 1. Restraint and Simplicity

- Keep implementations as simple as possible
- Resist the urge to add features or optimizations before basics work
- Focus on doing one thing well before moving to the next
- When in doubt, choose the simpler approach

### 2. Strict Component Isolation

- Components should never affect other components
- CSS must use BEM notation with component prefixes
- JS must query elements only within the component container
- Use relative positioning instead of absolute positioning
- Respect the boundaries between components and the main UI

### 3. Template-Based Development

- Use the Athena component as the gold standard reference template
- Make minimal modifications to the template pattern
- Follow the same structure and naming conventions consistently
- Document any deviations from the template pattern

### 4. Progressive Enhancement

- First ensure components load correctly
- Then add basic interactivity
- Add more complex features only after basics work
- Test each stage before proceeding

## Implementation Approach

### Phase 1: Foundation (Completed)

- Established the foundation with the component loader
- Created golden component templates based on Athena
- Defined component contracts for lifecycle, events, and state
- Implemented debug instrumentation

### Phase 2: Component Implementation (Current Focus)

1. **Implement Telos component** ⚠️
   - Start with HTML structure following the Athena template
   - Add CSS with BEM naming
   - Implement JS with lifecycle methods
   - Add requirements management functionality
   - Ensure visual consistency with other components, especially Athena

### Phase 3: Validation and Documentation (Ongoing)

1. **Documentation updates** (continuous)
   - Document the Telos implementation
   - Update guides and references
   - Create troubleshooting information

2. **Testing and validation** (with Telos component)
   - Test loading and functionality
   - Verify isolation from other components
   - Test error handling and recovery

## Specific Guidelines

### Working with HTML

- Follow semantic HTML principles
- Use clear, descriptive class names following BEM
- Ensure proper nesting and hierarchy
- Keep markup clean and minimal
- Follow the established structure:
  - Component container
  - Header with title
  - Menu bar with tabs
  - Content area with panels
  - Footer with input (for chat components)

### Working with CSS

- Always use BEM notation: `.telos__element--modifier`
- Scope all styles to the component root
- Avoid global styles or resets
- Use relative units when possible
- Prefer flexbox/grid for layout
- Match heights and spacing with Athena component:
  - Header height: 50px
  - Menu bar height: 46px
  - Footer height: 70px

### Working with JavaScript

- Scope queries to component container: `document.querySelector('.telos').querySelector()`
- Use clear method and variable names
- Follow the defined lifecycle pattern
- Implement proper error handling
- Clean up event listeners and resources
- Protect against UI Manager interference

## Key Files to Modify

### Telos Component (to implement)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/telos/telos-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/telos/telos-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/telos/telos-service.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/telos/requirements-manager.js`

### Reference Components (already implemented)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html` (PRIMARY REFERENCE)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/ergon/ergon-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/hermes/hermes-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/engram/engram-component.html`

### Debug Instrumentation
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/debug-shim.js`

## Getting Started

1. Verify you're on the correct branch:
   ```bash
   git branch
   # Should show sprint/Clean_Slate_051125
   ```

2. Examine the Athena component as your primary reference:
   ```bash
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html
   ```

3. Begin implementing the Telos component following the established patterns from Athena

4. Test the component in the Hephaestus UI by running:
   ```bash
   cd /Users/cskoons/projects/github/Tekton/Hephaestus/ui && python server/server.py
   ```

## Implementation Requirements

**CRITICAL**: You MUST follow the TelosImplementationGuide.md document exactly, without any deviations. If you believe any changes are needed, you MUST discuss these with Casey (human-in-the-loop) first before implementation. No architectural changes, altered patterns, or extra features are allowed without explicit approval.

## Important Notes

1. **Use Athena as the gold standard**: The Athena component is the canonical reference for all UI patterns
2. **Make small, incremental changes**: This makes debugging easier
3. **Test thoroughly**: Test each change before moving on
4. **Document your work**: Document any challenges, decisions, or patterns
5. **Follow the established patterns**: Consistency is crucial
6. **Maintain restraint**: Focus on reliability over features
7. **Visual consistency**: Ensure the Telos component visually matches other components

## Documentation

Refer to these documents for detailed guidance:

- [Sprint Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/SprintPlan.md)
- [Architectural Decisions](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ArchitecturalDecisions.md)
- [Implementation Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ImplementationPlan.md)
- [Telos Implementation Guide](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/TelosImplementationGuide.md)
- [Debug Instrumentation Guide](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/DeveloperGuides/Debugging/ComponentInstrumentation.md)

## Telos Component Overview

The Telos component is Tekton's requirements management system, designed to help users track, analyze, and manage project requirements throughout the software development lifecycle. It should include the following key features:

1. **Projects Panel** - For managing requirement projects and collections
2. **Requirements Panel** - For viewing, filtering, and managing requirements
3. **Traceability Panel** - For visualizing requirement relationships and dependencies
4. **Validation Panel** - For validating requirements against quality criteria
5. **Requirements Chat Panel** - For requirements-specific assistance
6. **Team Chat Panel** - For team communication (consistent with other components)

The component should follow the same visual and structural patterns as the other components, with tabs at the top, content panels in the middle, and a consistent footer for input. The Telos component should match the visual style of other components, especially Athena.

Build the component following the same BEM patterns, component isolation, and debug instrumentation as implemented in the Athena component.