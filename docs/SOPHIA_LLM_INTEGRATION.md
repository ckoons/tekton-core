# Sophia LLM Integration Guide

This document outlines how Sophia should integrate with Tekton's LLM capabilities following the established patterns and leveraging the standardized `tekton-llm-client` library.

## Overview

Sophia requires robust LLM integration for several critical functions:

1. Natural language interaction for analysis querying and explanation
2. Pattern analysis in unstructured feedback and observations
3. Intelligent recommendation generation based on collected metrics
4. Experiment design and hypothesis formulation
5. Translation between technical metrics and human-understandable insights

## LLM Integration Requirements

### 1. Use Standardized `tekton-llm-client`

Sophia must use the standardized `tekton-llm-client` library following the same patterns implemented in other components like Synthesis:

```python
from tekton_llm_client import Client
from tekton_llm_client.models import ChatMessage, ChatCompletionOptions

async def get_llm_client():
    """Get a configured LLM client."""
    return Client(
        base_url=os.getenv("TEKTON_LLM_URL", "http://localhost:8001"),
        default_model=os.getenv("TEKTON_LLM_MODEL", "default"),
        timeout=60
    )

async def generate_recommendation(metrics_data, component_id):
    """Generate a recommendation based on metrics data."""
    client = await get_llm_client()
    
    messages = [
        ChatMessage(
            role="system",
            content="You are Sophia, Tekton's machine learning and continuous improvement component. "
                   "Analyze the provided metrics and generate improvement recommendations."
        ),
        ChatMessage(
            role="user",
            content=f"Generate an improvement recommendation for component {component_id} "
                   f"based on the following metrics data:\n\n{json.dumps(metrics_data, indent=2)}"
        )
    ]
    
    options = ChatCompletionOptions(
        temperature=0.2,
        max_tokens=1000,
        stream=False
    )
    
    response = await client.chat_completion(messages=messages, options=options)
    return response.choices[0].message.content
```

### 2. Support WebSocket Streaming

Implement streaming for long-running analyses and real-time updates:

```python
async def stream_analysis_explanation(analysis_id, recipient_ws):
    """Stream an explanation of the analysis to a WebSocket client."""
    client = await get_llm_client()
    
    messages = [
        ChatMessage(
            role="system",
            content="You are Sophia, Tekton's machine learning and continuous improvement component. "
                   "Explain analysis results in clear, concise language."
        ),
        ChatMessage(
            role="user",
            content=f"Explain analysis {analysis_id} in detail, covering the methods used, "
                   f"findings, and recommendations."
        )
    ]
    
    options = ChatCompletionOptions(
        temperature=0.3,
        max_tokens=2000,
        stream=True
    )
    
    async for chunk in client.stream_chat_completion(messages=messages, options=options):
        content = chunk.choices[0].delta.content
        if content:
            await recipient_ws.send_text(json.dumps({
                "type": "analysis_explanation",
                "content": content
            }))
```

### 3. Implement Fallback Mechanisms

Ensure Sophia can operate with degraded LLM capabilities:

```python
from tekton_llm_client.adapters import FallbackAdapter

def configure_llm_client_with_fallback():
    """Configure LLM client with fallback capabilities."""
    return Client(
        base_url=os.getenv("TEKTON_LLM_URL", "http://localhost:8001"),
        default_model=os.getenv("TEKTON_LLM_MODEL", "default"),
        adapter=FallbackAdapter(
            fallback_models=["local-small-model", "rule-based"],
            max_retries=3,
            timeout=30
        )
    )
```

### 4. Create Model-Specific Prompts

Design prompts optimized for different model capabilities:

```python
SYSTEM_PROMPTS = {
    "default": "You are Sophia, Tekton's machine learning and continuous improvement component...",
    "analysis": "You are Sophia's Analysis Engine. Examine the following metrics and identify patterns...",
    "recommendation": "You are Sophia's Recommendation System. Generate specific, actionable recommendations..."
}

PROMPT_TEMPLATES = {
    "metrics_analysis": "Analyze the following metrics data from {component_id}:\n\n{metrics_json}\n\n"
                       "Identify patterns, anomalies, and potential optimization opportunities.",
    
    "experiment_design": "Design an experiment to test the hypothesis: {hypothesis}\n\n"
                        "Available components: {components_list}\n"
                        "Recent metrics: {metrics_summary}",
    
    "recommendation_generation": "Based on the following analysis:\n\n{analysis_summary}\n\n"
                               "Generate {count} specific recommendations to improve {target}."
}
```

### 5. Support Multi-Model Integration

Enable Sophia to leverage different models for different tasks:

```python
MODEL_CONFIGURATION = {
    "analysis": {
        "preferred_model": "claude-3-opus-20240229",
        "fallback_model": "claude-3-haiku-20240307",
        "local_fallback": "mistral-7b-instruct",
        "temperature": 0.2,
        "max_tokens": 2000
    },
    "recommendation": {
        "preferred_model": "claude-3-sonnet-20240229",
        "fallback_model": "claude-3-haiku-20240307",
        "local_fallback": "llama-3-8b",
        "temperature": 0.4,
        "max_tokens": 1000
    },
    "explanation": {
        "preferred_model": "claude-3-sonnet-20240229",
        "fallback_model": "gpt-3.5-turbo",
        "local_fallback": "phi-2",
        "temperature": 0.7,
        "max_tokens": 1500
    }
}

async def get_task_specific_client(task_type):
    """Get an LLM client configured for a specific task type."""
    config = MODEL_CONFIGURATION.get(task_type, MODEL_CONFIGURATION["analysis"])
    
    return Client(
        base_url=os.getenv("TEKTON_LLM_URL", "http://localhost:8001"),
        default_model=config["preferred_model"],
        adapter=FallbackAdapter(
            fallback_models=[config["fallback_model"], config["local_fallback"]],
            max_retries=2
        )
    )
```

## Core LLM-Powered Functions

Sophia should implement the following LLM-powered functions:

### 1. Metric Pattern Analysis

```python
async def analyze_metric_patterns(metrics_data, component_id=None, time_period=None):
    """Analyze patterns in collected metrics using LLM."""
    client = await get_task_specific_client("analysis")
    
    # Prepare context with relevant metrics
    context = prepare_metrics_context(metrics_data, component_id, time_period)
    
    # Construct prompt
    prompt = PROMPT_TEMPLATES["metrics_analysis"].format(
        component_id=component_id or "all components",
        metrics_json=json.dumps(context, indent=2)
    )
    
    # Get analysis from LLM
    result = await client.analyze_with_llm(
        system_prompt=SYSTEM_PROMPTS["analysis"],
        user_prompt=prompt
    )
    
    # Extract structured analysis from result
    return extract_structured_analysis(result)
```

### 2. Recommendation Generation

```python
async def generate_recommendations(analysis_results, target_component=None, count=3):
    """Generate recommendations based on analysis results."""
    client = await get_task_specific_client("recommendation")
    
    # Create summary of analysis results
    analysis_summary = summarize_analysis(analysis_results)
    
    # Construct prompt
    prompt = PROMPT_TEMPLATES["recommendation_generation"].format(
        analysis_summary=analysis_summary,
        count=count,
        target=target_component or "the Tekton ecosystem"
    )
    
    # Get recommendations from LLM
    result = await client.analyze_with_llm(
        system_prompt=SYSTEM_PROMPTS["recommendation"],
        user_prompt=prompt
    )
    
    # Extract structured recommendations
    return extract_structured_recommendations(result)
```

### 3. Experiment Design

```python
async def design_experiment(hypothesis, available_components=None):
    """Design an experiment to test a hypothesis."""
    client = await get_task_specific_client("analysis")
    
    # Get recent metrics summary
    metrics_summary = await get_recent_metrics_summary()
    
    # Construct prompt
    prompt = PROMPT_TEMPLATES["experiment_design"].format(
        hypothesis=hypothesis,
        components_list=available_components or "all components",
        metrics_summary=metrics_summary
    )
    
    # Get experiment design from LLM
    result = await client.analyze_with_llm(
        system_prompt=SYSTEM_PROMPTS["analysis"],
        user_prompt=prompt
    )
    
    # Extract structured experiment design
    return extract_structured_experiment(result)
```

