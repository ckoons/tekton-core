# Tekton Import Analysis Report
Generated: 2025-06-05 16:00:31

## Summary
- Components analyzed: 14
- Total circular dependencies: 0
- Total star imports: 4
- Total deep imports (depth ≥ 5): 229

## Engram

### Deep Imports (depth ≥ 5) (65)
- `from tekton.mcp.fastmcp.utils.endpoints import create_mcp_router` (used in 1 files)
- `from tekton.mcp.fastmcp.utils.endpoints import add_standard_mcp_endpoints` (used in 1 files)
- `from tekton.mcp.fastmcp.utils.tooling import ToolRegistry` (used in 1 files)
- `from engram.core.structured.memory.base import StructuredMemory` (used in 3 files)
- `from engram.core.memory.storage.file_storage import FileStorage` (used in 1 files)

### Top Flattening Candidates
- **MemoryService** from `engram.core.memory.base` (imported 7 times)
  - ⚠️ Conflicts with: engram.integrations.hermes.memory_adapter
- **save_metadata_index** from `engram.core.structured.memory.index` (imported 5 times)
- **search_by_content** from `engram.core.structured.search.content` (imported 5 times)

### Import Depth Distribution
- Depth 1: 314 imports
- Depth 2: 97 imports
- Depth 3: 122 imports
- Depth 4: 53 imports
- Depth 5: 40 imports

## Prometheus

### Star Imports (2)
- Prometheus/prometheus/core/mcp/__init__.py:8
  - `from tools import *`
- Prometheus/prometheus/core/mcp/__init__.py:9
  - `from capabilities import *`

### Deep Imports (depth ≥ 5) (1)
- `from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints` (used in 1 files)

### Import Depth Distribution
- Depth 1: 144 imports
- Depth 2: 29 imports
- Depth 3: 37 imports
- Depth 4: 9 imports
- Depth 5: 1 imports

## Hermes

### Deep Imports (depth ≥ 5) (45)
- `from hermes.core.logging.base.levels import LogLevel` (used in 7 files)
- `from hermes.core.logging.base.entry import LogEntry` (used in 5 files)
- `from hermes.core.logging.storage.file_storage import LogStorage` (used in 3 files)
- `from hermes.core.logging.management.manager import LogManager` (used in 4 files)
- `from hermes.core.logging.interface.logger import Logger` (used in 3 files)

### Top Flattening Candidates
- **DatabaseType** from `hermes.core.database.database_types` (imported 14 times)
- **DatabaseBackend** from `hermes.core.database.database_types` (imported 11 times)
- **VectorDatabaseAdapter** from `hermes.core.database.adapters` (imported 8 times)
- **BaseRequest** from `hermes.api.database.client_base` (imported 8 times)
- **LogLevel** from `hermes.core.logging.base.levels` (imported 7 times)

### Import Depth Distribution
- Depth 1: 147 imports
- Depth 2: 35 imports
- Depth 3: 94 imports
- Depth 4: 101 imports
- Depth 5: 36 imports

## Athena

### Deep Imports (depth ≥ 5) (4)
- `from tekton.mcp.fastmcp.utils.tooling import ToolRegistry` (used in 2 files)
- `from tekton.mcp.fastmcp.utils.endpoints import create_mcp_router` (used in 1 files)
- `from tekton.mcp.fastmcp.utils.endpoints import add_standard_mcp_endpoints` (used in 1 files)

### Top Flattening Candidates
- **QueryMode** from `tekton.core.query.modes` (imported 7 times)
- **QueryParameters** from `tekton.core.query.modes` (imported 6 times)

### Import Depth Distribution
- Depth 1: 116 imports
- Depth 2: 31 imports
- Depth 3: 48 imports
- Depth 4: 18 imports
- Depth 5: 3 imports

## Rhetor

### Deep Imports (depth ≥ 5) (1)
- `from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints` (used in 1 files)

### Import Depth Distribution
- Depth 1: 89 imports
- Depth 2: 17 imports
- Depth 3: 46 imports
- Depth 4: 10 imports
- Depth 5: 1 imports

## Budget

