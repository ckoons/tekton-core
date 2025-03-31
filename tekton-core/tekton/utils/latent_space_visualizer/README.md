# Latent Space Visualizer

A set of utilities for visualizing and analyzing latent space reasoning traces to help understand and debug the iterative reasoning process.

## Module Structure

The visualizer has been refactored into a modular structure:

- `__init__.py`: Re-exports the main LatentSpaceVisualizer class
- `visualizer.py`: Main visualizer class with public API methods
- `html_generator.py`: HTML visualization generation
- `exporters.py`: Export functionality for different formats
- `comparisons.py`: Comparison utilities for multiple traces

## Features

- Generate interactive HTML visualizations of reasoning traces
- Export reasoning traces to JSON format
- Compare multiple reasoning traces side-by-side
- Highlight changes between iterations
- Calculate and display statistics about reasoning processes

## Usage

```python
from tekton.utils.latent_space_visualizer import LatentSpaceVisualizer

# Example reasoning trace
reasoning_trace = {
    "id": "thought_1234567890",
    "metadata": {
        "component_id": "example_component",
        "created_at": 1627484400,
        "finalized": True,
        "iterations_performed": 3,
        "converged": True,
        "process_type": "iterative_refinement"
    },
    "iterations": [
        {
            "content": "Initial thought...",
            "timestamp": 1627484400,
            "iteration": 0,
            "metadata": {"processing_time": 1.2}
        },
        {
            "content": "Refined thought...",
            "timestamp": 1627484500,
            "iteration": 1,
            "metadata": {
                "processing_time": 1.5,
                "similarity": 0.6
            }
        },
        {
            "content": "Final thought...",
            "timestamp": 1627484600,
            "iteration": 2,
            "metadata": {
                "processing_time": 1.8,
                "similarity": 0.85
            }
        }
    ]
}

# Generate HTML visualization
html_path = LatentSpaceVisualizer.generate_html_trace(
    reasoning_trace,
    title="My Reasoning Trace",
    highlight_changes=True
)

# Export to JSON
json_path = LatentSpaceVisualizer.export_trace_json(reasoning_trace)

# Compare two traces
comparison_path = LatentSpaceVisualizer.compare_traces(trace1, trace2)
```

## HTML Visualization Features

The HTML visualization provides:

- Interactive tabs to view all iterations or just first/last
- Highlighting of changes between iterations
- Statistics about the reasoning process
- Metadata display
- Mobile-responsive design