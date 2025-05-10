# [ARCHIVED] - This document is no longer current

> **NOTICE:** This documentation has been archived on 2025-05-10 as part of the Hephaestus UI simplification.
> Please refer to the current documentation in [Hephaestus_UI_Implementation.md](/MetaData/TektonDocumentation/DeveloperGuides/Hephaestus_UI_Implementation.md).
> Retained for historical reference only.

# UI Component Communication

**Last Updated:** May 10, 2025

## Overview

This document describes the communication mechanisms between UI components in the Hephaestus framework. Proper communication is essential for coordinating components while maintaining isolation through Shadow DOM boundaries. The architecture provides several complementary methods for components to exchange data and trigger actions.

## Table of Contents

1. [Communication Goals](#communication-goals)
2. [Communication Mechanisms](#communication-mechanisms)
3. [Custom Events](#custom-events)
4. [Service Objects](#service-objects)
5. [Global State](#global-state)
6. [Message Bus](#message-bus)
7. [Communication Patterns](#communication-patterns)
8. [Implementation Examples](#implementation-examples)
9. [Best Practices](#best-practices)
10. [Future Enhancements](#future-enhancements)

## Communication Goals

The component communication architecture aims to:

1. **Maintain Isolation**: Preserve the benefits of Shadow DOM encapsulation
2. **Support Multiple Patterns**: Provide appropriate mechanisms for different use cases
3. **Minimize Coupling**: Reduce direct dependencies between components
4. **Enable Extensibility**: Allow new components to integrate with existing ones
5. **Ensure Performance**: Optimize communication for UI responsiveness
6. **Support Debugging**: Provide tools to monitor and debug communication

## Communication Mechanisms

The framework employs four primary mechanisms for component communication:

1. **Custom Events**: For notifications and simple data passing
2. **Service Objects**: For shared functionality and complex data exchange
3. **Global State**: For application-wide state management
4. **Message Bus**: For decoupled, event-driven communication

Each mechanism is appropriate for different scenarios and can be combined as needed.

## Custom Events

Custom events allow components to notify others about actions or state changes:

### Event Dispatch Implementation

```javascript
// Component context provides a dispatch method
component.dispatch('settingsChanged', {
  theme: 'dark',
  fontSize: 14,
  showIcons: true
});
```

### Event Listening Implementation

```javascript
// Document-level listener for events from any component
document.addEventListener('settingsChanged', (event) => {
  // Check source to avoid circular updates
  if (event.detail.componentId !== component.id) {
    applySettings(event.detail);
  }
});

// Component-level listener for focused handling
component.root.addEventListener('buttonClicked', (event) => {
  handleButtonAction(event.detail);
});
```

### Custom Event Types

The framework defines several standard event types:

1. **Component Lifecycle Events**:
   - `componentMounted`: Component has been added to DOM
   - `componentWillUnmount`: Component is about to be removed
   - `componentError`: Component encountered an error

2. **User Interaction Events**:
   - `menuSelected`: User selected a menu item
   - `tabChanged`: User switched tabs
   - `settingChanged`: User changed a setting

3. **System Events**:
   - `themeChanged`: Application theme has changed
   - `servicesInitialized`: All services are ready
   - `connectionStateChanged`: Network status changed

## Service Objects

Service objects provide shared functionality and state across components:

### Service Registration

```javascript
class SettingsService extends window.tektonUI.componentUtils.BaseService {
  constructor() {
    super('settingsService', '/api/settings');
    this.settings = this.getDefaultSettings();
    this.initialize();
  }
  
  async initialize() {
    // Initialize service
    await this.loadSettings();
    
    // Register globally
    window.tektonUI.services.settingsService = this;
  }
  
  // Service methods...
}
```

### Service Usage

```javascript
// Get existing service or create new instance
const settingsService = window.tektonUI.services.settingsService || 
  new SettingsService();

// Use service methods
settingsService.getSetting('theme').then(theme => {
  applyTheme(theme);
});

// Subscribe to service events
settingsService.addEventListener('settingChanged', (event) => {
  if (event.detail.key === 'fontSize') {
    updateFontSize(event.detail.value);
  }
});
```

### Service Lifecycle

Services implement standard lifecycle methods:

```javascript
class BaseService extends EventTarget {
  constructor(serviceId, apiUrl) {
    super();
    this.serviceId = serviceId;
    this.apiUrl = apiUrl;
    this.connected = false;
  }
  
  async connect() {
    if (this.connected) return true;
    
    try {
      // Connect to backend or initialize
      this.connected = true;
      this.dispatchEvent(new CustomEvent('connected'));
      return true;
    } catch (error) {
      console.error(`Service ${this.serviceId} connection failed:`, error);
      this.connected = false;
      this.dispatchEvent(new CustomEvent('connectionFailed', {
        detail: { error }
      }));
      return false;
    }
  }
  
  disconnect() {
    if (!this.connected) return;
    
    // Cleanup resources
    this.connected = false;
    this.dispatchEvent(new CustomEvent('disconnected'));
  }
}
```

## Global State

For application-wide state that must be shared across all components:

### State Store Implementation

```javascript
class StateStore {
  constructor() {
    this.state = {};
    this.listeners = {};
  }
  
  setState(key, value) {
    const oldValue = this.state[key];
    this.state[key] = value;
    
    // Notify listeners
    if (this.listeners[key]) {
      this.listeners[key].forEach(listener => {
        try {
          listener(value, oldValue, key);
        } catch (error) {
          console.error('Error in state listener:', error);
        }
      });
    }
    
    // Dispatch global event
    document.dispatchEvent(new CustomEvent('stateChanged', {
      detail: { key, value, oldValue }
    }));
  }
  
  getState(key, defaultValue = null) {
    return key in this.state ? this.state[key] : defaultValue;
  }
  
  subscribe(key, listener) {
    if (!this.listeners[key]) {
      this.listeners[key] = [];
    }
    
    this.listeners[key].push(listener);
    
    // Return unsubscribe function
    return () => {
      this.listeners[key] = this.listeners[key].filter(l => l !== listener);
    };
  }
}

// Create global store
window.tektonUI.store = new StateStore();
```

### State Usage

```javascript
// Get state
const theme = window.tektonUI.store.getState('theme', 'light');

// Update state
window.tektonUI.store.setState('theme', 'dark');

// Subscribe to changes
const unsubscribe = window.tektonUI.store.subscribe('theme', (newTheme) => {
  updateTheme(newTheme);
});

// Remember to unsubscribe on cleanup
component.registerCleanup(unsubscribe);
```

## Message Bus

For more complex, decoupled communication between components:

### Message Bus Implementation

```javascript
class MessageBus {
  constructor() {
    this.handlers = {};
    this.middlewares = [];
  }
  
  publish(channel, message) {
    // Apply middlewares
    let processedMessage = this.applyMiddlewares(message, channel);
    
    // Notify subscribers
    if (this.handlers[channel]) {
      this.handlers[channel].forEach(handler => {
        try {
          handler(processedMessage, channel);
        } catch (error) {
          console.error(`Error in message handler for ${channel}:`, error);
        }
      });
    }
    
    return this;
  }
  
  subscribe(channel, handler) {
    if (!this.handlers[channel]) {
      this.handlers[channel] = [];
    }
    
    this.handlers[channel].push(handler);
    
    // Return unsubscribe function
    return () => {
      this.handlers[channel] = this.handlers[channel].filter(h => h !== handler);
    };
  }
  
  addMiddleware(middleware) {
    this.middlewares.push(middleware);
    return this;
  }
  
  applyMiddlewares(message, channel) {
    return this.middlewares.reduce((msg, middleware) => {
      try {
        return middleware(msg, channel) || msg;
      } catch (error) {
        console.error('Error in message middleware:', error);
        return msg;
      }
    }, message);
  }
}

// Create global message bus
window.tektonUI.messageBus = new MessageBus();
```

### Message Bus Usage

```javascript
// Subscribe to messages
const unsubscribe = window.tektonUI.messageBus.subscribe('user:action', (message) => {
  handleUserAction(message);
});

// Publish message
window.tektonUI.messageBus.publish('user:action', {
  action: 'openFile',
  path: '/documents/report.md'
});

// Register cleanup
component.registerCleanup(unsubscribe);
```

## Communication Patterns

The framework supports several communication patterns:

### 1. Publish/Subscribe

Components publish events/messages that others can subscribe to:

```javascript
// Publisher: Dispatching an event
component.dispatch('dataLoaded', { items: loadedItems });

// Subscriber: Listening for events
document.addEventListener('dataLoaded', (event) => {
  updateUI(event.detail.items);
});
```

### 2. Request/Response

Components can request data or actions from services:

```javascript
// Request: Call service method
const result = await dataService.fetchItems({ category: 'reports' });

// Response: Handle result
displayItems(result.items);
```

### 3. Command

Components can issue commands to be executed:

```javascript
// Issue command
window.tektonUI.messageBus.publish('command', {
  name: 'openFile',
  params: { path: '/documents/report.md' }
});

// Command handler
window.tektonUI.messageBus.subscribe('command', (message) => {
  if (message.name === 'openFile') {
    fileSystem.openFile(message.params.path);
  }
});
```

### 4. Observer

Components can observe state changes:

```javascript
// Observer registration
window.tektonUI.store.subscribe('selectedItem', (newItem) => {
  highlightItem(newItem);
});

// State update
window.tektonUI.store.setState('selectedItem', 'item-123');
```

## Implementation Examples

### Theme Change Communication

```javascript
// Theme Service
class ThemeService extends BaseService {
  constructor() {
    super('themeService');
    this.themes = ['light', 'dark', 'system'];
    this.currentTheme = localStorage.getItem('theme') || 'system';
  }
  
  setTheme(theme) {
    if (!this.themes.includes(theme)) {
      throw new Error(`Invalid theme: ${theme}`);
    }
    
    this.currentTheme = theme;
    localStorage.setItem('theme', theme);
    
    // Update document attribute
    document.documentElement.dataset.theme = theme;
    
    // Dispatch custom event
    document.dispatchEvent(new CustomEvent('themeChanged', {
      detail: { theme }
    }));
    
    // Update global state
    window.tektonUI.store.setState('theme', theme);
  }
  
  getTheme() {
    return this.currentTheme;
  }
}

// Theme usage in a component
function initializeTheme() {
  const themeService = window.tektonUI.services.themeService || 
    new ThemeService();
  
  // Get current theme
  const currentTheme = themeService.getTheme();
  
  // Set up theme controls
  component.$('.theme-selector').addEventListener('change', (event) => {
    themeService.setTheme(event.target.value);
  });
  
  // Listen for theme changes from other components
  document.addEventListener('themeChanged', (event) => {
    updateThemeUI(event.detail.theme);
  });
}
```

### Component Coordination Example

```javascript
// Rhetor component wants to notify Budget about usage
function notifyBudgetOfTokenUsage(tokens, model) {
  // Method 1: Custom event
  component.dispatch('tokenUsed', {
    tokens,
    model,
    timestamp: Date.now()
  });
  
  // Method 2: Service method
  if (window.tektonUI.services.budgetService) {
    window.tektonUI.services.budgetService.recordTokenUsage(tokens, model);
  }
  
  // Method 3: Message bus
  window.tektonUI.messageBus.publish('rhetor:tokenUsed', {
    tokens,
    model,
    timestamp: Date.now()
  });
}

// Budget component receiving notification
function setupBudgetNotifications() {
  // Method 1: Listen for custom events
  document.addEventListener('tokenUsed', (event) => {
    if (event.detail.componentId !== component.id) {
      updateBudgetDisplay(event.detail);
    }
  });
  
  // Method 2: Implement service method
  class BudgetService extends BaseService {
    recordTokenUsage(tokens, model) {
      this.updateBudget(tokens, model);
      this.dispatchEvent(new CustomEvent('budgetUpdated'));
    }
  }
  
  // Method 3: Subscribe to message bus
  window.tektonUI.messageBus.subscribe('rhetor:tokenUsed', (message) => {
    updateBudgetDisplay(message);
  });
}
```

## Best Practices

1. **Choose the Right Mechanism**:
   - Use custom events for notifications and simple data passing
   - Use services for shared functionality and complex data
   - Use global state for application-wide settings
   - Use message bus for decoupled, event-driven communication

2. **Prevent Circular Updates**:
   - Include component ID in event detail
   - Check source when handling events
   - Implement update filters to prevent loops

3. **Error Handling**:
   - Wrap event handlers in try/catch
   - Provide fallbacks when services are unavailable
   - Log communication errors for debugging

4. **Performance Optimization**:
   - Throttle frequent events
   - Batch updates when possible
   - Clean up listeners when components are unmounted

5. **Debugging Support**:
   - Add debug mode with enhanced logging
   - Use meaningful event names and service methods
   - Document communication patterns for each component

## Future Enhancements

1. **Typed Communication**: Implement TypeScript interfaces for events and messages
2. **Middleware Support**: Extend message bus with pluggable middleware
3. **Communication Visualization**: Create debug tools to visualize component communication
4. **Contract Testing**: Implement automated tests for communication contracts
5. **State Time-Travel**: Add history and rollback capabilities to state store
6. **Inter-Tab Communication**: Support communication across browser tabs
7. **Offline Queue**: Queue messages when services are unavailable
8. **Priority Channels**: Implement priority-based message delivery

## See Also

- [Component Isolation Architecture](./ComponentIsolationArchitecture.md) - Overall isolation architecture
- [Component Integration Patterns](./ComponentIntegrationPatterns.md) - Standardized patterns for component integration
- [State Management Architecture](./StateManagementArchitecture.md) - State management framework