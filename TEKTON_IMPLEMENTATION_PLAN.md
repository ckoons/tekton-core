# Tekton Implementation Plan

## Overview and Architecture

Tekton is a sophisticated AI orchestration system designed to coordinate multiple AI models and resources for complex software engineering tasks. This document outlines the implementation plan for enhancing Tekton with improved component management, LLM integration, and UI interactions.

### Core Architectural Principles

1. **Message-Based Architecture**: Components communicate via messages routed through Hermes
2. **Component Lifecycle Management**: Hermes manages component launching, monitoring, and recovery
3. **LLM Management via Rhetor**: Rhetor handles prompt engineering, context management, and LLM selection
4. **UI Integration**: Hephaestus provides a unified interface with component-specific views
5. **Persistent Memory via Engram**: Shared memory system for cross-component context

### Component Relationships

```
┌─────────────┐         ┌─────────────┐
│             │ launches │             │
│  Launch     ├────────►│  Hermes     │
│  Script     │         │  (Message   │
│             │         │   Bus)      │
└─────────────┘         └──────┬──────┘
                              │
                              │ launches
                              ▼
     ┌────────────────────────┬────────────────────────┬────────────────┐
     │                        │                        │                │
┌────▼─────┐           ┌──────▼──────┐          ┌──────▼──────┐  ┌──────▼──────┐
│          │           │             │          │             │  │             │
│  Engram  │◄─────────►│   Rhetor    │◄────────►│ Hephaestus  │  │   Other     │
│ (Memory) │           │(LLM Manager)│          │    (UI)     │  │ Components  │
│          │           │             │          │             │  │             │
└──────────┘           └──────┬──────┘          └─────────────┘  └─────────────┘
                              │
                              │ manages
                              ▼
                       ┌──────────────┐
                       │    LLMs      │
                       │ (Claude,     │
                       │  Ollama,     │
                       │  OpenAI)     │
                       └──────────────┘
```

### Message Flow

1. Component A needs to send a message to Component B
2. Message is sent to Hermes
3. Hermes checks if Component B is registered
   - If registered, routes message to Component B
   - If not registered, launches Component B and queues message
4. Component B processes message and may respond via Hermes

### LLM Interaction Flow

1. Component needs to use an LLM
2. Component sends LLM request message via Hermes
3. Hermes routes to Rhetor for LLM management
4. Rhetor:
   - Selects appropriate model
   - Applies component-specific prompt templates
   - Manages context limitations
   - Sends to LLM
   - Processes response
5. Rhetor returns processed LLM response to original component

## Implementation Plan

### Phase 1: Hermes Enhancement for Component Management

#### 1.1 Component Manager

Add a `ComponentManager` class to Hermes to handle component lifecycle:

```python
# hermes/core/component_manager.py
class ComponentManager:
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.active_components = {}  # Track running components
        self.component_processes = {}  # Track process IDs
        
    async def start_component(self, component_id):
        """Launch a component if it's not already running"""
        if component_id in self.active_components:
            return
            
        component_config = self.config.get('components', {}).get(component_id)
        if not component_config:
            logger.error(f"No configuration found for component {component_id}")
            return
            
        # Build launch command
        component_path = os.path.join(self.config['base_paths'][component_id], 
                                     component_config['start_script'])
        
        # Start component process
        process = await asyncio.create_subprocess_exec(
            component_path,
            '--config', json.dumps(component_config),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        self.component_processes[component_id] = process
        logger.info(f"Started component {component_id} with PID {process.pid}")
        
    async def check_component_health(self):
        """Check if all components are running"""
        for component_id, process in list(self.component_processes.items()):
            if process.returncode is not None:  # Process has terminated
                logger.warning(f"Component {component_id} terminated unexpectedly")
                await self.start_component(component_id)
```

#### 1.2 Enhanced Message Router

Enhance the message router to trigger component starts:

```python
# hermes/core/message_bus.py
class MessageBus:
    def __init__(self, component_manager):
        self.component_manager = component_manager
        self.message_queue = {}  # Queue messages by component
        
    async def route_message(self, message):
        """Route a message to the target component"""
        target = message.get('target')
        
        # Check if target component is registered
        if target not in self.component_manager.active_components:
            # Queue message
            if target not in self.message_queue:
                self.message_queue[target] = []
            self.message_queue[target].append(message)
            
            # Start the component
            await self.component_manager.start_component(target)
            return
            
        # Route message to component
        await self._deliver_message(target, message)
```

#### 1.3 Heartbeat System

Implement a heartbeat system for component health monitoring:

```python
# hermes/core/heartbeat_monitor.py
class HeartbeatMonitor:
    def __init__(self, component_manager):
        self.component_manager = component_manager
        self.last_heartbeat = {}
        self.heartbeat_interval = 30  # seconds
        self.max_missed_beats = 3
        self.missed_beats = {}
        
    async def start(self):
        """Start the heartbeat monitor loop"""
        while True:
            await self.check_components()
            await asyncio.sleep(self.heartbeat_interval / 2)
            
    async def check_components(self):
        """Check if components are still responsive"""
        now = time.time()
        
        for component_id, last_beat in list(self.last_heartbeat.items()):
            if now - last_beat > self.heartbeat_interval:
                # Missed heartbeat
                self.missed_beats[component_id] = self.missed_beats.get(component_id, 0) + 1
                
                if self.missed_beats[component_id] >= self.max_missed_beats:
                    logger.warning(f"Component {component_id} appears unresponsive")
                    
                    # Remove registration
                    await self.component_manager.deregister_component(component_id)
                    
                    # Attempt restart if component is essential
                    if self.component_manager.is_essential(component_id):
                        logger.info(f"Attempting to restart essential component {component_id}")
                        await self.component_manager.start_component(component_id)
```

#### 1.4 Dependency Manager

Implement dependency resolution for component startup:

```python
# hermes/core/dependency.py
class DependencyManager:
    def __init__(self, config):
        self.config = config
        self.dependency_graph = self._build_dependency_graph()
        
    def _build_dependency_graph(self):
        """Build a dependency graph from config"""
        graph = {}
        
        for component_id, component_config in self.config.get('components', {}).items():
            graph[component_id] = component_config.get('dependencies', [])
            
        return graph
        
    def get_start_order(self):
        """Get component start order based on dependencies"""
        # Topological sort
        visited = set()
        temp = set()
        order = []
        
        def visit(node):
            if node in temp:
                raise ValueError(f"Circular dependency detected involving {node}")
            if node in visited:
                return
                
            temp.add(node)
            
            for dep in self.dependency_graph.get(node, []):
                visit(dep)
                
            temp.remove(node)
            visited.add(node)
            order.append(node)
            
        for node in self.dependency_graph:
            if node not in visited:
                visit(node)
                
        return list(reversed(order))
```

### Phase 2: Rhetor Enhancement for LLM Management

#### 2.1 LLM Manager

Implement LLM management in Rhetor:

```python
# rhetor/core/llm_manager.py
class LLMManager:
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.model_instances = {}  # Initialized model clients
        self.component_mappings = {}  # Component to model mappings
        
    async def process_llm_request(self, message):
        """Process an LLM request from a component"""
        sender = message.get('sender')
        original_target = message.get('original_target', 'llm')
        
        # Determine which model to use
        model_id = self.get_model_for_component(sender, original_target)
        
        # Apply prompt engineering
        enhanced_prompt = await self.apply_prompt_template(
            sender, 
            message.get('payload', {}).get('prompt'),
            model_id
        )
        
        # Get model client
        model_client = await self.get_model_client(model_id)
        
        # Execute against model
        response = await model_client.generate(enhanced_prompt)
        
        # Post-process response
        processed_response = await self.post_process_response(response, sender)
        
        return processed_response
        
    def get_model_for_component(self, component_id, target_hint=None):
        """Determine which model a component should use"""
        # First check explicit mapping in config
        if component_id in self.component_mappings:
            return self.component_mappings[component_id]
            
        # Check target hint (e.g., llm:claude)
        if target_hint and target_hint.startswith("llm:"):
            model_name = target_hint.split(":", 1)[1]
            # Validate model exists
            if model_name in self.config['models']:
                return model_name
        
        # Fall back to default model for the component type
        component_type = component_id.split("-")[0]  # e.g., "ergon" from "ergon-main"
        if component_type in self.config['component_defaults']:
            return self.config['component_defaults'][component_type]
            
        # Ultimate fallback
        return self.config['default_model']
```