### Deep Imports (depth ≥ 5) (3)
- `from tekton.mcp.fastmcp.utils.endpoints import create_mcp_router` (used in 1 files)
- `from tekton.mcp.fastmcp.utils.endpoints import add_standard_mcp_endpoints` (used in 1 files)
- `from tekton.mcp.fastmcp.utils.tooling import ToolRegistry` (used in 1 files)

### Import Depth Distribution
- Depth 1: 84 imports
- Depth 2: 13 imports
- Depth 3: 144 imports
- Depth 4: 12 imports
- Depth 5: 2 imports

## Apollo

### Import Depth Distribution
- Depth 1: 64 imports
- Depth 2: 20 imports
- Depth 3: 77 imports
- Depth 4: 25 imports

## Ergon

### Deep Imports (depth ≥ 5) (103)
- `from ergon.core.memory.models.schema import Memory` (used in 6 files)
- `from ergon.core.memory.utils.categories import MemoryCategory` (used in 7 files)
- `from ergon.core.agents.mail.tools import MailTools` (used in 1 files)
- `from ergon.core.agents.mail.tools import mail_tool_definitions` (used in 3 files)
- `from ergon.core.agents.mail.tools import register_mail_tools` (used in 2 files)

### Top Flattening Candidates
- **settings** from `ergon.utils.config.settings` (imported 57 times)
- **get_db_session** from `ergon.core.database.engine` (imported 27 times)
- **Agent** from `ergon.core.database.models` (imported 22 times)
- **init_db** from `ergon.core.database.engine` (imported 12 times)
- **LLMClient** from `ergon.core.llm.client` (imported 12 times)

### Import Depth Distribution
- Depth 1: 286 imports
- Depth 2: 100 imports
- Depth 3: 54 imports
- Depth 4: 263 imports
- Depth 5: 66 imports
- Depth 6: 12 imports

## Harmonia

### Import Depth Distribution
- Depth 1: 62 imports
- Depth 2: 18 imports
- Depth 3: 62 imports
- Depth 4: 4 imports

## Metis

### Star Imports (2)
- Metis/metis/core/mcp/__init__.py:7
  - `from tools import *`
- Metis/metis/core/mcp/__init__.py:8
  - `from capabilities import *`

### Deep Imports (depth ≥ 5) (1)
- `from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints` (used in 1 files)

### Top Flattening Candidates
- **analyze_task_complexity** from `metis.core.mcp.tools` (imported 6 times)

### Import Depth Distribution
- Depth 1: 67 imports
- Depth 2: 5 imports
- Depth 3: 127 imports
- Depth 4: 17 imports
- Depth 5: 1 imports

## Sophia

### Deep Imports (depth ≥ 5) (1)
- `from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints` (used in 1 files)

### Import Depth Distribution
- Depth 1: 98 imports
- Depth 2: 5 imports
- Depth 3: 69 imports
- Depth 4: 16 imports
- Depth 5: 1 imports

## Synthesis

### Deep Imports (depth ≥ 5) (1)
- `from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints` (used in 1 files)

### Import Depth Distribution
- Depth 1: 47 imports
- Depth 2: 6 imports
- Depth 3: 55 imports
- Depth 4: 10 imports
- Depth 5: 1 imports

## Telos

### Deep Imports (depth ≥ 5) (3)
- `from tekton.mcp.fastmcp.utils.endpoints import create_mcp_router` (used in 1 files)
- `from tekton.mcp.fastmcp.utils.endpoints import add_standard_mcp_endpoints` (used in 1 files)
- `from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints` (used in 1 files)

### Import Depth Distribution
- Depth 1: 62 imports
- Depth 2: 16 imports
- Depth 3: 56 imports
- Depth 4: 7 imports
- Depth 5: 2 imports

## Terma

### Deep Imports (depth ≥ 5) (1)
- `from tekton.mcp.fastmcp.utils.endpoints import add_mcp_endpoints` (used in 1 files)

### Import Depth Distribution
- Depth 1: 39 imports
- Depth 2: 33 imports
- Depth 3: 6 imports
- Depth 4: 6 imports
- Depth 5: 1 imports
