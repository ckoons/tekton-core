Plan for Terminal-Focused UI Implementation

  Overview

  We will simplify the Tekton UI by removing the header and footer from the right panel, expanding the
  terminal to fill the entire right side, and removing any trace of the separate chat interface. This
  will provide a more reliable and maintainable UI.

  Files to Modify

  1. CSS Files:

  - /Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/main.css
    - Remove styles for content-header and content-footer
    - Modify content-main to take full height
    - Adjust terminal panel to fill entire area
  - /Users/cskoons/projects/github/Tekton/Hephaestus/ui/styles/terminal-chat.css
    - This file can be removed entirely or retained only for terminal styling

  2. HTML Structure:

  - /Users/cskoons/projects/github/Tekton/Hephaestus/ui/index.html
    - Remove content-header section
    - Remove content-footer section with chat-input
    - Adjust content-main div to be full height

  3. JavaScript Files:

  - /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/main.js
    - Remove chat input event handlers and functions
    - Modify tektonUI object to use terminal for all messaging
    - Add proper debug logging for all terminal operations
  - /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/terminal.js
    - Enhance with input capability within the terminal itself
    - Add command history navigation
    - Improve formatting for command/response clarity
  - /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/terminal-chat.js
    - This file can be removed entirely
  - /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/ergon-component.js
    - Update to interact directly with terminal instead of chat interface
    - Remove chat-specific code

  4. WebSocket Communication:

  - /Users/cskoons/projects/github/Tekton/Hephaestus/ui/scripts/websocket.js
    - Update to send messages directly to terminal
    - Simplify response handling to work with terminal

  Implementation Steps

  1. Backup Current State
    - Commit current code to Git for easy rollback
  2. HTML Structure Modifications
    - Remove header and footer divs
    - Adjust main content div structure
  3. CSS Adjustments
    - Modify layout styles for full-height terminal
    - Remove unused chat-related styles
    - Enhance terminal appearance for clearer interaction
  4. Terminal Enhancement
    - Add input capability directly in terminal
    - Implement command processing
    - Add command history (up/down arrows)
    - Add proper debug logging
  5. JavaScript Logic Updates
    - Streamline message handling through terminal
    - Update component interaction logic
    - Remove chat-specific code
  6. WebSocket Integration
    - Ensure messages flow correctly to/from backend
    - Improve error handling and reconnection logic
  7. Testing
    - Verify terminal input/output
    - Test component switching
    - Check WebSocket communication

  Debug Logging Strategy

  - Add comprehensive logging at key points:
    - Input capture
    - Message processing
    - WebSocket communication
    - Component interaction
    - Terminal rendering
  - Log format should include:
    - Timestamp
    - Component/source
    - Action type
    - Message content
    - Status/result

  Expected Outcome

  A simplified UI with:
  - Full-height terminal panel on the right side
  - Direct input/output through the terminal
  - No separate chat interface
  - Clear visual distinction between user commands and AI responses
  - Improved reliability and maintainability

  This approach significantly reduces DOM complexity and focuses on what works reliably (the terminal),
  while maintaining all core functionality.

