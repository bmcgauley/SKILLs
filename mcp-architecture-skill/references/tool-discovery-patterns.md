# Tool Discovery Patterns

**Last Updated**: 2025-11-09

## Overview

Tool discovery is the mechanism by which agents find and learn about available tools in an MCP. This document provides detailed implementation patterns for discovery endpoints that enable progressive disclosure.

## Core Discovery Endpoints

### 1. List Tools Endpoint

The `list_tools` endpoint returns available tools with configurable detail levels.

#### Basic Implementation

```python
from typing import Literal, Optional
import json

TOOLS_REGISTRY = {
    "myapp_scrape_url": {
        "name": "myapp_scrape_url",
        "description": "Scrape content from a URL",
        "category": "scraping",
        "tags": ["web", "html", "http"],
        "schema": {
            "parameters": {
                "url": {"type": "string", "required": True},
                "format": {"type": "string", "enum": ["html", "markdown"]}
            }
        }
    },
    "myapp_extract_links": {
        "name": "myapp_extract_links",
        "description": "Extract all links from HTML content",
        "category": "parsing",
        "tags": ["html", "links", "parsing"],
        "schema": {
            "parameters": {
                "html": {"type": "string", "required": True}
            }
        }
    }
}

@mcp.tool(name="myapp_list_tools")
async def list_tools(
    detail_level: Literal["minimal", "brief", "full"] = "minimal",
    category: Optional[str] = None
) -> str:
    """
    List available tools with configurable detail.

    Args:
        detail_level:
            - minimal: Tool names only
            - brief: Names, descriptions, categories
            - full: Complete schemas
        category: Optional category filter

    Returns:
        JSON array of tools at requested detail level
    """
    # Filter by category if specified
    tools = TOOLS_REGISTRY.values()
    if category:
        tools = [t for t in tools if t.get("category") == category]

    # Build response based on detail level
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
        result = [
            {
                "name": t["name"],
                "description": t["description"],
                "category": t.get("category", "general"),
                "tags": t.get("tags", []),
                "schema": t.get("schema", {})
            }
            for t in tools
        ]

    return json.dumps(result, indent=2)
```

#### Response Examples

**Minimal**:
```json
[
  "myapp_scrape_url",
  "myapp_extract_links"
]
```

**Brief**:
```json
[
  {
    "name": "myapp_scrape_url",
    "description": "Scrape content from a URL",
    "category": "scraping"
  },
  {
    "name": "myapp_extract_links",
    "description": "Extract all links from HTML content",
    "category": "parsing"
  }
]
```

**Full**:
```json
[
  {
    "name": "myapp_scrape_url",
    "description": "Scrape content from a URL",
    "category": "scraping",
    "tags": ["web", "html", "http"],
    "schema": {
      "parameters": {
        "url": {"type": "string", "required": true},
        "format": {"type": "string", "enum": ["html", "markdown"]}
      }
    }
  }
]
```

### 2. Search Tools Endpoint

The `search_tools` endpoint finds tools by keyword with relevance scoring.

#### Implementation with Fuzzy Matching

