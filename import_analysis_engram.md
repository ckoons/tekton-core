# Import Analysis Report for engram
Analyzed 167 unique import sources

## Import Depth Distribution
| Depth | Count | Visual |
|-------|-------|--------|
| 1 | 297 | ████████████████████████████████████████ |
| 2 | 89 | ███████████ |
| 3 | 111 | ██████████████ |
| 4 | 53 | ███████ |
| 5 | 40 | █████ |

## Top 20 Most Imported Deep Paths (depth >= 3)

### 1. MemoryService (imported 14 times)
- Full import: `from engram.core.memory import MemoryService`
- Depth: 3
- Module: `engram.core.memory`
- ⚠️  **Conflict Warning**: Also imported from:
  - `core.memory.base`
  - `engram.core.memory.base`
  - `engram.core.memory_faiss`
  - `service`
  - `engram.integrations.hermes.memory_adapter`
  - `base.service`

### 2. MemoryService (imported 7 times)
- Full import: `from engram.core.memory.base import MemoryService`
- Depth: 4
- Module: `engram.core.memory.base`
- ⚠️  **Conflict Warning**: Also imported from:
  - `core.memory.base`
  - `engram.core.memory`
  - `engram.core.memory_faiss`
  - `service`
  - `engram.integrations.hermes.memory_adapter`
  - `base.service`

### 3. MemoryManager (imported 7 times)
- Full import: `from engram.core.memory_manager import MemoryManager`
- Depth: 3
- Module: `engram.core.memory_manager`
- ⚠️  **Conflict Warning**: Also imported from:
  - `core.memory_manager`

### 4. StructuredMemory (imported 7 times)
- Full import: `from engram.core.structured_memory import StructuredMemory`
- Depth: 3
- Module: `engram.core.structured_memory`
- ⚠️  **Conflict Warning**: Also imported from:
  - `engram.core.structured.memory.base`
  - `engram.core.structured.base`

### 5. NexusInterface (imported 6 times)
- Full import: `from engram.core.nexus import NexusInterface`
- Depth: 3
- Module: `engram.core.nexus`

### 6. save_metadata_index (imported 5 times)
- Full import: `from engram.core.structured.memory.index import save_metadata_index`
- Depth: 5
- Module: `engram.core.structured.memory.index`

### 7. search_by_content (imported 5 times)
- Full import: `from engram.core.structured.search.content import search_by_content`
- Depth: 5
- Module: `engram.core.structured.search.content`

### 8. get_memory_service (imported 5 times)
- Full import: `from engram.api.dependencies import get_memory_service`
- Depth: 3
- Module: `engram.api.dependencies`

### 9. VectorStore (imported 4 times)
- Full import: `from engram.core.vector_store import VectorStore`
- Depth: 3
- Module: `engram.core.vector_store`
- ⚠️  **Conflict Warning**: Also imported from:
  - `vector.lancedb.vector_store`
  - `vector_store`
  - `base.store`

### 10. MCPCapability (imported 4 times)
- Full import: `from tekton.mcp.fastmcp.schema import MCPCapability`
- Depth: 4
- Module: `tekton.mcp.fastmcp.schema`

### 11. CORSMiddleware (imported 4 times)
- Full import: `from fastapi.middleware.cors import CORSMiddleware`
- Depth: 3
- Module: `fastapi.middleware.cors`

### 12. setup_component_logging (imported 4 times)
- Full import: `from shared.utils.logging_setup import setup_component_logging`
- Depth: 3
- Module: `shared.utils.logging_setup`

### 13. get_config (imported 4 times)
- Full import: `from engram.core.config import get_config`
- Depth: 3
- Module: `engram.core.config`

### 14. load_json_file (imported 4 times)
- Full import: `from engram.core.memory.utils import load_json_file`
- Depth: 4
- Module: `engram.core.memory.utils`
- ⚠️  **Conflict Warning**: Also imported from:
  - `engram.core.structured.utils`

### 15. save_json_file (imported 4 times)
- Full import: `from engram.core.memory.utils import save_json_file`
- Depth: 4
- Module: `engram.core.memory.utils`
- ⚠️  **Conflict Warning**: Also imported from:
  - `engram.core.structured.utils`

### 16. HermesMemoryService (imported 4 times)
- Full import: `from engram.integrations.hermes.memory_adapter import HermesMemoryService`
- Depth: 4
- Module: `engram.integrations.hermes.memory_adapter`
- ⚠️  **Conflict Warning**: Also imported from:
  - `core.service`

### 17. search_memory (imported 3 times)
- Full import: `from engram.core.memory.search import search_memory`
- Depth: 4
- Module: `engram.core.memory.search`

### 18. get_relevant_context (imported 3 times)
- Full import: `from engram.core.memory.search import get_relevant_context`
- Depth: 4
- Module: `engram.core.memory.search`
- ⚠️  **Conflict Warning**: Also imported from:
  - `operations.search`
  - `engram.core.memory_faiss.search`
  - `context`

### 19. mcp_tool (imported 3 times)
- Full import: `from tekton.mcp.fastmcp import mcp_tool`
- Depth: 3
- Module: `tekton.mcp.fastmcp`

### 20. mcp_capability (imported 3 times)
- Full import: `from tekton.mcp.fastmcp import mcp_capability`
- Depth: 3
- Module: `tekton.mcp.fastmcp`

## Flattening Recommendations

## Naming Conflicts to Avoid
These items are imported from multiple modules and would conflict if flattened:

- **CompartmentManager**: imported from 2 modules:
  - `compartments.manager`
  - `engram.core.memory.compartments`
- **DatabaseClient**: imported from 2 modules:
  - `hermes.utils.database_helper`
  - `imports`
- **FileStorage**: imported from 2 modules:
  - `engram.core.memory.storage`
  - `engram.core.memory.storage.file_storage`
- **HAS_HERMES**: imported from 3 modules:
  - `core.imports`
  - `engram.integrations.hermes.memory_adapter`
  - `imports`
- **HAS_VECTOR_DB**: imported from 2 modules:
  - `engram.core.memory`
  - `engram.core.memory.config`
- **HermesMemoryService**: imported from 2 modules:
  - `core.service`
  - `engram.integrations.hermes.memory_adapter`
- **LatentSpaceManager**: imported from 4 modules:
  - `engram.core.memory`
  - `engram.core.memory.latent_space`
  - `latent.manager`
  - `manager`
- **MODEL_CAPABILITIES**: imported from 2 modules:
  - `api.models`
  - `ollama_system_prompts`
- **Memory**: imported from 3 modules:
  - `engram`
  - `engram.simple`
  - `simple`