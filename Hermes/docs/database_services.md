# Centralized Database Services

Hermes provides centralized database services for all Tekton components, offering a unified interface for various types of databases with namespace isolation, hardware optimization, and consistent APIs.

## Overview

The centralized database services in Hermes provide the following benefits:

- **Single Source of Truth**: All data is managed through Hermes, preventing duplication and inconsistencies.
- **Namespace Isolation**: Data is segregated by component and purpose while enabling cross-cutting analysis.
- **Hardware Optimization**: Database backends are automatically selected based on available hardware.
- **Connection Pooling**: Connections are managed efficiently to reduce resource usage.
- **Consistent APIs**: All database types share similar interface patterns, making them easy to learn and use.
- **Fallback Mechanisms**: Simple implementations are provided when specialized databases are unavailable.

## Supported Database Types

Hermes supports six types of databases for different use cases:

1. **Vector Database**: For storing and searching vector embeddings (FAISS, Qdrant, ChromaDB, LanceDB)
2. **Graph Database**: For knowledge representation and relationship analysis (Neo4j, NetworkX)
3. **Key-Value Database**: For simple, fast data storage (Redis, LevelDB, RocksDB)
4. **Document Database**: For structured document storage (MongoDB, JSONDB)
5. **Cache Database**: For temporary data with expiration (Memory, Memcached)
6. **Relational Database**: For structured data and SQL queries (SQLite, PostgreSQL)

## Getting Started

To use Hermes's database services, you will need to import the appropriate utilities:

```python
# For standalone functions
from hermes.utils.database_helper import get_vector_db, get_graph_db, get_key_value_db

# For the client class (recommended)
from hermes.utils.database_helper import DatabaseClient
```

### Using the DatabaseClient

The `DatabaseClient` class is the recommended way to access database services. It automatically manages connections and provides namespace prefixing:

```python
import asyncio
from hermes.utils.database_helper import DatabaseClient

async def example():
    # Create a client for your component
    client = DatabaseClient("my_component")
    
    # Get a vector database connection
    vector_db = await client.get_vector_db(namespace="embeddings")
    
    # Store a vector
    await vector_db.store(
        id="doc1",
        vector=[0.1, 0.2, 0.3, 0.4, 0.5],
        metadata={"type": "example"},
        text="Example document"
    )
    
    # Close connections when done
    await client.close_connections()

# Run the async function
asyncio.run(example())
```

You can also use the client as a context manager:

```python
async def example():
    async with DatabaseClient("my_component") as client:
        # Get connections
        vector_db = await client.get_vector_db()
        kv_db = await client.get_key_value_db()
        
        # Use databases...
        
        # Connections are automatically closed when exiting the context
```

### Using Standalone Functions

For simpler use cases, you can use the standalone helper functions:

```python
import asyncio
from hermes.utils.database_helper import get_vector_db, get_graph_db

async def example():
    # Get a vector database connection
    vector_db = await get_vector_db(namespace="my_component.embeddings")
    
    # Get a graph database connection
    graph_db = await get_graph_db(namespace="my_component.knowledge")
    
    # Use databases...

# Run the async function
asyncio.run(example())
```

## Namespace Isolation

Namespaces are used to isolate data between components and purposes. The `DatabaseClient` automatically prefixes namespaces with the component ID:

```python
# Create a client for your component
client = DatabaseClient("my_component")

# These create different namespaces
vector_db1 = await client.get_vector_db(namespace="embeddings")  # Actual: "my_component.embeddings"
vector_db2 = await client.get_vector_db(namespace="models")     # Actual: "my_component.models"

# Default namespace is the component ID
vector_db3 = await client.get_vector_db()  # Actual: "my_component"
```

When using standalone functions, you should manually include the component prefix:

```python
vector_db = await get_vector_db(namespace="my_component.embeddings")
```

## Vector Database

The vector database is used for storing and searching vector embeddings, such as those created by language models.

### Vector Database Operations