#### 2.2 Prompt Manager

Implement prompt template management:

```python
# rhetor/core/prompt_manager.py
class PromptManager:
    def __init__(self, template_dir=None):
        self.template_dir = template_dir or "config/prompts"
        self.templates = self._load_templates()
        self.dynamic_templates = {}  # Templates modified at runtime
        
    async def apply_template(self, component_id, user_input, model_id):
        """Apply a prompt template for a component"""
        template = self.get_template(component_id)
        if not template:
            return user_input  # No template, pass through
            
        # Apply template with component-specific variables
        system_prompt = template.get('system', '')
        
        # Construct final prompt based on model requirements
        if model_id.startswith('claude'):
            # Claude format
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            return messages
        elif model_id.startswith('gpt'):
            # OpenAI format
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            return messages
        else:
            # Simple format for other models
            return f"{system_prompt}\n\nUser: {user_input}\nAssistant:"
```

#### 2.3 Context Manager

Implement context management for LLM interactions:

```python
# rhetor/core/context_manager.py
class ContextManager:
    def __init__(self, engram_client=None):
        self.engram_client = engram_client
        self.contexts = {}  # In-memory contexts
        
    async def get_context(self, context_id, max_tokens=None):
        """Get conversation context"""
        # First check in-memory cache
        if context_id in self.contexts:
            context = self.contexts[context_id]
            if max_tokens:
                return self._trim_context(context, max_tokens)
            return context
            
        # Then check Engram
        if self.engram_client:
            context_key = f"llm_context:{context_id}"
            stored_context = await self.engram_client.retrieve(context_key)
            if stored_context:
                self.contexts[context_id] = stored_context
                if max_tokens:
                    return self._trim_context(stored_context, max_tokens)
                return stored_context
                
        # No context found
        return []
        
    async def update_context(self, context_id, new_messages):
        """Update conversation context with new messages"""
        context = await self.get_context(context_id) or []
        context.extend(new_messages)
        
        # Update in-memory cache
        self.contexts[context_id] = context
        
        # Update in Engram
        if self.engram_client:
            context_key = f"llm_context:{context_id}"
            await self.engram_client.store(context_key, context)
            
        return context
```

### Phase 3: MCP Services for UI and LLM Integration

#### 3.1 UI MCP Server

Implement an MCP server for UI interactions:

```python
# hephaestus/mcp/ui_mcp_server.py
class UIMCPServer:
    """MCP Server for UI interactions"""
    
    async def get_manifest(self):
        """Return capabilities for UI control"""
        return {
            "name": "ui-mcp",
            "version": "0.1.0",
            "capabilities": [
                {
                    "name": "update_ui_element",
                    "description": "Update a UI element's content or properties",
                    "parameters": {
                        "element_id": {"type": "string", "description": "ID of the element to update"},
                        "updates": {"type": "object", "description": "Updates to apply"}
                    }
                },
                {
                    "name": "navigate",
                    "description": "Navigate to a different component or view",
                    "parameters": {
                        "component": {"type": "string", "description": "Component to navigate to"},
                        "view": {"type": "string", "description": "Optional view within component"}
                    }
                },
                # More UI capabilities
            ]
        }
    
    async def handle_request(self, request):
        """Handle a capability invocation"""
        capability = request.get("capability")
        
        if capability == "update_ui_element":
            return await self._update_ui_element(request["parameters"])
        elif capability == "navigate":
            return await self._navigate(request["parameters"])
        # Handle other capabilities
```

#### 3.2 LLM MCP Server

Implement an MCP server for LLM capabilities:

```python
# rhetor/mcp/llm_mcp_server.py
class LLMMCPServer:
    """MCP Server for LLM capabilities"""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
    
    async def get_manifest(self):
        """Return capabilities for LLM operations"""
        return {
            "name": "llm-mcp",
            "version": "0.1.0",
            "capabilities": [
                {
                    "name": "generate_text",
                    "description": "Generate text with an LLM",
                    "parameters": {
                        "prompt": {"type": "string", "description": "Input prompt"},
                        "model": {"type": "string", "description": "Model to use"},
                        "max_tokens": {"type": "integer", "description": "Maximum tokens to generate"}
                    }
                },
                {
                    "name": "chat_completion",
                    "description": "Generate chat response with an LLM",
                    "parameters": {
                        "messages": {"type": "array", "description": "Chat messages"},
                        "model": {"type": "string", "description": "Model to use"},
                        "max_tokens": {"type": "integer", "description": "Maximum tokens to generate"}
                    }
                }
                # More LLM capabilities
            ]
        }
    
    async def handle_request(self, request):
        """Handle a capability invocation"""
        capability = request.get("capability")
        
        if capability == "generate_text":
            return await self._generate_text(request["parameters"])
        elif capability == "chat_completion":
            return await self._chat_completion(request["parameters"])
        # Handle other capabilities
```

#### 3.3 WebSocket Bridge

Implement a WebSocket bridge for MCP services:

```javascript
// ui/scripts/mcp-bridge.js
class MCPBridge {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.handlers = {};
    }
    
    initialize() {
        // Connect to MCP WebSocket
        this.socket = new WebSocket('ws://localhost:8081/mcp');
        
        this.socket.onopen = () => {
            this.connected = true;
            console.log('MCP bridge connected');
        };
        
        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this._handleMessage(message);
        };
    }
    
    _handleMessage(message) {
        const action = message.action;
        
        if (action === 'update_ui_element') {
            const { element_id, updates } = message.parameters;
            const element = document.getElementById(element_id);
            
            if (element) {
                // Apply updates
                Object.entries(updates).forEach(([prop, value]) => {
                    if (prop === 'text') {
                        element.textContent = value;
                    } else if (prop === 'html') {
                        element.innerHTML = value;
                    } else if (prop === 'value') {
                        element.value = value;
                    } else if (prop === 'style') {
                        Object.assign(element.style, value);
                    } else if (prop === 'class') {
                        element.className = value;
                    }
                });
            }
        } else if (action === 'navigate') {
            // Handle navigation
            const { component, view } = message.parameters;
            window.tektonUI.navigateTo(component, view);
        }
    }
}
```

### Phase 4: UI Enhancement for LLM Management and User Profiles

#### 4.1 LLM Settings UI

Implement a UI for LLM configuration:

```javascript
// ui/scripts/settings-llm.js
class LLMSettingsUI {
    constructor() {
        this.settingsContainer = document.getElementById('llm-settings-container');
        this.components = [];
        this.availableModels = [];
    }
    
    async initialize() {
        // Fetch component list from Hermes
        this.components = await this.fetchComponents();
        
        // Fetch available models
        this.availableModels = await this.fetchModels();
        
        // Fetch current mappings
        this.componentMappings = await this.fetchComponentMappings();
        
        // Render settings UI
        this.renderSettings();
    }
    
    renderSettings() {
        // Create settings form
        const form = document.createElement('form');
        form.className = 'llm-settings-form';
        
        // Add header
        const header = document.createElement('h2');
        header.textContent = 'LLM Settings';
        form.appendChild(header);
        
        // Add component model mappings
        this.components.forEach(component => {
            const row = document.createElement('div');
            row.className = 'setting-row';
            
            const label = document.createElement('label');
            label.textContent = `${component.name} Component:`;
            row.appendChild(label);
            
            const select = document.createElement('select');
            select.setAttribute('data-component', component.id);
            
            // Add model options
            this.availableModels.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = `${model.provider}: ${model.name}`;
                
                // Set selected if this is the current mapping
                if (this.componentMappings[component.id] === model.id) {
                    option.selected = true;
                }
                
                select.appendChild(option);
            });
            
            row.appendChild(select);
            form.appendChild(row);
        });
        
        // Add save button
        const saveButton = document.createElement('button');
        saveButton.textContent = 'Save Settings';
        saveButton.addEventListener('click', e => {
            e.preventDefault();
            this.saveSettings();
        });
        
        form.appendChild(saveButton);
        
        // Add to container
        this.settingsContainer.innerHTML = '';
        this.settingsContainer.appendChild(form);
    }
}
```

