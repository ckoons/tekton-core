"""
Database Manager - Centralized database services for Tekton components.

This module provides a unified interface for all database operations in the Tekton
ecosystem, supporting different database types with namespace isolation.
"""

import os
import json
import time
import uuid
import threading
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Type
from enum import Enum
from abc import ABC, abstractmethod

from hermes.core.logging import get_logger

# Logger for this module
logger = get_logger("hermes.core.database_manager")


class DatabaseType(Enum):
    """Types of databases supported by the Database Manager."""
    
    VECTOR = "vector"       # Vector database for embeddings and similarity search
    GRAPH = "graph"         # Graph database for knowledge representation
    KEY_VALUE = "key_value" # Key-value store for simple data
    DOCUMENT = "document"   # Document database for structured data
    CACHE = "cache"         # In-memory cache for temporary data
    RELATION = "relation"   # Relational database for structured data
    
    @classmethod
    def from_string(cls, type_str: str) -> 'DatabaseType':
        """Convert string to DatabaseType."""
        try:
            return cls[type_str.upper()]
        except KeyError:
            raise ValueError(f"Unknown database type: {type_str}")


class DatabaseBackend(Enum):
    """Specific database backends supported for each type."""
    
    # Vector database backends
    FAISS = "faiss"         # Facebook AI Similarity Search
    QDRANT = "qdrant"       # Qdrant vector database
    CHROMADB = "chromadb"   # ChromaDB vector database
    LANCEDB = "lancedb"     # LanceDB vector database
    
    # Graph database backends
    NEO4J = "neo4j"         # Neo4j graph database
    NETWORKX = "networkx"   # NetworkX in-memory graph
    
    # Key-value database backends
    REDIS = "redis"         # Redis key-value store
    LEVELDB = "leveldb"     # LevelDB key-value store
    ROCKSDB = "rocksdb"     # RocksDB key-value store
    
    # Document database backends
    MONGODB = "mongodb"     # MongoDB document database
    JSONDB = "jsondb"       # Simple JSON file-based database
    
    # Cache backends
    MEMORY = "memory"       # In-memory cache
    MEMCACHED = "memcached" # Memcached distributed cache
    
    # Relational database backends
    SQLITE = "sqlite"       # SQLite database
    POSTGRES = "postgres"   # PostgreSQL database
    
    @classmethod
    def from_string(cls, backend_str: str) -> 'DatabaseBackend':
        """Convert string to DatabaseBackend."""
        try:
            return cls[backend_str.upper()]
        except KeyError:
            raise ValueError(f"Unknown database backend: {backend_str}")
    
    @classmethod
    def for_type(cls, db_type: DatabaseType) -> List['DatabaseBackend']:
        """Get available backends for a database type."""
        if db_type == DatabaseType.VECTOR:
            return [cls.FAISS, cls.QDRANT, cls.CHROMADB, cls.LANCEDB]
        elif db_type == DatabaseType.GRAPH:
            return [cls.NEO4J, cls.NETWORKX]
        elif db_type == DatabaseType.KEY_VALUE:
            return [cls.REDIS, cls.LEVELDB, cls.ROCKSDB]
        elif db_type == DatabaseType.DOCUMENT:
            return [cls.MONGODB, cls.JSONDB]
        elif db_type == DatabaseType.CACHE:
            return [cls.MEMORY, cls.MEMCACHED]
        elif db_type == DatabaseType.RELATION:
            return [cls.SQLITE, cls.POSTGRES]
        else:
            return []


