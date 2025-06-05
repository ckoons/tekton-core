#!/usr/bin/env python3
"""Debug script to check MCP routes in running Hermes."""

import requests
import json

# Test basic health
resp = requests.get("http://localhost:8001/health")
print(f"Health endpoint: {resp.status_code}")

# Try to get OpenAPI spec
resp = requests.get("http://localhost:8001/openapi.json")
if resp.status_code == 200:
    spec = resp.json()
    paths = spec.get("paths", {})
    mcp_paths = [p for p in paths if "mcp" in p]
    print(f"\nMCP paths in OpenAPI spec: {len(mcp_paths)}")
    for path in mcp_paths[:10]:
        print(f"  {path}")
else:
    print(f"OpenAPI spec not available: {resp.status_code}")

# Test various MCP endpoint patterns
test_urls = [
    "http://localhost:8001/api/mcp/v2/test",
    "http://localhost:8001/api/mcp/v2/health",
    "http://localhost:8001/api/mcp/v2/capabilities",
    "http://localhost:8001/api/mcp/v2/tools",
    "http://localhost:8001/mcp/v2/test",
    "http://localhost:8001/api/v1/mcp/test",
]

print("\nTesting various URL patterns:")
for url in test_urls:
    resp = requests.get(url)
    print(f"  {url}: {resp.status_code}")

# Check what's actually at /api
resp = requests.get("http://localhost:8001/api")
print(f"\n/api root: {resp.status_code}")
if resp.status_code == 200:
    print(f"Response: {resp.text[:200]}...")