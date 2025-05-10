# [ARCHIVED] - This document is no longer current

> **NOTICE:** This documentation has been archived on 2025-05-10 as part of the Hephaestus UI simplification.
> Please refer to the current documentation in [Hephaestus_UI_Implementation.md](/MetaData/TektonDocumentation/DeveloperGuides/Hephaestus_UI_Implementation.md).
> Retained for historical reference only.

# Component Isolation Architecture

**Last Updated:** May 10, 2025

## Overview

This document outlines the architecture for component isolation in the Hephaestus UI framework. The implementation uses Shadow DOM to create strong boundaries between components, preventing style bleeding, DOM duplication, and event handler collisions while maintaining a consistent theming and interaction model.

## Table of Contents

1. [Architecture Principles](#architecture-principles)
2. [Shadow DOM Implementation](#shadow-dom-implementation)
3. [Component Structure](#component-structure)
4. [Integration with UI Manager](#integration-with-ui-manager)
5. [Theming Across Shadow Boundaries](#theming-across-shadow-boundaries)
6. [Handling Events](#handling-events)
7. [Component Lifecycle Management](#component-lifecycle-management)
8. [Implementation Challenges](#implementation-challenges)

## Architecture Principles

The component isolation architecture is built on the following principles:

1. **Strong Isolation**: Each component should operate within its own boundary without affecting other components.
2. **Consistent Theming**: Theme variables must propagate across component boundaries.
3. **Efficient Communication**: Components need standardized methods to communicate with each other.
4. **Graceful Degradation**: Components should handle errors and missing dependencies gracefully.
5. **Resource Management**: Components should clean up all resources when unmounted.

## Shadow DOM Implementation

The architecture uses Shadow DOM as the primary isolation mechanism with the following structure:

1. **Host Element**: The container that holds the shadow root
2. **Shadow Root**: The boundary for isolation (mode: 'open')
3. **Component Container**: The root element within the shadow DOM
4. **Component Structure**: The actual HTML structure of the component

```javascript
function loadComponentInShadowDOM(componentId, containerElement) {
  // Clear container
  containerElement.innerHTML = '';
  
  // Create host element
  const host = document.createElement('div');
  host.id = `${componentId}-host`;
  containerElement.appendChild(host);
  
  // Create shadow root
  const shadowRoot = host.attachShadow({ mode: 'open' });
  
  // Return shadow root for content insertion
  return shadowRoot;
}
```

## Component Structure

Each component follows a standardized file and object structure:

### File Structure
```
ui/
├── components/
│   └── [component-name]/
│       └── [component-name]-component.html
├── styles/
│   └── [component-name]/
│       └── [component-name]-component.css
└── scripts/
    └── [component-name]/
        ├── [component-name]-service.js (optional)
        └── [component-name]-component.js
```

### Object Structure

Each component receives a component context object that provides:

1. **Root Access**: Reference to the shadow root
2. **DOM Utilities**: Scoped query selectors and DOM manipulation
3. **Event Delegation**: Methods for efficient event handling
4. **Lifecycle Management**: Hooks for initialization and cleanup
5. **Service Registry**: Access to shared services
6. **Utility Methods**: Common utilities for UI operations

```javascript
const component = {
  id: componentId,
  root: shadowRoot,
  
  // Scoped querySelector that only searches within component
  $(selector) {
    return this.root.querySelector(selector);
  },
  
  // Scoped event delegation
  on(eventType, selector, handler) {
    this.root.addEventListener(eventType, (event) => {
      const elements = this.root.querySelectorAll(selector);
      const element = event.target.closest(selector);
      if (element && [...elements].includes(element)) {
        handler.call(element, event);
      }
    });
  },
  
  // Lifecycle hooks
  registerCleanup(cleanupFunction) {
    // Store cleanup function for later execution
  },
  
  // Utility methods
  utils: {
    dom: { /* DOM manipulation utilities */ },
    notifications: { /* Notification system */ },
    loading: { /* Loading indicators */ },
    lifecycle: { /* Lifecycle management */ }
  }
};
```

## Integration with UI Manager

The UI Manager is responsible for loading components using the Component Loader:

```javascript
async function loadComponent(componentId) {
  // Get the panel element
  const targetPanel = document.getElementById('content-panel');
  
  // Load component using the unified loader
  const component = await componentLoader.loadComponent(componentId, targetPanel);
  
  // Activate the panel if successful
  if (component) {
    uiManager.activatePanel('content');
  }
  
  return component;
}
```

The Component Loader manages component lifecycle:

1. **Loading**: Fetching HTML, CSS, and JS resources
2. **Initialization**: Creating the shadow root and component context
3. **Theming**: Applying theme variables to the shadow root
4. **Cleanup**: Executing cleanup handlers when component is unloaded
5. **Error Handling**: Displaying error messages when loading fails

## Theming Across Shadow Boundaries

Theme variables propagate across shadow boundaries through CSS custom properties:

```javascript
function addThemeStylesToShadowRoot(shadowRoot) {
  const themeStyle = document.createElement('style');
  themeStyle.textContent = `
    :host {
      /* Import all theme variables from parent */
      --bg-primary: var(--bg-primary, #1e1e1e);
      --bg-secondary: var(--bg-secondary, #252525);
      --text-primary: var(--text-primary, #f0f0f0);
      /* Add all other theme variables... */
    }
  `;
  shadowRoot.prepend(themeStyle);
}
```

Theme changes are observed and propagated:

```javascript
function setupThemeObserver(shadowRoot) {
  // Create MutationObserver to watch for theme attribute changes
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.attributeName === 'data-theme') {
        // Theme changed, update component theme
        const newTheme = document.documentElement.dataset.theme;
        shadowRoot.host.dataset.theme = newTheme;
      }
    });
  });
  
  // Start observing
  observer.observe(document.documentElement, { 
    attributes: true,
    attributeFilter: ['data-theme']
  });
  
  // Return cleanup function
  return () => observer.disconnect();
}
```

## Handling Events

Events are handled with several approaches:

1. **Internal Events**: Scoped to component shadow root
2. **Delegated Events**: Using component.on() for efficient delegation
3. **Custom Events**: For communication between components
4. **Global Events**: Used sparingly for system-wide notifications

Example of custom event dispatch for component communication:

```javascript
// Dispatch custom event
component.dispatch('settingsChanged', {
  theme: 'dark',
  showGreekNames: true
});

// Listen for custom events
document.addEventListener('settingsChanged', (event) => {
  if (event.detail.componentId !== component.id) {
    // Handle event from another component
    applySettings(event.detail);
  }
});
```

## Component Lifecycle Management

Components follow a standardized lifecycle:

1. **Initialization**: Setting up services, event listeners, and initial state
2. **Mounting**: Adding component to the DOM and initializing view
3. **Updates**: Responding to data changes and user interaction
4. **Unmounting**: Cleaning up resources and event listeners

Example of component cleanup registration:

```javascript
// Register the main cleanup function
component.registerCleanup(function() {
  // Clean up resources
  disconnectFromServices();
  cancelPendingRequests();
  releaseReferences();
});
```

## Implementation Challenges

Challenges encountered and solutions implemented:

1. **Shadow DOM Browser Support**: Implemented feature detection and fallbacks
2. **Theme Propagation**: Used CSS variables with fallback values
3. **Event Delegation**: Created specialized delegation system for shadow DOM
4. **Component Communication**: Implemented custom events with proper bubbling
5. **Service Sharing**: Created global service registry with proper lifecycle management
6. **Terminal Integration**: Custom solutions for keyboard events and terminal rendering
7. **Performance Optimization**: Implemented lazy loading and batched updates

The Shadow DOM isolation approach has successfully addressed the original problems of style bleeding, DOM duplication, and event handler collisions, creating a maintainable and scalable component architecture.

## See Also

- [UI Component Communication](./UIComponentCommunication.md) - Event-based communication between components
- [Component Integration Patterns](./ComponentIntegrationPatterns.md) - Standardized patterns for component integration
- [State Management Architecture](./StateManagementArchitecture.md) - State management framework