```python
# Store a vector
await vector_db.store(
    id="doc1",
    vector=[0.1, 0.2, 0.3, 0.4, 0.5],
    metadata={"type": "example", "category": "tutorial"},
    text="Example document text"
)

# Search for similar vectors
results = await vector_db.search(
    query_vector=[0.1, 0.2, 0.3, 0.4, 0.5],
    limit=10,
    filter={"category": "tutorial"}
)

# Get a specific vector
vector = await vector_db.get(id="doc1")

# List vectors
vectors = await vector_db.list(
    limit=100,
    offset=0,
    filter={"type": "example"}
)

# Delete vectors
await vector_db.delete(id="doc1")  # Delete by ID
await vector_db.delete(filter={"type": "example"})  # Delete by filter
```

## Graph Database

The graph database is used for storing and querying relationships between entities.

### Graph Database Operations

```python
# Add nodes
await graph_db.add_node(
    id="person1",
    labels=["Person"],
    properties={"name": "Alice", "age": 30}
)

await graph_db.add_node(
    id="company1",
    labels=["Company"],
    properties={"name": "Acme Inc", "founded": 2000}
)

# Add relationships
await graph_db.add_relationship(
    source_id="person1",
    target_id="company1",
    type="WORKS_FOR",
    properties={"since": 2018, "position": "Developer"}
)

# Get a node
node = await graph_db.get_node(id="person1")

# Get relationships
relationships = await graph_db.get_relationships(
    node_id="person1",
    types=["WORKS_FOR"],
    direction="outgoing"  # or "incoming" or "both"
)

# Execute a custom query (Neo4j Cypher)
results = await graph_db.query(
    query="""
    MATCH (p:Person {namespace: $namespace})-[r:WORKS_FOR]->(c:Company {namespace: $namespace})
    RETURN p.name AS name, r.position AS position, c.name AS company
    """,
    params={}
)

# Delete nodes and relationships
await graph_db.delete_node(id="person1")
await graph_db.delete_relationship(
    source_id="person1",
    target_id="company1",
    type="WORKS_FOR"
)
```

## Key-Value Database

The key-value database is used for simple data storage with fast access.

### Key-Value Database Operations

```python
# Set values
await kv_db.set("string_key", "Hello, world!")
await kv_db.set("int_key", 42)
await kv_db.set("dict_key", {"name": "Example", "values": [1, 2, 3]})

# Set with expiration (in seconds)
await kv_db.set("expiring_key", "I will expire", expiration=60)

# Get values
value = await kv_db.get("string_key")

# Check if key exists
exists = await kv_db.exists("string_key")

# Batch operations
await kv_db.set_batch({
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
})

values = await kv_db.get_batch(["key1", "key2", "key3"])

# Delete keys
await kv_db.delete("string_key")
await kv_db.delete_batch(["key1", "key2", "key3"])
```

## Document Database

The document database is used for storing structured documents with query capabilities.

### Document Database Operations

```python
# Insert documents
user_id = await doc_db.insert(
    collection="users",
    document={
        "name": "John Doe",
        "email": "john@example.com",
        "age": 35,
        "interests": ["programming", "databases", "AI"]
    }
)

# Find documents
users = await doc_db.find(
    collection="users",
    query={"age": {"$gt": 30}},
    projection={"name": 1, "email": 1},
    limit=10,
    offset=0
)

# Find a single document
user = await doc_db.find_one(
    collection="users",
    query={"email": "john@example.com"}
)

# Update documents
updated = await doc_db.update(
    collection="users",
    query={"email": "john@example.com"},
    update={"$set": {"age": 36}},
    upsert=False
)

# Count documents
count = await doc_db.count(
    collection="users",
    query={"age": {"$gt": 30}}
)

# Delete documents
deleted = await doc_db.delete(
    collection="users",
    query={"email": "john@example.com"}
)
```

## Cache Database

The cache database is used for temporary data storage with automatic expiration.

### Cache Database Operations

```python
# Set values with expiration (in seconds)
await cache_db.set("cache_key", "Cache value", expiration=60)

# Get values
value = await cache_db.get("cache_key")

# Update expiration
await cache_db.touch("cache_key", expiration=120)

# Delete values
await cache_db.delete("cache_key")

# Clear all cache
await cache_db.flush()
```

## Relational Database

The relational database is used for structured data and SQL queries.

### Relational Database Operations

