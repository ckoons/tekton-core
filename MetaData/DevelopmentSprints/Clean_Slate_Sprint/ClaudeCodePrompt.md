# Clean Slate Sprint - Claude Code Implementation Guide

## Context

You are assisting with the Clean Slate Sprint for the Tekton project. This sprint focuses on rebuilding the UI component architecture to address persistent issues in previous implementations. The goal is to establish a reliable, standardized approach to UI components with proper isolation and clear patterns.

The project has already been reset to a clean state with the main branch, providing a solid foundation to build upon. The key architectural decisions and implementation plan have been documented in detail.

## Your Role

As the AI assistant for this sprint, your role is to implement the plans following a methodical, restrained approach that prioritizes reliability over feature richness. You should:

1. Follow the implementation plan exactly, progressing through phases in order
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

- Use the golden template as the starting point for all components
- Make minimal modifications to the template pattern
- Follow the same structure and naming conventions consistently
- Document any deviations from the template pattern

### 4. Progressive Enhancement

- First ensure components load correctly
- Then add basic interactivity
- Add more complex features only after basics work
- Test each stage before proceeding

## Implementation Approach

### Phase 1: Foundation and Component Loader

1. **First, analyze the existing component loader**:
   - How components are loaded and initialized
   - How paths are resolved
   - Error handling mechanisms
   - Points of failure in the current implementation

2. **Create simplified component loader**:
   - Focus solely on reliable loading
   - Clear error handling
   - Simplified path resolution
   - Proper cleanup

3. **Establish golden component template**:
   - Create HTML template with proper structure
   - Create CSS template with BEM naming
   - Create JS template with lifecycle methods
   - Document usage clearly

4. **Define component contract**:
   - Lifecycle methods (init, activate, cleanup)
   - Event handling
   - State management
   - Integration with UI manager

### Phase 2: Component Implementation

1. **Implement Ergon component**:
   - Start with HTML structure following template
   - Add CSS with BEM naming
   - Implement JS with lifecycle methods
   - Verify basic loading works

2. **Add interactivity**:
   - Implement tab switching
   - Add basic state management
   - Handle environmental configuration
   - Test interactions thoroughly

3. **Create test harness**:
   - Simple tests for component loading
   - Verification of component behavior
   - Error case testing
   - Isolation verification

### Phase 3: Validation and Documentation

1. **Comprehensive testing**:
   - Test all components together
   - Verify no interference
   - Test error handling
   - Test different scenarios

2. **Documentation**:
   - Update component development guide
   - Create troubleshooting guide
   - Document patterns and contracts
   - Provide clear examples

## Specific Guidelines

### Working with HTML

- Follow semantic HTML principles
- Use clear, descriptive class names following BEM
- Ensure proper nesting and hierarchy
- Keep markup clean and minimal

### Working with CSS

- Always use BEM notation: `.component__element--modifier`
- Scope all styles to the component root
- Avoid global styles or resets
- Use relative units when possible
- Prefer flexbox/grid for layout

### Working with JavaScript

- Scope queries to component container: `this.root.querySelector()`
- Use clear method and variable names
- Follow the defined lifecycle pattern
- Proper error handling
- Clean up event listeners and resources

## File Organization

Maintain the current file organization structure:

```
Hephaestus/ui/
├── components/                   # Component HTML templates
│   ├── ergon/
│   │   └── ergon-component.html  # Ergon component HTML
├── scripts/                      # JavaScript files
│   ├── component-loader.js       # Component loader
│   └── ergon/                    # Component-specific JS
│       └── ergon-component.js    # Ergon functionality
└── styles/                       # CSS stylesheets
    └── ergon/                    # Component-specific CSS
        └── ergon-component.css   # Ergon styles
```

## Key Files to Modify

### Component Loader
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/component-loader.js`

### UI Manager
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager-core.js`

### Ergon Component
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/ergon/ergon-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ergon/ergon-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/ergon/ergon-component.css`

## Getting Started

1. Verify you're on the correct branch:
   ```bash
   git branch
   # Should show sprint/Clean_Slate_051125
   ```

2. Analyze the component loader and UI manager:
   ```bash
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/component-loader.js
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ui-manager-core.js
   ```

3. Examine the Athena component for reference:
   ```bash
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/athena/athena-component.js
   ```

4. Begin implementation following the phased approach in the implementation plan

## Important Notes

1. **Ask questions if unclear**: If any part of the implementation plan is unclear, ask for clarification before proceeding
2. **Make small, incremental changes**: This makes debugging easier
3. **Test thoroughly**: Test each change before moving on
4. **Document your work**: Document any challenges, decisions, or patterns
5. **Follow the established patterns**: Consistency is crucial
6. **Maintain restraint**: Focus on reliability over features

## Documentation

Refer to these sprint documents for detailed guidance:

- [Sprint Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/SprintPlan.md)
- [Architectural Decisions](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ArchitecturalDecisions.md)
- [Implementation Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ImplementationPlan.md)