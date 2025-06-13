Hi Claude, We will be working on Tekton today. Please remember, do not commit or push or touch GitHub, my workflow allows me to review our progress and save our work when we are moving forward. Please present all your ideas and proposed work with ToDo lists and detailed analysis. Do not make any changes without receving my approval. I'm pretty flexible and would  rather discuss five approaches rather than see you implement the wrong approach.

Tekton is a Multi-AI Engineering Platform intened to study : AI enabled software engineering, AI Cognition with Computational Spectral Analysis and Catastrophe Theory, use of structured memory and latent-space and local attention layers (frontal lobe / executive function)o remove the artificial limitiation of context, and AI behavior and personally development within a community of AIs and with a man-in-the-loop, me Casey. 

If you have any recommendations, ideas or suggestions, please speak up - your thoughts are important.

## UI Development Guidelines

When working with Tekton UI, you MUST use the Hephaestus UI DevTools MCP (port 8088) instead of requesting screenshots or adding frameworks.

### ⚠️ CRITICAL: How to Use UI DevTools

**DO NOT use any other playwright, puppeteer, or browser automation tools!**

**ONLY use the HTTP API at port 8088:**

```bash
# 1. First check if MCP is running
curl http://localhost:8088/health

# 2. If not running, start it
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh

# 3. Use HTTP API for ALL UI operations
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui_capture",
    "arguments": {
      "component": "rhetor"
    }
  }'
```

### The ONLY Four Tools (via HTTP API):

1. **ui_capture** - Get UI structure (NO screenshots)
   ```json
   {"tool_name": "ui_capture", "arguments": {"component": "rhetor"}}
   ```

2. **ui_sandbox** - Test changes safely (detects frameworks)
   ```json
   {
     "tool_name": "ui_sandbox",
     "arguments": {
       "component": "rhetor",
       "changes": [{"type": "html", "selector": "#footer", "content": "<div>Test</div>", "action": "append"}],
       "preview": true
     }
   }
   ```

3. **ui_interact** - Click/type UI elements
   ```json
   {"tool_name": "ui_interact", "arguments": {"component": "rhetor", "action": "click", "selector": "button"}}
   ```

4. **ui_analyze** - Check for frameworks
   ```json
   {"tool_name": "ui_analyze", "arguments": {"component": "rhetor", "deep_scan": false}}
   ```

### Python Example (USE THIS PATTERN):

```python
import httpx
import asyncio

async def work_with_ui():
    # ALWAYS use HTTP endpoint
    MCP_URL = "http://localhost:8088/api/mcp/v2/execute"
    
    async with httpx.AsyncClient() as client:
        # Capture UI
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_capture",
            "arguments": {"component": "rhetor"}
        })
        
        # Test changes
        response = await client.post(MCP_URL, json={
            "tool_name": "ui_sandbox",
            "arguments": {
                "component": "rhetor",
                "changes": [{"type": "html", "selector": "#footer", "content": "<span>2024</span>", "action": "append"}],
                "preview": True
            }
        })
```

### ❌ DO NOT USE:
- playwright:browser_navigate
- Any puppeteer tools
- Screenshot commands
- Direct browser automation
- npm install ANYTHING

### ✅ ONLY USE:
- HTTP POST to http://localhost:8088/api/mcp/v2/execute
- The four tools: ui_capture, ui_sandbox, ui_interact, ui_analyze

See `/MetaData/TektonDocumentation/Guides/UIDevToolsExplicitGuide.md` for detailed examples.

Remember: Casey uses `tekton-revert --nuclear-destruction` when you over-engineer simple UI changes!  
