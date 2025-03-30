#!/usr/bin/env python3
"""
Database Services Example - Demonstrates usage of Hermes's database services.

This script shows how to use the database services provided by Hermes,
including different types of databases and operations.
"""

import os
import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional

from hermes.utils.database_helper import DatabaseClient
from hermes.core.database_manager import DatabaseBackend


async def demonstrate_vector_db(namespace: str, logger) -> None:
    """
    Demonstrate vector database operations.
    
    Args:
        namespace: Database namespace
        logger: Logger instance
    """
    logger.info("\n=== Vector Database ===\n")
    
    # Get vector database connection
    client = DatabaseClient("example")
    vector_db = await client.get_vector_db(namespace=namespace)
    logger.info(f"Connected to vector database with backend: {vector_db.backend.value}")
    
    # Store vectors
    vector1 = [0.1, 0.2, 0.3, 0.4, 0.5]
    vector2 = [0.2, 0.3, 0.4, 0.5, 0.6]
    vector3 = [0.3, 0.4, 0.5, 0.6, 0.7]
    
    await vector_db.store(
        id="doc1",
        vector=vector1,
        metadata={"type": "example", "topic": "databases"},
        text="This is document 1 about databases"
    )
    
    await vector_db.store(
        id="doc2",
        vector=vector2,
        metadata={"type": "example", "topic": "vectors"},
        text="This is document 2 about vectors"
    )
    
    await vector_db.store(
        id="doc3",
        vector=vector3,
        metadata={"type": "example", "topic": "search"},
        text="This is document 3 about search"
    )
    
    logger.info("Stored 3 vectors")
    
    # Search vectors
    results = await vector_db.search(
        query_vector=vector2,
        limit=2
    )
    
    logger.info("Search results:")
    for result in results:
        logger.info(f"  - ID: {result['id']}, Text: {result['text']}, Score: {result['relevance']:.4f}")
    
    # Filter by metadata
    filtered_results = await vector_db.search(
        query_vector=vector2,
        limit=2,
        filter={"topic": "databases"}
    )
    
    logger.info("\nFiltered search results:")
    for result in filtered_results:
        logger.info(f"  - ID: {result['id']}, Text: {result['text']}, Score: {result['relevance']:.4f}")
    
    # Get specific vector
    doc = await vector_db.get("doc1")
    logger.info(f"\nDocument 1: {doc['text']}")
    
    # List vectors
    all_docs = await vector_db.list(limit=10)
    logger.info(f"\nAll documents ({len(all_docs)}):")
    for doc in all_docs:
        logger.info(f"  - ID: {doc['id']}, Text: {doc['text']}")
    
    # Delete a vector
    await vector_db.delete("doc3")
    logger.info("\nDeleted document 3")
    
    # List again
    remaining_docs = await vector_db.list(limit=10)
    logger.info(f"\nRemaining documents ({len(remaining_docs)}):")
    for doc in remaining_docs:
        logger.info(f"  - ID: {doc['id']}, Text: {doc['text']}")
    
    # Close connection
    await client.close_connections()


async def demonstrate_graph_db(namespace: str, logger) -> None:
    """
    Demonstrate graph database operations.
    
    Args:
        namespace: Database namespace
        logger: Logger instance
    """
    logger.info("\n=== Graph Database ===\n")
    
    try:
        # Get graph database connection
        client = DatabaseClient("example")
        graph_db = await client.get_graph_db(namespace=namespace)
        logger.info(f"Connected to graph database with backend: {graph_db.backend.value}")
        
        # Add nodes
        await graph_db.add_node(
            id="person1",
            labels=["Person"],
            properties={"name": "Alice", "age": 30}
        )
        
        await graph_db.add_node(
            id="person2",
            labels=["Person"],
            properties={"name": "Bob", "age": 28}
        )
        
        await graph_db.add_node(
            id="company1",
            labels=["Company"],
            properties={"name": "Acme Inc", "founded": 2000}
        )
        
        logger.info("Added 3 nodes")
        
        # Add relationships
        await graph_db.add_relationship(
            source_id="person1",
            target_id="company1",
            type="WORKS_FOR",
            properties={"since": 2018, "position": "Developer"}
        )
        
        await graph_db.add_relationship(
            source_id="person2",
            target_id="company1",
            type="WORKS_FOR",
            properties={"since": 2020, "position": "Manager"}
        )
        
        await graph_db.add_relationship(
            source_id="person1",
            target_id="person2",
            type="KNOWS",
            properties={"since": 2019}
        )
        
        logger.info("Added 3 relationships")
        
        # Get node
        person = await graph_db.get_node("person1")
        logger.info(f"\nPerson 1: {person['properties'].get('name')} (age {person['properties'].get('age')})")
        
        # Get relationships
        relationships = await graph_db.get_relationships(
            node_id="person1",
            direction="outgoing"
        )
        
        logger.info(f"\nRelationships for Person 1 ({len(relationships)}):")
        for rel in relationships:
            logger.info(f"  - Type: {rel['type']}, Target: {rel['target_id']}")
        
        # Execute a custom query
        query_results = await graph_db.query(
            query="""
            MATCH (p:Person {namespace: $namespace})-[r:WORKS_FOR]->(c:Company {namespace: $namespace})
            RETURN p.name AS name, r.position AS position, c.name AS company
            """,
            params={}
        )
        
        logger.info(f"\nQuery results ({len(query_results)}):")
        for result in query_results:
            logger.info(f"  - {result['name']} works as {result['position']} at {result['company']}")
        
        # Close connection
        await client.close_connections()
    
    except Exception as e:
        logger.error(f"Error demonstrating graph database: {e}")


