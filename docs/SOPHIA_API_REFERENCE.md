# Sophia API Reference

This document provides a comprehensive reference for the Sophia API, including all endpoints, request/response formats, and usage examples.

## Overview

Sophia provides a unified API following the Single Port Architecture pattern, with a base URL of `http://localhost:8006` by default. The API is organized into logical sections:

- **Metrics API**: Collection and analysis of performance metrics
- **Experiments API**: Design, execution, and analysis of experiments
- **Recommendations API**: Generation and tracking of improvement recommendations
- **Intelligence API**: Measurement and comparison of AI cognitive capabilities
- **Components API**: Registration and analysis of Tekton components
- **Research API**: Creation and management of research projects

## Base URL

The base URL for all API endpoints is configurable via the `SOPHIA_PORT` environment variable:

- Default: `http://localhost:8006`
- With custom port: `http://localhost:{SOPHIA_PORT}`

## Authentication

*Note: Authentication is planned for future implementation.*

## Common Response Format

Most API responses follow a common format:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Operation-specific response data
  }
}
```

Error responses include:

```json
{
  "success": false,
  "message": "Error message describing what went wrong",
  "error": {
    "code": "ERROR_CODE",
    "details": { /* Additional error details */ }
  }
}
```

## Metrics API

### Submit a Metric

Submit a single metric measurement.

**Endpoint**: `POST /api/metrics`

**Request**:
```json
{
  "metric_id": "component.performance.latency",
  "value": 42.5,
  "source": "my_component",
  "timestamp": "2025-04-28T12:34:56Z",
  "context": {
    "operation": "query",
    "load": "high"
  },
  "tags": ["performance", "latency"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Metric submitted successfully",
  "data": {
    "metric_id": "12345678-1234-5678-1234-567812345678"
  }
}
```

### Query Metrics

Query metrics with filtering.

**Endpoint**: `GET /api/metrics`

**Parameters**:
- `metric_id` (optional): Filter by metric ID
- `source` (optional): Filter by source
- `tags` (optional): Comma-separated list of tags
- `start_time` (optional): Start time in ISO format
- `end_time` (optional): End time in ISO format
- `min_value` (optional): Minimum value filter
- `max_value` (optional): Maximum value filter
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Offset for pagination (default: 0)
- `sort` (optional): Sort order (e.g., "timestamp:desc")

**Response**:
```json
{
  "data": [
    {
      "metric_id": "component.performance.latency",
      "value": 42.5,
      "source": "my_component",
      "timestamp": "2025-04-28T12:34:56Z",
      "context": {
        "operation": "query",
        "load": "high"
      },
      "tags": ["performance", "latency"]
    },
    // Additional metrics...
  ],
  "pagination": {
    "total": 243,
    "limit": 100,
    "offset": 0
  }
}
```

### Aggregate Metrics

Aggregate metrics for analysis.

**Endpoint**: `POST /api/metrics/aggregate`

**Request**:
```json
{
  "metric_id": "component.performance.latency",
  "aggregation": "avg",
  "interval": "1h",
  "source": "my_component",
  "tags": ["performance"],
  "start_time": "2025-04-01T00:00:00Z",
  "end_time": "2025-04-28T23:59:59Z"
}
```

**Response**:
```json
{
  "data": {
    "aggregation": "avg",
    "interval": "1h",
    "series": [
      {
        "timestamp": "2025-04-01T00:00:00Z",
        "value": 38.2
      },
      {
        "timestamp": "2025-04-01T01:00:00Z",
        "value": 42.5
      },
      // Additional intervals...
    ],
    "summary": {
      "min": 35.1,
      "max": 67.3,
      "avg": 41.7,
      "count": 672
    }
  }
}
```

### Get Metric Definitions

Get definitions for available metrics.

**Endpoint**: `GET /api/metrics/definitions`

**Parameters**:
- `component` (optional): Filter by component
- `category` (optional): Filter by category

**Response**:
```json
{
  "data": {
    "component.performance.latency": {
      "name": "Operation Latency",
      "description": "Time taken to complete an operation",
      "type": "gauge",
      "unit": "milliseconds",
      "component": "component",
      "category": "performance",
      "tags": ["performance", "latency"]
    },
    // Additional definitions...
  }
}
```

## Experiments API

### Create an Experiment

Create a new experiment.

**Endpoint**: `POST /api/experiments`

**Request**:
```json
{
  "name": "Latency Optimization",
  "description": "Testing a new algorithm to reduce latency",
  "experiment_type": "a_b_test",
  "target_components": ["my_component"],
  "hypothesis": "The new algorithm reduces latency by 20%",
  "metrics": ["component.performance.latency"],
  "parameters": {
    "control": {"algorithm": "current"},
    "treatment": {"algorithm": "new"}
  },
  "start_time": "2025-05-01T00:00:00Z",
  "end_time": "2025-05-08T00:00:00Z",
  "sample_size": 10000,
  "min_confidence": 0.95,
  "tags": ["performance", "optimization"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Experiment created successfully",
  "data": {
    "experiment_id": "exp-12345678"
  }
}
```

### Query Experiments

Query experiments with filtering.

**Endpoint**: `GET /api/experiments`

**Parameters**:
- `status` (optional): Filter by status
- `experiment_type` (optional): Filter by experiment type
- `target_components` (optional): Comma-separated list of target components
- `tags` (optional): Comma-separated list of tags
- `start_after` (optional): Filter by start time after
- `start_before` (optional): Filter by start time before
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Response**:
```json
{
  "data": [
    {
      "experiment_id": "exp-12345678",
      "name": "Latency Optimization",
      "status": "running",
      "experiment_type": "a_b_test",
      "target_components": ["my_component"],
      "start_time": "2025-05-01T00:00:00Z",
      "end_time": "2025-05-08T00:00:00Z",
      "progress": 0.35,
      "tags": ["performance", "optimization"]
    },
    // Additional experiments...
  ],
  "pagination": {
    "total": 12,
    "limit": 100,
    "offset": 0
  }
}
```

### Get Experiment Details

Get details of a specific experiment.

**Endpoint**: `GET /api/experiments/{id}`

**Path Parameters**:
- `id`: Experiment ID

**Response**:
```json
{
  "data": {
    "experiment_id": "exp-12345678",
    "name": "Latency Optimization",
    "description": "Testing a new algorithm to reduce latency",
    "status": "running",
    "experiment_type": "a_b_test",
    "target_components": ["my_component"],
    "hypothesis": "The new algorithm reduces latency by 20%",
    "metrics": ["component.performance.latency"],
    "parameters": {
      "control": {"algorithm": "current"},
      "treatment": {"algorithm": "new"}
    },
    "start_time": "2025-05-01T00:00:00Z",
    "end_time": "2025-05-08T00:00:00Z",
    "actual_start_time": "2025-05-01T00:00:12Z",
    "sample_size": {
      "target": 10000,
      "current": 3500,
      "control": 1750,
      "treatment": 1750
    },
    "min_confidence": 0.95,
    "current_confidence": 0.82,
    "preliminary_results": {
      "component.performance.latency": {
        "control": {
          "avg": 120.5,
          "p95": 180.2
        },
        "treatment": {
          "avg": 95.3,
          "p95": 142.8
        }
      }
    },
    "progress": 0.35,
    "tags": ["performance", "optimization"],
    "created_at": "2025-04-28T12:34:56Z",
    "created_by": "system"
  }
}
```

### Update an Experiment

Update an existing experiment.

**Endpoint**: `PUT /api/experiments/{id}`

**Path Parameters**:
- `id`: Experiment ID

**Request**:
```json
{
  "description": "Updated description",
  "end_time": "2025-05-10T00:00:00Z",
  "sample_size": 15000,
  "tags": ["performance", "optimization", "high-priority"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Experiment updated successfully",
  "data": {
    "experiment_id": "exp-12345678"
  }
}
```

### Start an Experiment

Start an experiment.

**Endpoint**: `POST /api/experiments/{id}/start`

**Path Parameters**:
- `id`: Experiment ID

**Response**:
```json
{
  "success": true,
  "message": "Experiment started successfully",
  "data": {
    "experiment_id": "exp-12345678",
    "status": "running",
    "start_time": "2025-04-28T12:34:56Z"
  }
}
```

### Stop an Experiment

Stop an experiment.

**Endpoint**: `POST /api/experiments/{id}/stop`

**Path Parameters**:
- `id`: Experiment ID

**Response**:
```json
{
  "success": true,
  "message": "Experiment stopped successfully",
  "data": {
    "experiment_id": "exp-12345678",
    "status": "stopped",
    "stop_time": "2025-04-28T15:30:45Z"
  }
}
```

### Analyze Experiment Results

Analyze the results of an experiment.

**Endpoint**: `POST /api/experiments/{id}/analyze`

**Path Parameters**:
- `id`: Experiment ID

**Request**:
```json
{
  "confidence_level": 0.95,
  "include_segments": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Experiment analysis completed",
  "data": {
    "experiment_id": "exp-12345678",
    "analysis_id": "analysis-87654321",
    "status": "completed"
  }
}
```

### Get Experiment Results

Get the results of a completed experiment.

**Endpoint**: `GET /api/experiments/{id}/results`

**Path Parameters**:
- `id`: Experiment ID

**Response**:
```json
{
  "data": {
    "experiment_id": "exp-12345678",
    "name": "Latency Optimization",
    "status": "completed",
    "metrics": {
      "component.performance.latency": {
        "control": {
          "avg": 120.5,
          "p95": 180.2,
          "sample_size": 5000
        },
        "treatment": {
          "avg": 95.3,
          "p95": 142.8,
          "sample_size": 5000
        }
      }
    },
    "analysis": {
      "statistical_significance": true,
      "p_value": 0.001,
      "effect_size": {
        "relative": -0.209,
        "absolute": -25.2
      },
      "confidence_interval": {
        "lower": -29.8,
        "upper": -20.6
      }
    },
    "conclusion": "The treatment shows a statistically significant reduction in latency (20.9% reduction, p=0.001)",
    "recommendations": [
      {
        "recommendation_id": "rec-12345678",
        "title": "Implement new algorithm across all components",
        "priority": "high"
      }
    ]
  }
}
```

## Recommendations API

### Create a Recommendation

Create a new improvement recommendation.

**Endpoint**: `POST /api/recommendations`

**Request**:
```json
{
  "title": "Implement new algorithm across all components",
  "description": "The new algorithm has been shown to reduce latency by 20% in experiments. It should be implemented across all components to improve system performance.",
  "recommendation_type": "performance_improvement",
  "target_components": ["component_a", "component_b", "component_c"],
  "priority": "high",
  "rationale": "Experiment exp-12345678 demonstrated a statistically significant reduction in latency (20.9%, p=0.001).",
  "expected_impact": {
    "performance": "high",
    "resource_usage": "medium",
    "reliability": "neutral"
  },
  "implementation_complexity": "medium",
  "supporting_evidence": {
    "experiment_results": {
      "experiment_id": "exp-12345678",
      "effect_size": -0.209,
      "p_value": 0.001
    },
    "metrics": {
      "component.performance.latency": {
        "before": 120.5,
        "after": 95.3
      }
    }
  },
  "experiment_ids": ["exp-12345678"],
  "tags": ["performance", "optimization", "algorithm"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Recommendation created successfully",
  "data": {
    "recommendation_id": "rec-12345678"
  }
}
```

### Query Recommendations

Query recommendations with filtering.

**Endpoint**: `GET /api/recommendations`

**Parameters**:
- `status` (optional): Filter by status
- `recommendation_type` (optional): Filter by recommendation type
- `priority` (optional): Filter by priority
- `target_components` (optional): Comma-separated list of target components
- `experiment_ids` (optional): Comma-separated list of experiment IDs
- `tags` (optional): Comma-separated list of tags
- `created_after` (optional): Filter by creation time after
- `created_before` (optional): Filter by creation time before
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Response**:
```json
{
  "data": [
    {
      "recommendation_id": "rec-12345678",
      "title": "Implement new algorithm across all components",
      "recommendation_type": "performance_improvement",
      "target_components": ["component_a", "component_b", "component_c"],
      "priority": "high",
      "status": "pending",
      "created_at": "2025-04-28T12:34:56Z",
      "tags": ["performance", "optimization", "algorithm"]
    },
    // Additional recommendations...
  ],
  "pagination": {
    "total": 42,
    "limit": 100,
    "offset": 0
  }
}
```

### Get Recommendation Details

Get details of a specific recommendation.

**Endpoint**: `GET /api/recommendations/{id}`

**Path Parameters**:
- `id`: Recommendation ID

**Response**:
```json
{
  "data": {
    "recommendation_id": "rec-12345678",
    "title": "Implement new algorithm across all components",
    "description": "The new algorithm has been shown to reduce latency by 20% in experiments. It should be implemented across all components to improve system performance.",
    "recommendation_type": "performance_improvement",
    "target_components": ["component_a", "component_b", "component_c"],
    "priority": "high",
    "status": "pending",
    "rationale": "Experiment exp-12345678 demonstrated a statistically significant reduction in latency (20.9%, p=0.001).",
    "expected_impact": {
      "performance": "high",
      "resource_usage": "medium",
      "reliability": "neutral"
    },
    "implementation_complexity": "medium",
    "supporting_evidence": {
      "experiment_results": {
        "experiment_id": "exp-12345678",
        "effect_size": -0.209,
        "p_value": 0.001
      },
      "metrics": {
        "component.performance.latency": {
          "before": 120.5,
          "after": 95.3
        }
      }
    },
    "experiment_ids": ["exp-12345678"],
    "tags": ["performance", "optimization", "algorithm"],
    "created_at": "2025-04-28T12:34:56Z",
    "created_by": "system",
    "updated_at": "2025-04-28T12:34:56Z",
    "status_history": [
      {
        "status": "pending",
        "timestamp": "2025-04-28T12:34:56Z",
        "notes": "Initial recommendation creation"
      }
    ]
  }
}
```

### Update a Recommendation

Update an existing recommendation.

**Endpoint**: `PUT /api/recommendations/{id}`

**Path Parameters**:
- `id`: Recommendation ID

**Request**:
```json
{
  "description": "Updated description",
  "priority": "critical",
  "implementation_complexity": "low",
  "tags": ["performance", "optimization", "algorithm", "high-priority"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Recommendation updated successfully",
  "data": {
    "recommendation_id": "rec-12345678"
  }
}
```

### Update Recommendation Status

Update the status of a recommendation.

**Endpoint**: `POST /api/recommendations/{id}/status/{status}`

**Path Parameters**:
- `id`: Recommendation ID
- `status`: New status (pending, accepted, in_progress, implemented, rejected, deferred)

**Query Parameters**:
- `notes` (optional): Notes on the status update

**Response**:
```json
{
  "success": true,
  "message": "Recommendation status updated successfully",
  "data": {
    "recommendation_id": "rec-12345678",
    "status": "accepted",
    "previous_status": "pending",
    "updated_at": "2025-04-28T15:30:45Z"
  }
}
```

### Verify Recommendation Implementation

Verify the implementation of a recommendation.

**Endpoint**: `POST /api/recommendations/{id}/verify`

**Path Parameters**:
- `id`: Recommendation ID

**Request**:
```json
{
  "verification_metrics": {
    "component.performance.latency": {
      "before": 120.5,
      "after": 95.3,
      "improvement": 0.209,
      "sample_size": 5000
    }
  },
  "observed_impact": {
    "performance": "high",
    "resource_usage": "low",
    "reliability": "neutral"
  },
  "verification_status": "success",
  "verification_notes": "The implementation achieved the expected performance improvement with lower resource impact than anticipated.",
  "follow_up_actions": [
    "Monitor performance over the next week to ensure stability",
    "Consider additional optimizations for component_d"
  ]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Recommendation verification successful",
  "data": {
    "recommendation_id": "rec-12345678",
    "verification_id": "verify-87654321",
    "verification_status": "success",
    "verification_date": "2025-04-28T15:30:45Z"
  }
}
```

## Intelligence API

### Record an Intelligence Measurement

Record a measurement of a component's intelligence along a specific dimension.

**Endpoint**: `POST /api/intelligence/measurements`

**Request**:
```json
{
  "component_id": "component_a",
  "dimension": "reasoning",
  "measurement_method": "output_evaluation",
  "score": 0.85,
  "confidence": 0.75,
  "context": {
    "task": "logical deduction",
    "difficulty": "medium"
  },
  "evidence": {
    "output": "Step-by-step reasoning process...",
    "evaluation": "Correct logical steps with minor inefficiencies"
  },
  "evaluator": "expert_system",
  "timestamp": "2025-04-28T12:34:56Z",
  "tags": ["reasoning", "logic", "deduction"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Intelligence measurement recorded successfully",
  "data": {
    "measurement_id": "im-12345678"
  }
}
```

### Query Intelligence Measurements

Query intelligence measurements with filtering.

**Endpoint**: `GET /api/intelligence/measurements`

**Parameters**:
- `component_id` (optional): Filter by component ID
- `dimensions` (optional): Comma-separated list of dimensions
- `measurement_method` (optional): Filter by measurement method
- `min_score` (optional): Filter by minimum score
- `max_score` (optional): Filter by maximum score
- `min_confidence` (optional): Filter by minimum confidence
- `evaluator` (optional): Filter by evaluator
- `measured_after` (optional): Filter by measurement time after
- `measured_before` (optional): Filter by measurement time before
- `tags` (optional): Comma-separated list of tags
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Response**:
```json
{
  "data": [
    {
      "measurement_id": "im-12345678",
      "component_id": "component_a",
      "dimension": "reasoning",
      "measurement_method": "output_evaluation",
      "score": 0.85,
      "confidence": 0.75,
      "timestamp": "2025-04-28T12:34:56Z",
      "tags": ["reasoning", "logic", "deduction"]
    },
    // Additional measurements...
  ],
  "pagination": {
    "total": 158,
    "limit": 100,
    "offset": 0
  }
}
```

### Get Component Intelligence Profile

Get the intelligence profile of a component.

**Endpoint**: `GET /api/intelligence/components/{id}/profile`

**Path Parameters**:
- `id`: Component ID

**Query Parameters**:
- `timestamp` (optional): Timestamp for historical profile

**Response**:
```json
{
  "data": {
    "component_id": "component_a",
    "timestamp": "2025-04-28T15:30:45Z",
    "dimensions": {
      "language_processing": 0.92,
      "reasoning": 0.85,
      "knowledge": 0.78,
      "learning": 0.70,
      "creativity": 0.65,
      "planning": 0.82,
      "problem_solving": 0.88,
      "adaptation": 0.75,
      "collaboration": 0.90,
      "metacognition": 0.72
    },
    "overall_score": 0.80,
    "confidence": {
      "language_processing": 0.90,
      "reasoning": 0.75,
      "knowledge": 0.85,
      "learning": 0.70,
      "creativity": 0.60,
      "planning": 0.80,
      "problem_solving": 0.85,
      "adaptation": 0.70,
      "collaboration": 0.85,
      "metacognition": 0.65
    },
    "strengths": [
      "language_processing",
      "problem_solving",
      "collaboration"
    ],
    "improvement_areas": [
      "creativity",
      "learning",
      "metacognition"
    ],
    "comparison": {
      "ecosystem_average": {
        "overall": 0.72,
        "delta": 0.08
      }
    },
    "historical_trend": {
      "periods": ["2025-03", "2025-04"],
      "overall_scores": [0.75, 0.80],
      "dimension_deltas": {
        "language_processing": 0.02,
        "reasoning": 0.05,
        "knowledge": 0.03,
        "learning": 0.10,
        "creativity": 0.05,
        "planning": 0.02,
        "problem_solving": 0.03,
        "adaptation": 0.05,
        "collaboration": 0.00,
        "metacognition": 0.07
      }
    }
  }
}
```

### Compare Intelligence Profiles

Compare intelligence profiles between components.

**Endpoint**: `POST /api/intelligence/components/compare`

**Request**:
```json
{
  "component_ids": ["component_a", "component_b"],
  "dimensions": ["language_processing", "reasoning", "problem_solving", "collaboration"]
}
```

**Response**:
```json
{
  "data": {
    "component_ids": ["component_a", "component_b"],
    "dimensions": ["language_processing", "reasoning", "problem_solving", "collaboration"],
    "timestamp": "2025-04-28T15:30:45Z",
    "scores": {
      "component_a": {
        "language_processing": 0.92,
        "reasoning": 0.85,
        "problem_solving": 0.88,
        "collaboration": 0.90
      },
      "component_b": {
        "language_processing": 0.75,
        "reasoning": 0.92,
        "problem_solving": 0.85,
        "collaboration": 0.70
      }
    },
    "relative_strengths": {
      "component_a": ["language_processing", "collaboration"],
      "component_b": ["reasoning"]
    },
    "collaboration_potential": {
      "component_a": {
        "component_b": 0.85
      },
      "component_b": {
        "component_a": 0.85
      }
    },
    "recommendations": [
      {
        "title": "Pair components for complex reasoning tasks",
        "description": "Component B's stronger reasoning combined with Component A's language processing and collaboration could be effective for complex reasoning tasks involving human interaction."
      }
    ]
  }
}
```

### Get Intelligence Dimensions

Get information about all intelligence dimensions.

**Endpoint**: `GET /api/intelligence/dimensions`

**Response**:
```json
{
  "data": {
    "language_processing": {
      "name": "Language Processing",
      "description": "Understanding, interpreting, and generating human language",
      "metrics": [
        "comprehension_accuracy",
        "generation_quality",
        "contextual_understanding",
        "multilingual_capability",
        "domain_adaptation"
      ],
      "measurement_methods": [
        "capability_test",
        "output_evaluation",
        "user_feedback",
        "expert_assessment"
      ]
    },
    "reasoning": {
      "name": "Reasoning",
      "description": "Making inferences, deductions, and logical arguments",
      "metrics": [
        "logical_consistency",
        "chain_of_thought_quality",
        "fallacy_detection",
        "conditional_reasoning",
        "causal_analysis"
      ],
      "measurement_methods": [
        "capability_test",
        "output_evaluation",
        "expert_assessment"
      ]
    },
    // Additional dimensions...
  }
}
```

### Get Intelligence Dimension Details

Get detailed information about a specific intelligence dimension.

**Endpoint**: `GET /api/intelligence/dimensions/{dimension}`

**Path Parameters**:
- `dimension`: Intelligence dimension

**Response**:
```json
{
  "data": {
    "name": "Reasoning",
    "description": "Making inferences, deductions, and logical arguments",
    "metrics": [
      {
        "name": "logical_consistency",
        "description": "Consistency in applying logical rules",
        "measurement_scale": "0.0-1.0"
      },
      {
        "name": "chain_of_thought_quality",
        "description": "Quality of step-by-step reasoning processes",
        "measurement_scale": "0.0-1.0"
      },
      {
        "name": "fallacy_detection",
        "description": "Ability to identify logical fallacies",
        "measurement_scale": "0.0-1.0"
      },
      {
        "name": "conditional_reasoning",
        "description": "Performance in if-then reasoning tasks",
        "measurement_scale": "0.0-1.0"
      },
      {
        "name": "causal_analysis",
        "description": "Accuracy in identifying cause-and-effect relationships",
        "measurement_scale": "0.0-1.0"
      }
    ],
    "measurement_methods": [
      {
        "name": "capability_test",
        "description": "Direct testing of specific capabilities",
        "example": "Logic puzzles and syllogisms"
      },
      {
        "name": "output_evaluation",
        "description": "Assessment of component outputs",
        "example": "Analysis of reasoning chains in generated content"
      },
      {
        "name": "expert_assessment",
        "description": "Evaluation by domain experts",
        "example": "Expert review of complex reasoning tasks"
      }
    ],
    "benchmark_tasks": [
      "Syllogistic reasoning",
      "Multi-step logical deduction",
      "Scientific reasoning",
      "Counterfactual reasoning",
      "Causal inference"
    ],
    "improvement_strategies": [
      "Enhanced logical training data",
      "Step-by-step reasoning frameworks",
      "Explicit fallacy detection modules",
      "Causal modeling integration"
    ]
  }
}
```

### Get Ecosystem Intelligence Profile

Get an intelligence profile for the entire Tekton ecosystem.

**Endpoint**: `GET /api/intelligence/ecosystem/profile`

**Response**:
```json
{
  "data": {
    "timestamp": "2025-04-28T15:30:45Z",
    "dimensions": {
      "language_processing": 0.85,
      "reasoning": 0.82,
      "knowledge": 0.78,
      "learning": 0.70,
      "creativity": 0.68,
      "planning": 0.80,
      "problem_solving": 0.83,
      "adaptation": 0.75,
      "collaboration": 0.82,
      "metacognition": 0.72
    },
    "overall_score": 0.78,
    "confidence": {
      "language_processing": 0.90,
      "reasoning": 0.85,
      "knowledge": 0.85,
      "learning": 0.75,
      "creativity": 0.70,
      "planning": 0.85,
      "problem_solving": 0.85,
      "adaptation": 0.80,
      "collaboration": 0.85,
      "metacognition": 0.75
    },
    "strengths": [
      "language_processing",
      "reasoning",
      "problem_solving"
    ],
    "improvement_areas": [
      "creativity",
      "learning",
      "metacognition"
    ],
    "component_breakdown": {
      "strongest_components": {
        "language_processing": "component_a",
        "reasoning": "component_b",
        "problem_solving": "component_c"
      },
      "component_specializations": {
        "component_a": ["language_processing", "collaboration"],
        "component_b": ["reasoning", "planning"],
        "component_c": ["problem_solving", "adaptation"]
      }
    },
    "historical_trend": {
      "periods": ["2025-01", "2025-02", "2025-03", "2025-04"],
      "overall_scores": [0.70, 0.72, 0.75, 0.78],
      "dimension_deltas": {
        "language_processing": 0.05,
        "reasoning": 0.10,
        "knowledge": 0.08,
        "learning": 0.12,
        "creativity": 0.08,
        "planning": 0.05,
        "problem_solving": 0.08,
        "adaptation": 0.10,
        "collaboration": 0.06,
        "metacognition": 0.15
      }
    },
    "improvement_recommendations": [
      {
        "recommendation_id": "rec-23456789",
        "title": "Improve creativity capabilities across components",
        "priority": "medium"
      },
      {
        "recommendation_id": "rec-34567890",
        "title": "Enhance metacognition through explicit self-assessment",
        "priority": "high"
      }
    ]
  }
}
```

## Components API

### Register a Component

Register a component with Sophia.

**Endpoint**: `POST /api/components/register`

**Request**:
```json
{
  "component_id": "my_component",
  "name": "My Component",
  "description": "A component for processing data",
  "component_type": "processing",
  "version": "1.0.0",
  "api_endpoints": [
    "http://localhost:8005/api",
    "ws://localhost:8005/ws"
  ],
  "capabilities": [
    "data_processing",
    "data_analysis",
    "data_visualization"
  ],
  "dependencies": [
    "engram",
    "rhetor"
  ],
  "metrics_provided": [
    "my_component.performance.latency",
    "my_component.performance.throughput",
    "my_component.resource.memory_usage"
  ],
  "port": 8005,
  "tags": ["data", "processing", "analysis"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Component registered successfully",
  "data": {
    "component_id": "my_component",
    "registration_id": "reg-12345678",
    "registration_time": "2025-04-28T12:34:56Z"
  }
}
```

### Query Components

Query registered components with filtering.

**Endpoint**: `GET /api/components`

**Parameters**:
- `component_type` (optional): Filter by component type
- `capabilities` (optional): Comma-separated list of capabilities
- `dependencies` (optional): Comma-separated list of dependencies
- `metrics_provided` (optional): Comma-separated list of provided metrics
- `tags` (optional): Comma-separated list of tags
- `status` (optional): Filter by status
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Response**:
```json
{
  "data": [
    {
      "component_id": "my_component",
      "name": "My Component",
      "component_type": "processing",
      "version": "1.0.0",
      "capabilities": [
        "data_processing",
        "data_analysis",
        "data_visualization"
      ],
      "status": "active",
      "tags": ["data", "processing", "analysis"]
    },
    // Additional components...
  ],
  "pagination": {
    "total": 8,
    "limit": 100,
    "offset": 0
  }
}
```

### Get Component Details

Get details of a specific registered component.

**Endpoint**: `GET /api/components/{id}`

**Path Parameters**:
- `id`: Component ID

**Response**:
```json
{
  "data": {
    "component_id": "my_component",
    "name": "My Component",
    "description": "A component for processing data",
    "component_type": "processing",
    "version": "1.0.0",
    "api_endpoints": [
      "http://localhost:8005/api",
      "ws://localhost:8005/ws"
    ],
    "capabilities": [
      "data_processing",
      "data_analysis",
      "data_visualization"
    ],
    "dependencies": [
      "engram",
      "rhetor"
    ],
    "metrics_provided": [
      "my_component.performance.latency",
      "my_component.performance.throughput",
      "my_component.resource.memory_usage"
    ],
    "port": 8005,
    "tags": ["data", "processing", "analysis"],
    "status": "active",
    "registration_time": "2025-04-28T12:34:56Z",
    "last_heartbeat": "2025-04-28T15:30:45Z",
    "intelligence_profile": {
      "overall_score": 0.75,
      "top_dimensions": [
        "problem_solving",
        "adaptation",
        "knowledge"
      ]
    }
  }
}
```

### Update a Component

Update a registered component.

**Endpoint**: `PUT /api/components/{id}`

**Path Parameters**:
- `id`: Component ID

**Request**:
```json
{
  "description": "Updated component description",
  "version": "1.1.0",
  "capabilities": [
    "data_processing",
    "data_analysis",
    "data_visualization",
    "data_export"
  ],
  "tags": ["data", "processing", "analysis", "export"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Component updated successfully",
  "data": {
    "component_id": "my_component",
    "update_time": "2025-04-28T15:30:45Z"
  }
}
```

### Analyze Component Performance

Analyze the performance of a component.

**Endpoint**: `GET /api/components/{id}/performance`

**Path Parameters**:
- `id`: Component ID

**Query Parameters**:
- `start_time` (optional): Filter by start time
- `end_time` (optional): Filter by end time
- `metrics` (optional): Comma-separated list of metrics to include

**Response**:
```json
{
  "data": {
    "component_id": "my_component",
    "analysis_period": {
      "start": "2025-04-01T00:00:00Z",
      "end": "2025-04-28T23:59:59Z"
    },
    "metrics": {
      "my_component.performance.latency": {
        "current": {
          "avg": 42.5,
          "p95": 78.3,
          "min": 12.1,
          "max": 95.6
        },
        "trend": {
          "direction": "improving",
          "rate": -0.15,
          "significance": 0.95
        },
        "anomalies": [
          {
            "timestamp": "2025-04-15T14:30:00Z",
            "value": 156.2,
            "severity": "high"
          }
        ]
      },
      "my_component.performance.throughput": {
        "current": {
          "avg": 250.3,
          "p95": 350.1,
          "min": 150.0,
          "max": 420.5
        },
        "trend": {
          "direction": "stable",
          "rate": 0.02,
          "significance": 0.30
        },
        "anomalies": []
      }
    },
    "health_score": 0.85,
    "issues": [
      {
        "issue_type": "latency_spike",
        "severity": "medium",
        "description": "Latency spike detected on April 15",
        "recommendation_id": "rec-45678901"
      }
    ],
    "recommendations": [
      {
        "recommendation_id": "rec-45678901",
        "title": "Investigate April 15 latency spike",
        "priority": "medium"
      }
    ]
  }
}
```

### Analyze Component Interaction

Analyze the interaction between components.

**Endpoint**: `POST /api/components/interaction`

**Request**:
```json
{
  "component_ids": ["component_a", "component_b", "component_c"],
  "start_time": "2025-04-01T00:00:00Z",
  "end_time": "2025-04-28T23:59:59Z"
}
```

**Response**:
```json
{
  "data": {
    "analysis_period": {
      "start": "2025-04-01T00:00:00Z",
      "end": "2025-04-28T23:59:59Z"
    },
    "interaction_matrix": {
      "component_a": {
        "component_b": {
          "frequency": 1250,
          "avg_latency": 35.2,
          "error_rate": 0.01,
          "correlation": 0.85
        },
        "component_c": {
          "frequency": 750,
          "avg_latency": 42.1,
          "error_rate": 0.02,
          "correlation": 0.70
        }
      },
      "component_b": {
        "component_c": {
          "frequency": 2000,
          "avg_latency": 28.5,
          "error_rate": 0.005,
          "correlation": 0.92
        }
      }
    },
    "bottlenecks": [
      {
        "source": "component_a",
        "target": "component_c",
        "metric": "latency",
        "severity": "medium",
        "description": "Higher than expected latency in component_a to component_c interactions"
      }
    ],
    "synergies": [
      {
        "components": ["component_b", "component_c"],
        "strength": "high",
        "description": "Strong synergy between component_b and component_c with low latency and error rate"
      }
    ],
    "recommendations": [
      {
        "recommendation_id": "rec-56789012",
        "title": "Optimize component_a to component_c interaction path",
        "priority": "medium"
      }
    ]
  }
}
```

## Research API

### Create a Research Project

Create a new research project.

**Endpoint**: `POST /api/research/projects`

**Request**:
```json
{
  "title": "Neural Network Catastrophe Theory Analysis",
  "description": "Research project to investigate the application of catastrophe theory to analyze stability in neural networks under different training regimes.",
  "approach": "theoretical_and_empirical",
  "research_questions": [
    "How can catastrophe theory help predict neural network stability?",
    "What are the critical points in neural network training processes?",
    "Can we develop early warning indicators for training instability?"
  ],
  "hypothesis": "Catastrophe theory can identify critical points in neural network training where small parameter changes cause large behavioral changes.",
  "target_components": ["sophia", "ergon", "telos"],
  "data_requirements": {
    "training_logs": "Detailed neural network training logs with parameter paths",
    "performance_metrics": "Comprehensive performance metrics across different parameters",
    "model_states": "Snapshots of model states at various training stages"
  },
  "expected_outcomes": [
    "Mathematical framework mapping neural network training to catastrophe theory",
    "Identification of critical parameter thresholds for stability",
    "Early warning system for detecting approaching instability",
    "Recommendations for more stable training approaches"
  ],
  "estimated_duration": "3 months",
  "tags": ["neural_networks", "catastrophe_theory", "stability", "training"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Research project created successfully",
  "data": {
    "project_id": "rp-12345678"
  }
}
```

### Query Research Projects

Query research projects with filtering.

**Endpoint**: `GET /api/research/projects`

**Parameters**:
- `status` (optional): Filter by status
- `approach` (optional): Filter by research approach
- `target_components` (optional): Comma-separated list of target components
- `tags` (optional): Comma-separated list of tags
- `created_after` (optional): Filter by creation time after
- `created_before` (optional): Filter by creation time before
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Response**:
```json
{
  "data": [
    {
      "project_id": "rp-12345678",
      "title": "Neural Network Catastrophe Theory Analysis",
      "approach": "theoretical_and_empirical",
      "status": "in_progress",
      "created_at": "2025-04-28T12:34:56Z",
      "target_components": ["sophia", "ergon", "telos"],
      "tags": ["neural_networks", "catastrophe_theory", "stability", "training"]
    },
    // Additional projects...
  ],
  "pagination": {
    "total": 5,
    "limit": 100,
    "offset": 0
  }
}
```

### Get Research Project Details

Get details of a specific research project.

**Endpoint**: `GET /api/research/projects/{id}`

**Path Parameters**:
- `id`: Project ID

**Response**:
```json
{
  "data": {
    "project_id": "rp-12345678",
    "title": "Neural Network Catastrophe Theory Analysis",
    "description": "Research project to investigate the application of catastrophe theory to analyze stability in neural networks under different training regimes.",
    "approach": "theoretical_and_empirical",
    "research_questions": [
      "How can catastrophe theory help predict neural network stability?",
      "What are the critical points in neural network training processes?",
      "Can we develop early warning indicators for training instability?"
    ],
    "hypothesis": "Catastrophe theory can identify critical points in neural network training where small parameter changes cause large behavioral changes.",
    "target_components": ["sophia", "ergon", "telos"],
    "data_requirements": {
      "training_logs": "Detailed neural network training logs with parameter paths",
      "performance_metrics": "Comprehensive performance metrics across different parameters",
      "model_states": "Snapshots of model states at various training stages"
    },
    "expected_outcomes": [
      "Mathematical framework mapping neural network training to catastrophe theory",
      "Identification of critical parameter thresholds for stability",
      "Early warning system for detecting approaching instability",
      "Recommendations for more stable training approaches"
    ],
    "estimated_duration": "3 months",
    "status": "in_progress",
    "start_date": "2025-04-28T12:34:56Z",
    "progress": 0.35,
    "findings": [
      {
        "date": "2025-05-15T10:00:00Z",
        "title": "Initial mapping of cusp catastrophe to training dynamics",
        "description": "Successfully mapped the training dynamics of simple neural networks to the cusp catastrophe model, identifying two control parameters that most strongly influence stability.",
        "status": "verified"
      }
    ],
    "related_experiments": [
      {
        "experiment_id": "exp-23456789",
        "title": "Cusp Catastrophe Parameter Exploration",
        "status": "completed"
      }
    ],
    "related_recommendations": [
      {
        "recommendation_id": "rec-34567890",
        "title": "Implement cusp catastrophe monitoring in training loops",
        "status": "pending"
      }
    ],
    "tags": ["neural_networks", "catastrophe_theory", "stability", "training"],
    "created_at": "2025-04-28T12:34:56Z",
    "created_by": "system",
    "updated_at": "2025-05-15T10:00:00Z"
  }
}
```

### Update a Research Project

Update an existing research project.

**Endpoint**: `PUT /api/research/projects/{id}`

**Path Parameters**:
- `id`: Project ID

**Request**:
```json
{
  "description": "Updated description with refined focus on fold and cusp catastrophes in neural networks.",
  "research_questions": [
    "How can catastrophe theory help predict neural network stability?",
    "What are the critical points in neural network training processes?",
    "Can we develop early warning indicators for training instability?",
    "How do different architectures map to different catastrophe types?"
  ],
  "status": "active",
  "progress": 0.40,
  "findings": [
    {
      "date": "2025-05-15T10:00:00Z",
      "title": "Initial mapping of cusp catastrophe to training dynamics",
      "description": "Successfully mapped the training dynamics of simple neural networks to the cusp catastrophe model, identifying two control parameters that most strongly influence stability.",
      "status": "verified"
    },
    {
      "date": "2025-05-20T14:30:00Z",
      "title": "Architecture-specific catastrophe manifolds",
      "description": "Different neural network architectures appear to map to different catastrophe manifolds, with transformers showing more complex butterfly catastrophe characteristics.",
      "status": "preliminary"
    }
  ],
  "tags": ["neural_networks", "catastrophe_theory", "stability", "training", "transformers"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Research project updated successfully",
  "data": {
    "project_id": "rp-12345678",
    "update_time": "2025-05-20T14:30:45Z"
  }
}
```

## WebSocket API

Sophia provides a WebSocket endpoint at `/ws` for real-time updates and interactions.

### Connection

Connect to the WebSocket endpoint:

```javascript
const socket = new WebSocket('ws://localhost:8006/ws');

socket.onopen = () => {
  console.log('Connected to Sophia WebSocket');
};

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received message:', message);
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
};

socket.onclose = () => {
  console.log('Disconnected from Sophia WebSocket');
};
```

### Message Types

The WebSocket API supports various message types:

#### Subscription

Subscribe to updates for specific channels:

```javascript
// Subscribe to metric updates
socket.send(JSON.stringify({
  type: 'subscribe',
  channel: 'metrics',
  filters: {
    metric_id: 'component.performance.latency',
    source: 'my_component'
  }
}));

// Subscribe to experiment updates
socket.send(JSON.stringify({
  type: 'subscribe',
  channel: 'experiments',
  filters: {
    experiment_id: 'exp-12345678'
  }
}));

// Subscribe to recommendation updates
socket.send(JSON.stringify({
  type: 'subscribe',
  channel: 'recommendations',
  filters: {
    target_components: ['my_component']
  }
}));

// Subscribe to intelligence measurement updates
socket.send(JSON.stringify({
  type: 'subscribe',
  channel: 'intelligence',
  filters: {
    component_id: 'my_component'
  }
}));
```

#### Ping/Pong

Keep-alive mechanism:

```javascript
// Send ping message
socket.send(JSON.stringify({
  type: 'ping',
  timestamp: new Date().toISOString()
}));

// Receive pong response
{
  "type": "pong",
  "timestamp": "2025-04-28T15:30:45Z"
}
```

### Update Messages

The WebSocket sends various update messages:

#### Metric Update

```json
{
  "type": "metric_update",
  "metric_id": "component.performance.latency",
  "value": 42.5,
  "source": "my_component",
  "timestamp": "2025-04-28T15:30:45Z",
  "tags": ["performance", "latency"]
}
```

#### Experiment Update

```json
{
  "type": "experiment_update",
  "experiment_id": "exp-12345678",
  "status": "running",
  "timestamp": "2025-04-28T15:30:45Z",
  "progress": 0.35,
  "sample_size": {
    "control": 350,
    "treatment": 350,
    "total": 700
  },
  "preliminary_results": {
    "control": {"avg_latency": 120},
    "treatment": {"avg_latency": 95}
  }
}
```

#### Recommendation Update

```json
{
  "type": "recommendation_update",
  "recommendation_id": "rec-12345678",
  "status": "accepted",
  "timestamp": "2025-04-28T15:30:45Z",
  "previous_status": "pending",
  "notes": "Recommendation accepted for implementation"
}
```

#### Intelligence Measurement Update

```json
{
  "type": "intelligence_update",
  "component_id": "my_component",
  "dimension": "reasoning",
  "score": 0.85,
  "previous_score": 0.80,
  "timestamp": "2025-04-28T15:30:45Z"
}
```

#### Alert Notification

```json
{
  "type": "alert",
  "alert_id": "alert-12345678",
  "severity": "warning",
  "timestamp": "2025-04-28T15:30:45Z",
  "message": "Unusual latency pattern detected in component_a",
  "metric_id": "component_a.performance.latency",
  "value": 85.2,
  "threshold": 50.0,
  "actions": [
    {
      "type": "recommendation",
      "id": "rec-23456789"
    }
  ]
}
```

## Client Library

Sophia provides a Python client library for easy integration:

```python
from sophia.client import SophiaClient
import asyncio

async def example():
    # Create client
    client = SophiaClient(base_url="http://localhost:8006")
    
    try:
        # Check availability
        if await client.is_available():
            # Submit a metric
            await client.submit_metric(
                metric_id="component.performance.latency",
                value=42.5,
                source="my_component",
                tags=["performance", "latency"]
            )
            
            # Query metrics
            metrics = await client.query_metrics(
                metric_id="component.performance.latency",
                source="my_component",
                limit=10
            )
            
            # Create an experiment
            experiment_id = await client.create_experiment(
                name="Latency Optimization",
                description="Testing a new algorithm to reduce latency",
                experiment_type="a_b_test",
                target_components=["my_component"],
                hypothesis="The new algorithm reduces latency by 20%",
                metrics=["component.performance.latency"],
                parameters={
                    "control": {"algorithm": "current"},
                    "treatment": {"algorithm": "new"}
                }
            )
            
            # Get intelligence profile
            profile = await client.get_component_intelligence_profile("my_component")
            
            # Compare components
            comparison = await client.compare_intelligence_profiles(
                component_ids=["component_a", "component_b"],
                dimensions=["language_processing", "reasoning"]
            )
    finally:
        # Close client
        await client.close()

# Run the example
asyncio.run(example())
```

## Error Codes

Common error codes returned by the API:

| Code | Description |
|------|-------------|
| `AUTHENTICATION_REQUIRED` | Authentication is required for this endpoint |
| `AUTHORIZATION_FAILED` | User is not authorized to access this resource |
| `RESOURCE_NOT_FOUND` | The requested resource was not found |
| `VALIDATION_ERROR` | Request validation failed |
| `DUPLICATE_RESOURCE` | Resource already exists |
| `DEPENDENCY_ERROR` | Required dependency is missing or unavailable |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | Service is temporarily unavailable |

## Best Practices

1. **Use the Client Library**: The Python client library handles connection management, retries, and error handling.

2. **Batch Operations**: Use batch operations when submitting multiple metrics or measurements.

3. **Pagination**: Use pagination parameters to handle large result sets.

4. **WebSocket for Real-time Updates**: Use WebSocket for real-time updates instead of polling.

5. **Error Handling**: Implement proper error handling for API requests.

6. **Resource Cleanup**: Close the client when finished to release resources.

7. **Experiment Design**: Design experiments carefully with proper sample sizes and confidence levels.

8. **Contextual Information**: Include relevant context in metrics and measurements for better analysis.

9. **Tag Consistency**: Use consistent tagging conventions for easier filtering and organization.

10. **API Version Awareness**: Check API version compatibility when integrating with the API.