"""
Centralized Logging System - Core logging functionality for Tekton components.

This module implements the Centralized Logging System (CLS) for Tekton components,
providing structured, schema-versioned logging with effective timestamps and
comprehensive indexing capabilities.
"""

import json
import logging
import time
import uuid
import os
import datetime
import threading
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable, Set, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field, asdict

# Standard Python logger for internal use
_internal_logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Standardized log levels for Tekton components."""
    
    FATAL = 100   # Component is inoperable causing fatal system error
    ERROR = 80    # Component is inoperable, affecting other functionalities
    WARN = 60     # Unexpected event that may disrupt processes
    INFO = 40     # Event that doesn't affect operations
    NORMAL = 30   # System lifecycle events (startup, shutdown, etc.)
    DEBUG = 20    # Details useful for debugging in test environments
    TRACE = 10    # Full execution visibility
    
    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """Convert string representation to LogLevel."""
        try:
            return cls[level_str.upper()]
        except KeyError:
            # Default to INFO if level not recognized
            _internal_logger.warning(f"Unknown log level: {level_str}, defaulting to INFO")
            return cls.INFO
    
    @classmethod
    def to_python_level(cls, level: 'LogLevel') -> int:
        """Convert Tekton log level to Python logging level."""
        mapping = {
            cls.FATAL: logging.CRITICAL,
            cls.ERROR: logging.ERROR,
            cls.WARN: logging.WARNING,
            cls.INFO: logging.INFO,
            cls.NORMAL: logging.INFO,  # Map to INFO since Python doesn't have NORMAL
            cls.DEBUG: logging.DEBUG,
            cls.TRACE: logging.DEBUG   # Map to DEBUG since Python doesn't have TRACE
        }
        return mapping.get(level, logging.INFO)


@dataclass
class LogEntry:
    """
    Structured log entry with standardized fields.
    
    This class represents a single log entry in the Centralized Logging System,
    with all required metadata and content fields.
    """
    
    # Metadata fields
    timestamp: float = field(default_factory=time.time)
    effective_timestamp: Optional[float] = None
    component: str = ""
    level: LogLevel = LogLevel.INFO
    schema_version: str = "1.0.0"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: Optional[str] = None
    
    # Content fields
    message: str = ""
    code: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values after creation."""
        # Set effective_timestamp to timestamp if not provided
        if self.effective_timestamp is None:
            self.effective_timestamp = self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        result = asdict(self)
        # Convert Enum to string representation
        result["level"] = self.level.name
        return result
    
    def to_json(self) -> str:
        """Convert log entry to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create log entry from dictionary."""
        # Convert level string to Enum
        if "level" in data and isinstance(data["level"], str):
            data["level"] = LogLevel.from_string(data["level"])
        
        # Create instance
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LogEntry':
        """Create log entry from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


class LogStorage:
    """
    Storage interface for log entries.
    
    This class provides methods for storing and retrieving log entries
    from a persistent storage backend.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the log storage.
        
        Args:
            storage_path: Path to store log files (defaults to ~/.tekton/logs)
        """
        self.storage_path = storage_path or os.path.expanduser("~/.tekton/logs")
        os.makedirs(self.storage_path, exist_ok=True)
        
        # In-memory cache for recent logs (limited size)
        self.cache: List[LogEntry] = []
        self.cache_size = 1000
        self.cache_lock = threading.RLock()
        
        _internal_logger.info(f"Log storage initialized at {self.storage_path}")
    
    def store(self, log_entry: LogEntry) -> bool:
        """
        Store a log entry.
        
        Args:
            log_entry: Log entry to store
            
        Returns:
            True if storage successful
        """
        try:
            # Add to in-memory cache
            with self.cache_lock:
                self.cache.append(log_entry)
                # Trim cache if needed
                if len(self.cache) > self.cache_size:
                    self.cache = self.cache[-self.cache_size:]
            
            # Store to file
            # Group logs by date for easier management
            date_str = datetime.datetime.fromtimestamp(
                log_entry.timestamp
            ).strftime("%Y-%m-%d")
            
            # Create date directory if it doesn't exist
            date_dir = os.path.join(self.storage_path, date_str)
            os.makedirs(date_dir, exist_ok=True)
            
            # Determine log file name based on component
            component_name = log_entry.component.replace("/", "_")
            log_file = os.path.join(date_dir, f"{component_name}.jsonl")
            
            # Append to log file
            with open(log_file, "a") as f:
                f.write(log_entry.to_json() + "\n")
            
            return True
            
        except Exception as e:
            _internal_logger.error(f"Error storing log entry: {e}")
            return False
    
    def query(self,
             start_time: Optional[float] = None,
             end_time: Optional[float] = None,
             components: Optional[List[str]] = None,
             levels: Optional[List[LogLevel]] = None,
             limit: int = 100) -> List[LogEntry]:
        """
        Query log entries.
        
        Args:
            start_time: Start time for query (Unix timestamp)
            end_time: End time for query (Unix timestamp)
            components: List of components to include
            levels: List of log levels to include
            limit: Maximum number of entries to return
            
        Returns:
            List of matching log entries
        """
        # Set default values
        now = time.time()
        start_time = start_time or (now - 86400)  # Default to last 24 hours
        end_time = end_time or now
        
        # For simple queries, check the in-memory cache first
        with self.cache_lock:
            matching_entries = []
            
            for entry in reversed(self.cache):
                # Check if entry is within time range
                if entry.timestamp < start_time or entry.timestamp > end_time:
                    continue
                
                # Check if entry is from specified components
                if components and entry.component not in components:
                    continue
                
                # Check if entry has specified levels
                if levels and entry.level not in levels:
                    continue
                
                matching_entries.append(entry)
                
                # Limit results
                if len(matching_entries) >= limit:
                    break
            
            # If we have enough entries from cache, return them
            if len(matching_entries) >= limit:
                return matching_entries
        
        # If not enough entries in cache, check log files
        # Convert timestamps to dates
        start_date = datetime.datetime.fromtimestamp(start_time).date()
        end_date = datetime.datetime.fromtimestamp(end_time).date()
        current_date = start_date
        
        # Iterate through dates
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            date_dir = os.path.join(self.storage_path, date_str)
            
            # Check if directory exists
            if os.path.exists(date_dir):
                # Get log files
                log_files = []
                
                if components:
                    # Only include specified components
                    for component in components:
                        component_name = component.replace("/", "_")
                        file_path = os.path.join(date_dir, f"{component_name}.jsonl")
                        if os.path.exists(file_path):
                            log_files.append(file_path)
                else:
                    # Include all components
                    log_files = [
                        os.path.join(date_dir, f) for f in os.listdir(date_dir)
                        if f.endswith(".jsonl")
                    ]
                
                # Process log files
                for file_path in log_files:
                    try:
                        with open(file_path, "r") as f:
                            for line in f:
                                try:
                                    entry = LogEntry.from_json(line.strip())
                                    
                                    # Check if entry is within time range
                                    if entry.timestamp < start_time or entry.timestamp > end_time:
                                        continue
                                    
                                    # Check if entry has specified levels
                                    if levels and entry.level not in levels:
                                        continue
                                    
                                    matching_entries.append(entry)
                                    
                                    # Limit results
                                    if len(matching_entries) >= limit:
                                        break
                                        
                                except json.JSONDecodeError:
                                    continue
                                    
                        # Check if we have enough entries
                        if len(matching_entries) >= limit:
                            break
                            
                    except Exception as e:
                        _internal_logger.error(f"Error reading log file {file_path}: {e}")
            
            # Move to next date
            current_date += datetime.timedelta(days=1)
            
            # Check if we have enough entries
            if len(matching_entries) >= limit:
                break
        
        # Sort entries by timestamp (newest first)
        matching_entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        return matching_entries[:limit]


class LogManager:
    """
    Central manager for the Tekton logging system.
    
    This class manages log processing, storage, and querying for
    all Tekton components.
    """
    
    def __init__(self, 
                storage_path: str = None,
                console_output: bool = True,
                console_level: LogLevel = LogLevel.INFO):
        """
        Initialize the log manager.
        
        Args:
            storage_path: Path to store log files
            console_output: Whether to output logs to console
            console_level: Minimum level for console output
        """
        self.storage = LogStorage(storage_path)
        self.console_output = console_output
        self.console_level = console_level
        
        # Set up Python logger for console output
        if console_output:
            # Configure root logger
            root_logger = logging.getLogger()
            
            # Remove existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Add console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(LogLevel.to_python_level(console_level))
            
            # Set formatter
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            
            root_logger.addHandler(console_handler)
        
        _internal_logger.info("Log manager initialized")
    
    def log(self, log_entry: LogEntry) -> bool:
        """
        Process and store a log entry.
        
        Args:
            log_entry: Log entry to process
            
        Returns:
            True if logging successful
        """
        # Store log entry
        storage_success = self.storage.store(log_entry)
        
        # Output to console if enabled
        if self.console_output and log_entry.level.value >= self.console_level.value:
            # Convert to Python log level
            python_level = LogLevel.to_python_level(log_entry.level)
            
            # Create logger for component
            logger = logging.getLogger(log_entry.component)
            
            # Log message
            extra_info = ""
            if log_entry.context:
                extra_info = f" - Context: {log_entry.context}"
            
            logger.log(
                python_level,
                f"{log_entry.message}{extra_info}"
            )
        
        return storage_success
    
    def query(self,
             start_time: Optional[float] = None,
             end_time: Optional[float] = None,
             components: Optional[List[str]] = None,
             levels: Optional[List[LogLevel]] = None,
             limit: int = 100) -> List[LogEntry]:
        """
        Query log entries.
        
        Args:
            start_time: Start time for query (Unix timestamp)
            end_time: End time for query (Unix timestamp)
            components: List of components to include
            levels: List of log levels to include
            limit: Maximum number of entries to return
            
        Returns:
            List of matching log entries
        """
        return self.storage.query(
            start_time=start_time,
            end_time=end_time,
            components=components,
            levels=levels,
            limit=limit
        )


class Logger:
    """
    Logger interface for Tekton components.
    
    This class provides methods for logging messages at different levels,
    with structured contextual information.
    """
    
    def __init__(self,
                component: str,
                log_manager: LogManager,
                client_id: Optional[str] = None,
                default_context: Optional[Dict[str, Any]] = None):
        """
        Initialize the logger.
        
        Args:
            component: Component name for log entries
            log_manager: Log manager for storing logs
            client_id: Optional client ID for categorization
            default_context: Default context for all log entries
        """
        self.component = component
        self.log_manager = log_manager
        self.client_id = client_id
        self.default_context = default_context or {}
        
        _internal_logger.info(f"Logger initialized for component {component}")
    
    def _log(self,
           level: LogLevel,
           message: str,
           code: Optional[str] = None,
           context: Optional[Dict[str, Any]] = None,
           effective_timestamp: Optional[float] = None,
           correlation_id: Optional[str] = None,
           stack_trace: Optional[str] = None) -> bool:
        """
        Log a message at the specified level.
        
        Args:
            level: Log level
            message: Log message
            code: Optional event code
            context: Optional context information
            effective_timestamp: Optional effective timestamp
            correlation_id: Optional correlation ID
            stack_trace: Optional stack trace for errors
            
        Returns:
            True if logging successful
        """
        # Combine default context with provided context
        combined_context = self.default_context.copy()
        if context:
            combined_context.update(context)
        
        # Create log entry
        log_entry = LogEntry(
            timestamp=time.time(),
            effective_timestamp=effective_timestamp,
            component=self.component,
            level=level,
            correlation_id=correlation_id or str(uuid.uuid4()),
            client_id=self.client_id,
            message=message,
            code=code,
            context=combined_context,
            stack_trace=stack_trace
        )
        
        # Send to log manager
        return self.log_manager.log(log_entry)
    
    def fatal(self,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None,
            stack_trace: Optional[str] = None) -> bool:
        """
        Log a fatal message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            stack_trace: Optional stack trace
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.FATAL,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id,
            stack_trace=stack_trace
        )
    
    def error(self,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None,
            stack_trace: Optional[str] = None) -> bool:
        """
        Log an error message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            stack_trace: Optional stack trace
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.ERROR,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id,
            stack_trace=stack_trace
        )
    
    def warn(self,
           message: str,
           code: Optional[str] = None,
           context: Optional[Dict[str, Any]] = None,
           correlation_id: Optional[str] = None) -> bool:
        """
        Log a warning message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.WARN,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def info(self,
           message: str,
           code: Optional[str] = None,
           context: Optional[Dict[str, Any]] = None,
           correlation_id: Optional[str] = None) -> bool:
        """
        Log an informational message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.INFO,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def normal(self,
             message: str,
             code: Optional[str] = None,
             context: Optional[Dict[str, Any]] = None,
             correlation_id: Optional[str] = None) -> bool:
        """
        Log a normal system event.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.NORMAL,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def debug(self,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None) -> bool:
        """
        Log a debug message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.DEBUG,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def trace(self,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None) -> bool:
        """
        Log a trace message.
        
        Args:
            message: Log message
            code: Optional event code
            context: Optional context information
            correlation_id: Optional correlation ID
            
        Returns:
            True if logging successful
        """
        return self._log(
            level=LogLevel.TRACE,
            message=message,
            code=code,
            context=context,
            correlation_id=correlation_id
        )
    
    def with_context(self, context: Dict[str, Any]) -> 'Logger':
        """
        Create a new logger with additional context.
        
        Args:
            context: Context to add to default context
            
        Returns:
            New logger instance with combined context
        """
        # Combine contexts
        combined_context = self.default_context.copy()
        combined_context.update(context)
        
        # Create new logger with combined context
        return Logger(
            component=self.component,
            log_manager=self.log_manager,
            client_id=self.client_id,
            default_context=combined_context
        )
    
    def with_correlation(self, correlation_id: str) -> 'Logger':
        """
        Create a new logger that uses the specified correlation ID.
        
        Args:
            correlation_id: Correlation ID to use for all log entries
            
        Returns:
            New logger instance with specified correlation ID
        """
        logger = Logger(
            component=self.component,
            log_manager=self.log_manager,
            client_id=self.client_id,
            default_context=self.default_context.copy()
        )
        
        # Override the _log method to always use the provided correlation ID
        original_log = logger._log
        
        def _log_with_correlation(
            level: LogLevel,
            message: str,
            code: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None,
            effective_timestamp: Optional[float] = None,
            correlation_id_override: Optional[str] = None,
            stack_trace: Optional[str] = None
        ) -> bool:
            return original_log(
                level=level,
                message=message,
                code=code,
                context=context,
                effective_timestamp=effective_timestamp,
                correlation_id=correlation_id,  # Always use the provided correlation ID
                stack_trace=stack_trace
            )
        
        logger._log = _log_with_correlation
        return logger


# Global log manager instance
_global_log_manager: Optional[LogManager] = None


def init_logging(
    storage_path: Optional[str] = None,
    console_output: bool = True,
    console_level: Union[LogLevel, str] = LogLevel.INFO
) -> LogManager:
    """
    Initialize the global logging system.
    
    Args:
        storage_path: Path to store log files
        console_output: Whether to output logs to console
        console_level: Minimum level for console output
        
    Returns:
        LogManager instance
    """
    global _global_log_manager
    
    # Convert string level to LogLevel if needed
    if isinstance(console_level, str):
        console_level = LogLevel.from_string(console_level)
    
    # Create log manager
    _global_log_manager = LogManager(
        storage_path=storage_path,
        console_output=console_output,
        console_level=console_level
    )
    
    return _global_log_manager


def get_logger(
    component: str,
    client_id: Optional[str] = None,
    default_context: Optional[Dict[str, Any]] = None
) -> Logger:
    """
    Get a logger for a component.
    
    Args:
        component: Component name
        client_id: Optional client ID
        default_context: Default context for all log entries
        
    Returns:
        Logger instance
    """
    global _global_log_manager
    
    # Initialize global log manager if not already initialized
    if _global_log_manager is None:
        init_logging()
    
    # Create logger
    return Logger(
        component=component,
        log_manager=_global_log_manager,
        client_id=client_id,
        default_context=default_context
    )