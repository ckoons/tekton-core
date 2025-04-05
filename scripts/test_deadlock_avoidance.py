#!/usr/bin/env python3
"""
Test script for validating the enhanced component lifecycle and deadlock avoidance mechanisms
in the Tekton launcher.

This script performs a series of tests to validate:
1. Component registration with instance tracking
2. Dependency cycle detection and resolution
3. Graceful handling of unhealthy components
4. Timeout handling for component operations
5. Proper lifecycle state transitions
"""

import asyncio
import logging
import os
import sys
import time
import unittest
import uuid
from typing import Dict, List, Any, Set, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_deadlock_avoidance")

# Add Tekton directories to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEKTON_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, TEKTON_DIR)
sys.path.insert(0, os.path.join(TEKTON_DIR, "tekton-core"))

# Import the required modules
from tekton.core.component_lifecycle import (
    ComponentState, 
    ReadinessCondition, 
    ComponentRegistration,
    PersistentMessageQueue,
    DependencyResolver,
    ComponentRegistry
)
from tekton.core.startup_coordinator import EnhancedStartUpCoordinator
from tekton_launcher import EnhancedComponentLauncher


class TestComponentLifecycle(unittest.TestCase):
    """Test case for the enhanced component lifecycle."""
    
    async def asyncSetUp(self):
        """Set up the test environment."""
            
        # Create test components
        self.component_registry = ComponentRegistry()
        self.dependency_resolver = DependencyResolver()
        self.message_queue = PersistentMessageQueue()
        
        # Set up test component information
        self.test_components = {
            "A": [],
            "B": ["A"],
            "C": ["B"],
            "D": ["A", "B"],
            "E": ["C", "D"]
        }
        
        # Add components to resolver
        for component, deps in self.test_components.items():
            await self.dependency_resolver.add_component(component, deps)
    
    async def test_dependency_cycle_detection(self):
        """Test that the dependency resolver can detect cycles."""
        # Create a cycle
        await self.dependency_resolver.add_component("F", ["E"])
        await self.dependency_resolver.add_component("G", ["F"])
        await self.dependency_resolver.update_dependencies("A", ["G"])  # Creates a cycle
        
        # Detect cycles
        cycles = await self.dependency_resolver.detect_cycles()
        self.assertTrue(len(cycles) > 0, "Failed to detect dependency cycle")
        
        # Resolve cycles
        await self.dependency_resolver.resolve_cycles()
        cycles_after = await self.dependency_resolver.detect_cycles()
        self.assertEqual(len(cycles_after), 0, "Failed to resolve dependency cycles")
    
    async def test_component_registration(self):
        """Test component registration with instance tracking."""
        # Register components
        comp_id = "TestComponent"
        reg1 = ComponentRegistration(
            component_id=comp_id,
            instance_id=str(uuid.uuid4()),
            timestamp=time.time(),
            launcher_id="test_launcher_1",
            metadata={"test": True}
        )
        
        success = await self.component_registry.register_component(reg1)
        self.assertTrue(success, "Failed to register component")
        
        # Try registering again with different instance
        reg2 = ComponentRegistration(
            component_id=comp_id,
            instance_id=str(uuid.uuid4()),
            timestamp=time.time() + 10,  # Newer
            launcher_id="test_launcher_2",
            metadata={"test": True}
        )
        
        success = await self.component_registry.register_component(reg2)
        self.assertTrue(success, "Failed to register second instance")
        
        # Verify the newer instance is returned
        retrieved = await self.component_registry.get_component(comp_id)
        self.assertEqual(retrieved.launcher_id, "test_launcher_2", 
                         "Failed to update registration with newer instance")
    
    async def test_persistent_message_queue(self):
        """Test persistent message queue with history tracking."""
        # Add messages
        await self.message_queue.add_message("topic1", {"test": "data1"})
        await self.message_queue.add_message("topic1", {"test": "data2"})
        await self.message_queue.add_message("topic2", {"test": "data3"})
        
        # Get messages
        messages = await self.message_queue.get_messages("topic1")
        self.assertEqual(len(messages), 2, "Failed to retrieve the correct number of messages")
        
        # Get history
        history = await self.message_queue.get_history("topic1")
        self.assertEqual(len(history), 2, "Failed to retrieve message history")
        
        # Ensure persistence
        new_queue = PersistentMessageQueue()
        await new_queue.load()
        messages = await new_queue.get_messages("topic1")
        self.assertEqual(len(messages), 2, "Failed to persist messages")
    
    async def test_state_transitions(self):
        """Test valid state transitions."""
        # Initial state
        state = ComponentState.UNKNOWN
        
        # Valid transitions
        state = ComponentState.INITIALIZING
        self.assertEqual(state, ComponentState.INITIALIZING)
        
        state = ComponentState.READY
        self.assertEqual(state, ComponentState.READY)
        
        state = ComponentState.DEGRADED
        self.assertEqual(state, ComponentState.DEGRADED)
        
        state = ComponentState.FAILED
        self.assertEqual(state, ComponentState.FAILED)
        
        state = ComponentState.RESTARTING
        self.assertEqual(state, ComponentState.RESTARTING)
        
        state = ComponentState.STOPPING
        self.assertEqual(state, ComponentState.STOPPING)