```python
from typing import List, Optional
import json

def calculate_relevance(tool: dict, query: str) -> int:
    """Calculate relevance score for tool matching query."""
    score = 0
    query_lower = query.lower()

    # Exact name match (highest priority)
    if query_lower == tool["name"].lower():
        score += 100

    # Name contains query
    if query_lower in tool["name"].lower():
        score += 50

    # Description contains query
    if query_lower in tool.get("description", "").lower():
        score += 20

    # Tag match
    for tag in tool.get("tags", []):
        if query_lower in tag.lower():
            score += 10

    # Category match
    if query_lower in tool.get("category", "").lower():
        score += 15

    return score

@mcp.tool(name="myapp_search_tools")
async def search_tools(
    query: str,
    category: Optional[str] = None,
    detail_level: Literal["brief", "full"] = "brief",
    max_results: int = 10
) -> str:
    """
    Search for tools by keyword.

    Args:
        query: Search term (searches name, description, tags, category)
        category: Optional category filter
        detail_level: brief or full (minimal not useful for search)
        max_results: Maximum results to return (default 10)

    Returns:
        JSON array of matching tools sorted by relevance
    """
    # Filter by category if specified
    tools = list(TOOLS_REGISTRY.values())
    if category:
        tools = [t for t in tools if t.get("category") == category]

    # Calculate relevance for each tool
    results = []
    for tool in tools:
        score = calculate_relevance(tool, query)
        if score > 0:
            results.append({
                "tool": tool,
                "relevance": score
            })

    # Sort by relevance (highest first)
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
                "name": r["tool"]["name"],
                "description": r["tool"]["description"],
                "category": r["tool"].get("category", "general"),
                "tags": r["tool"].get("tags", []),
                "schema": r["tool"].get("schema", {}),
                "relevance": r["relevance"]
            }
            for r in results
        ]

    return json.dumps(formatted, indent=2)
```

#### Search Response Example

```json
[
  {
    "name": "myapp_scrape_url",
    "description": "Scrape content from a URL",
    "category": "scraping",
    "relevance": 70
  },
  {
    "name": "myapp_scrape_with_js",
    "description": "Scrape JavaScript-rendered pages",
    "category": "scraping",
    "relevance": 50
  }
]
```

## Advanced Discovery Patterns

### 3. Category Management

#### List Categories

```python
@mcp.tool(name="myapp_list_categories")
async def list_categories() -> str:
    """
    List all available tool categories.

    Returns:
        JSON array of categories with tool counts
    """
    categories = {}

    for tool in TOOLS_REGISTRY.values():
        cat = tool.get("category", "general")
        if cat not in categories:
            categories[cat] = {
                "name": cat,
                "count": 0,
                "description": get_category_description(cat)
            }
        categories[cat]["count"] += 1

    return json.dumps(list(categories.values()), indent=2)

def get_category_description(category: str) -> str:
    """Get description for a category."""
    descriptions = {
        "scraping": "Tools for fetching web content",
        "parsing": "Tools for parsing and extracting data",
        "analysis": "Tools for analyzing content",
        "storage": "Tools for saving and retrieving data"
    }
    return descriptions.get(category, "General tools")
```

**Response**:
```json
[
  {
    "name": "scraping",
    "count": 3,
    "description": "Tools for fetching web content"
  },
  {
    "name": "parsing",
    "count": 2,
    "description": "Tools for parsing and extracting data"
  }
]
```

### 4. Tag-Based Discovery

```python
@mcp.tool(name="myapp_find_by_tags")
async def find_by_tags(
    tags: List[str],
    match_mode: Literal["any", "all"] = "any",
    detail_level: Literal["brief", "full"] = "brief"
) -> str:
    """
    Find tools by tags.

    Args:
        tags: List of tags to match
        match_mode:
            - any: Tool matches if it has ANY of the tags
            - all: Tool matches if it has ALL of the tags
        detail_level: brief or full

    Returns:
        JSON array of matching tools
    """
    results = []

    for tool in TOOLS_REGISTRY.values():
        tool_tags = set(tool.get("tags", []))
        search_tags = set(tags)

        if match_mode == "any":
            matches = bool(tool_tags & search_tags)
        else:  # all
            matches = search_tags.issubset(tool_tags)

        if matches:
            results.append(tool)

    # Format based on detail level
    if detail_level == "brief":
        formatted = [
            {
                "name": t["name"],
                "description": t["description"],
                "tags": t.get("tags", [])
            }
            for t in results
        ]
    else:  # full
        formatted = results

    return json.dumps(formatted, indent=2)
```

### 5. Tool Relationships