async def demonstrate_key_value_db(namespace: str, logger) -> None:
    """
    Demonstrate key-value database operations.
    
    Args:
        namespace: Database namespace
        logger: Logger instance
    """
    logger.info("\n=== Key-Value Database ===\n")
    
    # Get key-value database connection
    client = DatabaseClient("example")
    kv_db = await client.get_key_value_db(namespace=namespace)
    logger.info(f"Connected to key-value database with backend: {kv_db.backend.value}")
    
    # Set values
    await kv_db.set("string_key", "Hello, world!")
    await kv_db.set("int_key", 42)
    await kv_db.set("dict_key", {"name": "Example", "values": [1, 2, 3]})
    
    # Set value with expiration
    await kv_db.set("expiring_key", "I will expire soon", expiration=5)
    
    logger.info("Set 4 key-value pairs")
    
    # Get values
    string_val = await kv_db.get("string_key")
    int_val = await kv_db.get("int_key")
    dict_val = await kv_db.get("dict_key")
    
    logger.info(f"\nString value: {string_val}")
    logger.info(f"Integer value: {int_val}")
    logger.info(f"Dictionary value: {dict_val}")
    
    # Check existence
    exists = await kv_db.exists("string_key")
    logger.info(f"\nstring_key exists: {exists}")
    
    # Batch operations
    batch_items = {
        "batch1": "First batch item",
        "batch2": "Second batch item",
        "batch3": "Third batch item"
    }
    
    await kv_db.set_batch(batch_items)
    logger.info("\nSet batch of 3 items")
    
    # Get batch
    batch_values = await kv_db.get_batch(["batch1", "batch2", "batch3"])
    logger.info("\nBatch values:")
    for key, value in batch_values.items():
        logger.info(f"  - {key}: {value}")
    
    # Delete key
    await kv_db.delete("int_key")
    logger.info("\nDeleted int_key")
    
    # Verify deletion
    exists = await kv_db.exists("int_key")
    logger.info(f"int_key exists: {exists}")
    
    # Wait for expiration
    logger.info("\nWaiting for expiring_key to expire...")
    await asyncio.sleep(6)
    
    # Check if expired
    expired_val = await kv_db.get("expiring_key")
    logger.info(f"expiring_key value: {expired_val}")
    
    # Close connection
    await client.close_connections()


async def demonstrate_document_db(namespace: str, logger) -> None:
    """
    Demonstrate document database operations.
    
    Args:
        namespace: Database namespace
        logger: Logger instance
    """
    logger.info("\n=== Document Database ===\n")
    
    # Get document database connection
    client = DatabaseClient("example")
    doc_db = await client.get_document_db(namespace=namespace)
    logger.info(f"Connected to document database with backend: {doc_db.backend.value}")
    
    # Insert documents
    user1_id = await doc_db.insert(
        collection="users",
        document={
            "name": "John Doe",
            "email": "john@example.com",
            "age": 35,
            "interests": ["programming", "databases", "AI"]
        }
    )
    
    user2_id = await doc_db.insert(
        collection="users",
        document={
            "name": "Jane Smith",
            "email": "jane@example.com",
            "age": 28,
            "interests": ["design", "databases", "photography"]
        }
    )
    
    user3_id = await doc_db.insert(
        collection="users",
        document={
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "age": 42,
            "interests": ["AI", "machine learning", "data science"]
        }
    )
    
    logger.info(f"Inserted 3 documents with IDs: {user1_id}, {user2_id}, {user3_id}")
    
    # Find specific document
    user = await doc_db.find_one(
        collection="users",
        query={"name": "Jane Smith"}
    )
    
    logger.info(f"\nFound user: {user.get('name')} ({user.get('email')})")
    
    # Find with query
    database_users = await doc_db.find(
        collection="users",
        query={"interests": "databases"}
    )
    
    logger.info(f"\nUsers interested in databases ({len(database_users)}):")
    for user in database_users:
        logger.info(f"  - {user.get('name')} ({user.get('email')})")
    
    # Update document
    updated_count = await doc_db.update(
        collection="users",
        query={"name": "John Doe"},
        update={"$set": {"age": 36, "interests": ["programming", "databases", "AI", "cloud"]}}
    )
    
    logger.info(f"\nUpdated {updated_count} documents")
    
    # Verify update
    updated_user = await doc_db.find_one(
        collection="users",
        query={"name": "John Doe"}
    )
    
    logger.info(f"Updated user: {updated_user.get('name')} (age {updated_user.get('age')})")
    logger.info(f"Interests: {', '.join(updated_user.get('interests', []))}")
    
    # Count documents
    count = await doc_db.count(
        collection="users",
        query={"age": {"$gt": 30}}
    )
    
    logger.info(f"\nUsers over 30: {count}")
    
    # Delete document
    deleted_count = await doc_db.delete(
        collection="users",
        query={"name": "Bob Johnson"}
    )
    
    logger.info(f"\nDeleted {deleted_count} documents")
    
    # Verify deletion
    remaining_count = await doc_db.count(
        collection="users",
        query={}
    )
    
    logger.info(f"Remaining users: {remaining_count}")
    
    # Close connection
    await client.close_connections()


