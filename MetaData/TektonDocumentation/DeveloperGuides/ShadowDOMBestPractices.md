# Shadow DOM Best Practices

**Last Updated:** May 10, 2025

## Overview

This document outlines best practices and lessons learned from implementing Shadow DOM for component isolation in the Hephaestus UI framework. It provides guidance for developers working with Shadow DOM to ensure proper encapsulation, performance, and maintainability.

## Table of Contents

1. [Shadow DOM Fundamentals](#shadow-dom-fundamentals)
2. [Component Initialization](#component-initialization)
3. [Style Management](#style-management)
4. [DOM Manipulation](#dom-manipulation)
5. [Event Handling](#event-handling)
6. [Cross-Component Communication](#cross-component-communication)
7. [Performance Considerations](#performance-considerations)
8. [Accessibility](#accessibility)
9. [Testing Shadow DOM Components](#testing-shadow-dom-components)
10. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)

## Shadow DOM Fundamentals

### Shadow DOM Mode

Always use `open` mode for Shadow DOM in the Hephaestus framework:

```javascript
// Create shadow root with open mode
const shadowRoot = element.attachShadow({ mode: 'open' });
```

Using `open` mode allows:
- Easier debugging of components
- Better integration with browser dev tools
- Access to the shadow root via the `shadowRoot` property
- Simplified testing

### Shadow DOM Options

When creating a Shadow DOM, consider these options:

```javascript
const shadowRoot = element.attachShadow({
  mode: 'open',                 // 'open' or 'closed'
  delegatesFocus: true,         // Improves focus delegation
  slotAssignment: 'named'       // 'named' or 'manual'
});
```

- **delegatesFocus**: Set to `true` to improve keyboard navigation and focus handling
- **slotAssignment**: Use `'named'` for most cases (using `<slot>` elements)

### Shadow DOM Structure

Follow this structure for consistency:

```
Host Element
└── Shadow Root
    ├── Style Elements (theme variables, component styles)
    ├── Component Container (root element for component)
    │   ├── Component Header
    │   ├── Component Content
    │   └── Component Footer
    └── Component-specific Elements
```

## Component Initialization

### Shadow DOM Creation

Use a consistent pattern for creating the Shadow DOM:

```javascript
/**
 * Create shadow DOM for a component
 */
function createShadowDOM(host, options = {}) {
  // Create shadow root
  const shadowRoot = host.attachShadow({
    mode: 'open',
    delegatesFocus: options.delegatesFocus !== false
  });
  
  // Add theme variables
  addThemeVariables(shadowRoot);
  
  // Create component container
  const container = document.createElement('div');
  container.className = `${options.componentId}-container`;
  shadowRoot.appendChild(container);
  
  return {
    root: shadowRoot,
    container
  };
}
```

### Content Initialization

Separate DOM creation from data population:

```javascript
/**
 * Initialize component content
 */
function initializeContent(container, data) {
  // Create static DOM structure first
  createComponentStructure(container);
  
  // Then populate with data
  populateComponentData(container, data);
}

/**
 * Create component structure
 */
function createComponentStructure(container) {
  // Create header
  const header = document.createElement('header');
  header.className = 'component-header';
  container.appendChild(header);
  
  // Create content area
  const content = document.createElement('main');
  content.className = 'component-content';
  container.appendChild(content);
  
  // Create footer
  const footer = document.createElement('footer');
  footer.className = 'component-footer';
  container.appendChild(footer);
}
```

### Component Context

Provide a consistent component context object:

```javascript
/**
 * Create component context
 */
function createComponentContext(shadowRoot, componentId) {
  // Cleanup registry
  const cleanupTasks = [];
  
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
      // Implement event delegation
      // (see Event Handling section)
    },
    
    // Dispatch custom events
    dispatch(eventName, detail) {
      // Create and dispatch event
      // (see Cross-Component Communication section)
    },
    
    // Lifecycle management
    registerCleanup(task) {
      if (typeof task === 'function') {
        cleanupTasks.push(task);
      }
      return component;
    },
    
    // Execute cleanup tasks
    cleanup() {
      cleanupTasks.forEach(task => {
        try {
          task();
        } catch (error) {
          console.error('Error in cleanup task:', error);
        }
      });
      
      cleanupTasks.length = 0;
    },
    
    // Component utilities
    utils: {
      dom: createDomUtils(shadowRoot),
      notifications: createNotificationUtils(shadowRoot, componentId),
      loading: createLoadingUtils(shadowRoot, componentId),
      lifecycle: createLifecycleUtils(shadowRoot, componentId, cleanupTasks)
    }
  };
  
  return component;
}
```

## Style Management

### Theme Variables

Properly propagate theme variables to Shadow DOM:

```javascript
/**
 * Add theme variables to Shadow DOM
 */
function addThemeVariables(shadowRoot) {
  // Create style element for theme variables
  const themeStyle = document.createElement('style');
  
  // Get computed styles from document root
  const rootStyles = getComputedStyle(document.documentElement);
  
  // Build CSS variables with fallbacks
  let cssVars = '';
  
  // Extract CSS custom properties (variables)
  for (let i = 0; i < rootStyles.length; i++) {
    const prop = rootStyles[i];
    if (prop.startsWith('--')) {
      const value = rootStyles.getPropertyValue(prop).trim();
      cssVars += `${prop}: var(${prop}, ${value || 'initial'});\n`;
    }
  }
  
  // Set theme style content
  themeStyle.textContent = `:host {\n${cssVars}}\n`;
  
  // Add as first child for correct cascade
  shadowRoot.insertBefore(themeStyle, shadowRoot.firstChild);
  
  return themeStyle;
}
```

### Style Isolation

Keep styles isolated with proper selectors:

```css
/* Use :host for styling the component container */
:host {
  display: block;
  margin: var(--spacing-md, 1rem);
}

/* Use :host() for state variations */
:host([data-theme="dark"]) {
  --component-bg-color: var(--dark-bg-color, #1e1e1e);
}

/* Avoid styling elements directly */
p { color: red; } /* BAD: Too broad */

/* Instead, use component class selectors */
.component-text { color: red; } /* GOOD: Properly scoped */
```

### Component-Specific Classes

Use component-specific prefixes for class names:

```html
<!-- BAD: Generic class names -->
<div class="container">
  <div class="header">
    <h2 class="title">Component Title</h2>
  </div>
</div>

<!-- GOOD: Component-specific BEM classes -->
<div class="component-container">
  <div class="component-header">
    <h2 class="component-header__title">Component Title</h2>
  </div>
</div>
```

### Style Loading

Load styles properly into Shadow DOM:

```javascript
/**
 * Load component styles
 */
async function loadComponentStyles(shadowRoot, componentId) {
  try {
    // Fetch CSS file
    const response = await fetch(`/styles/${componentId}-component.css`);
    
    if (!response.ok) {
      throw new Error(`Failed to load styles: ${response.status}`);
    }
    
    const css = await response.text();
    
    // Create style element
    const styleElement = document.createElement('style');
    styleElement.textContent = css;
    
    // Add to shadow root
    shadowRoot.appendChild(styleElement);
    
    return styleElement;
  } catch (error) {
    console.error('Error loading component styles:', error);
    
    // Add basic fallback styles
    const fallbackStyle = document.createElement('style');
    fallbackStyle.textContent = `
      .${componentId}-container {
        padding: var(--spacing-md, 16px);
      }
    `;
    shadowRoot.appendChild(fallbackStyle);
    
    throw error;
  }
}
```

## DOM Manipulation

### Querying Elements

Use the component context for element queries:

```javascript
// BAD: Using document.querySelector
const header = document.querySelector('.component-header');

// GOOD: Using component's scoped query methods
const header = component.$('.component-header');
const buttons = component.$$('.component-button');
```

### Creating Elements

Use helper methods to create elements:

```javascript
// Component DOM utilities
function createDomUtils(shadowRoot) {
  return {
    // Create element with attributes and properties
    createElement(tagName, props = {}) {
      const element = document.createElement(tagName);
      
      // Apply properties and attributes
      Object.entries(props).forEach(([key, value]) => {
        if (key === 'className') {
          element.className = value;
        } else if (key === 'textContent') {
          element.textContent = value;
        } else if (key === 'innerHTML') {
          element.innerHTML = value;
        } else if (key === 'dataset') {
          Object.entries(value).forEach(([dataKey, dataValue]) => {
            element.dataset[dataKey] = dataValue;
          });
        } else if (key === 'style' && typeof value === 'object') {
          Object.entries(value).forEach(([styleKey, styleValue]) => {
            element.style[styleKey] = styleValue;
          });
        } else if (key.startsWith('on') && typeof value === 'function') {
          const eventName = key.slice(2).toLowerCase();
          element.addEventListener(eventName, value);
        } else {
          element.setAttribute(key, value);
        }
      });
      
      return element;
    },
    
    // Append multiple children to a parent
    appendChildren(parent, children) {
      children.forEach(child => parent.appendChild(child));
      return parent;
    },
    
    // Remove all children from an element
    removeAllChildren(element) {
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }
      return element;
    }
  };
}
```

### Example Usage

```javascript
// Create a card element
const card = component.utils.dom.createElement('div', {
  className: 'component-card',
  dataset: {
    id: item.id,
    type: item.type
  }
});

// Create card title
const title = component.utils.dom.createElement('h3', {
  className: 'component-card__title',
  textContent: item.title
});

// Create card description
const description = component.utils.dom.createElement('p', {
  className: 'component-card__description',
  textContent: item.description
});

// Add to card
component.utils.dom.appendChildren(card, [title, description]);

// Add to container
component.$('.component-card-container').appendChild(card);
```

## Event Handling

### Event Delegation

Use event delegation for efficient event handling:

```javascript
/**
 * Implement event delegation
 */
function on(eventType, selector, handler) {
  const delegationHandler = function(event) {
    // Find the matching elements
    const elements = this.root.querySelectorAll(selector);
    
    // Check if the event target matches the selector
    const element = event.target.closest(selector);
    
    // Call handler if element matches and is in our shadow root
    if (element && [...elements].includes(element)) {
      // Call with element as 'this' and pass event
      handler.call(element, event);
    }
  }.bind(component);
  
  // Add event listener to shadow root
  shadowRoot.addEventListener(eventType, delegationHandler);
  
  // Store for cleanup
  const cleanup = () => {
    shadowRoot.removeEventListener(eventType, delegationHandler);
  };
  
  component.registerCleanup(cleanup);
  
  return component;
}
```

### Focus Management

Handle focus properly within the Shadow DOM:

```javascript
/**
 * Focus first focusable element within a container
 */
function focusFirstElement(container) {
  // Find all focusable elements
  const focusableElements = container.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  // Focus the first one if it exists
  if (focusableElements.length > 0) {
    focusableElements[0].focus();
    return true;
  }
  
  return false;
}
```

### Keyboard Navigation

Implement proper keyboard navigation:

```javascript
/**
 * Set up tab navigation
 */
function setupTabNavigation(component) {
  // Get all tab buttons
  const tabButtons = component.$$('.component-tabs__button');
  
  // Set up keyboard navigation
  tabButtons.forEach((button, index) => {
    button.addEventListener('keydown', (event) => {
      // Handle arrow navigation
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
        event.preventDefault();
        const nextIndex = (index + 1) % tabButtons.length;
        tabButtons[nextIndex].focus();
        tabButtons[nextIndex].click();
      } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
        event.preventDefault();
        const prevIndex = (index - 1 + tabButtons.length) % tabButtons.length;
        tabButtons[prevIndex].focus();
        tabButtons[prevIndex].click();
      }
    });
  });
}
```

## Cross-Component Communication

### Custom Events

Dispatch custom events for component communication:

```javascript
/**
 * Dispatch a custom event
 */
function dispatchCustomEvent(eventName, detail = {}) {
  // Add component ID to detail
  const eventDetail = {
    ...detail,
    componentId: component.id
  };
  
  // Create custom event
  const event = new CustomEvent(eventName, {
    bubbles: true,      // Allow event to bubble up
    composed: true,     // Allow event to cross shadow DOM boundary
    detail: eventDetail // Event data
  });
  
  // Dispatch from shadow root
  shadowRoot.dispatchEvent(event);
  
  return component; // For chaining
}
```

### Event Listening

Listen for events from other components:

```javascript
/**
 * Listen for custom events from other components
 */
function listenForComponentEvents() {
  // Listen for a specific event
  document.addEventListener('componentStateChanged', (event) => {
    // Ignore events from this component
    if (event.detail.componentId === component.id) {
      return;
    }
    
    // Handle event from another component
    console.log('State changed in component:', event.detail.componentId);
    console.log('New state:', event.detail.state);
    
    // Update this component based on the event
    handleExternalStateChange(event.detail);
  });
}
```

### Service Communication

Use shared service objects for complex data exchange:

```javascript
/**
 * Create a service for cross-component communication
 */
class SharedDataService extends EventTarget {
  constructor() {
    super();
    this.data = {};
  }
  
  setData(key, value) {
    this.data[key] = value;
    
    // Notify listeners
    this.dispatchEvent(new CustomEvent('dataChanged', {
      detail: { key, value, previousValue: this.data[key] }
    }));
  }
  
  getData(key, defaultValue = null) {
    return key in this.data ? this.data[key] : defaultValue;
  }
}

// Register globally
window.tektonUI.services.sharedData = new SharedDataService();

// Use in component
component.utils.lifecycle.registerEventHandler(
  window.tektonUI.services.sharedData,
  'dataChanged',
  event => {
    if (event.detail.key === 'theme') {
      updateTheme(event.detail.value);
    }
  }
);
```

## Performance Considerations

### DOM Updates

Batch DOM updates for better performance:

```javascript
/**
 * Update list with efficient DOM operations
 */
function updateList(items) {
  // Create document fragment for batching
  const fragment = document.createDocumentFragment();
  
  // Build all items
  items.forEach(item => {
    const element = createListItem(item);
    fragment.appendChild(element);
  });
  
  // Single DOM update
  const list = component.$('.component-list');
  component.utils.dom.removeAllChildren(list);
  list.appendChild(fragment);
}
```

### Style Operations

Minimize style recalculations:

```javascript
/**
 * Update multiple styles efficiently
 */
function updateElementStyles(element, styles) {
  // Batch style changes
  requestAnimationFrame(() => {
    Object.entries(styles).forEach(([property, value]) => {
      element.style[property] = value;
    });
  });
}
```

### Event Handling

Use event delegation instead of multiple listeners:

```javascript
// BAD: Adding listeners to each button
component.$$('.component-button').forEach(button => {
  button.addEventListener('click', handleButtonClick);
});

// GOOD: Using event delegation
component.on('click', '.component-button', handleButtonClick);
```

### Shadow DOM Creation

Create Shadow DOM elements efficiently:

```javascript
/**
 * Create component content efficiently
 */
function createContent(data) {
  // Create HTML string for batch insertion
  const html = `
    <div class="component-header">
      <h2 class="component-header__title">${data.title}</h2>
    </div>
    <div class="component-content">
      ${data.items.map(item => `
        <div class="component-item" data-id="${item.id}">
          <h3 class="component-item__title">${item.name}</h3>
          <p class="component-item__description">${item.description}</p>
        </div>
      `).join('')}
    </div>
  `;
  
  // Set innerHTML once
  component.$('.component-container').innerHTML = html;
  
  // Add event handlers after DOM is created
  setupEventHandlers();
}
```

## Accessibility

### Focus Management

Ensure proper focus management:

```javascript
/**
 * Set up focus trap for modals
 */
function setupFocusTrap(container) {
  // Get all focusable elements
  const focusable = container.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  if (focusable.length === 0) return;
  
  const firstFocusable = focusable[0];
  const lastFocusable = focusable[focusable.length - 1];
  
  // Focus first element
  firstFocusable.focus();
  
  // Handle tab key to create a focus loop
  container.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
      // Shift + Tab on first element should go to last element
      if (e.shiftKey && document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      } 
      // Tab on last element should go to first element
      else if (!e.shiftKey && document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  });
}
```

### ARIA Attributes

Use proper ARIA attributes:

```javascript
/**
 * Create accessible tab interface
 */
function createAccessibleTabs(tabContainer, contentContainer) {
  // Set up ARIA attributes for tabs
  tabContainer.setAttribute('role', 'tablist');
  
  // Get tabs and panels
  const tabs = [...tabContainer.querySelectorAll('.component-tab')];
  const panels = [...contentContainer.querySelectorAll('.component-tab-panel')];
  
  // Set up each tab
  tabs.forEach((tab, index) => {
    const panel = panels[index];
    
    // Generate IDs if needed
    const tabId = tab.id || `tab-${component.id}-${index}`;
    const panelId = panel.id || `panel-${component.id}-${index}`;
    
    // Set IDs if not already set
    tab.id = tabId;
    panel.id = panelId;
    
    // Set up tab
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-selected', index === 0 ? 'true' : 'false');
    tab.setAttribute('aria-controls', panelId);
    tab.setAttribute('tabindex', index === 0 ? '0' : '-1');
    
    // Set up panel
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', tabId);
    panel.setAttribute('tabindex', '0');
    panel.hidden = index !== 0;
  });
}
```

### Screen Reader Support

Ensure proper screen reader support:

```javascript
/**
 * Create loading indicator with screen reader support
 */
function showLoadingIndicator(message) {
  const loadingElement = component.utils.dom.createElement('div', {
    className: 'component-loading',
    role: 'status',
    'aria-live': 'polite'
  });
  
  // Add loading icon
  const spinnerElement = component.utils.dom.createElement('div', {
    className: 'component-loading__spinner',
    'aria-hidden': 'true'
  });
  
  // Add text message for screen readers
  const messageElement = component.utils.dom.createElement('p', {
    className: 'component-loading__message',
    textContent: message || 'Loading...'
  });
  
  // Assemble loading indicator
  component.utils.dom.appendChildren(loadingElement, [
    spinnerElement,
    messageElement
  ]);
  
  // Add to component
  component.$('.component-container').appendChild(loadingElement);
  
  // Return function to hide loading indicator
  return () => {
    if (loadingElement.parentNode) {
      loadingElement.parentNode.removeChild(loadingElement);
    }
  };
}
```

## Testing Shadow DOM Components

### Test Component Creation

Test Shadow DOM component creation:

```javascript
describe('Component Creation', () => {
  let host, shadowRoot, component;
  
  beforeEach(() => {
    // Create host element
    host = document.createElement('div');
    document.body.appendChild(host);
    
    // Create shadow root
    shadowRoot = host.attachShadow({ mode: 'open' });
    
    // Create component context
    component = createComponentContext(shadowRoot, 'test');
    
    // Initialize component
    initComponent(component);
  });
  
  afterEach(() => {
    // Clean up
    if (component && component.cleanup) {
      component.cleanup();
    }
    
    if (host && host.parentNode) {
      host.parentNode.removeChild(host);
    }
    
    host = null;
    shadowRoot = null;
    component = null;
  });
  
  test('should create component structure', () => {
    // Check if container exists
    const container = shadowRoot.querySelector('.test-container');
    expect(container).not.toBeNull();
    
    // Check for header
    const header = shadowRoot.querySelector('.test-header');
    expect(header).not.toBeNull();
    
    // Check for content
    const content = shadowRoot.querySelector('.test-content');
    expect(content).not.toBeNull();
  });
});
```

### Test Event Handling

Test event handling in Shadow DOM:

```javascript
test('should handle button click', () => {
  // Create spy function
  const handleClick = jest.fn();
  
  // Add event listener
  component.on('click', '.test-button', handleClick);
  
  // Get button
  const button = shadowRoot.querySelector('.test-button');
  expect(button).not.toBeNull();
  
  // Simulate click
  button.click();
  
  // Check if handler was called
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

### Test Custom Events

Test custom event dispatch and handling:

```javascript
test('should dispatch custom event', () => {
  // Create spy function
  const handleEvent = jest.fn();
  
  // Listen for event
  document.addEventListener('testEvent', handleEvent);
  
  // Dispatch event
  component.dispatch('testEvent', { foo: 'bar' });
  
  // Check if handler was called with correct data
  expect(handleEvent).toHaveBeenCalledTimes(1);
  expect(handleEvent.mock.calls[0][0].detail).toMatchObject({
    foo: 'bar',
    componentId: 'test'
  });
  
  // Cleanup
  document.removeEventListener('testEvent', handleEvent);
});
```

## Common Pitfalls and Solutions

### Styling Issues

**Pitfall**: Styles not applying within Shadow DOM.

**Solution**: 
- Ensure styles are added to Shadow DOM, not the main document
- Use component-specific selectors
- Propagate CSS variables from root to Shadow DOM
- Check for specificity issues within your selectors

```javascript
// Add styles to shadow DOM, not document head
const styleElement = document.createElement('style');
styleElement.textContent = css;
shadowRoot.appendChild(styleElement);
```

### Event Bubbling

**Pitfall**: Events not crossing Shadow DOM boundaries.

**Solution**: Use `composed: true` for events that need to cross boundaries.

```javascript
// Create event that can cross Shadow DOM boundaries
const event = new CustomEvent('componentEvent', {
  bubbles: true,   // Allow event to bubble up
  composed: true,  // Allow event to cross shadow boundary
  detail: { /* event data */ }
});
```

### Element Access

**Pitfall**: Unable to access Shadow DOM elements from outside.

**Solution**: Provide public methods for necessary interactions.

```javascript
// Define public API for the component
function defineComponentAPI(host, shadowRoot) {
  // Public methods
  host.focusFirstInput = () => {
    const input = shadowRoot.querySelector('input');
    if (input) input.focus();
  };
  
  host.setValue = (value) => {
    const input = shadowRoot.querySelector('input');
    if (input) input.value = value;
  };
  
  host.getValue = () => {
    const input = shadowRoot.querySelector('input');
    return input ? input.value : null;
  };
}
```

### Memory Leaks

**Pitfall**: Memory leaks from event listeners and references.

**Solution**: Implement proper cleanup.

```javascript
// Register cleanup tasks
function registerCleanupTasks() {
  const abortController = new AbortController();
  
  // Add event listener with signal
  document.addEventListener('themeChanged', handleTheme, {
    signal: abortController.signal
  });
  
  // Store references for cleanup
  const intervals = [];
  intervals.push(setInterval(checkUpdates, 5000));
  
  // Register cleanup function
  component.registerCleanup(() => {
    // Abort all listeners
    abortController.abort();
    
    // Clear intervals
    intervals.forEach(clearInterval);
    
    // Clear references
    componentData = null;
  });
}
```

### Slot Content

**Pitfall**: Difficulties with slotted content.

**Solution**: Use slot change events to detect content changes.

```javascript
// Listen for slot content changes
const slot = shadowRoot.querySelector('slot');
slot.addEventListener('slotchange', () => {
  // Get assigned elements
  const assignedElements = slot.assignedElements();
  
  // Process newly assigned elements
  processSlottedContent(assignedElements);
});
```

### Focus Management

**Pitfall**: Focus not properly maintained within component.

**Solution**: Use `delegatesFocus` and proper focus handling.

```javascript
// Create shadow root with delegatesFocus
const shadowRoot = element.attachShadow({
  mode: 'open',
  delegatesFocus: true
});

// Track focus manually when needed
shadowRoot.addEventListener('focusin', (event) => {
  // Handle focus entering component
  component.hasFocus = true;
  component.dispatch('componentFocused', { element: event.target });
});

shadowRoot.addEventListener('focusout', (event) => {
  // Check if focus is still within component
  setTimeout(() => {
    const newFocusedElement = shadowRoot.activeElement;
    if (!newFocusedElement) {
      // Focus has left the component
      component.hasFocus = false;
      component.dispatch('componentBlurred');
    }
  }, 0);
});
```

By following these best practices, you can create robust, maintainable, and performant Shadow DOM components for the Hephaestus UI framework while avoiding common pitfalls.

## See Also

- [Component Isolation Architecture](../Architecture/ComponentIsolationArchitecture.md) - Isolation architecture overview
- [Shadow DOM Implementation](../Architecture/Hephaestus/ShadowDOMImplementation.md) - Detailed implementation guide
- [BEM Naming Conventions](../DeveloperGuides/BEMNamingConventions.md) - CSS naming conventions