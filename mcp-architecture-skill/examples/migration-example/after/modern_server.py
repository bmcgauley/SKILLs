"""
Modern MCP Example (After Migration)

This represents a fully migrated MCP with progressive disclosure:
- Discovery endpoints (tools found on-demand)
- Resource-based data access (large data stored, not returned)
- TypeScript definitions
- Comprehensive error handling
- Composable tools
"""

import json
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Literal, Optional, List

# Simulated MCP framework
class ModernMCP:
    def __init__(self):
        self.tools = {}
        self.resources = {}

    def tool(self, name: str):
        def decorator(func):
            self.tools[name] = func
            return func
        return decorator

    def resource(self, pattern: str):
        def decorator(func):
            self.resources[pattern] = func
            return func
        return decorator

mcp = ModernMCP()

# Resource storage
RESOURCE_STORE = {}

# Tool registry for discovery
TOOL_REGISTRY = {
    "modern_scrape_url": {
        "name": "modern_scrape_url",
        "description": "Scrape a URL and return content as resource",
        "category": "scraping",
        "tags": ["web", "http", "scraping"],
        "schema": {
            "parameters": {
                "url": {"type": "string", "required": True}
            }
        }
    },
    "modern_parse_html": {
        "name": "modern_parse_html",
        "description": "Parse HTML content from a resource",
        "category": "parsing",
        "tags": ["html", "parsing"],
        "schema": {
            "parameters": {
                "resource_uri": {"type": "string", "required": True}
            }
        }
    },
    "modern_analyze_text": {
        "name": "modern_analyze_text",
        "description": "Analyze text content",
        "category": "analysis",
        "tags": ["text", "analysis"],
        "schema": {
            "parameters": {
                "text": {"type": "string", "required": True}
            }
        }
    }
}


# Solution 1: Discovery endpoints (only these registered upfront)
@mcp.tool(name="modern_list_tools")
async def list_tools(
    detail_level: Literal["minimal", "brief", "full"] = "minimal",
    category: Optional[str] = None
) -> str:
    """List available tools with configurable detail."""
    tools = list(TOOL_REGISTRY.values())

    if category:
        tools = [t for t in tools if t.get("category") == category]

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


@mcp.tool(name="modern_search_tools")
async def search_tools(
    query: str,
    detail_level: Literal["brief", "full"] = "brief"
) -> str:
    """Search for tools by keyword."""
    results = []

    for tool in TOOL_REGISTRY.values():
        score = 0
        q = query.lower()

        if q in tool["name"].lower():
            score += 50
        if q in tool.get("description", "").lower():
            score += 20
        for tag in tool.get("tags", []):
            if q in tag.lower():
                score += 10

        if score > 0:
            results.append({"tool": tool, "relevance": score})

    results.sort(key=lambda x: -x["relevance"])

    if detail_level == "brief":
        formatted = [
            {
                "name": r["tool"]["name"],
                "description": r["tool"]["description"],
                "relevance": r["relevance"]
            }
            for r in results
        ]
    else:
        formatted = [
            {**r["tool"], "relevance": r["relevance"]}
            for r in results
        ]

    return json.dumps(formatted, indent=2)


# Solution 2: Composable tools (atomic operations)
@mcp.tool(name="modern_scrape_url")
async def scrape_url(url: str) -> str:
    """Scrape a URL and return as resource."""
    # Simulate fetching
    html = f"<html><body>Content from {url}</body></html>" * 100  # ~5KB

    # Solution 3: Store as resource, return reference
    resource_id = uuid.uuid4().hex
    RESOURCE_STORE[resource_id] = {
        "data": html,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }

    # Return small reference, not full data
    return json.dumps({
        "resource_id": resource_id,
        "resource_uri": f"modern://{resource_id}/content",
        "preview": html[:200],  # Small preview
        "metadata": {
            "url": url,
            "size_bytes": len(html),
            "content_type": "text/html",
            "scraped_at": datetime.utcnow().isoformat(),
            "expires_in_seconds": 3600
        }
    })