```python
# Execute a SQL query
results = await rel_db.execute(
    query="SELECT * FROM users WHERE age > ?",
    params=[30]
)

# Execute multiple queries
results = await rel_db.execute_batch(
    queries=[
        "INSERT INTO users (name, email) VALUES (?, ?)",
        "INSERT INTO users (name, email) VALUES (?, ?)"
    ],
    params_list=[
        ["John Doe", "john@example.com"],
        ["Jane Smith", "jane@example.com"]
    ]
)

# Transactions
await rel_db.begin_transaction()
try:
    await rel_db.execute("INSERT INTO users (name) VALUES (?)", ["User 1"])
    await rel_db.execute("INSERT INTO users (name) VALUES (?)", ["User 2"])
    await rel_db.commit_transaction()
except:
    await rel_db.rollback_transaction()

# Schema operations
await rel_db.create_table(
    table_name="users",
    columns={
        "id": "INTEGER",
        "name": "TEXT",
        "email": "TEXT",
        "age": "INTEGER"
    },
    primary_key="id"
)

await rel_db.drop_table(table_name="users")
```

## Hardware Optimization

Hermes automatically selects the optimal database backend based on available hardware:

- For vector databases:
  - FAISS if NVIDIA GPU is available
  - Qdrant for Apple Silicon
  - FAISS for CPU-only systems

- For graph databases:
  - Neo4j if available
  - NetworkX as a fallback

- For key-value databases:
  - Redis if available
  - LevelDB as a fallback

- For document databases:
  - MongoDB if available
  - JSONDB as a fallback

You can override the automatic selection by specifying a backend:

```python
from hermes.core.database_manager import DatabaseBackend

# Use a specific backend
vector_db = await client.get_vector_db(
    namespace="embeddings",
    backend=DatabaseBackend.FAISS
)

# Or by string
vector_db = await client.get_vector_db(
    namespace="embeddings",
    backend="faiss"
)
```

## Custom Configuration

You can provide custom configuration for database connections:

```python
# Vector database configuration
vector_db = await client.get_vector_db(
    namespace="embeddings",
    config={
        "vector_dim": 1536,  # OpenAI embedding dimension
        "use_gpu": True
    }
)

# Neo4j configuration
graph_db = await client.get_graph_db(
    namespace="knowledge",
    backend=DatabaseBackend.NEO4J,
    config={
        "uri": "bolt://localhost:7687",
        "username": "neo4j",
        "password": "password"
    }
)

# Redis configuration
kv_db = await client.get_key_value_db(
    namespace="config",
    backend=DatabaseBackend.REDIS,
    config={
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": "password"
    }
)
```

## Best Practices

1. **Use DatabaseClient**: The `DatabaseClient` class provides the best developer experience with automatic connection management and namespace prefixing.

2. **Organize by Purpose**: Use different namespaces for different types of data, even within the same component.

3. **Close Connections**: Always close connections when done, either manually or using a context manager.

4. **Use Appropriate Database Type**: Choose the right database type for your use case:
   - Vector database for embeddings and similarity search
   - Graph database for relationships and knowledge representation
   - Key-value database for simple data storage
   - Document database for structured documents
   - Cache database for temporary data
   - Relational database for SQL and structured data

5. **Handle Errors**: Database operations can fail for various reasons. Always handle errors appropriately:

   ```python
   try:
       result = await vector_db.search(query_vector=[0.1, 0.2, 0.3])
   except Exception as e:
       logger.error(f"Vector search failed: {e}")
       result = []
   ```

6. **Use Batch Operations**: When possible, use batch operations instead of individual operations for better performance.

7. **Respect Namespaces**: Don't access data from other components' namespaces unless explicitly designed for cross-component analysis.

## Extending the System

You can extend the database services by implementing new adapters for additional backends:

1. Create a new adapter class that inherits from the appropriate base class (e.g., `VectorDatabaseAdapter`)
2. Implement all abstract methods required by the interface
3. Add backend detection and adapter creation in the `DatabaseFactory` class

See existing adapters in the `hermes/adapters/` directory for examples.

## Next Steps

- Check out the [Database Example Script](../scripts/database_example.py) for complete usage examples.
- See the [API Reference](api_reference.md) for detailed documentation of all classes and methods.
- Explore the [Migration Guide](migration_guide.md) for information on moving existing components to use Hermes's database services.