#!/usr/bin/env python3
"""
Latent Space Reasoning Framework Demo

This script demonstrates the use of the Latent Space Reasoning Framework
with different components and approaches.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("latent_reasoning_demo")

# Add Tekton root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEKTON_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, TEKTON_ROOT)

# Import necessary components
from tekton.core.latent_reasoning import LatentReasoningMixin
from tekton.utils.latent_space_visualizer import LatentSpaceVisualizer
from Prometheus.prometheus.core.planning_engine import PlanningEngine


class SimpleComponent(LatentReasoningMixin):
    """Simple component demonstrating basic latent reasoning capabilities."""
    
    def __init__(self, component_id: str = "demo.simple"):
        self.component_id = component_id
    
    async def process_input(self, input_text: str, use_latent_reasoning: bool = True) -> Dict[str, Any]:
        """
        Process input text with or without latent reasoning.
        
        Args:
            input_text: The text to process
            use_latent_reasoning: Whether to use latent reasoning
            
        Returns:
            Processing result
        """
        # Initialize latent space if not already done
        if not hasattr(self, 'latent_space'):
            await self.initialize_latent_space(namespace="demo")
        
        if use_latent_reasoning:
            return await self.with_latent_reasoning(
                input_content=input_text,
                process_func=self._simulate_processing,
                max_iterations=3
            )
        else:
            # Direct processing without latent reasoning
            result = await self._simulate_processing(input_text)
            return {"result": result, "iterations": 1}
    
    async def _simulate_processing(self, input_text: str) -> str:
        """Simulate processing with some basic transformations."""
        # This is a placeholder for actual processing
        # In a real implementation, this might call an LLM or other processing system
        
        # Check if this is an iteration request
        if "Iteration 1" in input_text:
            return f"{input_text}\n\nInitial processing: Analyzing the key concepts in the input."
        elif "Iteration 2" in input_text:
            return f"{input_text}\n\nDeeper analysis: Identifying relationships between concepts and potential implications."
        elif "Iteration 3" in input_text:
            return f"{input_text}\n\nFinal synthesis: Comprehensive understanding with context and nuance."
        else:
            return f"Processed result: Initial analysis of '{input_text}'."


async def run_simple_demo():
    """Run a simple demonstration of latent reasoning."""
    print("\n==== Simple Latent Reasoning Demo ====\n")
    
    # Create component
    component = SimpleComponent()
    
    # Define test inputs
    simple_input = "Analyze the impact of remote work on organizational culture."
    
    # Process with and without latent reasoning
    print("Processing with direct approach...")
    direct_result = await component.process_input(simple_input, use_latent_reasoning=False)
    
    print("Processing with latent reasoning...")
    latent_result = await component.process_input(simple_input, use_latent_reasoning=True)
    
    # Display results
    print("\n-- Direct Processing Result --")
    print(direct_result.get("result", ""))
    
    print("\n-- Latent Reasoning Result --")
    print(latent_result.get("result", ""))
    print(f"Iterations: {latent_result.get('iterations', 0)}")
    
    # Generate visualization
    output_file = LatentSpaceVisualizer.generate_html_trace(
        latent_result.get("trace", {}),
        title="Simple Latent Reasoning Example"
    )
    print(f"\nGenerated visualization: {output_file}")
    
    # Clean up
    await component.close_latent_space()


async def run_planning_demo():
    """Run a demonstration of planning with latent reasoning."""
    print("\n==== Planning with Latent Reasoning Demo ====\n")
    
    # Initialize planning engine
    planning_engine = PlanningEngine()
    await planning_engine.initialize()
    
    try:
        # Simple planning task
        simple_objective = "Create a marketing website for a new product."
        simple_context = {
            "deadline": "2 weeks",
            "budget": "Limited",
            "team": "1 designer, 1 developer"
        }
        
        # Complex planning task
        complex_objective = (
            "Design and implement a distributed data processing pipeline that handles "
            "real-time analytics, ensures data privacy compliance across multiple jurisdictions, "
            "integrates with legacy systems, and optimizes for both performance and cost efficiency."
        )
        complex_context = {
            "constraints": {
                "timeline": "3 months",
                "team": "Cross-functional team of 8 specialists",
                "compliance": "GDPR, CCPA, HIPAA"
            },
            "technologies": ["Kafka", "Spark", "Kubernetes", "TensorFlow"],
            "requirements": [
                "99.99% uptime",
                "Sub-second latency for critical operations",
                "Comprehensive audit trail",
                "Automatic scaling based on load"
            ]
        }
        
        # Generate plans
        print("Generating plan for simple objective...")
        simple_result = await planning_engine.create_plan(simple_objective, simple_context)
        
        print("Generating plan for complex objective...")
        complex_result = await planning_engine.create_plan(complex_objective, complex_context)
        
        # Display results
        print("\n-- Simple Planning Result --")
        print(f"Used latent reasoning: {simple_result.get('used_latent_reasoning', False)}")
        print(f"Complexity score: {simple_result.get('complexity_score', 0):.4f}")
        print(f"Iterations: {simple_result.get('iterations', 1)}")
        
        print("\n-- Complex Planning Result --")
        print(f"Used latent reasoning: {complex_result.get('used_latent_reasoning', False)}")
        print(f"Complexity score: {complex_result.get('complexity_score', 0):.4f}")
        print(f"Iterations: {complex_result.get('iterations', 1)}")
        
        # Generate visualizations
        if simple_result.get("reasoning_trace"):
            simple_viz = LatentSpaceVisualizer.generate_html_trace(
                simple_result.get("reasoning_trace", {}),
                title="Simple Planning Reasoning"
            )
            print(f"\nGenerated simple planning visualization: {simple_viz}")
        
        if complex_result.get("reasoning_trace"):
            complex_viz = LatentSpaceVisualizer.generate_html_trace(
                complex_result.get("reasoning_trace", {}),
                title="Complex Planning Reasoning"
            )
            print(f"\nGenerated complex planning visualization: {complex_viz}")
        
    finally:
        # Clean up
        await planning_engine.close()


async def main():
    """Run all demos."""
    # Create output directory for visualizations
    os.makedirs("latent_reasoning_visualizations", exist_ok=True)
    
    # Run demos
    await run_simple_demo()
    await run_planning_demo()
    
    print("\nAll demos completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())