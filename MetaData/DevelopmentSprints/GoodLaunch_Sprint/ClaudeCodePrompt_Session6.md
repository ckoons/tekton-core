# GoodLaunch Sprint - Session 6 Prompt

## Critical Context - READ FIRST
You are continuing the GoodLaunch Sprint. The previous sessions have been thrashing the code with band-aid fixes. This session's goal is to make WORKING code that actually launches, not just code that avoids errors.

## Current Status
- **Unknown number of components working** (Session 5 ended without a final test)
- Multiple components have had their functionality commented out just to make them "launch"
- The system is full of inconsistencies and half-implemented features

## Session 5 Key Discovery - Rhetor's Real Problem

In Session 5, we discovered that Rhetor's `tools.py` file has fundamental architectural issues:

### The Problem
1. Someone uncommented the MCPTool definitions but they have syntax errors throughout
2. The `input_schema` structure is malformed - `return_type` is incorrectly placed inside `parameters`
3. There's confusion between two MCP integration approaches:
   - Decorator-based registration (`@mcp_tool`)
   - Manual MCPTool instantiation

### The Band-Aid Applied
We commented out all the tool definitions, which makes Rhetor launch but completely disables its functionality. This is unacceptable for a production system.

### The Proper Solution - Use Decorators (Option A)
Convert all tools to use the modern decorator approach:

```python
from tekton.mcp.fastmcp.decorators import mcp_tool

@mcp_tool
async def get_available_models() -> Dict[str, Any]:
    """Get all available LLM models and providers"""
    # implementation already exists
    
# The decorator handles all registration automatically
# No manual MCPTool creation needed
# No complex schema definitions needed
```

## Session 6 Primary Objectives

### 1. Centralize Port Configuration (FIRST PRIORITY)
Multiple components have their own `utils/port_config.py` files that duplicate port assignments, causing drift and maintenance issues. This MUST be fixed first.

#### Current Problems:
- 10+ duplicate `port_config.py` files across components
- Missing components (Sophia, Budget, Metis, Apollo) in most files
- Wrong ports in test scripts (e.g., Sophia test uses 8009 instead of 8014)
- Violates DRY principle and single source of truth

#### Required Actions:
1. **DELETE all individual port_config.py files** in:
   - Apollo, Engram, Harmonia, Hermes, Metis, Prometheus, Rhetor, Synthesis, Telos, Terma
   
2. **CREATE one centralized port configuration** at:
   - `/Users/cskoons/projects/github/Tekton/tekton/utils/port_config.py`
   - Should read from the official `/config/port_assignments.md` file
   - Provide all helper functions (get_component_port, get_component_url, etc.)
   
3. **UPDATE all imports** to use:
   ```python
   from tekton.utils.port_config import get_component_port, get_rhetor_port
   ```
   
4. **FIX incorrect port references**:
   - `/Users/cskoons/projects/github/Tekton/Sophia/examples/run_fastmcp_test.sh` (8009 → 8014)
   - Any other hardcoded ports

### 2. Fix Rhetor Properly
- Read `/Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/tools.py`
- Remove ALL the commented-out MCPTool instantiations
- Add `@mcp_tool` decorator to each tool function
- Ensure the functions are properly exported in `__all__`
- Test that Rhetor launches WITH its tools functional

### 2. Audit and Fix Port Configuration Files
Multiple files are exporting incorrect port numbers instead of using the centralized `/Users/cskoons/projects/github/Tekton/config/port_assignments.md`. Find and fix ALL of these.

Known issues:
- Some files hardcode ports
- Some use wrong environment variable names
- Some have outdated port numbers

### 3. Fix Other Components Properly
For each component that's failing:
- Don't just comment out errors
- Understand WHY it's failing
- Implement a real fix that preserves functionality
- If functionality must be disabled, clearly mark it as TODO with explanation

## Anti-Patterns to Avoid

1. **Don't Comment Out Functionality**
   - If code doesn't work, fix it or replace it with a working stub
   - Don't just delete/comment features to avoid errors

2. **Don't Mix Architecture Patterns**
   - Choose one approach and stick with it
   - For MCP: Use decorators, not manual registration

3. **Don't Hardcode Configuration**
   - All ports should come from port_assignments.md
   - All paths should use proper base directories

4. **Don't Apply Band-Aids**
   - Each fix should move us toward a working system
   - Temporary fixes should be clearly marked with TODOs

## Success Criteria
1. All 14 components launch successfully
2. Each component retains its core functionality
3. No hardcoded ports - all use centralized configuration
4. Clear documentation of any remaining issues
5. System is ready for actual use, not just "technically launching"

## Technical Guidelines

### For MCP Tool Registration
Use this pattern consistently:
```python
from tekton.mcp.fastmcp.decorators import mcp_tool

@mcp_tool
async def tool_name(param1: str, param2: int = 0) -> Dict[str, Any]:
    """Tool description"""
    # implementation
    return result
```

### For Port Configuration
Always use:
```python
from utils.port_config import get_component_port
port = get_component_port()  # or get_rhetor_port(), etc.
```

Never hardcode ports or create new port configuration files.

## Important Context from Session 5

### Files Modified
1. `/Users/cskoons/projects/github/Tekton/Rhetor/rhetor/core/mcp/tools.py` - Commented out broken tool definitions
2. `/Users/cskoons/projects/github/Tekton/Sophia/sophia/utils/llm_integration.py` - Fixed multiple f-string indentation errors
3. `/Users/cskoons/projects/github/Tekton/Telos/telos/api/app.py` - Made startup synchronous
4. `/Users/cskoons/projects/github/Tekton/Harmonia/harmonia/api/app.py` - Added missing root endpoint
5. `/Users/cskoons/projects/github/Tekton/Budget/budget/api/app.py` - Removed problematic decorator

### Patterns Observed
1. Many components have f-string indentation errors
2. Several components missing root endpoints
3. Deprecated FastAPI patterns (@app.on_event) causing hangs
4. Decorator/async incompatibilities
5. Import path issues with shared modules

## Your First Steps
1. Run `tekton-launch --launch-all` and capture the full output
2. Read the Rhetor analysis above carefully
3. Fix Rhetor using the decorator approach
4. Find all files that export/define ports incorrectly
5. Create a systematic plan to fix each failing component properly

Remember: The goal is a WORKING system, not just one that launches with disabled features.