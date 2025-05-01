# Rhetor

## Overview

Rhetor is Tekton's LLM orchestration and prompt management component, designed to provide a unified interface for interacting with large language models. Named after the Greek term for a master of rhetoric, Rhetor manages the selection, configuration, and utilization of language models, providing sophisticated prompt engineering, context management, and response handling.

## Key Features

- **LLM Provider Integration**: Unified access to multiple LLM providers (OpenAI, Anthropic, etc.)
- **Model Selection**: Intelligent routing of requests to appropriate models based on task requirements
- **Prompt Management**: Library of optimized prompts for different tasks and domains
- **Context Management**: Maintaining and managing conversational context
- **Budget Awareness**: Cost tracking and optimization for LLM API usage
- **Template System**: Reusable prompt templates with parameter substitution
- **Response Streaming**: Real-time streaming of LLM responses
- **Multi-model Collaboration**: Orchestrating multiple models for complex tasks
- **Evaluation Framework**: Automated evaluation of LLM responses
- **Fallback Mechanisms**: Graceful degradation when primary models are unavailable
- **Single Port Architecture**: Unified API access through standardized endpoints

## Architecture

Rhetor follows a modular architecture with the following components:

1. **Core LLM Client**: The foundation that handles communication with LLM providers
   - Provider Clients: Adapters for different LLM providers (OpenAI, Anthropic, etc.)
   - Response Streaming: Handling of real-time response streams
   - Rate Limiting: Managing API request rates
   - Error Handling: Robust handling of API errors and failures

2. **Prompt Engine**: Sophisticated prompt construction and management
   - Template Registry: Storage and retrieval of prompt templates
   - Parameter Substitution: Dynamic insertion of parameters into templates
   - Context Formatting: Preparation of context for LLM consumption
   - Few-shot Learning: Management of examples for in-context learning

3. **Model Router**: Intelligent selection of LLM models
   - Capability Matching: Mapping task requirements to model capabilities
   - Cost Optimization: Selecting models based on budget constraints
   - Performance Tracking: Monitoring model performance
   - Load Balancing: Distributing requests across models and providers

4. **Budget Manager**: Monitoring and controlling LLM API costs
   - Usage Tracking: Recording API usage and costs
   - Budget Enforcement: Ensuring usage stays within budget limits
   - Cost Estimation: Predicting costs before sending requests
   - Usage Analytics: Reporting on usage patterns and trends

5. **API Layer**: Exposing RESTful and WebSocket interfaces
   - Completion Endpoints: Synchronous text generation
   - Streaming Endpoints: Asynchronous, real-time text generation
   - Management Endpoints: Configuration and monitoring
   - Template Endpoints: Prompt template management

## Integration with LLM Providers

Rhetor abstracts away the differences between LLM providers, offering a unified interface:

```python
from rhetor.client import RhetorClient

# Create client
client = RhetorClient()

# Generate text using the most appropriate model
response = await client.generate(
    prompt="Explain quantum computing in simple terms",
    max_tokens=500,
    temperature=0.7
)

# Specify a particular model
response = await client.generate(
    prompt="Explain quantum computing in simple terms",
    model="claude-3-sonnet-20240229",
    max_tokens=500,
    temperature=0.7
)

# Stream response in real-time
async for chunk in client.generate_stream(
    prompt="Write a short story about a robot learning to paint",
    model="gpt-4",
    max_tokens=1000,
    temperature=0.8
):
    print(chunk, end="", flush=True)
```

## Prompt Templates

Rhetor provides a powerful template system for managing prompts:

```python
from rhetor.client import RhetorClient

# Create client
client = RhetorClient()

# Use a built-in template
response = await client.generate_from_template(
    template_name="explain_concept",
    parameters={
        "concept": "quantum computing",
        "audience": "high school students",
        "length": "brief"
    }
)

# Create a custom template
template_id = await client.create_template(
    name="analyze_code",
    content="""Analyze the following {language} code for:
1. Potential bugs
2. Performance issues
3. Security vulnerabilities
4. Style improvements

Code:
```{language}
{code}
```

Provide your analysis with specific recommendations for improvement.
""",
    metadata={
        "description": "Template for code analysis",
        "required_parameters": ["language", "code"],
        "recommended_models": ["claude-3-opus-20240229", "gpt-4"]
    }
)

# Use the custom template
response = await client.generate_from_template(
    template_id=template_id,
    parameters={
        "language": "python",
        "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
    }
)
```

