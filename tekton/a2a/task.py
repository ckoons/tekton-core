"""
Task Management for A2A Protocol v2

Implements task lifecycle management with formal state transitions according
to the A2A Protocol v0.2.1 specification.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4

from tekton.models.base import TektonBaseModel
from .errors import TaskStateError, TaskNotFoundError


class TaskState(str, Enum):
    """Task lifecycle states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskUpdate(TektonBaseModel):
    """Update event for a task"""
    timestamp: datetime
    state: Optional[TaskState] = None
    progress: Optional[float] = None  # 0.0 to 1.0
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class Task(TektonBaseModel):
    """
    Task representation according to A2A Protocol v2.
    
    Manages task lifecycle with formal state transitions.
    """
    
    # Task identification
    id: str
    name: str
    description: Optional[str] = None
    
    # Task assignment
    agent_id: Optional[str] = None
    created_by: str
    
    # Task state
    state: TaskState = TaskState.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    
    # Task data
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None
    
    # Progress tracking
    progress: float = 0.0  # 0.0 to 1.0
    updates: List[TaskUpdate] = []
    
    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    
    # Valid state transitions
    _valid_transitions = {
        TaskState.PENDING: [TaskState.RUNNING, TaskState.CANCELLED],
        TaskState.RUNNING: [TaskState.COMPLETED, TaskState.FAILED, TaskState.PAUSED, TaskState.CANCELLED],
        TaskState.PAUSED: [TaskState.RUNNING, TaskState.CANCELLED],
        TaskState.COMPLETED: [],  # Terminal state
        TaskState.FAILED: [],     # Terminal state
        TaskState.CANCELLED: []   # Terminal state
    }
    
    @classmethod
    def create(
        cls,
        name: str,
        created_by: str,
        description: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        **kwargs
    ) -> 'Task':
        """Create a new task with generated ID"""
        return cls(
            id=f"task-{uuid4()}",
            name=name,
            created_by=created_by,
            description=description,
            input_data=input_data,
            priority=priority,
            created_at=datetime.utcnow(),
            **kwargs
        )
    
    def can_transition_to(self, new_state: TaskState) -> bool:
        """Check if transition to new state is valid"""
        return new_state in self._valid_transitions.get(self.state, [])
    
    def transition_to(self, new_state: TaskState, message: Optional[str] = None) -> None:
        """Transition task to new state"""
        if not self.can_transition_to(new_state):
            raise TaskStateError(self.state.value, new_state.value)
        
        # Update timestamps
        if new_state == TaskState.RUNNING and self.started_at is None:
            self.started_at = datetime.utcnow()
        elif new_state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
            self.completed_at = datetime.utcnow()
        
        # Update progress
        if new_state == TaskState.COMPLETED:
            self.progress = 1.0
        
        # Record update
        update = TaskUpdate(
            timestamp=datetime.utcnow(),
            state=new_state,
            progress=self.progress,
            message=message
        )
        self.updates.append(update)
        
        # Update state
        self.state = new_state
    
    def update_progress(self, progress: float, message: Optional[str] = None) -> None:
        """Update task progress (0.0 to 1.0)"""
        if not 0.0 <= progress <= 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        self.progress = progress
        
        update = TaskUpdate(
            timestamp=datetime.utcnow(),
            progress=progress,
            message=message
        )
        self.updates.append(update)
    
    def add_update(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Add a general update to the task"""
        update = TaskUpdate(
            timestamp=datetime.utcnow(),
            message=message,
            data=data
        )
        self.updates.append(update)
    
    def set_output(self, output_data: Dict[str, Any]) -> None:
        """Set task output data"""
        self.output_data = output_data
    
    def set_error(self, error_data: Dict[str, Any]) -> None:
        """Set task error data"""
        self.error_data = error_data
    
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state"""
        return self.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]
    
    def duration(self) -> Optional[float]:
        """Get task duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class TaskManager:
    """
    Manager for task lifecycle and operations.
    
    Handles task creation, assignment, and state management.
    """
    
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
    
    def create_task(
        self,
        name: str,
        created_by: str,
        **kwargs
    ) -> Task:
        """Create and register a new task"""
        task = Task.create(name=name, created_by=created_by, **kwargs)
        self._tasks[task.id] = task
        return task
    
    def get_task(self, task_id: str) -> Task:
        """Get a task by ID"""
        task = self._tasks.get(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task
    
    def list_tasks(
        self,
        agent_id: Optional[str] = None,
        state: Optional[TaskState] = None,
        created_by: Optional[str] = None
    ) -> List[Task]:
        """List tasks with optional filters"""
        tasks = list(self._tasks.values())
        
        if agent_id is not None:
            tasks = [t for t in tasks if t.agent_id == agent_id]
        
        if state is not None:
            tasks = [t for t in tasks if t.state == state]
        
        if created_by is not None:
            tasks = [t for t in tasks if t.created_by == created_by]
        
        return tasks
    
    def assign_task(self, task_id: str, agent_id: str) -> Task:
        """Assign a task to an agent"""
        task = self.get_task(task_id)
        task.agent_id = agent_id
        task.add_update(f"Assigned to agent {agent_id}")
        return task
    
    def update_task_state(
        self,
        task_id: str,
        new_state: TaskState,
        message: Optional[str] = None
    ) -> Task:
        """Update task state with validation"""
        task = self.get_task(task_id)
        task.transition_to(new_state, message)
        return task
    
    def update_task_progress(
        self,
        task_id: str,
        progress: float,
        message: Optional[str] = None
    ) -> Task:
        """Update task progress"""
        task = self.get_task(task_id)
        task.update_progress(progress, message)
        return task
    
    def complete_task(
        self,
        task_id: str,
        output_data: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> Task:
        """Mark task as completed with output"""
        task = self.get_task(task_id)
        
        if output_data:
            task.set_output(output_data)
        
        task.transition_to(TaskState.COMPLETED, message or "Task completed successfully")
        return task
    
    def fail_task(
        self,
        task_id: str,
        error_data: Dict[str, Any],
        message: Optional[str] = None
    ) -> Task:
        """Mark task as failed with error information"""
        task = self.get_task(task_id)
        task.set_error(error_data)
        task.transition_to(TaskState.FAILED, message or "Task failed")
        return task
    
    def cancel_task(self, task_id: str, reason: Optional[str] = None) -> Task:
        """Cancel a task"""
        task = self.get_task(task_id)
        task.transition_to(TaskState.CANCELLED, reason or "Task cancelled")
        return task
    
    def cleanup_completed(self, before: Optional[datetime] = None) -> List[str]:
        """Remove completed tasks older than specified time"""
        removed_ids = []
        
        for task_id, task in list(self._tasks.items()):
            if task.is_terminal():
                if before is None or (task.completed_at and task.completed_at < before):
                    self._tasks.pop(task_id)
                    removed_ids.append(task_id)
        
        return removed_ids