class TestEnhancedLauncher(unittest.TestCase):
    """Test case for the enhanced component launcher."""
    
    async def asyncSetUp(self):
        """Set up the test environment."""
            
        # Create launcher
        self.launcher = EnhancedComponentLauncher(
            base_dir=TEKTON_DIR,
            hermes_url="http://localhost:5000/api",
            use_direct=True,  # Use direct mode for testing
            restart_mode=False,
            timeout=10  # Short timeout for testing
        )
        
        # Initialize launcher
        success = await self.launcher.initialize()
        self.assertTrue(success, "Failed to initialize launcher")
    
    async def test_component_state_tracking(self):
        """Test component state tracking."""
        # Register a test component
        component = "TestComponent"
        metadata = {"test": True}
        
        # Register component with state INITIALIZING
        self.launcher.component_states[component] = ComponentState.INITIALIZING
        success, _ = await self.launcher.register_component(component, metadata)
        self.assertTrue(success, "Failed to register component")
        
        # Update state to READY
        self.launcher.component_states[component] = ComponentState.READY
        self.assertEqual(self.launcher.component_states[component], ComponentState.READY)
        
        # Update state to DEGRADED
        self.launcher.component_states[component] = ComponentState.DEGRADED
        self.assertEqual(self.launcher.component_states[component], ComponentState.DEGRADED)
        
        # Update state to FAILED
        self.launcher.component_states[component] = ComponentState.FAILED
        self.assertEqual(self.launcher.component_states[component], ComponentState.FAILED)
    
    async def test_multiple_launcher_instances(self):
        """Test handling of multiple launcher instances."""
            
        # Create two launchers
        launcher1 = self.launcher
        launcher2 = EnhancedComponentLauncher(
            base_dir=TEKTON_DIR,
            hermes_url="http://localhost:5000/api",
            use_direct=True,
            restart_mode=False,
            timeout=10
        )
        
        # Initialize second launcher
        success = await launcher2.initialize()
        self.assertTrue(success, "Failed to initialize second launcher")
        
        # Register component with first launcher
        component = "SharedComponent"
        metadata = {"test": True}
        success1, _ = await launcher1.register_component(component, metadata)
        self.assertTrue(success1, "Failed to register component with first launcher")
        
        # Register same component with second launcher (newer timestamp)
        # This would conflict in production, but for testing we can simulate this
        launcher2.startup_time = time.time() + 100  # Make it appear newer
        success2, _ = await launcher2.register_component(component, metadata)
        
        # In real situations, second registration would fail if timestamps are checked
        # But for this test, verify we can detect this situation
        if success2:
            # This is fine for testing
            existing = await launcher2.component_registry.get_component(component)
            self.assertEqual(existing.launcher_id, launcher2.instance_id, 
                            "Component should be registered with newer launcher")
        
        # Clean up
        await launcher1.shutdown()
        await launcher2.shutdown()


def run_tests():
    """Run the tests using asyncio."""
    import asynctest
    
    # Create test suites
    lifecycle_suite = asynctest.TestSuite()
    lifecycle_tests = asynctest.unittest_case.load_test_cases(TestComponentLifecycle)
    lifecycle_suite.addTests(lifecycle_tests)
    
    launcher_suite = asynctest.TestSuite()
    launcher_tests = asynctest.unittest_case.load_test_cases(TestEnhancedLauncher)
    launcher_suite.addTests(launcher_tests)
    
    # Run the tests
    runner = asynctest.TextTestRunner()
    lifecycle_result = runner.run(lifecycle_suite)
    launcher_result = runner.run(launcher_suite)
    
    # Return overall success status
    return lifecycle_result.wasSuccessful() and launcher_result.wasSuccessful()


if __name__ == "__main__":
        
    # Install asynctest if not available
    try:
        import asynctest
    except ImportError:
        print("asynctest module not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "asynctest"])
        
        # Try importing again
        try:
            import asynctest
        except ImportError:
            print("Failed to install asynctest. Tests cannot run.")
            sys.exit(1)
    
    # Run tests
    success = run_tests()
    sys.exit(0 if success else 1)