#### 4.2 User Profile UI

Implement a user profile UI:

```javascript
// ui/scripts/user-profile.js
class UserProfileUI {
    constructor() {
        this.profileContainer = document.getElementById('profile-container');
        this.profile = {};
    }
    
    async initialize() {
        // Load profile data
        await this.loadProfile();
        
        // Render profile UI
        this.renderProfile();
    }
    
    async loadProfile() {
        try {
            const response = await fetch('/api/profile');
            if (response.ok) {
                this.profile = await response.json();
            } else {
                // Initialize with empty profile
                this.profile = {
                    givenName: '',
                    familyName: '',
                    emails: [''],
                    phoneNumber: '',
                    socialAccounts: {
                        x: '',
                        bluesky: '',
                        wechat: '',
                        whatsapp: '',
                        github: ''
                    }
                };
            }
        } catch (e) {
            console.error('Error loading profile:', e);
            // Initialize with empty profile
            this.profile = {
                givenName: '',
                familyName: '',
                emails: [''],
                phoneNumber: '',
                socialAccounts: {
                    x: '',
                    bluesky: '',
                    wechat: '',
                    whatsapp: '',
                    github: ''
                }
            };
        }
    }
    
    renderProfile() {
        // Create profile form
        const form = document.createElement('form');
        form.className = 'profile-form';
        
        // Add header
        const header = document.createElement('h2');
        header.textContent = 'User Profile';
        form.appendChild(header);
        
        // Name fields
        this.addTextField(form, 'givenName', 'Given Name', this.profile.givenName);
        this.addTextField(form, 'familyName', 'Family Name', this.profile.familyName);
        
        // Email fields (multiple)
        this.addArrayField(form, 'emails', 'Email Addresses', this.profile.emails || ['']);
        
        // Phone number
        this.addTextField(form, 'phoneNumber', 'Phone Number', this.profile.phoneNumber);
        
        // Social accounts
        const socialAccounts = this.profile.socialAccounts || {};
        this.addTextField(form, 'socialAccounts.x', 'X / Twitter', socialAccounts.x);
        this.addTextField(form, 'socialAccounts.bluesky', 'BlueSky', socialAccounts.bluesky);
        this.addTextField(form, 'socialAccounts.wechat', 'WeChat', socialAccounts.wechat);
        this.addTextField(form, 'socialAccounts.whatsapp', 'WhatsApp', socialAccounts.whatsapp);
        this.addTextField(form, 'socialAccounts.github', 'GitHub', socialAccounts.github);
        
        // Add save button
        const saveButton = document.createElement('button');
        saveButton.textContent = 'Save Profile';
        saveButton.addEventListener('click', e => {
            e.preventDefault();
            this.saveProfile();
        });
        
        form.appendChild(saveButton);
        
        // Add to container
        this.profileContainer.innerHTML = '';
        this.profileContainer.appendChild(form);
    }
    
    addTextField(form, name, label, value) {
        const row = document.createElement('div');
        row.className = 'profile-row';
        
        const labelEl = document.createElement('label');
        labelEl.textContent = label;
        labelEl.setAttribute('for', name);
        row.appendChild(labelEl);
        
        const input = document.createElement('input');
        input.type = 'text';
        input.name = name;
        input.id = name;
        input.value = value || '';
        row.appendChild(input);
        
        form.appendChild(row);
    }
    
    addArrayField(form, name, label, values) {
        const container = document.createElement('div');
        container.className = 'array-field-container';
        
        const headerRow = document.createElement('div');
        headerRow.className = 'array-field-header';
        
        const headerLabel = document.createElement('label');
        headerLabel.textContent = label;
        headerRow.appendChild(headerLabel);
        
        const addButton = document.createElement('button');
        addButton.textContent = 'Add';
        addButton.className = 'add-button';
        addButton.addEventListener('click', e => {
            e.preventDefault();
            const fieldContainer = container.querySelector('.array-fields');
            this.addArrayItem(fieldContainer, name, '');
        });
        headerRow.appendChild(addButton);
        
        container.appendChild(headerRow);
        
        const fieldsContainer = document.createElement('div');
        fieldsContainer.className = 'array-fields';
        container.appendChild(fieldsContainer);
        
        // Add existing values
        values.forEach(value => {
            this.addArrayItem(fieldsContainer, name, value);
        });
        
        form.appendChild(container);
    }
    
    addArrayItem(container, name, value) {
        const row = document.createElement('div');
        row.className = 'array-item';
        
        const input = document.createElement('input');
        input.type = 'text';
        input.name = `${name}[]`;
        input.value = value || '';
        row.appendChild(input);
        
        const removeButton = document.createElement('button');
        removeButton.textContent = 'Remove';
        removeButton.className = 'remove-button';
        removeButton.addEventListener('click', e => {
            e.preventDefault();
            container.removeChild(row);
        });
        row.appendChild(removeButton);
        
        container.appendChild(row);
    }
    
    async saveProfile() {
        // Collect form data
        const form = this.profileContainer.querySelector('form');
        const formData = new FormData(form);
        
        // Build profile object
        const profile = {
            givenName: formData.get('givenName'),
            familyName: formData.get('familyName'),
            phoneNumber: formData.get('phoneNumber'),
            emails: Array.from(formData.getAll('emails[]')).filter(email => email.trim() !== ''),
            socialAccounts: {
                x: formData.get('socialAccounts.x'),
                bluesky: formData.get('socialAccounts.bluesky'),
                wechat: formData.get('socialAccounts.wechat'),
                whatsapp: formData.get('socialAccounts.whatsapp'),
                github: formData.get('socialAccounts.github')
            }
        };
        
        // Save to API
        try {
            const response = await fetch('/api/profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profile)
            });
            
            if (response.ok) {
                // Show success message
                alert('Profile saved successfully');
                // Update local profile data
                this.profile = profile;
            } else {
                alert('Error saving profile');
            }
        } catch (e) {
            console.error('Error saving profile:', e);
            alert('Error saving profile');
        }
    }
}
```

