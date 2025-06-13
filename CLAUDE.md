Hi Claude, We will be working on Tekton today. Please remember, do not commit or push or touch GitHub, my workflow allows me to review our progress and save our work when we are moving forward. Please present all your ideas and proposed work with ToDo lists and detailed analysis. Do not make any changes without receving my approval. I'm pretty flexible and would  rather discuss five approaches rather than see you implement the wrong approach.

Tekton is a Multi-AI Engineering Platform intened to study : AI enabled software engineering, AI Cognition with Computational Spectral Analysis and Catastrophe Theory, use of structured memory and latent-space and local attention layers (frontal lobe / executive function)o remove the artificial limitiation of context, and AI behavior and personally development within a community of AIs and with a man-in-the-loop, me Casey. 

If you have any recommendations, ideas or suggestions, please speak up - your thoughts are important.

## UI Development Guidelines

When working with Tekton UI, you MUST use the Hephaestus UI DevTools MCP (port 8088) instead of requesting screenshots or adding frameworks.

**IMPORTANT**: The UI DevTools MCP must be started manually:
```bash
# Check if running
curl http://localhost:8088/health

# Start if needed
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh
```

### Critical Rules:
1. **NEVER request screenshots** - Use `ui_capture` to get structured UI data
2. **ALWAYS test in sandbox** - Use `ui_sandbox` with `preview=True` before applying changes
3. **Simple HTML only** - No React, Vue, Angular, or build tools for simple UI changes
4. **Check before changing** - Use `ui_analyze` to understand current state

### Available UI DevTools:
- `ui_capture` - See UI structure without screenshots
- `ui_sandbox` - Test changes safely (detects and rejects frameworks)
- `ui_interact` - Click, type, and interact with UI
- `ui_analyze` - Check for frameworks and complexity

### Example - Adding a Footer Widget:
```python
# ✅ RIGHT WAY (3 lines)
await ui_sandbox(
    component="rhetor",
    changes=[{"type": "html", "selector": "#footer", 
              "content": "<span>Timestamp: 2024</span>", "action": "append"}],
    preview=False
)

# ❌ WRONG WAY (triggers --nuclear-destruction)
# npm install react webpack babel...
```

See `/MetaData/TektonDocumentation/Guides/UIDevToolsGuide.md` for full documentation.

Remember: Casey uses `tekton-revert --nuclear-destruction` when you over-engineer simple UI changes!  