```python
@mcp.tool(name="myapp_get_related_tools")
async def get_related_tools(
    tool_name: str,
    max_results: int = 5
) -> str:
    """
    Get tools related to a specific tool.

    Args:
        tool_name: Name of the tool to find relatives for
        max_results: Maximum related tools to return

    Returns:
        JSON array of related tools with relationship type
    """
    if tool_name not in TOOLS_REGISTRY:
        return json.dumps({"error": f"Tool '{tool_name}' not found"})

    tool = TOOLS_REGISTRY[tool_name]
    results = []

    # Find tools in same category
    for other_name, other_tool in TOOLS_REGISTRY.items():
        if other_name == tool_name:
            continue

        relationship = None

        # Same category
        if other_tool.get("category") == tool.get("category"):
            relationship = "same_category"

        # Overlapping tags
        tool_tags = set(tool.get("tags", []))
        other_tags = set(other_tool.get("tags", []))
        overlap = tool_tags & other_tags
        if overlap:
            relationship = f"shared_tags:{','.join(overlap)}"

        # Explicit relationship
        if other_name in tool.get("related_tools", []):
            relationship = "explicitly_related"

        if relationship:
            results.append({
                "name": other_name,
                "description": other_tool["description"],
                "relationship": relationship
            })

    # Sort by relationship strength
    priority = {"explicitly_related": 3, "same_category": 2}
    results.sort(
        key=lambda x: priority.get(x["relationship"].split(":")[0], 1),
        reverse=True
    )

    return json.dumps(results[:max_results], indent=2)
```

## Discovery Flow Examples

### Flow 1: Explore by Category

```python
# Agent workflow
async def explore_by_category():
    # 1. List all categories
    categories = await mcp.call("myapp_list_categories")

    # 2. Pick interesting category
    selected = "scraping"

    # 3. List tools in category
    tools = await mcp.call("myapp_list_tools", {
        "category": selected,
        "detail_level": "brief"
    })

    # 4. Get full schema for specific tool
    schema = await mcp.call("myapp_search_tools", {
        "query": "scrape_url",
        "detail_level": "full"
    })

    return schema
```

### Flow 2: Search-First

```python
# Agent workflow
async def search_first_flow():
    # 1. Search for relevant tools
    results = await mcp.call("myapp_search_tools", {
        "query": "scrape webpage",
        "detail_level": "brief"
    })

    # 2. Pick best match
    best_match = results[0]["name"]

    # 3. Get related tools
    related = await mcp.call("myapp_get_related_tools", {
        "tool_name": best_match
    })

    # 4. Load full schemas for selected tools
    schemas = []
    for tool in [best_match] + [r["name"] for r in related[:2]]:
        schema = await mcp.call("myapp_search_tools", {
            "query": tool,
            "detail_level": "full"
        })
        schemas.append(schema)

    return schemas
```

### Flow 3: Tag-Based Discovery

```python
# Agent workflow
async def tag_based_flow():
    # 1. Search by tags
    html_tools = await mcp.call("myapp_find_by_tags", {
        "tags": ["html", "web"],
        "match_mode": "any",
        "detail_level": "brief"
    })

    # 2. Narrow with additional tag
    async_html_tools = await mcp.call("myapp_find_by_tags", {
        "tags": ["html", "async"],
        "match_mode": "all",
        "detail_level": "full"
    })

    return async_html_tools
```

## Performance Optimization

### 1. Caching Strategies

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache tool registry in memory
_registry_cache = None
_cache_timestamp = None
_cache_ttl = timedelta(minutes=5)

def get_tools_registry():
    """Get tools registry with caching."""
    global _registry_cache, _cache_timestamp

    now = datetime.utcnow()

    if (_registry_cache is None or
        _cache_timestamp is None or
        now - _cache_timestamp > _cache_ttl):

        # Rebuild registry
        _registry_cache = load_tools_from_source()
        _cache_timestamp = now

    return _registry_cache

# Use cached registry in endpoints
@mcp.tool(name="myapp_list_tools")
async def list_tools(detail_level: str = "minimal"):
    registry = get_tools_registry()
    # ... rest of implementation
