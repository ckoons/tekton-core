# Clean Slate Sprint - Claude Code Implementation Guide

## Context

You are assisting with the Clean Slate Sprint for the Tekton project. This sprint focuses on rebuilding the UI component architecture to address persistent issues in previous implementations. The goal is to establish a reliable, standardized approach to UI components with proper isolation and clear patterns.

The project has been making excellent progress. So far, we have:
1. Implemented the Athena component with BEM naming and proper isolation
2. Implemented the Ergon component and fixed its tab switching functionality
3. Implemented the Hermes component following the same patterns
4. Created a comprehensive debug instrumentation system for both frontend and backend
5. Added debug instrumentation to the Athena, Ergon, and Hermes components

The next major task is to implement the Engram component (memory system) using the same patterns and add debug instrumentation to it.

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

### Phase 1: Foundation (Completed)

- We've established the foundation with the component loader
- Created golden component templates based on Athena
- Defined component contracts for lifecycle, events, and state
- Implemented debug instrumentation

### Phase 2: Component Implementation (In Progress)

1. **Implemented Athena component** ✅
   - Used as the reference implementation with BEM naming
   - Verified proper isolation and functionality

2. **Implemented Ergon component** ✅
   - Followed the template pattern established by Athena
   - Added tab switching and state management
   - Verified isolation from other components

3. **Implemented Hermes component** ✅
   - Followed the same template and patterns
   - Added chat functionality and proper isolation
   - Ensured visual consistency with Athena

4. **Next: Implement Engram component** ⚠️
   - Start with HTML structure following the template
   - Add CSS with BEM naming
   - Implement JS with lifecycle methods
   - Add memory-specific functionality
   - Ensure visual consistency with other components

### Phase 3: Validation and Documentation (Ongoing)

1. **Documentation updates** (continuous)
   - Document each component implementation
   - Update guides and references
   - Create troubleshooting information

2. **Testing and validation** (with each component)
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

- Always use BEM notation: `.component__element--modifier`
- Scope all styles to the component root
- Avoid global styles or resets
- Use relative units when possible
- Prefer flexbox/grid for layout
- Match heights and spacing with Athena component:
  - Header height: 50px
  - Menu bar height: 46px
  - Footer height: 70px

### Working with JavaScript

- Scope queries to component container: `document.querySelector('.componentName').querySelector()`
- Use clear method and variable names
- Follow the defined lifecycle pattern
- Implement proper error handling
- Clean up event listeners and resources
- Protect against UI Manager interference

## Key Files to Modify

### Engram Component (to implement)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/engram/engram-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/engram/engram-component.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/engram/engram-service.js`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/engram/engram-memory-service.js`

### Reference Components (already implemented)
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/athena/athena-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/ergon/ergon-component.html`
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/hermes/hermes-component.html`

### Debug Instrumentation
- `/Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/debug-shim.js`

## Getting Started

1. Verify you're on the correct branch:
   ```bash
   git branch
   # Should show sprint/Clean_Slate_051125
   ```

2. Examine the completed Hermes component for reference:
   ```bash
   cat /Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/hermes/hermes-component.html
   ```

3. Review the Engram implementation guide:
   ```bash
   cat /Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/EngramComponentImplementation.md
   ```

4. Begin implementing the Engram component following the implementation guide and the patterns from Athena, Ergon, and Hermes

5. Test the component in the Hephaestus UI by running:
   ```bash
   cd /Users/cskoons/projects/github/Tekton/Hephaestus/ui && python server/server.py
   ```

## Important Notes

1. **Ask questions if unclear**: If any part of the implementation plan is unclear, ask for clarification before proceeding
2. **Make small, incremental changes**: This makes debugging easier
3. **Test thoroughly**: Test each change before moving on
4. **Document your work**: Document any challenges, decisions, or patterns
5. **Follow the established patterns**: Consistency is crucial
6. **Maintain restraint**: Focus on reliability over features
7. **Visual consistency**: Ensure the Engram component visually matches Athena and Hermes

## Documentation

Refer to these documents for detailed guidance:

- [Sprint Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/SprintPlan.md)
- [Architectural Decisions](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ArchitecturalDecisions.md)
- [Implementation Plan](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/ImplementationPlan.md)
- [Hermes Implementation Summary](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/HermesImplementationSummary.md)
- [Engram Implementation Guide](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/Clean_Slate_Sprint/EngramComponentImplementation.md)
- [Debug Instrumentation Guide](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/DeveloperGuides/Debugging/ComponentInstrumentation.md)