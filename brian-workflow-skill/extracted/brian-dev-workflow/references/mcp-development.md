# MCP Development Reference

Complete guide to Model Context Protocol development with progressive disclosure patterns.

**Last Updated**: 2025-11-09
**Related Files**:
- `c:/github/mcps/MCP-REFACTORING-GUIDE.md` - Comprehensive refactoring guide
- `c:/github/mcps/webscrape_mcp/REFACTORING-COMPLETE.md` - Real-world example

## Table of Contents

1. [Progressive Disclosure Architecture](#progressive-disclosure-architecture)
2. [Tool Discovery Patterns](#tool-discovery-patterns)
3. [Resource Management](#resource-management)
4. [Caching Strategies](#caching-strategies)
5. [TypeScript Definitions](#typescript-definitions)
6. [Code Execution Helper Patterns](#code-execution-helper-patterns)
7. [Testing Strategies](#testing-strategies)
8. [Token Reduction Measurement](#token-reduction-measurement)
9. [Common Patterns Library](#common-patterns-library)
10. [Troubleshooting](#troubleshooting)

## Progressive Disclosure Architecture

### Core Concept

Progressive disclosure enables agents to:
1. **Discover tools on-demand** (not load all upfront)
2. **Load only needed schemas** (minimal → brief → full)
3. **Access data via resources** (keep large data out of context)
4. **Compose tools in code** (chain operations efficiently)

**Result**: 98-99% token reduction vs traditional MCP architecture.

### Architecture Layers

```
┌─────────────────────────────────────────────┐
│ Agent Workflow (Code Execution)             │
├─────────────────────────────────────────────┤
│ 1. Discovery Layer                          │
│    - list_tools() → Get tool names          │
│    - search_tools() → Find relevant tools   │
│                                              │
│ 2. Schema Loading (Optional)                │
│    - Load TypeScript definitions on-demand  │
│    - Parse tool interfaces                  │
│                                              │
│ 3. Execution Layer                          │
│    - Call tools with parameters             │
│    - Receive resource references            │
│                                              │
│ 4. Resource Access Layer                    │
│    - Fetch full data only if needed         │
│    - Access via resource URIs               │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ MCP Server Architecture                     │
├─────────────────────────────────────────────┤
│ Discovery Endpoints                         │
│  ├─ list_tools                              │
│  └─ search_tools                            │
│                                              │
│ Tool Endpoints                              │
│  ├─ tool1 (returns resource URIs)           │
│  ├─ tool2                                   │
│  └─ toolN                                   │
│                                              │
│ Resource Endpoints                          │
│  ├─ {mcp}://{id}/content                    │
│  └─ {mcp}://{id}/metadata                   │
│                                              │
│ Cache Layer                                 │
│  ├─ Resource storage                        │
│  ├─ TTL management                          │
│  └─ Cleanup mechanism                       │
└─────────────────────────────────────────────┘
```

### Design Principles

1. **Metadata First**: Always return metadata + preview, not full data
2. **On-Demand Schema**: Agents load type definitions only when needed
3. **Stateless Tools**: Each tool call is independent
4. **Resource References**: Data >1KB returned as URIs
5. **Composability**: Tools designed to chain together

## Tool Discovery Patterns

### Pattern 1: List Tools Endpoint

```python
@mcp.tool(name="{mcp_name}_list_tools")
async def list_tools(
    detail_level: Literal["minimal", "brief", "full"] = "minimal",
    category: Optional[str] = None
) -> str:
    """
    List available tools with configurable detail level.

    Args:
        detail_level:
            - minimal: Names only (fastest, for exploration)
            - brief: Names + descriptions (for searching)
            - full: Complete schemas (for implementation)
        category: Filter by category (e.g., "scraping", "analysis")

    Returns:
        JSON with tool information at requested detail level
    """
    # Tool registry
    tools = {
        "tool1": {
            "name": "{mcp_name}_tool1",
            "description": "Brief description",
            "category": "category_name",
            "schema": {
                "input": {...},
                "output": {...}
            }
        },
        # ... more tools
    }

    # Filter by category if specified
    if category:
        tools = {
            k: v for k, v in tools.items()
            if v.get("category") == category
        }

    # Return based on detail level
    if detail_level == "minimal":
        # Just names (200-500 bytes)
        return json.dumps([v["name"] for v in tools.values()])

    elif detail_level == "brief":
        # Names + descriptions (1-2KB)
        return json.dumps([
            {
                "name": v["name"],
                "description": v["description"],
                "category": v["category"]
            }
            for v in tools.values()
        ], indent=2)

    else:  # full
        # Complete schemas (5-10KB)
        return json.dumps(tools, indent=2)
```

**Token Usage**:
- Minimal: 200-500 bytes (vs 150KB loading all schemas)
- Brief: 1-2KB
- Full: 5-10KB (only when needed)

### Pattern 2: Search Tools Endpoint

```python
@mcp.tool(name="{mcp_name}_search_tools")
async def search_tools(
    query: str,
    category: Optional[str] = None,
    max_results: int = 10
) -> str:
    """
    Search for tools by keyword.

    Args:
        query: Search term (searches name, description, tags)
        category: Optional category filter
        max_results: Limit results (default 10)

    Returns:
        JSON array of matching tools with relevance scores
    """
    tools = get_all_tools()

    # Filter by category
    if category:
        tools = [t for t in tools if t.get("category") == category]

    # Search in name, description, tags
    query_lower = query.lower()
    matches = []

    for tool in tools:
        score = 0

        # Exact match in name (highest priority)
        if query_lower in tool["name"].lower():
            score += 10

        # Match in description
        if query_lower in tool["description"].lower():
            score += 5

        # Match in tags
        if "tags" in tool:
            if any(query_lower in tag.lower() for tag in tool["tags"]):
                score += 3

        if score > 0:
            matches.append({
                **tool,
                "relevance_score": score
            })

    # Sort by relevance
    matches.sort(key=lambda x: x["relevance_score"], reverse=True)

    # Limit results
    return json.dumps(matches[:max_results], indent=2)
```

### Pattern 3: Category-Based Organization

```python
# Define tool categories
TOOL_CATEGORIES = {
    "scraping": "Web scraping and data extraction",
    "rendering": "JavaScript rendering and screenshots",
    "extraction": "Data parsing and extraction",
    "analysis": "Content analysis and processing"
}

def categorize_tools():
    """Organize tools by category for discovery"""
    return {
        "scraping": [
            "{mcp_name}_scrape_url",
            "{mcp_name}_crawl_site"
        ],
        "rendering": [
            "{mcp_name}_scrape_with_js",
            "{mcp_name}_screenshot_url"
        ],
        # ... more categories
    }
```

## Resource Management

### Pattern 1: Resource URI Design

**URI Format**: `{mcp_name}://{resource_id}/{resource_type}`

Examples:
- `webscrape://abc123/content` - Full scraped content
- `webscrape://abc123/metadata` - Metadata only
- `midi://def456/file` - Generated MIDI file
- `midi://def456/preview` - Note preview

### Pattern 2: Resource Storage

```python
from datetime import datetime, timedelta
import hashlib
from typing import Any, Dict, Optional

# Global cache (use Redis in production)
CACHE_TTL_SECONDS = 3600  # 1 hour
PREVIEW_LENGTH = 500
RESOURCE_CACHE: Dict[str, Dict[str, Any]] = {}

def _generate_resource_id(data: str, prefix: str = "") -> str:
    """Generate unique ID for resource"""
    content = f"{prefix}{data}{datetime.utcnow().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()

def _store_in_cache(
    resource_id: str,
    data: Any,
    metadata: Dict[str, Any],
    ttl_seconds: Optional[int] = None
) -> None:
    """Store resource with TTL"""
    ttl = ttl_seconds or CACHE_TTL_SECONDS

    RESOURCE_CACHE[resource_id] = {
        "data": data,
        "metadata": metadata,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
    }

def _clean_expired_cache() -> None:
    """Remove expired resources"""
    now = datetime.utcnow()
    expired_keys = [
        k for k, v in RESOURCE_CACHE.items()
        if v["expires_at"] < now
    ]

    for key in expired_keys:
        del RESOURCE_CACHE[key]

    if expired_keys:
        print(f"Cleaned {len(expired_keys)} expired resources")
```

### Pattern 3: Resource Access Endpoints

```python
@mcp.resource("{mcp_name}://{resource_id}/content")
async def get_resource_content(resource_id: str) -> str:
    """Retrieve full content by resource ID"""
    # Clean expired entries first
    _clean_expired_cache()

    # Check if resource exists
    if resource_id not in RESOURCE_CACHE:
        raise Exception(
            f"Resource {resource_id} not found or expired. "
            f"Resources expire after {CACHE_TTL_SECONDS} seconds. "
            f"You may need to re-execute the original tool."
        )

    entry = RESOURCE_CACHE[resource_id]

    # Double-check expiration
    if datetime.utcnow() > entry["expires_at"]:
        del RESOURCE_CACHE[resource_id]
        raise Exception(f"Resource {resource_id} has expired")

    return entry["data"]

@mcp.resource("{mcp_name}://{resource_id}/metadata")
async def get_resource_metadata(resource_id: str) -> str:
    """Retrieve metadata without full content"""
    _clean_expired_cache()

    if resource_id not in RESOURCE_CACHE:
        raise Exception(f"Resource {resource_id} not found or expired")

    entry = RESOURCE_CACHE[resource_id]

    return json.dumps({
        "resource_id": resource_id,
        "metadata": entry["metadata"],
        "created_at": entry["created_at"].isoformat(),
        "expires_at": entry["expires_at"].isoformat(),
        "time_remaining_seconds": (
            entry["expires_at"] - datetime.utcnow()
        ).total_seconds()
    }, indent=2)
```

### Pattern 4: Tool Response Structure

```python
@mcp.tool(name="{mcp_name}_process_data")
async def process_data(params: ProcessDataInput) -> str:
    """Process data and return resource reference"""

    # Perform operation
    full_data = perform_expensive_operation(params)

    # Generate unique ID
    resource_id = _generate_resource_id(
        str(full_data),
        prefix=f"{params.format}_"
    )

    # Store in cache
    _store_in_cache(
        resource_id,
        full_data,
        metadata={
            "size_bytes": len(str(full_data)),
            "format": params.format,
            "operation": "process_data",
            "parameters": params.dict()
        }
    )

    # Return reference (NOT full data)
    return json.dumps({
        "success": True,
        "resource_id": resource_id,
        "resource_uri": f"{MCP_NAME}://{resource_id}/content",
        "metadata_uri": f"{MCP_NAME}://{resource_id}/metadata",
        "preview": str(full_data)[:PREVIEW_LENGTH] + "..." if len(str(full_data)) > PREVIEW_LENGTH else str(full_data),
        "content_length": len(str(full_data)),
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (
            datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS)
        ).isoformat(),
        "expires_in_seconds": CACHE_TTL_SECONDS
    }, indent=2)
```

## Caching Strategies

### Pattern 1: Time-Based TTL

```python
# Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour default

# Per-operation TTL
TTL_CONFIG = {
    "scrape": 3600,      # 1 hour
    "screenshot": 1800,  # 30 minutes
    "generate": 7200,    # 2 hours
}

def get_ttl(operation: str) -> int:
    """Get TTL for specific operation"""
    return TTL_CONFIG.get(operation, CACHE_TTL_SECONDS)
```

### Pattern 2: Size-Based Cleanup

```python
MAX_CACHE_SIZE_MB = 100
MAX_CACHE_ENTRIES = 1000

def enforce_cache_limits():
    """Enforce size and entry limits"""
    # Check entry count
    if len(RESOURCE_CACHE) > MAX_CACHE_ENTRIES:
        # Remove oldest entries
        sorted_entries = sorted(
            RESOURCE_CACHE.items(),
            key=lambda x: x[1]["created_at"]
        )

        entries_to_remove = len(RESOURCE_CACHE) - MAX_CACHE_ENTRIES
        for key, _ in sorted_entries[:entries_to_remove]:
            del RESOURCE_CACHE[key]

    # Check total size
    total_size = sum(
        len(str(v["data"]))
        for v in RESOURCE_CACHE.values()
    )

    if total_size > MAX_CACHE_SIZE_MB * 1024 * 1024:
        # Remove largest entries until under limit
        sorted_by_size = sorted(
            RESOURCE_CACHE.items(),
            key=lambda x: len(str(x[1]["data"])),
            reverse=True
        )

        current_size = total_size
        target_size = MAX_CACHE_SIZE_MB * 1024 * 1024 * 0.8  # 80% of max

        for key, value in sorted_by_size:
            if current_size <= target_size:
                break
            current_size -= len(str(value["data"]))
            del RESOURCE_CACHE[key]
```

### Pattern 3: Background Cleanup Task

```python
import asyncio

async def cache_cleanup_task():
    """Background task to clean expired cache entries"""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        _clean_expired_cache()
        enforce_cache_limits()

# Start cleanup task when server starts
asyncio.create_task(cache_cleanup_task())
```

### Pattern 4: Production Caching with Redis

```python
import redis
import pickle

# Redis connection
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=False  # Store bytes for pickle
)

def store_in_redis(resource_id: str, data: Any, metadata: Dict, ttl: int):
    """Store resource in Redis with TTL"""
    cache_entry = {
        "data": data,
        "metadata": metadata,
        "created_at": datetime.utcnow().isoformat()
    }

    # Serialize
    serialized = pickle.dumps(cache_entry)

    # Store with expiration
    redis_client.setex(
        f"resource:{resource_id}",
        ttl,
        serialized
    )

def get_from_redis(resource_id: str) -> Optional[Dict]:
    """Retrieve resource from Redis"""
    data = redis_client.get(f"resource:{resource_id}")

    if data is None:
        return None

    return pickle.loads(data)
```

## TypeScript Definitions

### Pattern 1: Tool Interface Definition

```typescript
// tools/tool_name.ts

/**
 * Process data with specified parameters
 *
 * This tool processes input data and returns a resource reference
 * for efficient token usage.
 *
 * Best for:
 * - Large data processing
 * - Multi-step workflows
 * - Data transformation
 *
 * @example
 * ```typescript
 * const result = await processData({
 *   input: "data to process",
 *   format: "json"
 * });
 *
 * // Access full data only if needed
 * const content = await getResource(result.resource_uri);
 * ```
 */

export interface ProcessDataInput {
  /** Input data to process */
  input: string;

  /**
   * Output format
   * @default "json"
   */
  format?: "json" | "text" | "markdown";

  /**
   * Processing options
   */
  options?: {
    /** Include metadata in output */
    includeMetadata?: boolean;

    /** Compression level (0-9) */
    compressionLevel?: number;
  };
}

export interface ProcessDataOutput {
  /** Operation success status */
  success: boolean;

  /** Unique identifier for this resource */
  resource_id: string;

  /** URI to fetch full content */
  resource_uri: string;

  /** URI to fetch metadata only */
  metadata_uri: string;

  /** Preview of content (first 500 characters) */
  preview: string;

  /** Total content length in bytes */
  content_length: number;

  /** ISO timestamp when resource was created */
  created_at: string;

  /** ISO timestamp when resource expires */
  expires_at: string;

  /** Seconds until expiration */
  expires_in_seconds: number;
}
```

### Pattern 2: Discovery Interface

```typescript
// tools/index.ts

export interface Tool {
  /** Fully-qualified tool name */
  name: string;

  /** Brief description of tool functionality */
  description: string;

  /** Tool category for filtering */
  category: string;

  /** Tags for search */
  tags?: string[];

  /** Full schema (only in "full" detail level) */
  schema?: {
    input: any;
    output: any;
  };
}

export interface ListToolsInput {
  /**
   * Detail level for tool information
   * - minimal: names only
   * - brief: names + descriptions
   * - full: complete schemas
   */
  detail_level?: "minimal" | "brief" | "full";

  /** Filter by category */
  category?: string;
}

export interface SearchToolsInput {
  /** Search query */
  query: string;

  /** Optional category filter */
  category?: string;

  /** Maximum results to return */
  max_results?: number;
}

export interface SearchResult extends Tool {
  /** Relevance score (higher = more relevant) */
  relevance_score: number;
}
```

### Pattern 3: Resource Access Interface

```typescript
// tools/resources.ts

export interface Resource<T = any> {
  /** Resource unique identifier */
  resource_id: string;

  /** Resource data */
  data: T;

  /** Resource metadata */
  metadata: {
    [key: string]: any;
  };

  /** Creation timestamp */
  created_at: string;

  /** Expiration timestamp */
  expires_at: string;

  /** Seconds remaining until expiration */
  time_remaining_seconds: number;
}

export interface ResourceMetadata {
  /** Resource ID */
  resource_id: string;

  /** Metadata object */
  metadata: {
    size_bytes: number;
    format: string;
    [key: string]: any;
  };

  /** Creation timestamp */
  created_at: string;

  /** Expiration timestamp */
  expires_at: string;

  /** Seconds until expiration */
  time_remaining_seconds: number;
}
```

## Code Execution Helper Patterns

### Pattern 1: Data Pipeline Composition

```python
# Agent code example
async def data_processing_pipeline(url: str):
    """Multi-step data processing using MCP tools"""

    # Step 1: Scrape data
    scrape_result = await mcp.call("webscrape_scrape_url", {
        "url": url,
        "response_format": "markdown"
    })

    # Step 2: Get content (only if needed for processing)
    content = await mcp.get_resource(scrape_result["resource_uri"])

    # Step 3: Process locally (outside context)
    processed = analyze_content(content)

    # Step 4: Store results
    store_result = await mcp.call("storage_save_data", {
        "data": processed,
        "format": "json"
    })

    return store_result
```

### Pattern 2: Parallel Operations

```python
import asyncio

async def parallel_scraping(urls: List[str]):
    """Scrape multiple URLs concurrently"""

    # Create tasks
    tasks = [
        mcp.call("webscrape_scrape_url", {"url": url})
        for url in urls
    ]

    # Execute in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    successful = [
        r for r in results
        if not isinstance(r, Exception)
    ]

    failed = [
        (urls[i], r)
        for i, r in enumerate(results)
        if isinstance(r, Exception)
    ]

    return {
        "successful": successful,
        "failed": failed
    }
```

### Pattern 3: Resource Prefetching

```python
async def prefetch_resources(result_refs: List[dict]):
    """Prefetch resources that will be needed"""

    # Fetch metadata first to decide what to load
    metadata_tasks = [
        mcp.get_resource(ref["metadata_uri"])
        for ref in result_refs
    ]

    metadatas = await asyncio.gather(*metadata_tasks)

    # Only fetch content for small resources
    content_tasks = []
    for ref, meta in zip(result_refs, metadatas):
        if meta["metadata"]["size_bytes"] < 10000:  # <10KB
            content_tasks.append(mcp.get_resource(ref["resource_uri"]))
        else:
            content_tasks.append(None)

    contents = await asyncio.gather(*content_tasks)

    return list(zip(result_refs, metadatas, contents))
```

## Testing Strategies

### Strategy 1: Unit Testing Discovery

```python
import pytest
import json

@pytest.mark.asyncio
async def test_list_tools_minimal():
    """Test minimal tool listing"""
    result = await list_tools(detail_level="minimal")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert len(tools) > 0
    assert all(isinstance(t, str) for t in tools)

    # Response should be small
    assert len(result) < 1000  # <1KB

@pytest.mark.asyncio
async def test_list_tools_category_filter():
    """Test category filtering"""
    result = await list_tools(
        detail_level="brief",
        category="scraping"
    )
    tools = json.loads(result)

    assert all(t["category"] == "scraping" for t in tools)

@pytest.mark.asyncio
async def test_search_tools():
    """Test tool search"""
    result = await search_tools(query="scrape")
    tools = json.loads(result)

    assert len(tools) > 0
    assert all("scrape" in t["name"].lower() for t in tools)
    assert all("relevance_score" in t for t in tools)
```

### Strategy 2: Resource Lifecycle Testing

```python
@pytest.mark.asyncio
async def test_resource_creation_and_access():
    """Test complete resource lifecycle"""

    # Create resource
    result = await process_data(ProcessDataInput(
        input="test data",
        format="json"
    ))

    data = json.loads(result)

    # Verify response structure
    assert data["success"] is True
    assert "resource_id" in data
    assert "resource_uri" in data
    assert "preview" in data

    # Verify response is small
    assert len(result) < 2000  # <2KB

    # Access full content
    content = await get_resource_content(data["resource_id"])
    assert content is not None
    assert len(content) > len(data["preview"])

    # Access metadata
    metadata = await get_resource_metadata(data["resource_id"])
    meta = json.loads(metadata)

    assert meta["resource_id"] == data["resource_id"]
    assert "metadata" in meta
    assert "created_at" in meta

@pytest.mark.asyncio
async def test_resource_expiration():
    """Test resource TTL and expiration"""

    # Create resource with short TTL
    resource_id = _generate_resource_id("test")
    _store_in_cache(
        resource_id,
        "test data",
        {},
        ttl_seconds=1  # 1 second
    )

    # Should be accessible immediately
    content = await get_resource_content(resource_id)
    assert content == "test data"

    # Wait for expiration
    await asyncio.sleep(2)

    # Should raise exception
    with pytest.raises(Exception, match="expired"):
        await get_resource_content(resource_id)
```

### Strategy 3: Token Usage Measurement

```python
def test_token_efficiency():
    """Measure token reduction"""

    # Simulate large data
    large_data = "x" * 25000  # 25KB

    # OLD pattern (return full data)
    old_response = json.dumps({"content": large_data})
    old_size = len(old_response)

    # NEW pattern (return reference)
    resource_id = _generate_resource_id(large_data)
    _store_in_cache(resource_id, large_data, {})

    new_response = json.dumps({
        "resource_id": resource_id,
        "resource_uri": f"mcp://{resource_id}/content",
        "preview": large_data[:500],
        "content_length": len(large_data)
    })
    new_size = len(new_response)

    # Calculate savings
    reduction_percent = ((old_size - new_size) / old_size) * 100

    assert new_size < 2000  # <2KB
    assert reduction_percent >= 98  # 98%+ reduction
    print(f"Token reduction: {reduction_percent:.1f}%")
```

### Strategy 4: Integration Testing

```python
@pytest.mark.asyncio
async def test_complete_workflow():
    """Test agent workflow simulation"""

    # 1. Discovery
    tools = await list_tools(detail_level="minimal")
    tool_list = json.loads(tools)
    assert len(tool_list) > 0

    # 2. Search
    search = await search_tools(query="process")
    search_results = json.loads(search)
    assert len(search_results) > 0

    # 3. Execute
    result = await process_data(ProcessDataInput(
        input="test",
        format="json"
    ))
    result_data = json.loads(result)

    # 4. Access resource
    content = await get_resource_content(result_data["resource_id"])

    # Verify complete workflow used minimal tokens
    total_bytes = (
        len(tools) +
        len(search) +
        len(result) +
        0  # Content fetched outside context
    )

    assert total_bytes < 10000  # <10KB total
```

## Token Reduction Measurement

### Measurement Pattern 1: Before/After Comparison

```python
def measure_token_reduction():
    """Measure token savings from refactoring"""

    # Before: Traditional response
    traditional_data = generate_large_data()  # 50KB
    traditional_response = json.dumps({
        "content": traditional_data,
        "metadata": {"size": len(traditional_data)}
    })

    # After: Progressive disclosure
    resource_id = _generate_resource_id(traditional_data)
    _store_in_cache(resource_id, traditional_data, {})

    progressive_response = json.dumps({
        "resource_id": resource_id,
        "resource_uri": f"mcp://{resource_id}/content",
        "preview": traditional_data[:500],
        "metadata": {"size": len(traditional_data)}
    })

    # Calculate metrics
    traditional_size = len(traditional_response)
    progressive_size = len(progressive_response)
    reduction = traditional_size - progressive_size
    reduction_percent = (reduction / traditional_size) * 100

    print(f"""
Token Reduction Analysis:
- Traditional response: {traditional_size:,} bytes
- Progressive response: {progressive_size:,} bytes
- Reduction: {reduction:,} bytes ({reduction_percent:.1f}%)
    """)

    return reduction_percent
```

### Measurement Pattern 2: Session Tracking

```python
class TokenTracker:
    """Track token usage across MCP session"""

    def __init__(self):
        self.traditional_tokens = 0
        self.progressive_tokens = 0
        self.operations = []

    def log_operation(
        self,
        operation: str,
        traditional_size: int,
        progressive_size: int
    ):
        """Log a single operation"""
        self.traditional_tokens += traditional_size
        self.progressive_tokens += progressive_size

        self.operations.append({
            "operation": operation,
            "traditional": traditional_size,
            "progressive": progressive_size,
            "savings": traditional_size - progressive_size
        })

    def get_summary(self) -> dict:
        """Get session summary"""
        total_savings = self.traditional_tokens - self.progressive_tokens
        savings_percent = (
            (total_savings / self.traditional_tokens) * 100
            if self.traditional_tokens > 0
            else 0
        )

        return {
            "total_traditional_tokens": self.traditional_tokens,
            "total_progressive_tokens": self.progressive_tokens,
            "total_savings": total_savings,
            "savings_percent": savings_percent,
            "operations_count": len(self.operations),
            "operations": self.operations
        }

# Usage
tracker = TokenTracker()

# Log each operation
tracker.log_operation("scrape", 25000, 500)
tracker.log_operation("screenshot", 500000, 2000)

# Get summary
summary = tracker.get_summary()
print(f"Total savings: {summary['savings_percent']:.1f}%")
```

## Common Patterns Library

### Pattern: Batch Processing with Resources

```python
async def batch_process_urls(urls: List[str]) -> List[dict]:
    """Process multiple URLs efficiently"""

    # Scrape all URLs in parallel
    scrape_tasks = [
        mcp.call("webscrape_scrape_url", {"url": url})
        for url in urls
    ]

    scrape_results = await asyncio.gather(*scrape_tasks)

    # Process each result
    processed_results = []

    for result in scrape_results:
        # Get content only for processing (not stored in context)
        content = await mcp.get_resource(result["resource_uri"])

        # Process locally
        analysis = analyze_content(content)

        processed_results.append({
            "url": result["url"],
            "resource_id": result["resource_id"],
            "analysis": analysis
        })

    return processed_results
```

### Pattern: Conditional Resource Access

```python
async def smart_resource_access(result: dict) -> Optional[str]:
    """Only fetch full content if preview insufficient"""

    # Check if preview is enough
    if "preview" in result:
        if can_analyze_preview(result["preview"]):
            return analyze_preview(result["preview"])

    # Need full content
    content = await mcp.get_resource(result["resource_uri"])
    return analyze_full_content(content)
```

### Pattern: Resource Aggregation

```python
async def aggregate_resources(resource_refs: List[dict]) -> dict:
    """Aggregate multiple resources efficiently"""

    # Fetch all resources in parallel
    content_tasks = [
        mcp.get_resource(ref["resource_uri"])
        for ref in resource_refs
    ]

    contents = await asyncio.gather(*content_tasks)

    # Aggregate locally (outside context)
    aggregated = {
        "total_size": sum(len(c) for c in contents),
        "count": len(contents),
        "combined": "\n\n".join(contents)
    }

    return aggregated
```

## Troubleshooting

### Issue: Resource Not Found

**Symptom**: `Exception: Resource {id} not found or expired`

**Causes**:
1. Resource TTL expired (default 1 hour)
2. Resource ID incorrect
3. Cache cleared manually
4. Server restarted (in-memory cache)

**Solutions**:
```python
# 1. Increase TTL for long-running operations
_store_in_cache(
    resource_id,
    data,
    metadata,
    ttl_seconds=7200  # 2 hours
)

# 2. Check resource before accessing
if resource_id in RESOURCE_CACHE:
    content = await get_resource_content(resource_id)
else:
    # Re-execute operation
    result = await regenerate_resource()

# 3. Use persistent storage (Redis)
store_in_redis(resource_id, data, metadata, ttl=3600)
```

### Issue: Token Reduction Not Achieved

**Symptom**: Responses still large (>5KB)

**Causes**:
1. Returning full data in response
2. Large metadata objects
3. Not using resources for large data
4. Preview too long

**Solutions**:
```python
# 1. Always return resource URIs for large data
if len(data) > 1000:  # >1KB
    resource_id = _generate_resource_id(data)
    _store_in_cache(resource_id, data, {})
    return json.dumps({"resource_uri": f"mcp://{resource_id}/content"})

# 2. Keep metadata minimal
metadata = {
    "size": len(data),
    "format": params.format
    # Don't include large objects
}

# 3. Limit preview length
preview = data[:PREVIEW_LENGTH]  # Use constant
```

### Issue: Discovery Tools Not Working

**Symptom**: Agents can't find tools

**Causes**:
1. Tool names not following convention
2. Missing discovery endpoints
3. Incorrect response format
4. No categories defined

**Solutions**:
```python
# 1. Use naming convention
@mcp.tool(name="{mcp_name}_tool_name")  # Not just "tool_name"

# 2. Implement both discovery endpoints
@mcp.tool(name="{mcp_name}_list_tools")
@mcp.tool(name="{mcp_name}_search_tools")

# 3. Return JSON strings
return json.dumps(tools)  # Not Python objects

# 4. Add categories
tools = {
    "tool1": {
        "name": "mcp_tool1",
        "category": "processing",  # Required
        "description": "..."
    }
}
```

### Issue: Cache Memory Issues

**Symptom**: High memory usage, server slowdown

**Causes**:
1. No cache cleanup
2. No size limits
3. Long TTL values
4. Large objects cached

**Solutions**:
```python
# 1. Implement cleanup
async def cache_cleanup_task():
    while True:
        await asyncio.sleep(300)  # Every 5 min
        _clean_expired_cache()
        enforce_cache_limits()

# 2. Set size limits
MAX_CACHE_SIZE_MB = 100
MAX_CACHE_ENTRIES = 1000

# 3. Use appropriate TTL
CACHE_TTL_SECONDS = 3600  # 1 hour, not 24 hours

# 4. Consider Redis for production
# Moves cache out of process memory
```

---

## Additional Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **Anthropic Code Execution Blog**: https://www.anthropic.com/engineering/code-execution-with-mcp
- **FastMCP Library**: https://github.com/jlowin/fastmcp
- **MCP SDK**: https://github.com/modelcontextprotocol/sdk

## Version History

- **1.0.0** (2025-11-09): Initial comprehensive reference