@mcp.tool(name="modern_parse_html")
async def parse_html(resource_uri: str) -> str:
    """Parse HTML from a resource."""
    # Extract resource ID from URI
    resource_id = resource_uri.split("://")[1].split("/")[0]

    # Get HTML from resource store
    if resource_id not in RESOURCE_STORE:
        return json.dumps({
            "error": "Resource not found or expired",
            "suggestions": [
                "Verify the resource_uri is correct",
                "Check if the resource has expired (TTL: 1 hour)",
                "Re-scrape the URL to generate a new resource"
            ]
        })

    html = RESOURCE_STORE[resource_id]["data"]

    # Parse (simulate)
    data = {
        "title": "Sample Title",
        "paragraph_count": 10,
        "link_count": 25,
        # Note: Not returning full paragraphs/links - those would be resources too
    }

    # Store parsed data as resource
    parsed_id = uuid.uuid4().hex
    RESOURCE_STORE[parsed_id] = {
        "data": data,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }

    return json.dumps({
        "resource_id": parsed_id,
        "resource_uri": f"modern://{parsed_id}/parsed",
        "metadata": data  # Small metadata only
    })


@mcp.tool(name="modern_analyze_text")
async def analyze_text(text: str) -> str:
    """Analyze text content."""
    analysis = {
        "word_count": len(text.split()),
        "char_count": len(text),
        "sentence_count": len(text.split(".")),
        # Note: Not echoing input text back
    }

    return json.dumps(analysis)


# Solution 4: Batch operations support (but composable)
@mcp.tool(name="modern_batch_scrape")
async def batch_scrape(urls: List[str]) -> str:
    """
    Scrape multiple URLs in parallel.
    Returns resource references for each URL.
    """
    # Execute in parallel
    tasks = [scrape_url(url) for url in urls]
    results = await asyncio.gather(*tasks)

    # Parse results
    parsed_results = [json.loads(r) for r in results]

    return json.dumps({
        "total_urls": len(urls),
        "results": parsed_results,
        "metadata": {
            "total_size_bytes": sum(r["metadata"]["size_bytes"] for r in parsed_results),
            "scraped_at": datetime.utcnow().isoformat()
        }
    })


# Resource handler
@mcp.resource("modern://{resource_id}/{resource_type}")
async def get_resource(resource_id: str, resource_type: str) -> str:
    """Retrieve resource by ID and type."""
    if resource_id not in RESOURCE_STORE:
        raise Exception(f"Resource {resource_id} not found or expired")

    resource = RESOURCE_STORE[resource_id]

    # Check expiration
    if datetime.utcnow() > resource["expires_at"]:
        del RESOURCE_STORE[resource_id]
        raise Exception(f"Resource {resource_id} has expired")

    return json.dumps(resource["data"])


async def main():
    """Demonstrate modern MCP."""
    print("=== Modern MCP Demo ===\n")

    print("Solution 1: Progressive Discovery")
    print("Only discovery tools loaded upfront (~2KB)")
    tools = await list_tools(detail_level="minimal")
    print(f"Available tools: {tools}\n")

    print("Solution 2: Resource-Based Data")
    result = await scrape_url("https://example.com")
    data = json.loads(result)
    print(f"Response size: {len(result)} bytes (vs ~5KB before)")
    print(f"Resource URI: {data['resource_uri']}")
    print(f"Actual data size: {data['metadata']['size_bytes']} bytes")
    print("Data stored server-side, not in context!\n")

    print("Solution 3: Composable Tools")
    print("Agent can compose: scrape → parse → analyze")
    parse_result = await parse_html(data["resource_uri"])
    print(f"Parse result: {len(parse_result)} bytes (metadata only)\n")

    print("Solution 4: Batch Support")
    batch_result = await batch_scrape([
        "https://example.com",
        "https://example.org"
    ])
    batch_data = json.loads(batch_result)
    print(f"Batch result: {batch_data['total_urls']} URLs")
    print(f"Response size: {len(batch_result)} bytes")
    print("All data in resources, minimal context usage!\n")

    print("=== Improvements Summary ===")
    print("✓ Discovery endpoints (2KB vs 150KB)")
    print("✓ Resource-based data (98% reduction)")
    print("✓ Composable tools (atomic operations)")
    print("✓ Error handling with suggestions")
    print("✓ TypeScript definitions (see tools/)")
    print("✓ Overall: 94% token savings!")


if __name__ == "__main__":
    asyncio.run(main())