### 4. Natural Language Interface

```python
async def process_natural_language_query(query, context=None):
    """Process a natural language query about metrics or analysis."""
    client = await get_llm_client()
    
    # Create context with relevant information
    if context is None:
        context = await build_query_context()
    
    # Construct messages
    messages = [
        ChatMessage(
            role="system",
            content=SYSTEM_PROMPTS["default"]
        ),
        ChatMessage(
            role="user",
            content=f"Context information:\n{json.dumps(context, indent=2)}\n\nUser query: {query}"
        )
    ]
    
    # Get response from LLM
    response = await client.chat_completion(messages=messages)
    
    return response.choices[0].message.content
```

## UI Component Integration

The Sophia UI component should include LLM-powered features:

```javascript
// sophia-component.js

class SophiaComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.llmEnabled = true;
    this.initComponent();
  }
  
  async initComponent() {
    // Set up component structure
    this.shadowRoot.innerHTML = `
      <div class="sophia-container">
        <!-- Component HTML structure -->
        <div class="sophia-chat">
          <div class="chat-messages" id="chat-messages"></div>
          <div class="chat-input">
            <input type="text" id="query-input" placeholder="Ask Sophia about your metrics...">
            <button id="send-button">Send</button>
          </div>
        </div>
      </div>
    `;
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Check LLM availability
    await this.checkLlmAvailability();
  }
  
  async checkLlmAvailability() {
    try {
      const response = await fetch('/api/llm/status');
      const status = await response.json();
      this.llmEnabled = status.available;
      this.updateUiForLlmStatus();
    } catch (e) {
      console.error('Error checking LLM status:', e);
      this.llmEnabled = false;
      this.updateUiForLlmStatus();
    }
  }
  
  async sendQuery(query) {
    if (!this.llmEnabled) {
      this.addMessage('system', 'LLM capabilities are currently unavailable. Basic analytics are still functional.');
      return;
    }
    
    this.addMessage('user', query);
    
    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      const result = await response.json();
      this.addMessage('assistant', result.response);
      
      // If analysis was performed, update visualizations
      if (result.analysis) {
        this.updateVisualizations(result.analysis);
      }
    } catch (e) {
      console.error('Error sending query:', e);
      this.addMessage('system', 'An error occurred processing your query.');
    }
  }
  
  // Other component methods...
}

customElements.define('sophia-component', SophiaComponent);
```

## Best Practices

1. **Prompt Engineering**:
   - Create task-specific prompts with clear instructions
   - Include relevant context but avoid unnecessary details
   - Use consistent formatting for different query types
   - Provide examples for complex response formats

2. **Error Handling**:
   - Implement comprehensive error handling for LLM requests
   - Include fallback mechanisms for all LLM-dependent functions
   - Log failed requests with sufficient context for debugging
   - Provide graceful degradation when LLM services are unavailable

3. **Performance Optimization**:
   - Cache frequent LLM responses where appropriate
   - Use streaming for long-running analyses
   - Optimize token usage with concise prompts
   - Balance between query complexity and response quality

4. **Security Considerations**:
   - Validate all inputs before sending to LLM
   - Sanitize outputs before processing or display
   - Limit the scope of automatically executed recommendations
   - Implement appropriate authentication for LLM-powered endpoints

## Implementation Example from Synthesis

Following the pattern established in Synthesis, Sophia should implement LLM integration as follows:

```python
# sophia/core/llm_integration.py

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union

from tekton_llm_client import Client
from tekton_llm_client.models import ChatMessage, ChatCompletionOptions
from tekton_llm_client.adapters import FallbackAdapter

logger = logging.getLogger(__name__)

class LlmIntegration:
    """LLM integration for Sophia's analysis and recommendation capabilities."""
    
    def __init__(self):
        """Initialize the LLM integration."""
        self.base_url = os.getenv("TEKTON_LLM_URL", "http://localhost:8001")
        self.default_model = os.getenv("TEKTON_LLM_MODEL", "default")
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize the LLM client."""
        try:
            self.client = Client(
                base_url=self.base_url,
                default_model=self.default_model,
                adapter=FallbackAdapter(
                    fallback_models=["claude-3-haiku-20240307", "local-model"],
                    max_retries=2
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return False
    
    async def analyze_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metrics using LLM."""
        if not self.client:
            if not await self.initialize():
                logger.warning("LLM client unavailable for metrics analysis")
                return {"error": "LLM client unavailable"}
        
        try:
            messages = [
                ChatMessage(
                    role="system",
                    content="You are Sophia's metrics analysis engine. Analyze the provided metrics "
                           "and identify patterns, anomalies, and potential improvements."
                ),
                ChatMessage(
                    role="user",
                    content=f"Analyze the following metrics data:\n\n{json.dumps(metrics, indent=2)}"
                )
            ]
            
            options = ChatCompletionOptions(
                temperature=0.2,
                max_tokens=2000
            )
            
            response = await self.client.chat_completion(messages=messages, options=options)
            content = response.choices[0].message.content
            
            # Parse the response into structured analysis
            # This would typically involve parsing JSON or structured text
            return {
                "analysis": content,
                "structured": self._extract_structured_analysis(content)
            }
        except Exception as e:
            logger.error(f"Error analyzing metrics with LLM: {e}")
            return {"error": str(e)}
    
    async def generate_recommendations(self, 
                                     analysis: Dict[str, Any], 
                                     component_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis results."""
        if not self.client:
            if not await self.initialize():
                logger.warning("LLM client unavailable for recommendation generation")
                return [{"error": "LLM client unavailable"}]
        
        try:
            component_context = f"for component {component_id}" if component_id else "for the Tekton ecosystem"
            
            messages = [
                ChatMessage(
                    role="system",
                    content="You are Sophia's recommendation engine. Generate specific, actionable "
                           "recommendations based on the analysis results."
                ),
                ChatMessage(
                    role="user",
                    content=f"Generate recommendations {component_context} based on the following "
                           f"analysis:\n\n{json.dumps(analysis, indent=2)}\n\n"
                           f"Format your response as a JSON array of recommendation objects with "
                           f"'title', 'description', 'impact', and 'effort' fields."
                )
            ]
            
            options = ChatCompletionOptions(
                temperature=0.3,
                max_tokens=1500
            )
            
            response = await self.client.chat_completion(messages=messages, options=options)
            content = response.choices[0].message.content
            
            # Extract JSON array from the response
            return self._extract_json_recommendations(content)
        except Exception as e:
            logger.error(f"Error generating recommendations with LLM: {e}")
            return [{"error": str(e)}]
    
    def _extract_structured_analysis(self, content: str) -> Dict[str, Any]:
        """Extract structured analysis from LLM response."""
        # Implementation to parse text into structured format
        # This would typically involve regex or parsing logic
        return {"raw_analysis": content}  # Simplified return
    
    def _extract_json_recommendations(self, content: str) -> List[Dict[str, Any]]:
        """Extract JSON recommendations from LLM response."""
        try:
            # Find JSON array in the content
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback to basic parsing if JSON not found
                return [{"title": "Recommendation", "description": content}]
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON recommendations")
            return [{"title": "Recommendation", "description": content}]

# Singleton instance
_llm_integration = LlmIntegration()

async def get_llm_integration() -> LlmIntegration:
    """Get the global LLM integration instance."""
    if not _llm_integration.client:
        await _llm_integration.initialize()
    return _llm_integration
```

## Conclusion

By following these LLM integration patterns established in Synthesis and other Tekton components, Sophia will maintain consistency with the broader ecosystem while leveraging LLM capabilities for its unique scientific and improvement functions. The integration should be designed for flexibility, reliability, and maintainability, with appropriate fallback mechanisms to ensure Sophia remains functional even when LLM services are limited or unavailable.