# Socket Reuse Implementation Update

## Overview
Implemented socket reuse across all Tekton components to address port binding issues during rapid restarts.

## Changes Made

### 1. Socket Server Utilities
- Updated `/shared/utils/socket_server.py` to set both `SO_REUSEADDR` and `SO_REUSEPORT` socket options
- Changed default `reload` parameter from `True` to `False` in `run_component_server()`
- Added macOS-specific handling for `SO_REUSEPORT`

### 2. Component Updates
Updated all component `__main__.py` files to use socket reuse utilities:
- Apollo, Athena, Budget, Engram, Ergon, Harmonia, Hermes, Metis, Prometheus, Rhetor, Sophia, Synthesis, Telos, tekton-core

### 3. App.py Updates
Changed all `reload=True` to `reload=False` in app.py files to prevent reloader processes:
- All components now use `reload=False` consistently
- Fixed Hermes dynamic reload based on DEBUG environment variable

### 4. Special Fixes
- **Harmonia**: Fixed async/await mismatch by changing `async def main()` to `def main()`
- **Hermes**: Removed dynamic reload parameter based on DEBUG environment

## Current Status

### Working
- Socket reuse is implemented and functional
- Components shut down more gracefully (9/15 successful graceful shutdowns)
- Reload mode is disabled, preventing reloader process issues
- Harmonia async issue is fixed

### Known Issues on macOS
- Even with `SO_REUSEADDR` and `SO_REUSEPORT`, there's still a ~10-15 second delay before ports can be reused
- This is due to macOS's TIME_WAIT implementation being different from Linux
- Some components (6/15) still require force kill during shutdown

### Recommendations
1. On macOS, wait 10-15 seconds between stopping and starting components
2. Consider implementing a port rotation strategy for zero-downtime restarts
3. Investigate using Unix domain sockets for local inter-component communication
4. Consider implementing a custom shutdown sequence that ensures all connections are properly closed

## Testing
To test the implementation:
```bash
# Kill a component
python scripts/enhanced_tekton_killer.py --components hermes --force

# Wait for macOS TIME_WAIT (10-15 seconds)
sleep 15

# Restart the component
python scripts/enhanced_tekton_launcher.py --components hermes
```

## Future Improvements
1. Implement connection draining during shutdown
2. Add configurable shutdown timeout per component
3. Investigate SO_LINGER socket option for faster cleanup
4. Consider using systemd socket activation on Linux for true zero-downtime restarts