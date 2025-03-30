"""
FAISS Vector Adapter - High-performance vector database using Facebook AI Similarity Search.

This module provides a VectorDatabaseAdapter implementation that uses FAISS
for fast and efficient similarity search with hardware acceleration.
"""

import os
import json
import time
import uuid
import numpy as np
import faiss
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from hermes.core.logging import get_logger
from hermes.core.database_manager import VectorDatabaseAdapter, DatabaseBackend

# Logger for this module
logger = get_logger("hermes.adapters.vector.faiss")


class FAISSVectorAdapter(VectorDatabaseAdapter):
    """
    FAISS vector database adapter for high-performance similarity search.
    
    This adapter provides fast vector operations using FAISS for
    hardware-accelerated vector similarity search (CPU or GPU).
    """
    
    def __init__(self, 
                namespace: str,
                config: Optional[Dict[str, Any]] = None):
        """
        Initialize the FAISS vector adapter.
        
        Args:
            namespace: Namespace for data isolation
            config: Optional configuration parameters
        """
        super().__init__(namespace, config)
        
        # Get base path from config
        self.base_path = Path(self.config.get("base_path", os.path.expanduser("~/.tekton/data/vector")))
        
        # Create directory for this namespace
        self.namespace_path = self.base_path / namespace
        self.namespace_path.mkdir(parents=True, exist_ok=True)
        
        # Paths for data and index files
        self.data_file = self.namespace_path / "vectors.json"
        self.index_file = self.namespace_path / "index.faiss"
        
        # Vector dimensions
        self.vector_dim = self.config.get("vector_dim", 1536)  # Default for OpenAI embeddings
        
        # In-memory storage
        self.vectors: Dict[str, Dict[str, Any]] = {}
        self.index = None
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        
        # Internal state
        self._connected = False
        self._modified = False
        
        # GPU usage
        self.use_gpu = self.config.get("use_gpu", False)
        if self.use_gpu:
            try:
                # Check CUDA availability
                import torch
                self.use_gpu = torch.cuda.is_available()
                if not self.use_gpu:
                    logger.warning("GPU requested but CUDA not available, falling back to CPU")
            except ImportError:
                logger.warning("GPU requested but PyTorch not installed, falling back to CPU")
                self.use_gpu = False
    
    @property
    def backend(self) -> DatabaseBackend:
        """Get the database backend."""
        return DatabaseBackend.FAISS
    
    async def connect(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            True if connection successful
        """
        try:
            # Load vectors from file if it exists
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    self.vectors = json.load(f)
                
                # If vectors exist, get vector dimension from first vector
                if self.vectors:
                    first_id = next(iter(self.vectors))
                    self.vector_dim = len(self.vectors[first_id]["vector"])
            else:
                self.vectors = {}
            
            # Load index from file if it exists
            if self.index_file.exists() and self.vectors:
                try:
                    self.index = faiss.read_index(str(self.index_file))
                    
                    # Rebuild id mappings
                    self._rebuild_id_mappings()
                except Exception as e:
                    logger.error(f"Error loading FAISS index, rebuilding: {e}")
                    await self._build_index()
            else:
                # Create new index
                await self._build_index()
            
            self._connected = True
            self._modified = False
            
            logger.info(f"Connected to FAISS vector database for namespace {self.namespace}")
            logger.debug(f"Loaded {len(self.vectors)} vectors")
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to FAISS vector database: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the database.
        
        Returns:
            True if disconnection successful
        """
        try:
            # Save vectors if modified
            if self._modified:
                await self._save()
            
            self.vectors = {}
            self.index = None
            self.id_to_index = {}
            self.index_to_id = {}
            
            self._connected = False
            self._modified = False
            
            logger.info(f"Disconnected from FAISS vector database for namespace {self.namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from FAISS vector database: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """
        Check if connected to the database.
        
        Returns:
            True if connected
        """
        return self._connected
    
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
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            # Check vector dimensions
            if len(vector) != self.vector_dim and self.vectors:
                logger.error(f"Vector dimension mismatch: expected {self.vector_dim}, got {len(vector)}")
                return False
            elif not self.vectors:
                # First vector, set dimension
                self.vector_dim = len(vector)
                # Re-create index with correct dimensions
                await self._build_index()
            
            # Convert vector to numpy array
            vector_np = np.array([vector], dtype=np.float32)
            
            # Normalize vector
            faiss.normalize_L2(vector_np)
            
            # Store vector data
            self.vectors[id] = {
                "id": id,
                "vector": vector,
                "metadata": metadata or {},
                "text": text,
                "created_at": time.time()
            }
            
            # Add to index
            if id in self.id_to_index:
                # Update existing vector
                idx = self.id_to_index[id]
                self.index.remove_ids(np.array([idx], dtype=np.int64))
            
            # Add to index and get new ID
            idx = len(self.id_to_index)
            self.index.add(vector_np)
            
            # Update mappings
            self.id_to_index[id] = idx
            self.index_to_id[idx] = id
            
            # Mark as modified
            self._modified = True
            
            logger.debug(f"Stored vector with ID {id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing vector: {e}")
            return False
    
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
        if not self._connected:
            logger.error("Not connected to database")
            return []
        
        try:
            # If no vectors, return empty list
            if not self.vectors or self.index.ntotal == 0:
                return []
            
            # Convert query vector to numpy array
            query_np = np.array([query_vector], dtype=np.float32)
            
            # Normalize query vector
            faiss.normalize_L2(query_np)
            
            # Get more results for filtering
            search_limit = limit * 10 if filter else limit
            
            # Search index
            distances, indices = self.index.search(query_np, min(search_limit, self.index.ntotal))
            
            # Process results
            results = []
            
            for i, idx in enumerate(indices[0]):
                if idx == -1:  # FAISS sentinel value for no more results
                    break
                
                # Get vector ID
                vector_id = self.index_to_id.get(int(idx))
                if not vector_id or vector_id not in self.vectors:
                    continue
                
                vector = self.vectors[vector_id]
                
                # Apply filter if provided
                if filter and not self._matches_filter(vector, filter):
                    continue
                
                # Calculate similarity score (convert distance to similarity)
                similarity = 1.0 - float(distances[0][i] / 2.0)
                
                results.append({
                    "id": vector_id,
                    "metadata": vector.get("metadata", {}),
                    "text": vector.get("text"),
                    "relevance": similarity,
                    "vector": vector.get("vector")
                })
                
                if len(results) >= limit:
                    break
            
            logger.debug(f"Found {len(results)} similar vectors")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
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
        if not self._connected:
            logger.error("Not connected to database")
            return False
        
        try:
            if id:
                # Delete specific vector
                if id in self.vectors:
                    # Remove from index if present
                    if id in self.id_to_index:
                        idx = self.id_to_index[id]
                        self.index.remove_ids(np.array([idx], dtype=np.int64))
                        del self.index_to_id[idx]
                        del self.id_to_index[id]
                    
                    # Remove from vectors dict
                    del self.vectors[id]
                    self._modified = True
                    
                    # Rebuild ID mappings
                    if self.index.ntotal > 0:
                        self._rebuild_id_mappings()
                    
                    logger.debug(f"Deleted vector with ID {id}")
                    return True
                else:
                    logger.warning(f"Vector with ID {id} not found")
                    return False
            
            elif filter:
                # Delete vectors matching filter
                deleted = False
                ids_to_delete = []
                
                for vector_id, vector in self.vectors.items():
                    if self._matches_filter(vector, filter):
                        ids_to_delete.append(vector_id)
                
                if ids_to_delete:
                    # Delete from vectors dict
                    for vector_id in ids_to_delete:
                        del self.vectors[vector_id]
                    
                    # Rebuild index (more efficient than removing individual IDs)
                    await self._build_index()
                    
                    self._modified = True
                    deleted = True
                
                if deleted:
                    logger.debug(f"Deleted {len(ids_to_delete)} vectors matching filter")
                    return True
                else:
                    logger.warning("No vectors matched filter")
                    return False
            
            else:
                # Delete all vectors
                self.vectors = {}
                await self._build_index()
                self._modified = True
                
                logger.debug("Deleted all vectors")
                return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific vector by ID.
        
        Args:
            id: Vector ID to retrieve
            
        Returns:
            Vector with metadata if found, None otherwise
        """
        if not self._connected:
            logger.error("Not connected to database")
            return None
        
        try:
            if id in self.vectors:
                vector = self.vectors[id]
                
                return {
                    "id": id,
                    "metadata": vector.get("metadata", {}),
                    "text": vector.get("text"),
                    "vector": vector.get("vector"),
                    "created_at": vector.get("created_at")
                }
            else:
                logger.debug(f"Vector with ID {id} not found")
                return None
            
        except Exception as e:
            logger.error(f"Error getting vector: {e}")
            return None
    
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
        if not self._connected:
            logger.error("Not connected to database")
            return []
        
        try:
            # Get matching vectors
            matching_vectors = []
            
            for vector_id, vector in self.vectors.items():
                if filter and not self._matches_filter(vector, filter):
                    continue
                
                matching_vectors.append({
                    "id": vector_id,
                    "metadata": vector.get("metadata", {}),
                    "text": vector.get("text"),
                    "created_at": vector.get("created_at")
                })
            
            # Sort by creation time (newest first)
            matching_vectors.sort(key=lambda v: v.get("created_at", 0), reverse=True)
            
            # Apply pagination
            paginated = matching_vectors[offset:offset + limit]
            
            logger.debug(f"Listed {len(paginated)} vectors")
            return paginated
            
        except Exception as e:
            logger.error(f"Error listing vectors: {e}")
            return []
    
    async def _save(self) -> bool:
        """Save vectors and index to disk."""
        try:
            # Save vectors
            with open(self.data_file, "w") as f:
                json.dump(self.vectors, f)
            
            # Save index if it exists
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_file))
            
            self._modified = False
            
            logger.debug(f"Saved {len(self.vectors)} vectors to disk")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vectors to disk: {e}")
            return False
    
    async def _build_index(self) -> None:
        """Build FAISS search index."""
        try:
            # Create index
            if self.use_gpu:
                # Use IVF index for large datasets on GPU
                if len(self.vectors) > 1000:
                    # Number of centroids - rule of thumb: sqrt(n) * 4
                    n_centroids = max(4, min(1024, int(np.sqrt(len(self.vectors)) * 4)))
                    
                    # Create CPU index first
                    quantizer = faiss.IndexFlatIP(self.vector_dim)
                    index = faiss.IndexIVFFlat(quantizer, self.vector_dim, n_centroids, faiss.METRIC_INNER_PRODUCT)
                    
                    # Only train if we have vectors
                    if self.vectors:
                        # Extract vectors for training
                        train_vectors = np.array([v["vector"] for v in self.vectors.values()], dtype=np.float32)
                        faiss.normalize_L2(train_vectors)
                        
                        # Train index
                        index.train(train_vectors)
                    
                    # Convert to GPU
                    res = faiss.StandardGpuResources()
                    self.index = faiss.index_cpu_to_gpu(res, 0, index)
                else:
                    # Use flat index for small datasets
                    res = faiss.StandardGpuResources()
                    self.index = faiss.index_cpu_to_gpu(res, 0, faiss.IndexFlatIP(self.vector_dim))
            else:
                # Use IVF index for large datasets on CPU
                if len(self.vectors) > 10000:
                    # Number of centroids - rule of thumb: sqrt(n) * 4
                    n_centroids = max(4, min(1024, int(np.sqrt(len(self.vectors)) * 4)))
                    
                    quantizer = faiss.IndexFlatIP(self.vector_dim)
                    self.index = faiss.IndexIVFFlat(quantizer, self.vector_dim, n_centroids, faiss.METRIC_INNER_PRODUCT)
                    
                    # Only train if we have vectors
                    if self.vectors:
                        # Extract vectors for training
                        train_vectors = np.array([v["vector"] for v in self.vectors.values()], dtype=np.float32)
                        faiss.normalize_L2(train_vectors)
                        
                        # Train index
                        self.index.train(train_vectors)
                else:
                    # Use flat index for small/medium datasets
                    self.index = faiss.IndexFlatIP(self.vector_dim)
            
            # Add vectors to index
            if self.vectors:
                # Extract vectors and IDs
                all_vectors = []
                all_ids = []
                
                for i, (vector_id, vector_data) in enumerate(self.vectors.items()):
                    all_vectors.append(vector_data["vector"])
                    all_ids.append(vector_id)
                    
                    # Update mappings
                    self.id_to_index[vector_id] = i
                    self.index_to_id[i] = vector_id
                
                # Convert to numpy and normalize
                vectors_np = np.array(all_vectors, dtype=np.float32)
                faiss.normalize_L2(vectors_np)
                
                # Add to index
                self.index.add(vectors_np)
            
            logger.debug(f"Built FAISS search index with {len(self.vectors)} vectors")
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}")
            # Create empty index
            self.index = faiss.IndexFlatIP(self.vector_dim)
            self.id_to_index = {}
            self.index_to_id = {}
    
    def _rebuild_id_mappings(self) -> None:
        """Rebuild ID to index mappings."""
        self.id_to_index = {}
        self.index_to_id = {}
        
        for i, vector_id in enumerate(self.vectors.keys()):
            self.id_to_index[vector_id] = i
            self.index_to_id[i] = vector_id
    
    def _matches_filter(self, vector: Dict[str, Any], filter: Dict[str, Any]) -> bool:
        """Check if a vector matches a metadata filter."""
        metadata = vector.get("metadata", {})
        
        for key, value in filter.items():
            # Handle nested keys
            if "." in key:
                parts = key.split(".")
                current = metadata
                
                for part in parts[:-1]:
                    if not isinstance(current, dict) or part not in current:
                        return False
                    current = current[part]
                
                last_part = parts[-1]
                
                if not isinstance(current, dict) or last_part not in current:
                    return False
                
                if current[last_part] != value:
                    return False
            
            # Simple key
            elif key not in metadata or metadata[key] != value:
                return False
        
        return True