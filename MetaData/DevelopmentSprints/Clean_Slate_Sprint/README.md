# Clean Slate Sprint

## Overview

The Clean Slate Sprint focuses on rebuilding the Tekton UI component architecture with an emphasis on reliability, maintainability, and proper isolation. This sprint addresses persistent issues encountered in previous UI implementation efforts by establishing strict patterns, clear component boundaries, and methodical development procedures.

## Sprint Documents

The following documents define this sprint:

- [Sprint Plan](SprintPlan.md): Outlines the high-level goals, approach, and timeline
- [Architectural Decisions](ArchitecturalDecisions.md): Documents key architectural decisions and their rationale
- [Implementation Plan](ImplementationPlan.md): Provides detailed implementation tasks and phases
- [Clean Slate UI Implementation](CleanSlateUIImplementation.md): Documents the component architecture and implementation patterns
- [Ergon Component Migration](ErgonComponentMigration.md): Details the migration of the Ergon component to the Clean Slate architecture

## Sprint Branch

This sprint uses the branch `sprint/Clean_Slate_051125`.

## Key Principles

This sprint is guided by the following key principles:

1. **Strict Component Isolation**: Components operate only within their own container without affecting others
2. **Template-Based Development**: All components follow the same basic template and patterns
3. **Progressive Enhancement**: Core functionality is implemented and validated before adding features
4. **Clear Contracts**: Well-defined interfaces between components and the main UI
5. **Methodical Implementation**: Changes are incremental and validated at each step

## Working Guidelines for Development Sessions

For Claude Code sessions and development work during this sprint, follow these guidelines:

1. **Validate Branch First**: Always verify you're working on the correct branch before making changes
    ```bash
    git branch
    # Should show you are on sprint/Clean_Slate_051125
    ```

2. **Start Simple**: Focus on basic functionality before adding complexity
    - First make sure component loads correctly
    - Then add basic interactivity
    - Add more advanced features only after basics work

3. **Commit at Stable Points**: Create commits whenever you reach a stable point
    - Commit after component loads correctly
    - Commit after basic interactivity works
    - Commit after each feature is added

4. **Follow Established Patterns**: 
    - Use BEM naming for CSS: `.component__element--modifier`
    - Follow the lifecycle pattern in JS: `init()`, `activate()`, `cleanup()`
    - Match the HTML structure from the golden template

5. **Test Before Moving On**:
    - Verify component loads without errors
    - Check that styles apply correctly and don't leak
    - Confirm behavior matches expectations

6. **Documentation**:
    - Update documentation alongside code changes
    - Document any challenges or decisions made
    - Create examples for future reference

## Phase Checklist

### Phase 1: Foundation and Component Loader
- [x] Analyze existing component loader
- [x] Create simplified component loader
- [x] Establish golden component template
- [x] Create component contract documentation

### Phase 2: Component Implementation
- [x] Implement Athena component HTML with BEM naming
- [x] Implement Athena component CSS with BEM naming
- [x] Implement Athena component JS with container-scoped queries
- [x] Implement tab switching functionality
- [x] Implement Ergon component HTML with BEM naming
- [x] Implement Ergon component CSS with BEM naming
- [x] Implement Ergon component JS with container-scoped queries
- [x] Fix Ergon component tab switching functionality
- [ ] Implement Hermes component with Clean Slate architecture
- [ ] Create component test harness

### Phase 3: Debug Instrumentation & Validation
- [x] Implement debug-shim.js for frontend instrumentation 
- [x] Implement debug_utils.py for backend instrumentation
- [x] Add debug instrumentation to Athena component
- [x] Add debug instrumentation to Ergon component
- [x] Create debug instrumentation documentation
- [x] Create debug quick start guide
- [ ] Add debug instrumentation to Hermes component
- [x] Comprehensive component testing for Athena
- [x] Comprehensive component testing for Ergon
- [x] Update component development documentation
- [x] Create implementation guide for Clean Slate architecture
- [x] Create troubleshooting guide for debug instrumentation

## Session Handoff

When handing off between Claude Code sessions, ensure the following:

1. Create a summary of work completed
2. Document any challenges encountered
3. Specify the exact next steps
4. Highlight any decisions that need to be made
5. List any files that still need attention

## Contact

For questions or clarification during this sprint, contact Casey as the human-in-the-loop project manager.