class DatabaseAdapter(ABC):
    """
    Abstract base class for database adapters.
    
    This class defines the interface that all database adapters must implement,
    providing a consistent API regardless of the underlying database.
    """
    
    def __init__(self, 
                namespace: str,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the database adapter.
        
        Args:
            namespace: Namespace for data isolation
            config: Optional configuration parameters
        """
        self.namespace = namespace
        self.config = config or {}
        self.client = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the database.
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if connected to the database.
        
        Returns:
            True if connected
        """
        pass
    
    @property
    @abstractmethod
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        pass
    
    @property
    @abstractmethod
    def backend(self) -> DatabaseBackend:
        """Get the database backend."""
        pass


class VectorDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for vector databases.
    
    This class provides methods for storing and retrieving vector embeddings,
    with support for similarity search and metadata filtering.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.VECTOR
    
    @abstractmethod
    async def store(self,
                   id: str,
                   vector: List[float],
                   metadata: Optional[Dict[str, Any]] = None,
                   text: Optional[str] = None) -> bool:
        """
        Store a vector in the database.
        
        Args:
            id: Unique identifier for the vector
            vector: The vector embedding
            metadata: Optional metadata to store with the vector
            text: Optional text content associated with the vector
            
        Returns:
            True if storage successful
        """
        pass
    
    @abstractmethod
    async def search(self,
                    query_vector: List[float],
                    limit: int = 10,
                    filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: The query vector
            limit: Maximum number of results
            filter: Optional metadata filter
            
        Returns:
            List of matching vectors with metadata and similarity scores
        """
        pass
    
    @abstractmethod
    async def delete(self,
                    id: Optional[str] = None,
                    filter: Optional[Dict[str, Any]] = None) -> bool:
        """
        Delete vectors from the database.
        
        Args:
            id: Optional specific vector ID to delete
            filter: Optional metadata filter for bulk deletion
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific vector by ID.
        
        Args:
            id: Vector ID to retrieve
            
        Returns:
            Vector with metadata if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list(self,
                  limit: int = 100,
                  offset: int = 0,
                  filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List vectors in the database.
        
        Args:
            limit: Maximum number of results
            offset: Starting offset for pagination
            filter: Optional metadata filter
            
        Returns:
            List of vectors with metadata
        """
        pass


class GraphDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for graph databases.
    
    This class provides methods for storing and retrieving graph data,
    with support for nodes, relationships, and graph queries.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.GRAPH
    
    @abstractmethod
    async def add_node(self,
                      id: str,
                      labels: List[str],
                      properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a node to the graph.
        
        Args:
            id: Unique identifier for the node
            labels: List of labels for the node
            properties: Optional node properties
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def add_relationship(self,
                             source_id: str,
                             target_id: str,
                             type: str,
                             properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a relationship between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            type: Relationship type
            properties: Optional relationship properties
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def get_node(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.
        
        Args:
            id: Node ID to retrieve
            
        Returns:
            Node with properties if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_relationships(self,
                              node_id: str,
                              types: Optional[List[str]] = None,
                              direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get relationships for a node.
        
        Args:
            node_id: Node ID to get relationships for
            types: Optional list of relationship types to filter by
            direction: Relationship direction ("incoming", "outgoing", or "both")
            
        Returns:
            List of relationships
        """
        pass
    
    @abstractmethod
    async def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a graph query.
        
        Args:
            query: Query string in the database's query language
            params: Optional query parameters
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    async def delete_node(self, id: str) -> bool:
        """
        Delete a node.
        
        Args:
            id: Node ID to delete
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def delete_relationship(self, 
                                source_id: str, 
                                target_id: str,
                                type: Optional[str] = None) -> bool:
        """
        Delete a relationship.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            type: Optional relationship type
            
        Returns:
            True if deletion successful
        """
        pass


class KeyValueDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for key-value databases.
    
    This class provides methods for storing and retrieving key-value pairs,
    with support for expiration and batch operations.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.KEY_VALUE
    
    @abstractmethod
    async def set(self,
                key: str,
                value: Any,
                expiration: Optional[int] = None) -> bool:
        """
        Set a key-value pair.
        
        Args:
            key: The key
            value: The value
            expiration: Optional expiration time in seconds
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a key-value pair.
        
        Args:
            key: The key to delete
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists.
        
        Args:
            key: The key to check
            
        Returns:
            True if the key exists
        """
        pass
    
    @abstractmethod
    async def set_batch(self,
                       items: Dict[str, Any],
                       expiration: Optional[int] = None) -> bool:
        """
        Set multiple key-value pairs.
        
        Args:
            items: Dictionary of key-value pairs
            expiration: Optional expiration time in seconds
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def get_batch(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values by keys.
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            Dictionary of key-value pairs for found keys
        """
        pass
    
    @abstractmethod
    async def delete_batch(self, keys: List[str]) -> bool:
        """
        Delete multiple key-value pairs.
        
        Args:
            keys: List of keys to delete
            
        Returns:
            True if operation successful
        """
        pass


class DocumentDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for document databases.
    
    This class provides methods for storing and retrieving structured documents,
    with support for queries and indexing.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.DOCUMENT
    
    @abstractmethod
    async def insert(self,
                    collection: str,
                    document: Dict[str, Any],
                    id: Optional[str] = None) -> str:
        """
        Insert a document.
        
        Args:
            collection: Collection name
            document: Document to insert
            id: Optional document ID (generated if not provided)
            
        Returns:
            Document ID
        """
        pass
    
    @abstractmethod
    async def find(self,
                 collection: str,
                 query: Dict[str, Any],
                 projection: Optional[Dict[str, bool]] = None,
                 limit: int = 100,
                 offset: int = 0) -> List[Dict[str, Any]]:
        """
        Find documents matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            projection: Optional fields to include or exclude
            limit: Maximum number of results
            offset: Starting offset for pagination
            
        Returns:
            List of matching documents
        """
        pass
    
    @abstractmethod
    async def find_one(self,
                     collection: str,
                     query: Dict[str, Any],
                     projection: Optional[Dict[str, bool]] = None) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            projection: Optional fields to include or exclude
            
        Returns:
            Matching document if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self,
                   collection: str,
                   query: Dict[str, Any],
                   update: Dict[str, Any],
                   upsert: bool = False) -> int:
        """
        Update documents matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            update: Update operations
            upsert: Whether to insert if no matching document exists
            
        Returns:
            Number of documents updated
        """
        pass
    
    @abstractmethod
    async def delete(self,
                   collection: str,
                   query: Dict[str, Any]) -> int:
        """
        Delete documents matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            
        Returns:
            Number of documents deleted
        """
        pass
    
    @abstractmethod
    async def count(self,
                  collection: str,
                  query: Dict[str, Any]) -> int:
        """
        Count documents matching a query.
        
        Args:
            collection: Collection name
            query: Query to match documents
            
        Returns:
            Number of matching documents
        """
        pass


class CacheDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for cache databases.
    
    This class provides methods for caching data with expiration,
    supporting both simple values and structured data.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.CACHE
    
    @abstractmethod
    async def set(self,
                key: str,
                value: Any,
                expiration: int) -> bool:
        """
        Set a cached value with expiration.
        
        Args:
            key: Cache key
            value: Value to cache
            expiration: Expiration time in seconds
            
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a cached value.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete a cached value.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deletion successful
        """
        pass
    
    @abstractmethod
    async def flush(self) -> bool:
        """
        Clear all cached values.
        
        Returns:
            True if operation successful
        """
        pass
    
    @abstractmethod
    async def touch(self,
                  key: str,
                  expiration: int) -> bool:
        """
        Update expiration for a cached value.
        
        Args:
            key: Cache key
            expiration: New expiration time in seconds
            
        Returns:
            True if operation successful
        """
        pass


class RelationalDatabaseAdapter(DatabaseAdapter):
    """
    Adapter for relational databases.
    
    This class provides methods for executing SQL queries,
    with support for transactions and schema management.
    """
    
    @property
    def db_type(self) -> DatabaseType:
        """Get the database type."""
        return DatabaseType.RELATION
    
    @abstractmethod
    async def execute(self,
                    query: str,
                    params: Optional[List[Any]] = None) -> Any:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    async def execute_batch(self,
                          queries: List[str],
                          params_list: Optional[List[List[Any]]] = None) -> List[Any]:
        """
        Execute multiple SQL queries.
        
        Args:
            queries: List of SQL queries to execute
            params_list: Optional list of query parameters
            
        Returns:
            List of query results
        """
        pass
    
    @abstractmethod
    async def begin_transaction(self) -> bool:
        """
        Begin a transaction.
        
        Returns:
            True if transaction started successfully
        """
        pass
    
    @abstractmethod
    async def commit_transaction(self) -> bool:
        """
        Commit the current transaction.
        
        Returns:
            True if commit successful
        """
        pass
    
    @abstractmethod
    async def rollback_transaction(self) -> bool:
        """
        Rollback the current transaction.
        
        Returns:
            True if rollback successful
        """
        pass
    
    @abstractmethod
    async def create_table(self,
                         table_name: str,
                         columns: Dict[str, str],
                         primary_key: Optional[str] = None,
                         if_not_exists: bool = True) -> bool:
        """
        Create a database table.
        
        Args:
            table_name: Name of the table to create
            columns: Dictionary mapping column names to types
            primary_key: Optional primary key column
            if_not_exists: Whether to use IF NOT EXISTS
            
        Returns:
            True if table created successfully
        """
        pass
    
    @abstractmethod
    async def drop_table(self,
                       table_name: str,
                       if_exists: bool = True) -> bool:
        """
        Drop a database table.
        
        Args:
            table_name: Name of the table to drop
            if_exists: Whether to use IF EXISTS
            
        Returns:
            True if table dropped successfully
        """
        pass


class DatabaseFactory:
    """
    Factory for creating database adapters.
    
    This class provides methods for creating database adapters based on
    the database type and backend, with hardware-specific optimization.
    """
    
    @staticmethod
    def create_adapter(db_type: Union[DatabaseType, str],
                     backend: Optional[Union[DatabaseBackend, str]] = None,
                     namespace: str = "default",
                     config: Optional[Dict[str, Any]] = None) -> DatabaseAdapter:
        """
        Create a database adapter.
        
        Args:
            db_type: Type of database
            backend: Optional specific backend (auto-detected if not provided)
            namespace: Namespace for data isolation
            config: Optional configuration parameters
            
        Returns:
            Database adapter instance
        """
        # Convert string to enum if needed
        if isinstance(db_type, str):
            db_type = DatabaseType.from_string(db_type)
        
        # Auto-detect optimal backend if not specified
        if backend is None:
            backend = DatabaseFactory._detect_optimal_backend(db_type)
        elif isinstance(backend, str):
            backend = DatabaseBackend.from_string(backend)
        
        # Create appropriate adapter based on type and backend
        if db_type == DatabaseType.VECTOR:
            return DatabaseFactory._create_vector_adapter(backend, namespace, config)
        elif db_type == DatabaseType.GRAPH:
            return DatabaseFactory._create_graph_adapter(backend, namespace, config)
        elif db_type == DatabaseType.KEY_VALUE:
            return DatabaseFactory._create_key_value_adapter(backend, namespace, config)
        elif db_type == DatabaseType.DOCUMENT:
            return DatabaseFactory._create_document_adapter(backend, namespace, config)
        elif db_type == DatabaseType.CACHE:
            return DatabaseFactory._create_cache_adapter(backend, namespace, config)
        elif db_type == DatabaseType.RELATION:
            return DatabaseFactory._create_relational_adapter(backend, namespace, config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def _detect_optimal_backend(db_type: DatabaseType) -> DatabaseBackend:
        """
        Detect the optimal backend for a database type based on hardware.
        
        Args:
            db_type: Database type
            
        Returns:
            Optimal backend for the current hardware
        """
        if db_type == DatabaseType.VECTOR:
            # Check for Apple Silicon
            import platform
            if platform.processor() == 'arm':
                logger.info("Detected Apple Silicon, using Qdrant for vector database")
                return DatabaseBackend.QDRANT
            
            # Check for NVIDIA GPU
            try:
                import torch
                if torch.cuda.is_available():
                    logger.info("Detected NVIDIA GPU, using FAISS for vector database")
                    return DatabaseBackend.FAISS
            except ImportError:
                pass
            
            # Default to FAISS
            logger.info("Using FAISS as default vector database")
            return DatabaseBackend.FAISS
        
        elif db_type == DatabaseType.GRAPH:
            # Check if Neo4j is available
            try:
                import neo4j
                logger.info("Neo4j is available, using Neo4j for graph database")
                return DatabaseBackend.NEO4J
            except ImportError:
                logger.info("Neo4j not available, using NetworkX for graph database")
                return DatabaseBackend.NETWORKX
        
        elif db_type == DatabaseType.KEY_VALUE:
            # Check if Redis is available
            try:
                import redis
                logger.info("Redis is available, using Redis for key-value database")
                return DatabaseBackend.REDIS
            except ImportError:
                logger.info("Redis not available, using LevelDB for key-value database")
                return DatabaseBackend.LEVELDB
        
        elif db_type == DatabaseType.DOCUMENT:
            # Check if MongoDB is available
            try:
                import pymongo
                logger.info("MongoDB is available, using MongoDB for document database")
                return DatabaseBackend.MONGODB
            except ImportError:
                logger.info("MongoDB not available, using JSONDB for document database")
                return DatabaseBackend.JSONDB
        
        elif db_type == DatabaseType.CACHE:
            # Simple in-memory cache is always available
            return DatabaseBackend.MEMORY
        
        elif db_type == DatabaseType.RELATION:
            # SQLite is always available
            return DatabaseBackend.SQLITE
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    @staticmethod
    def _create_vector_adapter(backend: DatabaseBackend,
                             namespace: str,
                             config: Optional[Dict[str, Any]]) -> VectorDatabaseAdapter:
        """Create a vector database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.FAISS:
            from hermes.adapters.vector.faiss_adapter import FAISSVectorAdapter
            return FAISSVectorAdapter(namespace, config)
        elif backend == DatabaseBackend.QDRANT:
            from hermes.adapters.vector.qdrant_adapter import QdrantVectorAdapter
            return QdrantVectorAdapter(namespace, config)
        elif backend == DatabaseBackend.CHROMADB:
            from hermes.adapters.vector.chromadb_adapter import ChromaDBVectorAdapter
            return ChromaDBVectorAdapter(namespace, config)
        elif backend == DatabaseBackend.LANCEDB:
            from hermes.adapters.vector.lancedb_adapter import LanceDBVectorAdapter
            return LanceDBVectorAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.vector.fallback_adapter import FallbackVectorAdapter
            logger.warning(f"Using fallback vector adapter for backend {backend}")
            return FallbackVectorAdapter(namespace, config)
    
    @staticmethod
    def _create_graph_adapter(backend: DatabaseBackend,
                           namespace: str,
                           config: Optional[Dict[str, Any]]) -> GraphDatabaseAdapter:
        """Create a graph database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.NEO4J:
            from hermes.adapters.graph.neo4j_adapter import Neo4jGraphAdapter
            return Neo4jGraphAdapter(namespace, config)
        elif backend == DatabaseBackend.NETWORKX:
            from hermes.adapters.graph.networkx_adapter import NetworkXGraphAdapter
            return NetworkXGraphAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.graph.fallback_adapter import FallbackGraphAdapter
            logger.warning(f"Using fallback graph adapter for backend {backend}")
            return FallbackGraphAdapter(namespace, config)
    
    @staticmethod
    def _create_key_value_adapter(backend: DatabaseBackend,
                               namespace: str,
                               config: Optional[Dict[str, Any]]) -> KeyValueDatabaseAdapter:
        """Create a key-value database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.REDIS:
            from hermes.adapters.key_value.redis_adapter import RedisKeyValueAdapter
            return RedisKeyValueAdapter(namespace, config)
        elif backend == DatabaseBackend.LEVELDB:
            from hermes.adapters.key_value.leveldb_adapter import LevelDBKeyValueAdapter
            return LevelDBKeyValueAdapter(namespace, config)
        elif backend == DatabaseBackend.ROCKSDB:
            from hermes.adapters.key_value.rocksdb_adapter import RocksDBKeyValueAdapter
            return RocksDBKeyValueAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.key_value.fallback_adapter import FallbackKeyValueAdapter
            logger.warning(f"Using fallback key-value adapter for backend {backend}")
            return FallbackKeyValueAdapter(namespace, config)
    
    @staticmethod
    def _create_document_adapter(backend: DatabaseBackend,
                              namespace: str,
                              config: Optional[Dict[str, Any]]) -> DocumentDatabaseAdapter:
        """Create a document database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.MONGODB:
            from hermes.adapters.document.mongodb_adapter import MongoDBDocumentAdapter
            return MongoDBDocumentAdapter(namespace, config)
        elif backend == DatabaseBackend.JSONDB:
            from hermes.adapters.document.jsondb_adapter import JSONDBDocumentAdapter
            return JSONDBDocumentAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.document.fallback_adapter import FallbackDocumentAdapter
            logger.warning(f"Using fallback document adapter for backend {backend}")
            return FallbackDocumentAdapter(namespace, config)
    
    @staticmethod
    def _create_cache_adapter(backend: DatabaseBackend,
                           namespace: str,
                           config: Optional[Dict[str, Any]]) -> CacheDatabaseAdapter:
        """Create a cache database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.MEMORY:
            from hermes.adapters.cache.memory_adapter import MemoryCacheAdapter
            return MemoryCacheAdapter(namespace, config)
        elif backend == DatabaseBackend.MEMCACHED:
            from hermes.adapters.cache.memcached_adapter import MemcachedCacheAdapter
            return MemcachedCacheAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.cache.fallback_adapter import FallbackCacheAdapter
            logger.warning(f"Using fallback cache adapter for backend {backend}")
            return FallbackCacheAdapter(namespace, config)
    
    @staticmethod
    def _create_relational_adapter(backend: DatabaseBackend,
                                namespace: str,
                                config: Optional[Dict[str, Any]]) -> RelationalDatabaseAdapter:
        """Create a relational database adapter."""
        # Import implementations dynamically
        if backend == DatabaseBackend.SQLITE:
            from hermes.adapters.relation.sqlite_adapter import SQLiteRelationalAdapter
            return SQLiteRelationalAdapter(namespace, config)
        elif backend == DatabaseBackend.POSTGRES:
            from hermes.adapters.relation.postgres_adapter import PostgresRelationalAdapter
            return PostgresRelationalAdapter(namespace, config)
        else:
            # Default to fallback adapter
            from hermes.adapters.relation.fallback_adapter import FallbackRelationalAdapter
            logger.warning(f"Using fallback relational adapter for backend {backend}")
            return FallbackRelationalAdapter(namespace, config)


class DatabaseManager:
    """
    Centralized manager for all database operations.
    
    This class provides a unified interface for accessing different types
    of databases, with support for namespace isolation and connection pooling.
    """
    
    def __init__(self, 
                base_path: Optional[str] = None,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the database manager.
        
        Args:
            base_path: Base path for database storage (default: ~/.tekton/data)
            config: Optional configuration parameters
        """
        # Set up base path
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path(os.path.expanduser("~/.tekton/data"))
        
        # Ensure base path exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.config = config or {}
        
        # Dictionary to store active database connections
        self.connections: Dict[str, Dict[str, DatabaseAdapter]] = {
            db_type.value: {} for db_type in DatabaseType
        }
        
        # Connection lock to prevent race conditions
        self.lock = threading.RLock()
        
        logger.normal("Database manager initialized", context={"base_path": str(self.base_path)})
    
    async def get_connection(self,
                           db_type: Union[DatabaseType, str],
                           namespace: str = "default",
                           backend: Optional[Union[DatabaseBackend, str]] = None,
                           config: Optional[Dict[str, Any]] = None) -> DatabaseAdapter:
        """
        Get a database connection for a specific type and namespace.
        
        Args:
            db_type: Type of database
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Database adapter instance
        """
        # Convert string to enum if needed
        if isinstance(db_type, str):
            db_type = DatabaseType.from_string(db_type)
        
        # Create unique connection ID
        connection_id = f"{namespace}"
        if backend:
            if isinstance(backend, str):
                backend_str = backend.upper()
            else:
                backend_str = backend.value
            connection_id += f":{backend_str}"
        
        # Check if connection already exists
        with self.lock:
            if connection_id in self.connections[db_type.value]:
                adapter = self.connections[db_type.value][connection_id]
                
                # Check if connected
                if await adapter.is_connected():
                    return adapter
                
                # Try to reconnect
                try:
                    await adapter.connect()
                    return adapter
                except Exception as e:
                    logger.error(f"Failed to reconnect to {db_type.value} database for namespace {namespace}: {e}")
                    # Remove the failed connection
                    del self.connections[db_type.value][connection_id]
            
            # Create new connection
            merged_config = self.config.copy()
            if config:
                merged_config.update(config)
            
            # Add base path to config
            merged_config["base_path"] = str(self.base_path / db_type.value / namespace)
            
            try:
                # Create adapter
                adapter = DatabaseFactory.create_adapter(
                    db_type=db_type,
                    backend=backend,
                    namespace=namespace,
                    config=merged_config
                )
                
                # Connect to database
                await adapter.connect()
                
                # Store connection
                self.connections[db_type.value][connection_id] = adapter
                
                logger.info(f"Connected to {db_type.value} database for namespace {namespace} using {adapter.backend.value}")
                return adapter
                
            except Exception as e:
                logger.error(f"Failed to connect to {db_type.value} database for namespace {namespace}: {e}")
                raise
    
    async def get_vector_db(self,
                         namespace: str = "default",
                         backend: Optional[Union[DatabaseBackend, str]] = None,
                         config: Optional[Dict[str, Any]] = None) -> VectorDatabaseAdapter:
        """
        Get a vector database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Vector database adapter instance
        """
        adapter = await self.get_connection(
            db_type=DatabaseType.VECTOR,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, VectorDatabaseAdapter):
            raise TypeError(f"Expected VectorDatabaseAdapter, got {type(adapter)}")
        
        return adapter
    
    async def get_graph_db(self,
                        namespace: str = "default",
                        backend: Optional[Union[DatabaseBackend, str]] = None,
                        config: Optional[Dict[str, Any]] = None) -> GraphDatabaseAdapter:
        """
        Get a graph database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Graph database adapter instance
        """
        adapter = await self.get_connection(
            db_type=DatabaseType.GRAPH,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, GraphDatabaseAdapter):
            raise TypeError(f"Expected GraphDatabaseAdapter, got {type(adapter)}")
        
        return adapter
    
    async def get_key_value_db(self,
                             namespace: str = "default",
                             backend: Optional[Union[DatabaseBackend, str]] = None,
                             config: Optional[Dict[str, Any]] = None) -> KeyValueDatabaseAdapter:
        """
        Get a key-value database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Key-value database adapter instance
        """
        adapter = await self.get_connection(
            db_type=DatabaseType.KEY_VALUE,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, KeyValueDatabaseAdapter):
            raise TypeError(f"Expected KeyValueDatabaseAdapter, got {type(adapter)}")
        
        return adapter
    
    async def get_document_db(self,
                           namespace: str = "default",
                           backend: Optional[Union[DatabaseBackend, str]] = None,
                           config: Optional[Dict[str, Any]] = None) -> DocumentDatabaseAdapter:
        """
        Get a document database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Document database adapter instance
        """
        adapter = await self.get_connection(
            db_type=DatabaseType.DOCUMENT,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, DocumentDatabaseAdapter):
            raise TypeError(f"Expected DocumentDatabaseAdapter, got {type(adapter)}")
        
        return adapter
    
    async def get_cache_db(self,
                        namespace: str = "default",
                        backend: Optional[Union[DatabaseBackend, str]] = None,
                        config: Optional[Dict[str, Any]] = None) -> CacheDatabaseAdapter:
        """
        Get a cache database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Cache database adapter instance
        """
        adapter = await self.get_connection(
            db_type=DatabaseType.CACHE,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, CacheDatabaseAdapter):
            raise TypeError(f"Expected CacheDatabaseAdapter, got {type(adapter)}")
        
        return adapter
    
    async def get_relational_db(self,
                             namespace: str = "default",
                             backend: Optional[Union[DatabaseBackend, str]] = None,
                             config: Optional[Dict[str, Any]] = None) -> RelationalDatabaseAdapter:
        """
        Get a relational database connection.
        
        Args:
            namespace: Namespace for data isolation
            backend: Optional specific backend (auto-detected if not provided)
            config: Optional configuration parameters
            
        Returns:
            Relational database adapter instance
        """
        adapter = await self.get_connection(
            db_type=DatabaseType.RELATION,
            namespace=namespace,
            backend=backend,
            config=config
        )
        
        if not isinstance(adapter, RelationalDatabaseAdapter):
            raise TypeError(f"Expected RelationalDatabaseAdapter, got {type(adapter)}")
        
        return adapter
    
    async def close_connection(self,
                             db_type: Union[DatabaseType, str],
                             namespace: str = "default",
                             backend: Optional[Union[DatabaseBackend, str]] = None) -> bool:
        """
        Close a database connection.
        
        Args:
            db_type: Type of database
            namespace: Namespace for data isolation
            backend: Optional specific backend
            
        Returns:
            True if connection closed successfully
        """
        # Convert string to enum if needed
        if isinstance(db_type, str):
            db_type = DatabaseType.from_string(db_type)
        
        # Create unique connection ID
        connection_id = f"{namespace}"
        if backend:
            if isinstance(backend, str):
                backend_str = backend.upper()
            else:
                backend_str = backend.value
            connection_id += f":{backend_str}"
        
        # Check if connection exists
        with self.lock:
            if connection_id in self.connections[db_type.value]:
                adapter = self.connections[db_type.value][connection_id]
                
                try:
                    # Disconnect from database
                    await adapter.disconnect()
                    
                    # Remove connection
                    del self.connections[db_type.value][connection_id]
                    
                    logger.info(f"Closed {db_type.value} database connection for namespace {namespace}")
                    return True
                except Exception as e:
                    logger.error(f"Error closing {db_type.value} database connection for namespace {namespace}: {e}")
                    return False
            
            # Connection doesn't exist
            return True
    
    async def close_all_connections(self) -> bool:
        """
        Close all database connections.
        
        Returns:
            True if all connections closed successfully
        """
        success = True
        
        with self.lock:
            for db_type, connections in self.connections.items():
                for connection_id, adapter in list(connections.items()):
                    try:
                        # Disconnect from database
                        await adapter.disconnect()
                        
                        # Remove connection
                        del connections[connection_id]
                        
                        logger.info(f"Closed {db_type} database connection {connection_id}")
                    except Exception as e:
                        logger.error(f"Error closing {db_type} database connection {connection_id}: {e}")
                        success = False
        
        return success
    
    def get_namespaces(self, db_type: Union[DatabaseType, str]) -> List[str]:
        """
        Get list of available namespaces for a database type.
        
        Args:
            db_type: Type of database
            
        Returns:
            List of namespace names
        """
        # Convert string to enum if needed
        if isinstance(db_type, str):
            db_type = DatabaseType.from_string(db_type)
        
        # Get path for this database type
        db_path = self.base_path / db_type.value
        
        if not db_path.exists():
            return []
        
        # List directories (each is a namespace)
        try:
            return [d.name for d in db_path.iterdir() if d.is_dir()]
        except Exception as e:
            logger.error(f"Error getting namespaces for {db_type.value}: {e}")
            return []