```

### 2. Pagination

```python
@mcp.tool(name="myapp_list_tools")
async def list_tools(
    detail_level: str = "minimal",
    page: int = 1,
    page_size: int = 50
) -> str:
    """
    List tools with pagination.

    Args:
        detail_level: minimal, brief, or full
        page: Page number (1-indexed)
        page_size: Results per page (default 50, max 100)

    Returns:
        JSON with tools and pagination metadata
    """
    tools = list(TOOLS_REGISTRY.values())

    # Calculate pagination
    total = len(tools)
    page_size = min(page_size, 100)  # Cap at 100
    start = (page - 1) * page_size
    end = start + page_size

    # Slice tools
    page_tools = tools[start:end]

    # Format tools based on detail level
    formatted = format_tools(page_tools, detail_level)

    # Return with pagination metadata
    return json.dumps({
        "tools": formatted,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_tools": total,
            "total_pages": (total + page_size - 1) // page_size,
            "has_next": end < total,
            "has_prev": page > 1
        }
    }, indent=2)
```

## Error Handling

### Helpful Error Messages

```python
@mcp.tool(name="myapp_search_tools")
async def search_tools(query: str, **kwargs) -> str:
    """Search with helpful error messages."""

    # Validate query
    if not query or not query.strip():
        return json.dumps({
            "error": "Query cannot be empty",
            "suggestion": "Try searching for tool functionality, e.g., 'scrape' or 'parse'"
        })

    # Search
    results = perform_search(query, **kwargs)

    # No results
    if not results:
        return json.dumps({
            "error": f"No tools found matching '{query}'",
            "suggestions": [
                "Try a more general search term",
                "Use myapp_list_categories to browse available categories",
                "Use myapp_list_tools with detail_level='brief' to see all tools"
            ],
            "available_categories": list(get_categories())
        })

    return json.dumps(results)
```

## Testing Discovery Endpoints

### Unit Tests

```python
import pytest
import json

@pytest.mark.asyncio
async def test_list_tools_minimal():
    """Test minimal detail level."""
    result = await list_tools(detail_level="minimal")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert all(isinstance(t, str) for t in tools)
    assert len(tools) > 0

@pytest.mark.asyncio
async def test_list_tools_brief():
    """Test brief detail level."""
    result = await list_tools(detail_level="brief")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert all("name" in t and "description" in t for t in tools)

@pytest.mark.asyncio
async def test_search_tools():
    """Test search functionality."""
    result = await search_tools(query="scrape")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert all("scrape" in t["name"].lower() for t in tools)
    assert all("relevance" in t for t in tools)

@pytest.mark.asyncio
async def test_category_filter():
    """Test category filtering."""
    result = await list_tools(
        detail_level="brief",
        category="scraping"
    )
    tools = json.loads(result)

    assert all(t["category"] == "scraping" for t in tools)
```

## Best Practices

### 1. Consistent Response Formats

Always return JSON with consistent structure:

```python
# Good: Consistent structure
{
    "name": "tool_name",
    "description": "...",
    "category": "...",
    "tags": []
}

# Bad: Inconsistent
{
    "toolName": "...",  # Different key
    "desc": "...",      # Abbreviated
    "cat": "..."        # Unclear
}
```

### 2. Rich Metadata

Include helpful metadata in responses:

```python
{
    "tools": [...],
    "metadata": {
        "total_count": 50,
        "filtered_count": 10,
        "categories_available": ["scraping", "parsing"],
        "detail_level": "brief"
    }
}
```

### 3. Example Usage

Include examples in tool descriptions:

```python
{
    "name": "myapp_scrape_url",
    "description": "Scrape content from a URL",
    "example": {
        "input": {"url": "https://example.com", "format": "markdown"},
        "output": {"resource_uri": "myapp://abc123/content", "preview": "..."}
    }
}
```

## Conclusion

Effective tool discovery requires:
1. Multiple discovery paths (list, search, category, tags)
2. Configurable detail levels
3. Relevance scoring for search
4. Helpful error messages
5. Performance optimization (caching, pagination)
6. Rich metadata and examples

These patterns enable agents to efficiently discover and use tools without loading all schemas upfront.