### Phase 5: Configuration System and Environment Variables

#### 5.1 Configuration System

Implement a unified configuration system:

```python
# tekton/core/config.py
class ConfigManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.tekton")
        self.config_dir = os.path.join(self.base_dir, "config")
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration from files in priority order"""
        config = {}
        
        # Load default config
        default_config_path = os.path.join(self.config_dir, "default.json")
        if os.path.exists(default_config_path):
            with open(default_config_path, 'r') as f:
                config.update(json.load(f))
                
        # Load environment-specific config
        env = os.environ.get("TEKTON_ENV", "development")
        env_config_path = os.path.join(self.config_dir, f"{env}.json")
        if os.path.exists(env_config_path):
            with open(env_config_path, 'r') as f:
                config.update(json.load(f))
                
        # Load local config (highest priority)
        local_config_path = os.path.join(self.config_dir, "local.json")
        if os.path.exists(local_config_path):
            with open(local_config_path, 'r') as f:
                config.update(json.load(f))
                
        # Apply environment variable overrides
        config = self._apply_env_overrides(config)
                
        return config
        
    def _apply_env_overrides(self, config):
        """Apply environment variable overrides to config"""
        # Look for TEKTON_ prefixed environment variables
        for key, value in os.environ.items():
            if key.startswith("TEKTON_"):
                # Convert TEKTON_FOO_BAR to foo.bar
                config_key = key[7:].lower().replace('_', '.')
                # Set in config
                self._set_nested_key(config, config_key, value)
                
        return config
        
    def _set_nested_key(self, obj, key_path, value):
        """Set a nested key in an object using dot notation"""
        keys = key_path.split('.')
        current = obj
        
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                # Last key, set the value
                current[key] = value
            else:
                # Intermediate key, ensure it exists
                if key not in current or not isinstance(current[key], dict):
                    current[key] = {}
                current = current[key]
                
        return obj
        
    def get(self, key_path, default=None):
        """Get a config value using dot notation"""
        keys = key_path.split('.')
        current = self.config
        
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
            
        return current
        
    def set(self, key_path, value):
        """Set a config value using dot notation"""
        self._set_nested_key(self.config, key_path, value)
        
    def save_local_config(self):
        """Save local config to file"""
        os.makedirs(self.config_dir, exist_ok=True)
        local_config_path = os.path.join(self.config_dir, "local.json")
        
        with open(local_config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
```

