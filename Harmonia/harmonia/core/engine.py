"""
Workflow Engine - Core execution engine for workflows.

This module provides the main workflow execution capabilities, including
task scheduling, state management, and component coordination.
"""

import logging
import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Set, Union, Callable
from datetime import datetime

from harmonia.core.workflow import Workflow, Task, TaskStatus, WorkflowStatus
from harmonia.core.state import StateManager

# Configure logger
logger = logging.getLogger(__name__)


class WorkflowEngine:
    """
    Main workflow execution engine.
    
    This class is responsible for executing workflows, managing their state,
    and coordinating with Tekton components to execute tasks.
    """
    
    def __init__(self, 
                state_manager: Optional[StateManager] = None,
                component_registry: Optional[Dict[str, Any]] = None):
        """
        Initialize the workflow engine.
        
        Args:
            state_manager: Optional state manager for persisting workflow state
            component_registry: Optional registry of component adapters
        """
        self.state_manager = state_manager or StateManager()
        self.component_registry = component_registry or {}
        
        # Dictionary to store active workflow executions
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Workflow engine initialized")
    
    async def execute(self, 
                    workflow: Workflow, 
                    workflow_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a workflow with the given input.
        
        Args:
            workflow: Workflow to execute
            workflow_input: Input data for the workflow
            
        Returns:
            Workflow execution result
        """
        # Validate input
        workflow_input = workflow_input or {}
        logger.info(f"Executing workflow {workflow.name} (ID: {workflow.id})")
        
        # Create execution context
        execution_id = f"{workflow.id}_{int(time.time())}"
        execution_context = {
            "id": execution_id,
            "workflow": workflow,
            "input": workflow_input,
            "output": {},
            "task_results": {},
            "task_status": {task.name: TaskStatus.PENDING for task in workflow.tasks.values()},
            "status": WorkflowStatus.PENDING,
            "started_at": datetime.now(),
            "completed_at": None,
            "error": None
        }
        
        # Store execution context
        self.active_workflows[execution_id] = execution_context
        await self.state_manager.save_workflow_state(execution_id, execution_context)
        
        try:
            # Update status to running
            execution_context["status"] = WorkflowStatus.RUNNING
            await self.state_manager.save_workflow_state(execution_id, execution_context)
            
            # Execute workflow
            result = await self._execute_workflow(execution_id)
            
            # Update status to completed
            execution_context["status"] = WorkflowStatus.COMPLETED
            execution_context["completed_at"] = datetime.now()
            execution_context["output"] = result
            await self.state_manager.save_workflow_state(execution_id, execution_context)
            
            logger.info(f"Workflow {workflow.name} (ID: {workflow.id}) completed successfully")
            return result
            
        except Exception as e:
            # Update status to failed
            execution_context["status"] = WorkflowStatus.FAILED
            execution_context["completed_at"] = datetime.now()
            execution_context["error"] = str(e)
            await self.state_manager.save_workflow_state(execution_id, execution_context)
            
            logger.error(f"Error executing workflow {workflow.name} (ID: {workflow.id}): {e}")
            raise
    
    async def _execute_workflow(self, execution_id: str) -> Dict[str, Any]:
        """
        Execute a workflow by execution ID.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            Workflow execution result
        """
        execution_context = self.active_workflows[execution_id]
        workflow = execution_context["workflow"]
        
        # Get dependency graph
        dependency_graph = workflow.get_dependency_graph()
        
        # Get tasks with no dependencies (root tasks)
        ready_tasks = workflow.get_root_tasks()
        pending_tasks = set(workflow.tasks.keys())
        
        # Execute tasks in order
        while ready_tasks and pending_tasks:
            # Execute ready tasks in parallel
            tasks_to_execute = [task for task in ready_tasks if task.name in pending_tasks]
            
            if not tasks_to_execute:
                break
                
            # Execute tasks in parallel
            tasks_futures = [
                self._execute_task(execution_id, task)
                for task in tasks_to_execute
            ]
            
            await asyncio.gather(*tasks_futures)
            
            # Update pending tasks
            for task in tasks_to_execute:
                pending_tasks.remove(task.name)
            
            # Find next tasks that are ready
            ready_tasks = []
            for task_name in pending_tasks:
                task = workflow.tasks[task_name]
                dependencies = set(task.depends_on)
                
                # Check if all dependencies are completed
                dependencies_completed = True
                for dep_name in dependencies:
                    dep_status = execution_context["task_status"].get(dep_name)
                    if dep_status != TaskStatus.COMPLETED:
                        dependencies_completed = False
                        break
                
                if dependencies_completed:
                    ready_tasks.append(task)
        
        # Check if all tasks completed successfully
        all_completed = True
        for task_name, status in execution_context["task_status"].items():
            if status != TaskStatus.COMPLETED:
                all_completed = False
                break
        
        if not all_completed:
            raise Exception("Not all tasks completed successfully")
        
        # Extract workflow output
        output = {}
        for output_name, output_path in workflow.output.items():
            # Parse output path (e.g., tasks.task_name.output.field)
            parts = output_path.replace("${", "").replace("}", "").split(".")
            
            if len(parts) >= 3 and parts[0] == "tasks":
                task_name = parts[1]
                field_path = ".".join(parts[3:])
                
                if task_name in execution_context["task_results"]:
                    task_output = execution_context["task_results"][task_name]
                    
                    # Extract field from task output
                    value = task_output
                    for field in field_path.split("."):
                        if isinstance(value, dict) and field in value:
                            value = value[field]
                        else:
                            value = None
                            break
                    
                    output[output_name] = value
        
        return output
    
    async def _execute_task(self, execution_id: str, task: Task) -> Dict[str, Any]:
        """
        Execute a single task within a workflow.
        
        Args:
            execution_id: Workflow execution ID
            task: Task to execute
            
        Returns:
            Task execution result
        """
        execution_context = self.active_workflows[execution_id]
        logger.info(f"Executing task {task.name} in workflow {execution_context['workflow'].name}")
        
        try:
            # Update task status to running
            execution_context["task_status"][task.name] = TaskStatus.RUNNING
            await self.state_manager.save_workflow_state(execution_id, execution_context)
            
            # Resolve task input (replace expressions with values)
            resolved_input = await self._resolve_input(task.input, execution_context)
            
            # Execute task on component
            component_name = task.component
            action_name = task.action
            
            if component_name in self.component_registry:
                component = self.component_registry[component_name]
                result = await component.execute_action(action_name, resolved_input)
            else:
                # Mock execution for demo purposes
                logger.warning(f"Component {component_name} not found, mocking execution")
                result = {"status": "success", "message": f"Executed {action_name} on {component_name}"}
                await asyncio.sleep(0.5)  # Simulate execution time
            
            # Store task result
            execution_context["task_results"][task.name] = result
            
            # Update task status to completed
            execution_context["task_status"][task.name] = TaskStatus.COMPLETED
            await self.state_manager.save_workflow_state(execution_id, execution_context)
            
            logger.info(f"Task {task.name} completed successfully")
            return result
            
        except Exception as e:
            # Update task status to failed
            execution_context["task_status"][task.name] = TaskStatus.FAILED
            await self.state_manager.save_workflow_state(execution_id, execution_context)
            
            logger.error(f"Error executing task {task.name}: {e}")
            raise
    
    async def _resolve_input(self, 
                           input_data: Dict[str, Any], 
                           execution_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve input expressions to actual values.
        
        Args:
            input_data: Input data with expressions
            execution_context: Workflow execution context
            
        Returns:
            Resolved input data
        """
        if not input_data:
            return {}
            
        # Clone input to avoid modifying the original
        resolved = {}
        
        for key, value in input_data.items():
            if isinstance(value, str) and "${" in value and "}" in value:
                # This is an expression, resolve it
                expression = value.replace("${", "").replace("}", "")
                parts = expression.split(".")
                
                if parts[0] == "input":
                    # Reference to workflow input
                    if len(parts) > 1 and parts[1] in execution_context["input"]:
                        resolved[key] = execution_context["input"][parts[1]]
                    else:
                        resolved[key] = None
                        
                elif parts[0] == "tasks" and len(parts) >= 4:
                    # Reference to task output
                    task_name = parts[1]
                    if task_name in execution_context["task_results"]:
                        task_output = execution_context["task_results"][task_name]
                        
                        # Extract field from task output
                        value = task_output
                        for field in parts[3:]:
                            if isinstance(value, dict) and field in value:
                                value = value[field]
                            else:
                                value = None
                                break
                        
                        resolved[key] = value
                    else:
                        resolved[key] = None
                else:
                    # Unknown reference
                    resolved[key] = None
            else:
                # Regular value, use as is
                resolved[key] = value
        
        return resolved
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get the status of a workflow execution.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            Workflow status information
        """
        if execution_id in self.active_workflows:
            execution_context = self.active_workflows[execution_id]
        else:
            execution_context = await self.state_manager.load_workflow_state(execution_id)
            
        if not execution_context:
            raise ValueError(f"Workflow execution {execution_id} not found")
            
        return {
            "id": execution_id,
            "workflow_id": execution_context["workflow"].id,
            "workflow_name": execution_context["workflow"].name,
            "status": execution_context["status"],
            "task_status": execution_context["task_status"],
            "started_at": execution_context["started_at"],
            "completed_at": execution_context["completed_at"],
            "error": execution_context["error"]
        }
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            execution_id: Workflow execution ID
            
        Returns:
            True if cancellation was successful
        """
        if execution_id not in self.active_workflows:
            logger.warning(f"Workflow execution {execution_id} not found or already completed")
            return False
            
        execution_context = self.active_workflows[execution_id]
        
        # Only cancel if running
        if execution_context["status"] != WorkflowStatus.RUNNING:
            return False
            
        # Update status to canceled
        execution_context["status"] = WorkflowStatus.CANCELED
        execution_context["completed_at"] = datetime.now()
        await self.state_manager.save_workflow_state(execution_id, execution_context)
        
        logger.info(f"Workflow execution {execution_id} canceled")
        return True