## Model Router

The Model Router intelligently selects the most appropriate model for a given task:

```python
from rhetor.client import RhetorClient

# Create client
client = RhetorClient()

# Let Rhetor select the best model based on the task
response = await client.generate(
    prompt="Explain the theory of relativity",
    routing_parameters={
        "task_type": "explanation",
        "complexity": "high",
        "required_capabilities": ["scientific_knowledge", "explanation_ability"],
        "max_cost": 0.05  # Maximum cost in dollars
    }
)
```

## Budget Management

Rhetor provides tools for monitoring and controlling LLM API costs:

```python
from rhetor.client import RhetorClient

# Create client
client = RhetorClient()

# Get usage statistics
usage = await client.get_usage_stats(
    start_date="2025-01-01",
    end_date="2025-01-31"
)

print(f"Total cost: ${usage['total_cost']}")
print(f"Total tokens: {usage['total_tokens']}")

# Set budget limits
await client.set_budget_limits({
    "daily_limit": 5.00,  # $5 per day
    "monthly_limit": 100.00,  # $100 per month
    "per_request_limit": 0.10  # $0.10 per request
})

# Get cost estimate before sending request
estimate = await client.estimate_cost(
    prompt="Write a 2000 word essay on artificial intelligence",
    model="gpt-4",
    max_tokens=3000
)

print(f"Estimated cost: ${estimate['cost']}")
print(f"Estimated tokens: {estimate['tokens']}")
```

## Integration with Other Components

Rhetor seamlessly integrates with other Tekton components:

- **Hermes**: For service registration and message routing
- **Engram**: For persistent memory and context retrieval
- **Athena**: For knowledge graph access and fact-checking
- **Ergon**: For agent capabilities and specialized tasks
- **LLM Adapter**: For local model access and specialized interfaces

## API Reference

Rhetor provides a comprehensive API:

- `POST /api/rhetor/completions`: Generate text completions
- `POST /api/rhetor/streaming`: Stream text completions
- `POST /api/rhetor/templates`: Create prompt templates
- `GET /api/rhetor/templates`: List available templates
- `POST /api/rhetor/templates/{template_id}/render`: Render a template
- `GET /api/rhetor/models`: List available models
- `GET /api/rhetor/usage`: Get usage statistics
- `POST /api/rhetor/budget`: Set budget limits
- `POST /api/rhetor/evaluate`: Evaluate model responses

## WebSocket API

Rhetor also provides WebSocket endpoints for real-time interactions:

- `ws://localhost:8005/ws/rhetor/streaming`: Stream completions
- `ws://localhost:8005/ws/rhetor/chat`: Interactive chat sessions

## Deployment

Rhetor can be deployed in various configurations:

```bash
# Start Rhetor with default settings
cd Rhetor
python -m rhetor.api.app

# Start with specific configuration
RHETOR_PORT=8005 RHETOR_LOG_LEVEL=debug python -m rhetor.api.app

# Start with Docker
docker run -p 8005:8005 -v ~/.rhetor:/app/.rhetor -e OPENAI_API_KEY=sk-... tekton/rhetor
```

## Configuration

Rhetor is configured through environment variables and configuration files:

```bash
# Core Configuration
RHETOR_HOST=0.0.0.0
RHETOR_PORT=8005
RHETOR_LOG_LEVEL=info

# Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
COHERE_API_KEY=...

# Budget Configuration
RHETOR_DAILY_BUDGET=5.00
RHETOR_MONTHLY_BUDGET=100.00

# Model Selection
RHETOR_DEFAULT_MODEL=gpt-3.5-turbo
RHETOR_DEFAULT_PROVIDER=openai
```

## Getting Started

To use Rhetor in your Tekton component:

1. Import the Rhetor client:

```python
from rhetor.client import RhetorClient
```

2. Create a client instance:

```python
client = RhetorClient(host="localhost", port=8005)
```

3. Generate text:

```python
response = await client.generate(
    prompt="Hello, how can you help me today?",
    temperature=0.7
)
print(response.text)
```

4. Use templates:

```python
response = await client.generate_from_template(
    template_name="introduction",
    parameters={"role": "assistant", "capabilities": ["coding", "explanation"]}
)
print(response.text)
```

For more detailed information, see the [API Reference](./API_REFERENCE.md) and [Integration Guide](./INTEGRATION_GUIDE.md).