#### 5.2 Environment Variables Handler

Implement an environment variables loader:

```python
# tekton/core/env_loader.py
class EnvironmentLoader:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.expanduser("~/.tekton")
        
    def load_env(self):
        """Load environment variables from .env files in priority order"""
        # Load files in this order:
        # 1. .env (base environment variables)
        # 2. .env.local (local overrides)
        # 3. .env.tekton (Tekton-specific overrides)
        
        # Define files to load in order
        env_files = [
            os.path.join(self.base_dir, ".env"),
            os.path.join(self.base_dir, ".env.local"),
            os.path.join(self.base_dir, ".env.tekton")
        ]
        
        # Load each file if it exists
        for env_file in env_files:
            if os.path.exists(env_file):
                self._load_env_file(env_file)
                
    def _load_env_file(self, file_path):
        """Load environment variables from a file"""
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                    
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                        
                    # Set environment variable if not already set
                    if key not in os.environ:
                        os.environ[key] = value
```

## Additional Notes

### Environment Variables Setup

Tekton uses environment variables for API keys and configuration. The loading order is:

1. `.env` - Base environment variables
2. `.env.local` - Local overrides (not committed to git)
3. `.env.tekton` - Tekton-specific overrides (not committed to git)

Required API keys:

```
# Example .env.local file
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
GOOGLE_API_KEY=xxxxx
```

The `.env.local` and `.env.tekton` files have highest precedence and should be used for API keys and sensitive information.

### Future Implementation Plans

1. **Component UIs**:
   - Develop UIs for all existing Tekton CLI components
   - Create a consistent UI pattern for each component
   - Ensure each UI can be controlled via MCP

2. **Project Management**:
   - Create a Tekton Project CLI and UI
   - Manage GitHub repositories and local working directories
   - Store project guidelines and documentation pointers
   - Support multiple repository management

3. **Future Enhancements**:
   - Add support for team collaboration features
   - Implement analytics for LLM usage and effectiveness
   - Add visualization of component relationships
   - Create project templates and quickstart options

## Instructions for Implementation

**Important Notice for Claude Code:**

This implementation plan should be executed in a step-by-step manner, with careful consideration for the existing codebase. Please follow these guidelines:

1. **Discuss Before Implementing**: Before making any changes, discuss the proposed implementation with Casey.

2. **Get Explicit Permission**: Receive explicit permission from Casey before modifying any file. Make only the specific changes that have been approved.

3. **Check Existing Code**: Always review existing code to understand patterns and conventions before suggesting changes.

4. **Test Changes**: Test each change to ensure it doesn't break existing functionality.

5. **Document Changes**: Add appropriate comments and update documentation.

6. **Stay Within Scope**: Only make changes directly related to the task at hand.

The implementation should proceed in the specified phases, with each phase building on the previous one. Components should maintain their independence while being integrated through well-defined interfaces.

## Conclusion

This implementation plan provides a comprehensive roadmap for enhancing Tekton with improved component management, LLM integration, and UI interactions. By following this plan, Tekton will evolve into a robust orchestration system capable of coordinating multiple AI models for complex software engineering tasks.

The architecture maintains loose coupling through message passing, with Hermes serving as the central component manager and message bus. Rhetor takes on the critical role of LLM management, while Hephaestus provides a unified user interface.

By implementing this plan, Tekton will become more resilient, maintainable, and capable of supporting a wide range of AI-driven software engineering workflows.