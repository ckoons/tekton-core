# Tekton Storage Adapters

This directory contains storage adapters for Tekton, implementing the LightRAG integration. These adapters provide a unified interface for various storage backends, including vector stores, graph databases, and key-value stores.

## Overview

The storage adapters are organized into three categories:

1. **Vector Storage**: For storing and querying vector embeddings
2. **Graph Storage**: For storing and querying graph data (nodes and edges)
3. **Key-Value Storage**: For storing and querying arbitrary data by key

Each adapter implements the corresponding interface defined in `base.py`.

## Adapter Selection

The adapters are automatically selected based on hardware capabilities and configuration settings through the factory functions in `factory.py`. The factory provides graceful fallbacks if a requested adapter is not available.

### Vector Store Selection

- **Apple Silicon**: Automatically selects Qdrant, optimized for M1/M2 processors
- **NVIDIA GPU**: Automatically selects FAISS with GPU acceleration
- **CPU-only**: Falls back to FAISS CPU implementation

### Graph Store Selection

- **Neo4j**: Used when Neo4j connection is available
- **Memory**: Used as fallback when Neo4j is not available

### KV Store Selection

- **JSON**: Simple file-based storage, used by default
- **Memory**: In-memory storage, used for testing or when persistence is not required

## Available Adapters

### Vector Storage

- **FAISS**: High-performance vector similarity search with GPU acceleration
- **Qdrant**: Vector database optimized for Apple Silicon
- **Milvus**: Distributed vector database (coming soon)
- **Chroma**: Open-source embedding database (coming soon)
- **Nano**: Lightweight vector store (coming soon)
- **PGVector**: PostgreSQL-based vector store using pgvector extension (coming soon)

### Graph Storage

- **Neo4j**: Industry-standard graph database
- **Memory**: In-memory graph storage for testing or small datasets
- **NetworkX**: Python-based graph analysis library (coming soon)
- **PostgreSQL**: Relational database with graph extensions (coming soon)
- **AGE**: PostgreSQL extension for graph data (coming soon)

### KV Storage

- **JSON**: Simple file-based key-value store
- **Memory**: In-memory key-value store
- **MongoDB**: Document database (coming soon)
- **Redis**: In-memory data structure store (coming soon)
- **PostgreSQL**: Relational database for key-value storage (coming soon)

## LightRAG Integration

The storage adapters are designed to integrate with LightRAG functionality, providing:

1. **Multiple Query Modes**: Support for naive, local, global, hybrid, and mix query strategies
2. **Unified API**: Common interface for all storage types
3. **Hardware-Aware Selection**: Automatic selection of the most appropriate backend based on available hardware
4. **Graceful Degradation**: Fallback mechanisms when preferred storage is not available

## Usage

```python
from tekton.core.storage.factory import get_vector_store, get_graph_store, get_kv_store

# Get a vector store optimized for the current hardware
vector_store = get_vector_store(namespace="my_namespace", embedding_dim=1536)

# Get a specific vector store
qdrant_store = get_vector_store(store_type="qdrant", namespace="my_namespace")

# Get a graph store
graph_store = get_graph_store(namespace="my_namespace")

# Get a key-value store
kv_store = get_kv_store(namespace="my_namespace")

# Create multiple storage instances from configuration
config = {
    "vector_stores": {
        "main": {"type": "faiss", "namespace": "main_vectors"},
        "cache": {"type": "qdrant", "namespace": "vector_cache"}
    },
    "graph_stores": {
        "knowledge_graph": {"type": "neo4j", "namespace": "kg"}
    },
    "kv_stores": {
        "metadata": {"type": "json", "namespace": "meta"}
    }
}

storages = create_storage_from_config(config)
```

## Requirements

Each adapter has specific dependencies:

- **FAISS**: Requires `faiss-cpu` or `faiss-gpu`
- **Qdrant**: Requires `qdrant-client`
- **Neo4j**: Requires `neo4j` and/or `py2neo`
- **Sentence Transformers**: Required for text embedding in vector stores

Install required dependencies based on the adapters you plan to use.

## Contributing

To add a new adapter:

1. Create a new file in the appropriate directory (vector, graph, or kv)
2. Implement the corresponding interface from `base.py`
3. Register the adapter in `factory.py`
4. Add any necessary requirements to the setup file
5. Create tests for your adapter