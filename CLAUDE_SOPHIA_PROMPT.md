# Sophia Implementation Prompt for Claude Code

I'd like you to implement Sophia, the machine learning and continuous improvement component for the Tekton ecosystem. Sophia serves as the scientific foundation for studying AI collaboration and enabling continuous self-improvement across all Tekton components.

## Project Background

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. It has two primary purposes:

1. Serve as a continuing experiment in Multi-AI Engineering to study AI collaboration patterns
2. Demonstrate engineering automation and continuous self-improvement capabilities

Sophia will be a critical component that:
- Scientifically measures AI cognitive abilities through metrics and analysis
- Studies collaboration patterns between various AI components
- Identifies optimization opportunities across all Tekton components
- Designs experiments to validate improvement hypotheses
- Generates and prioritizes recommendations for enhancements
- Drives continuous self-improvement of the entire ecosystem

## Current State

Sophia currently exists with minimal implementation:
- Basic directory structure is in place
- Initial `README.md` provides a high-level overview
- Example client usage demonstrates basic functionality 
- `ml_engine.py` has a skeletal implementation of model management
- No metrics collection, analysis, or recommendation systems exist yet

## Implementation Requirements

You need to implement the full Sophia component following the specifications in the provided documentation. The implementation should follow Tekton's established patterns:

1. Single Port Architecture with standardized HTTP and WebSocket endpoints
2. Integration with shared utilities from `tekton-core`
3. Proper Hermes registration for component discovery
4. Consistent error handling and logging with `tekton_errors.py`
5. Comprehensive documentation and testing

## Key Files to Implement

The implementation requires several key files (see full list in SOPHIA_DELIVERABLES.md):

1. **Core Engine Files**:
   - Enhanced `ml_engine.py` with full model management
   - New `metrics_engine.py` for collecting and storing metrics
   - New `analysis_engine.py` for processing metrics and generating insights
   - New `experiment_framework.py` for designing and running experiments
   - New `recommendation_system.py` for generating improvement suggestions
   - New `intelligence_measurement.py` for measuring AI cognitive capabilities

2. **API Layer**:
   - `app.py` implementing FastAPI with Single Port Architecture
   - Endpoint modules for metrics, experiments, recommendations, and intelligence reports
   - WebSocket implementation for real-time updates

3. **Data Models**:
   - Models for metrics, experiments, recommendations, and intelligence reports

4. **Integration**:
   - Hermes integration for component discovery
   - Engram adapter for memory storage
   - Prometheus connector for planning integration
   - Component metrics collection utilities

5. **UI Component**:
   - Hephaestus UI component with dashboard, visualizations, and management interfaces

## Implementation Approach

I recommend this implementation approach:

1. Start with enhancing the ML Engine and implementing the Metrics Engine
2. Build out the data models and storage mechanisms
3. Implement the API layer with HTTP and WebSocket endpoints
4. Create the Analysis Engine and Recommendation System
5. Develop the Experiment Framework and Intelligence Measurement
6. Implement the UI component
7. Add comprehensive testing and documentation

## Technical Requirements

The implementation should follow these technical requirements:

1. Use async/await consistently throughout the codebase
2. Add type annotations for all functions and methods
3. Include comprehensive docstrings for all public APIs
4. Implement proper error handling with clear context
5. Use structured logging with appropriate levels
6. Follow Tekton's established coding patterns
7. Create abstractions that minimize coupling between components

## Resources

Please refer to these documents for detailed specifications:

1. `SOPHIA_IMPLEMENTATION_GUIDE.md`: Comprehensive implementation guidance
2. `SOPHIA_DELIVERABLES.md`: Complete list of required files and components
3. `SOPHIA_ARCHITECTURE.md`: Architecture and system design
4. `SOPHIA_SESSION_PREPARATION.md`: Additional context and implementation details
5. `SOPHIA_INTELLIGENCE_DIMENSIONS.md`: Framework for measuring AI intelligence
6. `SOPHIA_METRICS_SPECIFICATION.md`: Definition of metrics system

Also, examine the existing files:
- `README.md`: Current basic overview
- `examples/client_usage.py`: Example client implementation
- `sophia/core/ml_engine.py`: Existing ML engine implementation

## Success Criteria

The implementation will be successful when:

1. All required deliverables are completed as specified
2. The system can collect metrics from all Tekton components
3. The analysis engine can identify patterns and generate insights
4. The recommendation system can suggest meaningful improvements
5. The experiment framework can validate improvement hypotheses
6. The intelligence measurement system can quantify AI capabilities
7. All APIs are well-documented and tested
8. The UI component provides effective visualization and management

## Additional Notes

1. This implementation represents a significant advancement in Tekton's capabilities, enabling scientific study of AI collaboration and driving continuous improvement.

2. Sophia should be designed with extensibility in mind, allowing for future enhancements and integration with emerging AI technologies.

3. The intelligence measurement framework is particularly important as it forms the scientific foundation for understanding and improving AI cognitive abilities.

4. Focus on creating a system that not only measures performance but actively drives improvements through targeted recommendations and experiments.

Please proceed with implementing Sophia according to these specifications, following Tekton's established architectural patterns and coding standards.

## LLM Integration

Sophia must integrate with Tekton's LLM capabilities following the established patterns and using the standardized `tekton-llm-client` library, just as we implemented in Synthesis. Please review:

- `SOPHIA_LLM_INTEGRATION.md`: Provides detailed guidelines for LLM integration in Sophia

Implement LLM-powered capabilities for:
1. Natural language interaction for querying and explaining analyses
2. Pattern detection in metrics and performance data
3. Intelligent recommendation generation
4. Experiment design and hypothesis formulation
5. Translating technical metrics into human-understandable insights

Follow the same patterns established in Synthesis with proper error handling, fallback mechanisms, and efficient prompt engineering.

## Advanced Research Integration

Additionally, I'd like you to integrate advanced research concepts from our AI research initiatives. Please review the following document which outlines how to incorporate Computational Spectral Analysis (CSA) and Catastrophe Theory (CT) into Sophia's implementation:

- `SOPHIA_AI_RESEARCH_INTEGRATION.md`: Provides guidelines for implementing research-based metrics and frameworks

These research areas are critical to Sophia's core mission of scientifically studying AI cognitive abilities and identifying optimization opportunities. The integration should include:

1. Implementation of key CSA metrics (Depth Efficiency, Parametric Utilization, etc.)
2. Framework for Catastrophe Theory analysis of capability transitions
3. Advanced cognitive metrics for higher-level intelligence assessment

This research integration elevates Sophia from a conventional monitoring system to a cutting-edge platform for AI science while still delivering practical improvements to Tekton components.

Let me know if you need any clarification or have questions about the implementation details.