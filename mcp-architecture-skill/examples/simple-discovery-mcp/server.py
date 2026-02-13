"""
Simple Discovery MCP Example

A minimal MCP demonstrating progressive disclosure patterns:
- Tool discovery endpoints
- Basic resource management
- TypeScript definitions
- Simple testing

This is a learning example - suitable for understanding the fundamentals.
"""

from datetime import datetime, timedelta
from typing import Literal, Optional
import json
import uuid
import asyncio

# Simulated MCP framework (use fastmcp or mcp.server in production)
class SimpleMCP:
    def __init__(self):
        self.tools = {}
        self.resources = {}

    def tool(self, name: str):
        """Decorator to register tools."""
        def decorator(func):
            self.tools[name] = func
            return func
        return decorator

    def resource(self, pattern: str):
        """Decorator to register resource handlers."""
        def decorator(func):
            self.resources[pattern] = func
            return func
        return decorator

# Initialize MCP
mcp = SimpleMCP()

# In-memory resource storage
RESOURCE_STORE = {}

# Tool registry for discovery
TOOL_REGISTRY = {
    "simple_greet": {
        "name": "simple_greet",
        "description": "Return a greeting message",
        "category": "utility",
        "tags": ["simple", "example"],
        "schema": {
            "parameters": {
                "name": {
                    "type": "string",
                    "description": "Name to greet",
                    "required": True
                }
            },
            "returns": {
                "greeting": "string"
            }
        }
    },
    "simple_generate_data": {
        "name": "simple_generate_data",
        "description": "Generate sample data and return as resource",
        "category": "data",
        "tags": ["data", "resource", "example"],
        "schema": {
            "parameters": {
                "size": {
                    "type": "integer",
                    "description": "Number of items to generate",
                    "required": False,
                    "default": 10
                }
            },
            "returns": {
                "resource_uri": "string",
                "preview": "string",
                "metadata": "object"
            }
        }
    }
}


# Discovery Endpoint 1: List Tools
@mcp.tool(name="simple_list_tools")
async def list_tools(
    detail_level: Literal["minimal", "brief", "full"] = "minimal",
    category: Optional[str] = None
) -> str:
    """
    List available tools with configurable detail.

    Args:
        detail_level:
            - minimal: Tool names only
            - brief: Names and descriptions
            - full: Complete schemas
        category: Optional category filter

    Returns:
        JSON array of tools at requested detail level
    """
    tools = list(TOOL_REGISTRY.values())

    # Filter by category if specified
    if category:
        tools = [t for t in tools if t.get("category") == category]

    # Format based on detail level
    if detail_level == "minimal":
        result = [t["name"] for t in tools]

    elif detail_level == "brief":
        result = [
            {
                "name": t["name"],
                "description": t["description"],
                "category": t.get("category", "general")
            }
            for t in tools
        ]

    else:  # full
        result = tools

    return json.dumps(result, indent=2)


# Discovery Endpoint 2: Search Tools
@mcp.tool(name="simple_search_tools")
async def search_tools(
    query: str,
    detail_level: Literal["brief", "full"] = "brief",
    max_results: int = 10
) -> str:
    """
    Search for tools by keyword.

    Args:
        query: Search term (searches name, description, tags)
        detail_level: brief or full
        max_results: Maximum results to return

    Returns:
        JSON array of matching tools with relevance scores
    """
    results = []

    for tool in TOOL_REGISTRY.values():
        score = 0
        query_lower = query.lower()

        # Calculate relevance
        if query_lower in tool["name"].lower():
            score += 50
        if query_lower in tool.get("description", "").lower():
            score += 20
        for tag in tool.get("tags", []):
            if query_lower in tag.lower():
                score += 10

        if score > 0:
            results.append({
                "tool": tool,
                "relevance": score
            })

    # Sort by relevance
    results.sort(key=lambda x: -x["relevance"])

    # Limit results
    results = results[:max_results]

    # Format based on detail level
    if detail_level == "brief":
        formatted = [
            {
                "name": r["tool"]["name"],
                "description": r["tool"]["description"],
                "category": r["tool"].get("category", "general"),
                "relevance": r["relevance"]
            }
            for r in results
        ]
    else:  # full
        formatted = [
            {
                **r["tool"],
                "relevance": r["relevance"]
            }
            for r in results
        ]

    return json.dumps(formatted, indent=2)


# Actual Tools
@mcp.tool(name="simple_greet")
async def greet(name: str) -> str:
    """
    Return a greeting message.

    Args:
        name: Name to greet

    Returns:
        JSON with greeting
    """
    return json.dumps({
        "greeting": f"Hello, {name}!",
        "timestamp": datetime.utcnow().isoformat()
    })


@mcp.tool(name="simple_generate_data")
async def generate_data(size: int = 10) -> str:
    """
    Generate sample data and return as resource.

    Args:
        size: Number of items to generate

    Returns:
        JSON with resource reference
    """
    # Generate sample data
    data = [
        {
            "id": i,
            "value": f"Item {i}",
            "timestamp": datetime.utcnow().isoformat()
        }
        for i in range(size)
    ]

    # Store as resource
    resource_id = uuid.uuid4().hex
    RESOURCE_STORE[resource_id] = {
        "data": data,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }

    # Return reference (not full data)
    data_json = json.dumps(data)
    return json.dumps({
        "resource_id": resource_id,
        "resource_uri": f"simple://{resource_id}/data",
        "preview": data_json[:200] + "..." if len(data_json) > 200 else data_json,
        "metadata": {
            "item_count": size,
            "size_bytes": len(data_json),
            "created_at": datetime.utcnow().isoformat(),
            "expires_in_seconds": 3600
        }
    })


# Resource Handler
@mcp.resource("simple://{resource_id}/data")
async def get_resource(resource_id: str) -> str:
    """
    Retrieve resource by ID.

    Args:
        resource_id: Resource identifier

    Returns:
        Full resource data
    """
    if resource_id not in RESOURCE_STORE:
        raise Exception(f"Resource {resource_id} not found or expired")

    resource = RESOURCE_STORE[resource_id]

    # Check expiration
    if datetime.utcnow() > resource["expires_at"]:
        del RESOURCE_STORE[resource_id]
        raise Exception(f"Resource {resource_id} has expired")

    return json.dumps(resource["data"])


# Example usage (for testing)
async def main():
    """Test the MCP."""
    print("=== Simple Discovery MCP Test ===\n")

    # Test 1: List tools (minimal)
    print("1. List tools (minimal):")
    result = await list_tools(detail_level="minimal")
    print(result)
    print()

    # Test 2: Search tools
    print("2. Search for 'data' tools:")
    result = await search_tools(query="data", detail_level="brief")
    print(result)
    print()

    # Test 3: Use greet tool
    print("3. Greet 'World':")
    result = await greet(name="World")
    print(result)
    print()

    # Test 4: Generate data with resource
    print("4. Generate data (5 items):")
    result = await generate_data(size=5)
    print(result)

    # Extract resource_uri
    result_data = json.loads(result)
    resource_id = result_data["resource_id"]
    print()

    # Test 5: Access resource
    print("5. Access resource:")
    resource_data = await get_resource(resource_id)
    print(resource_data)
    print()

    print("=== All tests completed ===")


if __name__ == "__main__":
    asyncio.run(main())
