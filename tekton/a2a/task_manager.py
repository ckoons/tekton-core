"""
Task Manager - System for creating, assigning, and tracking tasks.

This module provides a task management system for A2A agents,
allowing them to create, assign, and track the status of tasks.
"""

import time
import uuid
import asyncio
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Callable, Union

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    """Status of a task in the A2A protocol."""
    CREATED = "created"       # Task has been created
    ASSIGNED = "assigned"     # Task has been assigned to an agent
    ACCEPTED = "accepted"     # Agent has accepted the task
    REJECTED = "rejected"     # Agent has rejected the task
    IN_PROGRESS = "in_progress"  # Task is being worked on
    COMPLETED = "completed"   # Task has been completed successfully
    FAILED = "failed"         # Task failed to complete
    CANCELLED = "cancelled"   # Task was cancelled


class TaskSpec:
    """
    Task specification for A2A agents.
    
    This class represents a task in the A2A protocol, including
    its requirements, status, and assignment information.
    """
    
    def __init__(
        self,
        task_id: Optional[str] = None,
        name: str = "",
        description: str = "",
        required_capabilities: Optional[List[str]] = None,
        preferred_agent: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        deadline: Optional[float] = None,
        priority: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a task specification.
        
        Args:
            task_id: Unique identifier for the task
            name: Human-readable name
            description: Detailed description
            required_capabilities: Capabilities required to complete the task
            preferred_agent: ID of preferred agent (if any)
            parameters: Task-specific parameters
            deadline: Deadline for task completion (Unix timestamp)
            priority: Task priority (low, normal, high, urgent)
            metadata: Additional task metadata
        """
        self.id = task_id or f"task-{uuid.uuid4()}"
        self.name = name
        self.description = description
        self.required_capabilities = required_capabilities or []
        self.preferred_agent = preferred_agent
        self.parameters = parameters or {}
        self.deadline = deadline
        self.priority = priority
        self.metadata = metadata or {}
        
        # Task lifecycle information
        self.created_at = time.time()
        self.assigned_to = None
        self.status = TaskStatus.CREATED
        self.status_history = [
            {
                "status": TaskStatus.CREATED,
                "timestamp": self.created_at,
                "agent_id": None,
                "message": "Task created"
            }
        ]
        self.result = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the task to a dictionary.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "required_capabilities": self.required_capabilities,
            "preferred_agent": self.preferred_agent,
            "parameters": self.parameters,
            "deadline": self.deadline,
            "priority": self.priority,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "assigned_to": self.assigned_to,
            "status": self.status,
            "status_history": self.status_history,
            "result": self.result
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskSpec":
        """
        Create a task from a dictionary.
        
        Args:
            data: Dictionary representation of a task
            
        Returns:
            TaskSpec instance
        """
        task = cls(
            task_id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            required_capabilities=data.get("required_capabilities"),
            preferred_agent=data.get("preferred_agent"),
            parameters=data.get("parameters"),
            deadline=data.get("deadline"),
            priority=data.get("priority", "normal"),
            metadata=data.get("metadata")
        )
        
        # Set task lifecycle information if provided
        if "created_at" in data:
            task.created_at = data["created_at"]
        if "assigned_to" in data:
            task.assigned_to = data["assigned_to"]
        if "status" in data:
            task.status = data["status"]
        if "status_history" in data:
            task.status_history = data["status_history"]
        if "result" in data:
            task.result = data["result"]
            
        return task
    
    def update_status(self, status: Union[TaskStatus, str], agent_id: Optional[str] = None, message: Optional[str] = None):
        """
        Update the task status.
        
        Args:
            status: New task status
            agent_id: ID of the agent updating the status
            message: Optional status message
        """
        status_str = status if isinstance(status, str) else status.value
        
        # Set new status
        self.status = status_str
        
        # Add to status history
        self.status_history.append({
            "status": status_str,
            "timestamp": time.time(),
            "agent_id": agent_id,
            "message": message or f"Status updated to {status_str}"
        })
        
        # Update assigned_to if relevant
        if status_str == TaskStatus.ASSIGNED and agent_id:
            self.assigned_to = agent_id


class TaskManager:
    """
    Manager for A2A tasks.
    
    This class provides methods for creating, assigning, and tracking
    tasks for A2A agents.
    """
    
    def __init__(self):
        """Initialize the task manager."""
        self.tasks: Dict[str, TaskSpec] = {}
        self._callbacks: Dict[str, List[Callable[[str, Dict[str, Any]], None]]] = {
            "created": [],
            "assigned": [],
            "status_changed": []
        }
        
        logger.info("Task manager initialized")
    
    async def create_task(self, task_spec: Union[TaskSpec, Dict[str, Any]]) -> str:
        """
        Create a new task.
        
        Args:
            task_spec: Task specification
            
        Returns:
            Task ID
        """
        # Convert dictionary to TaskSpec if needed
        if isinstance(task_spec, dict):
            task = TaskSpec.from_dict(task_spec)
        else:
            task = task_spec
            
        # Store task
        self.tasks[task.id] = task
        logger.info(f"Created task: {task.name} ({task.id})")
        
        # Trigger created callbacks
        for callback in self._callbacks["created"]:
            try:
                callback(task.id, task.to_dict())
            except Exception as e:
                logger.error(f"Error in task created callback: {e}")
        
        return task.id
    
    async def assign_task(self, task_id: str, agent_id: str) -> bool:
        """
        Assign a task to an agent.
        
        Args:
            task_id: ID of the task to assign
            agent_id: ID of the agent to assign to
            
        Returns:
            True if assignment successful
        """
        if task_id not in self.tasks:
            logger.warning(f"Task not found: {task_id}")
            return False
            
        task = self.tasks[task_id]
        
        # Update task status
        task.update_status(TaskStatus.ASSIGNED, agent_id, f"Task assigned to agent {agent_id}")
        logger.info(f"Assigned task {task_id} to agent {agent_id}")
        
        # Trigger assigned callbacks
        for callback in self._callbacks["assigned"]:
            try:
                callback(task_id, task.to_dict())
            except Exception as e:
                logger.error(f"Error in task assigned callback: {e}")
                
        return True
    
    async def update_task_status(
        self,
        task_id: str,
        status: Union[TaskStatus, str],
        agent_id: Optional[str] = None,
        message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a task's status.
        
        Args:
            task_id: ID of the task to update
            status: New task status
            agent_id: ID of the agent updating the status
            message: Optional status message
            result: Optional task result
            
        Returns:
            True if update successful
        """
        if task_id not in self.tasks:
            logger.warning(f"Task not found: {task_id}")
            return False
            
        task = self.tasks[task_id]
        old_status = task.status
        
        # Update task status
        task.update_status(status, agent_id, message)
        
        # Set result if provided
        if result is not None:
            task.result = result
            
        logger.info(f"Updated task {task_id} status to {task.status}")
        
        # Trigger status changed callbacks
        for callback in self._callbacks["status_changed"]:
            try:
                callback(task_id, task.to_dict())
            except Exception as e:
                logger.error(f"Error in task status changed callback: {e}")
                
        return True
    
    async def get_task(self, task_id: str) -> Optional[TaskSpec]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID to retrieve
            
        Returns:
            TaskSpec or None if not found
        """
        return self.tasks.get(task_id)
    
    async def get_agent_tasks(self, agent_id: str) -> List[TaskSpec]:
        """
        Get all tasks assigned to an agent.
        
        Args:
            agent_id: Agent ID to get tasks for
            
        Returns:
            List of tasks assigned to the agent
        """
        return [task for task in self.tasks.values() if task.assigned_to == agent_id]
    
    async def find_tasks_by_status(self, status: Union[TaskStatus, str]) -> List[TaskSpec]:
        """
        Find tasks with a specific status.
        
        Args:
            status: Status to search for
            
        Returns:
            List of tasks with the requested status
        """
        status_str = status if isinstance(status, str) else status.value
        return [task for task in self.tasks.values() if task.status == status_str]
    
    async def find_tasks_for_capabilities(self, capabilities: List[str]) -> List[TaskSpec]:
        """
        Find tasks that require specific capabilities.
        
        Args:
            capabilities: List of capabilities
            
        Returns:
            List of tasks requiring the specified capabilities
        """
        matching_tasks = []
        
        for task in self.tasks.values():
            # Only consider tasks that are created but not yet assigned
            if task.status == TaskStatus.CREATED:
                # Check if the task requires any of the provided capabilities
                if any(cap in task.required_capabilities for cap in capabilities):
                    matching_tasks.append(task)
                    
        return matching_tasks
    
    def on_created(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for task creation events.
        
        Args:
            callback: Function to call when a task is created
        """
        self._callbacks["created"].append(callback)
    
    def on_assigned(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for task assignment events.
        
        Args:
            callback: Function to call when a task is assigned
        """
        self._callbacks["assigned"].append(callback)
    
    def on_status_changed(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for task status change events.
        
        Args:
            callback: Function to call when a task's status changes
        """
        self._callbacks["status_changed"].append(callback)


# Global task manager instance for convenience functions
_global_task_manager: Optional[TaskManager] = None

def get_task_manager() -> TaskManager:
    """
    Get the global task manager, creating it if needed.
    
    Returns:
        Global TaskManager instance
    """
    global _global_task_manager
    if _global_task_manager is None:
        _global_task_manager = TaskManager()
    return _global_task_manager

async def create_task(task_spec: Union[TaskSpec, Dict[str, Any]]) -> str:
    """
    Create a new task using the global task manager.
    
    Args:
        task_spec: Task specification
        
    Returns:
        Task ID
    """
    task_manager = get_task_manager()
    return await task_manager.create_task(task_spec)

async def assign_task(task_id: str, agent_id: str) -> bool:
    """
    Assign a task to an agent using the global task manager.
    
    Args:
        task_id: ID of the task to assign
        agent_id: ID of the agent to assign to
        
    Returns:
        True if assignment successful
    """
    task_manager = get_task_manager()
    return await task_manager.assign_task(task_id, agent_id)

async def complete_task(task_id: str, agent_id: str, result: Dict[str, Any]) -> bool:
    """
    Mark a task as completed with the global task manager.
    
    Args:
        task_id: ID of the task to complete
        agent_id: ID of the agent completing the task
        result: Task result
        
    Returns:
        True if completion successful
    """
    task_manager = get_task_manager()
    return await task_manager.update_task_status(
        task_id=task_id,
        status=TaskStatus.COMPLETED,
        agent_id=agent_id,
        message="Task completed successfully",
        result=result
    )

async def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a task's status using the global task manager.
    
    Args:
        task_id: ID of the task to get status for
        
    Returns:
        Task status information or None if not found
    """
    task_manager = get_task_manager()
    task = await task_manager.get_task(task_id)
    
    if task:
        return {
            "id": task.id,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "last_update": task.status_history[-1] if task.status_history else None,
            "result": task.result
        }
    
    return None