async def demonstrate_cache_db(namespace: str, logger) -> None:
    """
    Demonstrate cache database operations.
    
    Args:
        namespace: Database namespace
        logger: Logger instance
    """
    logger.info("\n=== Cache Database ===\n")
    
    # Get cache database connection
    client = DatabaseClient("example")
    cache_db = await client.get_cache_db(namespace=namespace)
    logger.info(f"Connected to cache database with backend: {cache_db.backend.value}")
    
    # Set values with expiration
    await cache_db.set("cache_key1", "Cache value 1", expiration=10)
    await cache_db.set("cache_key2", {"complex": "object", "with": ["nested", "values"]}, expiration=20)
    
    logger.info("Set 2 cache values")
    
    # Get values
    value1 = await cache_db.get("cache_key1")
    value2 = await cache_db.get("cache_key2")
    
    logger.info(f"\nCache value 1: {value1}")
    logger.info(f"Cache value 2: {value2}")
    
    # Update expiration
    await cache_db.touch("cache_key1", expiration=30)
    logger.info("\nUpdated expiration for cache_key1 to 30 seconds")
    
    # Delete value
    await cache_db.delete("cache_key2")
    logger.info("\nDeleted cache_key2")
    
    # Verify deletion
    value2 = await cache_db.get("cache_key2")
    logger.info(f"Cache value 2 after deletion: {value2}")
    
    # Flush cache
    await cache_db.flush()
    logger.info("\nFlushed cache")
    
    # Verify flush
    value1 = await cache_db.get("cache_key1")
    logger.info(f"Cache value 1 after flush: {value1}")
    
    # Close connection
    await client.close_connections()


async def demonstrate_database_client(logger) -> None:
    """
    Demonstrate the DatabaseClient for managing connections.
    
    Args:
        logger: Logger instance
    """
    logger.info("\n=== DatabaseClient ===\n")
    
    # Create a client for a component
    client = DatabaseClient("my_component")
    logger.info("Created DatabaseClient for 'my_component'")
    
    # Get databases for different purposes
    vector_db = await client.get_vector_db(namespace="embeddings")
    kv_db = await client.get_key_value_db(namespace="config")
    cache_db = await client.get_cache_db(namespace="user_cache")
    
    logger.info(f"Connected to vector database with backend: {vector_db.backend.value}")
    logger.info(f"Connected to key-value database with backend: {kv_db.backend.value}")
    logger.info(f"Connected to cache database with backend: {cache_db.backend.value}")
    
    # Use client as context manager
    logger.info("\nUsing client as context manager:")
    async with DatabaseClient("another_component") as ctx_client:
        doc_db = await ctx_client.get_document_db(namespace="records")
        logger.info(f"Connected to document database with backend: {doc_db.backend.value}")
        logger.info("Context manager will automatically close connections")
    
    # Close connections manually
    await client.close_connections()
    logger.info("\nClosed all connections")


async def main():
    """Main function to demonstrate database services."""
    # Simple logger
    class Logger:
        def info(self, message):
            print(message)
        
        def error(self, message):
            print(f"ERROR: {message}")
    
    logger = Logger()
    
    # Create base namespace for examples
    namespace = f"example.{os.getpid()}"
    
    # Run demonstrations
    await demonstrate_vector_db(namespace, logger)
    await demonstrate_key_value_db(namespace, logger)
    
    try:
        await demonstrate_graph_db(namespace, logger)
    except ImportError:
        logger.error("Neo4j not available, skipping graph database example")
    
    await demonstrate_document_db(namespace, logger)
    await demonstrate_cache_db(namespace, logger)
    await demonstrate_database_client(logger)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())