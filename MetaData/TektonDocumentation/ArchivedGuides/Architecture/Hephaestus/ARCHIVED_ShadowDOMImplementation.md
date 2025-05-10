# [ARCHIVED] - This document is no longer current

> **NOTICE:** This documentation has been archived on 2025-05-10 as part of the Hephaestus UI simplification.
> Please refer to the current documentation in [Hephaestus_UI_Implementation.md](/MetaData/TektonDocumentation/DeveloperGuides/Hephaestus_UI_Implementation.md).
> Retained for historical reference only.

# Shadow DOM Implementation

**Last Updated:** May 10, 2025

## Overview

This document provides a detailed technical overview of the Shadow DOM implementation in the Hephaestus UI framework. It covers the technical aspects of Shadow DOM usage, implementation strategies, and the solutions to various challenges encountered during development.

## Table of Contents

1. [Shadow DOM Basics](#shadow-dom-basics)
2. [Implementation Details](#implementation-details)
3. [Shadow DOM Initialization](#shadow-dom-initialization)
4. [Content Injection](#content-injection)
5. [Style Handling](#style-handling)
6. [Script Execution](#script-execution)
7. [Event Handling](#event-handling)
8. [Component Communication](#component-communication)
9. [Challenges and Solutions](#challenges-and-solutions)
10. [Browser Compatibility](#browser-compatibility)

## Shadow DOM Basics

Shadow DOM provides encapsulation for DOM and CSS by creating a separate DOM tree that is attached to an element but kept separate from the main document DOM. This implementation uses Shadow DOM with the following properties:

- **Mode**: `open` for debugging and access purposes
- **Delegatesfocus**: `true` for proper focus delegation
- **Slotting**: Not used in the current implementation
- **Event Retargeting**: Modified to handle specific cases (see Event Handling)

## Implementation Details

### Component Loading Flow

The implementation follows this sequence:

1. Create a host element in the main DOM
2. Attach a shadow root to the host element
3. Add theme variables and styles to the shadow root
4. Fetch and inject component HTML into the shadow root
5. Fetch and add component-specific CSS
6. Initialize component JavaScript with shadow root context
7. Set up lifecycle management and cleanup handlers

### Core Implementation Classes

The implementation is built around these core classes:

1. **ComponentLoader**: Manages component loading and lifecycle
2. **ShadowDOMManager**: Handles Shadow DOM creation and management
3. **ComponentRegistry**: Stores component metadata and capabilities
4. **UIManager**: Controls UI state and component transitions

## Shadow DOM Initialization

The Shadow DOM is initialized with the following code:

```javascript
class ShadowDOMManager {
  createShadowRoot(hostElement, options = {}) {
    // Attach shadow root with options
    const shadowRootOptions = {
      mode: options.mode || 'open',
      delegatesFocus: options.delegatesFocus || true
    };
    
    const shadowRoot = hostElement.attachShadow(shadowRootOptions);
    
    // Add theme variables
    this.addThemeVariables(shadowRoot);
    
    // Add base styles
    if (options.addBaseStyles) {
      this.addBaseStyles(shadowRoot);
    }
    
    return shadowRoot;
  }
  
  addThemeVariables(shadowRoot) {
    const themeStyle = document.createElement('style');
    
    // Get all CSS variables from document root
    const rootStyles = getComputedStyle(document.documentElement);
    let cssVars = '';
    
    // Extract CSS variables with fallbacks
    for (let i = 0; i < rootStyles.length; i++) {
      const prop = rootStyles[i];
      if (prop.startsWith('--')) {
        const value = rootStyles.getPropertyValue(prop).trim();
        cssVars += `${prop}: var(${prop}, ${value || 'initial'});\n`;
      }
    }
    
    // Create style with all CSS variables
    themeStyle.textContent = `:host {\n${cssVars}}\n`;
    shadowRoot.appendChild(themeStyle);
    
    return themeStyle;
  }
  
  // Add MutationObserver for theme changes
  observeThemeChanges(shadowRoot) {
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (mutation.attributeName === 'data-theme') {
          const newTheme = document.documentElement.dataset.theme;
          shadowRoot.host.dataset.theme = newTheme;
          
          // Dispatch theme change event within shadow root
          shadowRoot.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: newTheme }
          }));
        }
      }
    });
    
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });
    
    return observer;
  }
}
```

## Content Injection

Component HTML is fetched and injected into the shadow root:

```javascript
async loadComponentHTML(shadowRoot, componentId) {
  try {
    // Fetch component HTML
    const response = await fetch(`/components/${componentId}/${componentId}-component.html`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch HTML: ${response.status}`);
    }
    
    const html = await response.text();
    
    // Create container for component content
    const container = document.createElement('div');
    container.className = `${componentId}-container`;
    container.innerHTML = html;
    
    // Add container to shadow root
    shadowRoot.appendChild(container);
    
    return container;
  } catch (error) {
    console.error('Error loading component HTML:', error);
    
    // Create error display
    const errorContainer = document.createElement('div');
    errorContainer.className = 'component-error';
    errorContainer.innerHTML = `
      <h3>Error Loading Component</h3>
      <p>${error.message}</p>
    `;
    
    shadowRoot.appendChild(errorContainer);
    throw error;
  }
}
```

## Style Handling

Component-specific styles are loaded and scoped to the shadow root:

```javascript
async loadComponentStyles(shadowRoot, componentId) {
  try {
    // Fetch component CSS
    const response = await fetch(`/styles/${componentId}/${componentId}-component.css`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch CSS: ${response.status}`);
    }
    
    const css = await response.text();
    
    // Create style element
    const styleElement = document.createElement('style');
    styleElement.textContent = css;
    
    // Add style to shadow root
    shadowRoot.appendChild(styleElement);
    
    return styleElement;
  } catch (error) {
    console.error('Error loading component styles:', error);
    
    // Create minimal fallback styles
    const fallbackStyle = document.createElement('style');
    fallbackStyle.textContent = `
      .${componentId}-container {
        padding: var(--spacing-md, 16px);
        color: var(--text-primary, #f0f0f0);
      }
      
      .component-error {
        color: var(--color-error, red);
        padding: var(--spacing-md, 16px);
      }
    `;
    
    shadowRoot.appendChild(fallbackStyle);
    throw error;
  }
}
```

## Script Execution

Component JavaScript is loaded and executed within a scoped context:

```javascript
async loadComponentScript(shadowRoot, componentId) {
  try {
    // Fetch component JS
    const response = await fetch(`/scripts/${componentId}/${componentId}-component.js`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch script: ${response.status}`);
    }
    
    const scriptText = await response.text();
    
    // Create component context object
    const component = this.createComponentContext(shadowRoot, componentId);
    
    // Execute script with component context
    const scriptFunction = new Function('component', scriptText);
    scriptFunction(component);
    
    return component;
  } catch (error) {
    console.error('Error loading component script:', error);
    throw error;
  }
}

createComponentContext(shadowRoot, componentId) {
  // Create cleanup registry
  const cleanupHandlers = [];
  
  // Create component context
  const component = {
    id: componentId,
    root: shadowRoot,
    
    // DOM query methods
    $(selector) {
      return shadowRoot.querySelector(selector);
    },
    
    $$(selector) {
      return [...shadowRoot.querySelectorAll(selector)];
    },
    
    // Event handling
    on(eventType, selector, handler) {
      const listener = (event) => {
        const elements = shadowRoot.querySelectorAll(selector);
        const element = event.target.closest(selector);
        
        if (element && [...elements].includes(element)) {
          handler.call(element, event);
        }
      };
      
      shadowRoot.addEventListener(eventType, listener);
      
      // Store for cleanup
      cleanupHandlers.push(() => {
        shadowRoot.removeEventListener(eventType, listener);
      });
      
      return component; // For chaining
    },
    
    // Custom event dispatch
    dispatch(eventName, detail = {}) {
      // Add component ID to detail
      const eventDetail = { ...detail, componentId };
      
      // Create event
      const event = new CustomEvent(eventName, {
        bubbles: true,
        composed: true,
        detail: eventDetail
      });
      
      // Dispatch from shadow root
      shadowRoot.dispatchEvent(event);
      
      return component; // For chaining
    },
    
    // Cleanup registration
    registerCleanup(handler) {
      if (typeof handler === 'function') {
        cleanupHandlers.push(handler);
      }
      
      return component; // For chaining
    },
    
    // Execute all cleanup handlers
    cleanup() {
      cleanupHandlers.forEach(handler => {
        try {
          handler();
        } catch (error) {
          console.error('Error in cleanup handler:', error);
        }
      });
      
      // Clear handlers
      cleanupHandlers.length = 0;
    },
    
    // Add utilities
    utils: this.getComponentUtils(shadowRoot, componentId)
  };
  
  return component;
}
```

## Event Handling

The implementation uses a combination of event delegation and custom events:

### Event Delegation

```javascript
// Implementation of event delegation
on(eventType, selector, handler) {
  const listener = (event) => {
    const elements = shadowRoot.querySelectorAll(selector);
    const element = event.target.closest(selector);
    
    if (element && [...elements].includes(element)) {
      handler.call(element, event);
    }
  };
  
  shadowRoot.addEventListener(eventType, listener);
  
  // Store for cleanup
  cleanupHandlers.push(() => {
    shadowRoot.removeEventListener(eventType, listener);
  });
  
  return component; // For chaining
}
```

### Custom Events

```javascript
// Implementation of custom event dispatch
dispatch(eventName, detail = {}) {
  // Add component ID to detail
  const eventDetail = { ...detail, componentId };
  
  // Create event
  const event = new CustomEvent(eventName, {
    bubbles: true,
    composed: true, // Allow event to cross shadow boundary
    detail: eventDetail
  });
  
  // Dispatch from shadow root
  shadowRoot.dispatchEvent(event);
  
  return component; // For chaining
}
```

## Component Communication

Components communicate through a combination of:

1. **Custom Events**: For general notifications and state changes
2. **Service Objects**: For sharing data and functionality
3. **Global State**: For application-wide state management

### Service Registration

```javascript
class ServiceRegistry {
  constructor() {
    this.services = {};
  }
  
  registerService(serviceId, service) {
    this.services[serviceId] = service;
    
    // Dispatch service registration event
    document.dispatchEvent(new CustomEvent('serviceRegistered', {
      detail: { serviceId, service }
    }));
    
    return service;
  }
  
  getService(serviceId) {
    return this.services[serviceId] || null;
  }
  
  removeService(serviceId) {
    if (this.services[serviceId]) {
      const service = this.services[serviceId];
      
      // Call disconnect if available
      if (typeof service.disconnect === 'function') {
        service.disconnect();
      }
      
      delete this.services[serviceId];
      
      // Dispatch service removed event
      document.dispatchEvent(new CustomEvent('serviceRemoved', {
        detail: { serviceId }
      }));
    }
  }
}
```

## Challenges and Solutions

### 1. Event Handling Across Shadow Boundaries

**Challenge**: Events do not naturally cross shadow boundaries without special handling.

**Solution**: Used `{ bubbles: true, composed: true }` for events that need to cross boundaries.

### 2. Theme Variable Propagation

**Challenge**: CSS variables do not automatically inherit across shadow boundaries.

**Solution**: Explicitly copied all CSS variables from root to shadow root with fallback values.

### 3. Keyboard Focus Management

**Challenge**: Focus can behave unexpectedly with shadow DOM.

**Solution**: Used `delegatesFocus: true` and explicit focus management for complex components.

### 4. Component Initialization Timing

**Challenge**: Components need proper loading sequence and initialization.

**Solution**: Implemented Promise-based loading sequence with proper error handling.

### 5. Terminal Component Integration

**Challenge**: Terminal requires direct keyboard input and complex rendering.

**Solution**: Implemented specialized event handling and rendering within shadow DOM context.

### 6. Clipboard Access

**Challenge**: Clipboard operations are restricted within shadow DOM.

**Solution**: Created special clipboard helper that works across shadow boundaries.

### 7. WebSocket Lifecycle Management

**Challenge**: WebSocket connections need proper cleanup when components are unloaded.

**Solution**: Implemented lifecycle management for connections with proper reconnection handling.

## Browser Compatibility

The Shadow DOM implementation has been tested and works in:

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Older browsers would require a polyfill, but this is not currently implemented as the target environment already supports Shadow DOM.

## See Also

- [Component Isolation Architecture](../ComponentIsolationArchitecture.md) - Overall isolation architecture
- [UI Component Communication](../UIComponentCommunication.md) - Event-based communication
- [Shadow DOM Best Practices](../../DeveloperGuides/ShadowDOMBestPractices.md) - Best practices for Shadow DOM usage