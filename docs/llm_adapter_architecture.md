# LLM Adapter Architecture

```mermaid
graph TD
    subgraph "Hephaestus UI"
        UI[Terminal Interface]
        Hermes[Hermes Connector]
        Ergon[Ergon Component]
    end

    subgraph "LLM Adapter"
        Server[Server Module]
        
        subgraph "HTTP Interface"
            HTTP[HTTP Server]
            REST[REST API Endpoints]
        end
        
        subgraph "WebSocket Interface"
            WS[WebSocket Server]
            WSHandler[Message Handler]
            Stream[Streaming Handler]
        end
        
        subgraph "LLM Client"
            Client[LLM Client]
            Claude[Claude API Client]
            Simulated[Simulated Responses]
        end
        
        Config[Configuration]
    end

    subgraph "External Services"
        AnthropicAPI[Anthropic Claude API]
    end

    %% Connections
    UI --> Hermes
    Ergon --> Hermes
    
    Hermes -- HTTP Request --> HTTP
    Hermes -- WebSocket --> WS
    
    Server --> HTTP
    Server --> WS
    
    HTTP --> REST
    REST --> Client
    
    WS --> WSHandler
    WSHandler --> Stream
    WSHandler --> Client
    Stream --> Client
    
    Client --> Claude
    Client --> Simulated
    Claude --> AnthropicAPI
    
    Config --> Server
    Config --> HTTP
    Config --> WS
    Config --> Client

    %% Descriptions
    classDef primary fill:#f9f,stroke:#333,stroke-width:2px
    classDef secondary fill:#bbf,stroke:#333,stroke-width:1px
    classDef external fill:#bfb,stroke:#333,stroke-width:1px
    
    class Server,HTTP,WS,Client primary
    class REST,WSHandler,Stream,Claude,Simulated,Config,UI,Hermes,Ergon secondary
    class AnthropicAPI external
```

## Component Flow

### Request Flow

1. **User Interaction**:
   - User enters a message in the Hephaestus UI terminal
   - Ergon component captures the input and triggers the Hermes connector

2. **Hermes Connector**:
   - Establishes WebSocket connection to LLM Adapter
   - Formats the message into a standardized request format
   - Sends request to the adapter's WebSocket interface

3. **WebSocket Server**:
   - Receives the request
   - Validates and processes the message
   - Sends typing indicator to the UI
   - Forwards the request to the LLM Client

4. **LLM Client**:
   - Determines whether to use Claude or simulated responses
   - Adds appropriate system prompt based on context
   - For Claude, formats the request for Anthropic's API
   - Initiates streaming or non-streaming request

5. **Claude Integration**:
   - Makes API call to Anthropic's Claude service
   - Receives streaming or complete response
   - Handles authentication and rate limiting

### Response Flow

1. **LLM Processing**:
   - Claude API generates response
   - Response is streamed back to the LLM Client

2. **Streaming Response Handling**:
   - LLM Client processes each chunk of the response
   - Formats chunks for the WebSocket interface
   - Manages streaming state

3. **WebSocket Response**:
   - WebSocket server streams chunks back to the UI
   - Sends completion signal when finished
   - Handles any errors that occur

4. **UI Display**:
   - Hermes connector processes incoming chunks
   - Updates the terminal display in real-time
   - Provides typing indicators and completion signals

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant User
    participant UI as Hephaestus UI
    participant Adapter as LLM Adapter
    participant Claude as Claude API
    
    User->>UI: Enter message
    UI->>Adapter: WebSocket connect
    Adapter->>UI: Connection established
    
    UI->>Adapter: Send LLM_REQUEST
    Adapter->>UI: UPDATE: typing=true
    
    Adapter->>Claude: API request
    
    loop Streaming Response
        Claude->>Adapter: Response chunk
        Adapter->>UI: UPDATE: chunk
    end
    
    Claude->>Adapter: Complete
    Adapter->>UI: UPDATE: done=true
    Adapter->>UI: UPDATE: typing=false
    
    UI->>User: Display complete response
```

## Component Interfaces

### HTTP API Endpoints

```mermaid
classDiagram
    class HTTPServer {
        +GET / : Basic info
        +GET /health : Health check
        +GET /providers : Available models
        +POST /provider : Set provider/model
        +POST /message : Send message
        +POST /stream : Stream response
    }
```

### WebSocket Message Types

```mermaid
classDiagram
    class ClientToServer {
        +LLM_REQUEST
        +REGISTER
        +STATUS
    }
    
    class ServerToClient {
        +UPDATE
        +RESPONSE
        +ERROR
    }
```

## Integration with Tekton Architecture

```mermaid
graph LR
    subgraph "Tekton System"
        Hephaestus[Hephaestus UI]
        LLMAdapter[LLM Adapter]
        Rhetor[Rhetor]
        Engram[Engram]
        Hermes[Hermes]
    end
    
    User[User] --> Hephaestus
    Hephaestus --> LLMAdapter
    
    %% Future connections (dotted)
    Hephaestus -.-> Rhetor
    Rhetor -.-> Engram
    Rhetor -.-> LLMs[External LLMs]
    Hermes -.-> Rhetor
    
    %% Current state
    LLMAdapter --> Claude[Claude API]
    
    %% Notes
    classDef current fill:#f9f,stroke:#333,stroke-width:2px
    classDef future fill:#bbf,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5
    classDef external fill:#bfb,stroke:#333,stroke-width:1px
    
    class Hephaestus,LLMAdapter,Claude current
    class Rhetor,Engram,Hermes future
    class User,LLMs external
```

## Configuration and Environment

```mermaid
graph TD
    subgraph "Environment Variables"
        API[ANTHROPIC_API_KEY]
        Model[DEFAULT_MODEL]
        Host[HOST]
        RhetorPort[RHETOR_PORT]
        HTTPPort[HTTP_PORT]
    end
    
    subgraph "Configuration Module"
        LoadEnv[Load Environment]
        SystemPrompts[System Prompts]
        DefaultSettings[Default Settings]
    end
    
    API --> LoadEnv
    Model --> LoadEnv
    Host --> LoadEnv
    RhetorPort --> LoadEnv
    HTTPPort --> LoadEnv
    
    LoadEnv --> Server[Server Configuration]
    SystemPrompts --> ContextHandler[Context Handler]
    DefaultSettings --> LLMOptions[LLM Options]
```