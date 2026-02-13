# Data Management Outside Context

**Last Updated**: 2025-11-09

## Overview

The most important optimization in code execution with MCPs is keeping large data outside the conversation context. This guide explains how to manage data efficiently in the execution environment.

## The Context Problem

### What Goes Into Context?

Every interaction between the agent and MCP tools flows through the conversation context:

1. **Tool calls** - Function names and parameters
2. **Tool responses** - Return values from tools
3. **Variables** - Any data you reference in conversation
4. **Intermediate results** - Data passed between operations

**Token Cost**: Each character ≈ 0.25-0.5 tokens (varies by tokenizer)

### Example: The Token Explosion

```python
# BAD: Everything flows through context
async def analyze_website(url: str):
    # Tool call: ~100 tokens
    # Response with 50KB HTML: ~25,000 tokens
    page = await mcp.call("scrape", {"url": url})

    # Links are extracted, but page is still in context: ~25,000 tokens
    links = await mcp.call("extract_links", {"html": page["content"]})

    # Scrape 5 more pages: ~125,000 additional tokens
    link_contents = []
    for link in links["links"][:5]:
        content = await mcp.call("scrape", {"url": link})
        link_contents.append(content)  # Each ~25KB

    # Total tokens in context: ~150,000
    # Context limit reached! 💥
```

## The Solution: Resources

### Resource-Based Architecture

MCP tools return **references** to data, not the data itself:

```python
# Tool returns this (small):
{
    "resource_uri": "scrape://abc123/content",
    "preview": "First 500 chars of content...",
    "metadata": {
        "size_bytes": 51200,
        "content_type": "text/html",
        "created_at": "2025-11-09T10:30:00Z"
    }
}
```

### Fetching Resources

Retrieve full data into execution environment:

```python
# Get reference (minimal tokens)
scrape_ref = await mcp.call("scrape_url", {"url": url})

# Fetch full data into execution environment
content = await mcp.get_resource(scrape_ref["resource_uri"])
# content is now a variable in the execution environment
# It does NOT occupy conversation tokens
```

## Data Flow Patterns

### Pattern 1: Single Large File

**Use Case**: Processing one large file or API response.

```python
async def process_large_file(file_path: str):
    # Step 1: Get file reference
    file_ref = await mcp.call("load_file", {"path": file_path})
    # Context usage: ~200 tokens (just the reference)

    # Step 2: Fetch into execution environment
    file_content = await mcp.get_resource(file_ref["resource_uri"])
    # Context usage: Still ~200 tokens
    # file_content is 10MB, but in execution env

    # Step 3: Process locally
    lines = file_content.split('\n')
    filtered_lines = [l for l in lines if condition(l)]
    result = '\n'.join(filtered_lines)
    # Context usage: Still ~200 tokens
    # All processing happens outside context

    # Step 4: Save result
    await mcp.call("save_file", {
        "path": "output.txt",
        "content": result
    })
    # Context usage: ~300 tokens (path + small confirmation)

    # Total context usage: ~500 tokens instead of ~2,500,000
```

### Pattern 2: Multiple Large Files

**Use Case**: Processing a batch of files or URLs.

```python
async def process_multiple_files(file_paths: List[str]):
    # Step 1: Get all references (in parallel)
    ref_tasks = [
        mcp.call("load_file", {"path": path})
        for path in file_paths
    ]
    file_refs = await asyncio.gather(*ref_tasks)
    # Context usage: ~1,000 tokens for 10 files

    # Step 2: Fetch all into execution environment
    contents = [
        await mcp.get_resource(ref["resource_uri"])
        for ref in file_refs
    ]
    # Context usage: Still ~1,000 tokens
    # Each content is 1MB, but all in execution env

    # Step 3: Process in execution environment
    processed = [
        transform_data(content)
        for content in contents
    ]

    # Step 4: Combine and save
    combined = combine_results(processed)
    await mcp.call("save_file", {
        "path": "combined.txt",
        "content": combined
    })

    # Total context usage: ~1,500 tokens instead of ~25,000,000
```

### Pattern 3: Streaming Large Data

**Use Case**: Processing data that's too large for memory.

```python
async def process_huge_dataset(data_uri: str):
    # Step 1: Get metadata
    metadata = await mcp.call("get_metadata", {"uri": data_uri})

    if metadata["size_bytes"] > 10_000_000:  # > 10MB
        # Step 2: Request chunking
        chunk_info = await mcp.call("chunk_data", {
            "uri": data_uri,
            "chunk_size": 1_000_000  # 1MB chunks
        })

        # Step 3: Process chunks one at a time
        results = []
        for chunk_id in chunk_info["chunk_ids"]:
            # Fetch chunk
            chunk = await mcp.get_resource(f"chunk://{chunk_id}")

            # Process chunk
            chunk_result = process_chunk(chunk)
            results.append(chunk_result)

            # Chunk goes out of scope, memory freed

        # Step 4: Combine results
        final_result = combine_chunk_results(results)
    else:
        # Small enough to process in one go
        data = await mcp.get_resource(data_uri)
        final_result = process_data(data)

    return final_result
```

## Memory Management

### Execution Environment Memory

The execution environment has its own memory:

```python
# Variables in execution environment
content = await mcp.get_resource(uri)  # 5MB
processed = transform(content)  # 10MB
filtered = filter_data(processed)  # 3MB

# Total memory in execution env: 18MB
# Total tokens in conversation: ~500 (just references)
```

### Garbage Collection

Python automatically frees memory when variables go out of scope:

```python
async def process_multiple_batches(batches: List[str]):
    for batch_uri in batches:
        # Load batch
        batch_data = await mcp.get_resource(batch_uri)  # 100MB

        # Process batch
        result = process_batch(batch_data)  # 50MB

        # Save result
        await mcp.call("save_batch", {"data": result})

        # batch_data and result go out of scope
        # Python frees ~150MB of memory
        # Ready for next batch

    # Never had more than 150MB in memory at once
```

### Explicit Memory Management

For critical applications, explicitly manage memory:

```python
import gc

async def process_with_gc(uris: List[str]):
    for uri in uris:
        # Load data
        data = await mcp.get_resource(uri)

        # Process
        result = process(data)

        # Save
        await save_result(result)

        # Explicitly delete variables
        del data
        del result

        # Force garbage collection
        gc.collect()
```

## Data Storage Strategies

### Temporary Storage in MCP

MCPs can provide temporary storage for intermediate results:

```python
async def multi_step_pipeline(input_uri: str):
    # Step 1: Transform data
    data = await mcp.get_resource(input_uri)
    transformed = transform(data)

    # Store temporarily in MCP
    temp_ref = await mcp.call("store_temp", {
        "data": transformed,
        "ttl": 3600  # 1 hour expiration
    })

    # Step 2: Later in pipeline, retrieve it
    retrieved = await mcp.get_resource(temp_ref["resource_uri"])

    # Step 3: Final processing
    final = final_transform(retrieved)

    return final
```

### Persistent Storage

For long-lived data:

```python
async def save_for_later(data: any):
    # Save to persistent storage
    ref = await mcp.call("save_persistent", {
        "data": data,
        "key": "my_data_key"
    })

    # Returns permanent URI
    # resource_uri = "storage://my_data_key"

    # Can retrieve anytime
    retrieved = await mcp.get_resource("storage://my_data_key")
```

### File System Storage

Sometimes the simplest solution is best:

```python
import json
import tempfile

async def process_with_filesystem(large_data: dict):
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        json.dump(large_data, f)
        temp_path = f.name

    # Process in chunks from file
    result = process_file_in_chunks(temp_path)

    # Clean up
    os.unlink(temp_path)

    return result
```

## Performance Considerations

### Token Savings Calculation

```python
# Scenario: Process 10 web pages, 50KB each

# Method 1: Through context
# - 10 scrape calls: 10 * 50KB = 500KB = ~250,000 tokens
# - Processing: 250,000 tokens
# Total: ~500,000 tokens

# Method 2: Using resources
# - 10 scrape calls return refs: 10 * 200 bytes = 2KB = ~1,000 tokens
# - Fetch into exec env: No context tokens
# - Processing: In exec env, no context tokens
# Total: ~1,000 tokens

# Savings: 99.8% reduction in token usage
```

### Speed Comparison

```python
import time

# Method 1: Through context (slow)
start = time.time()
data = await mcp.call("get_large_data", {"id": 123})
# Large response travels through context
process(data["content"])  # Data already in memory
elapsed1 = time.time() - start  # ~2 seconds

# Method 2: Using resources (faster)
start = time.time()
ref = await mcp.call("get_large_data", {"id": 123})
# Small response, quick
content = await mcp.get_resource(ref["resource_uri"])
# Direct data transfer, no context overhead
process(content)
elapsed2 = time.time() - start  # ~0.5 seconds

# Resource method is 4x faster
```

## Best Practices

### 1. Always Use Resources for Large Data

**Threshold**: If data > 1KB, use resources.

```python
# Rule of thumb
if estimated_size > 1024:  # > 1KB
    # Return resource reference
    return {
        "resource_uri": f"data://{id}",
        "preview": data[:500]
    }
else:
    # Small enough for direct return
    return {"data": data}
```

### 2. Include Metadata with References

```python
# Good reference response
{
    "resource_uri": "scrape://abc123/content",
    "metadata": {
        "size_bytes": 51200,
        "content_type": "text/html",
        "url": "https://example.com",
        "scraped_at": "2025-11-09T10:30:00Z",
        "preview": "First 500 chars..."
    }
}
```

### 3. Use Preview for Quick Checks

```python
# Check preview before fetching full data
ref = await mcp.call("scrape_url", {"url": url})

if "error" in ref["metadata"]["preview"]:
    # Don't bother fetching full content
    return handle_error(ref["metadata"]["preview"])

# Preview looks good, fetch full content
content = await mcp.get_resource(ref["resource_uri"])
```

### 4. Clean Up Resources

```python
# Delete resources when done
async def process_and_cleanup(uri: str):
    # Fetch and process
    data = await mcp.get_resource(uri)
    result = process(data)

    # Clean up resource
    await mcp.call("delete_resource", {"uri": uri})

    return result
```

### 5. Set Appropriate TTLs

```python
# Short-lived data (minutes)
await mcp.call("store_temp", {
    "data": intermediate_result,
    "ttl": 300  # 5 minutes
})

# Medium-lived data (hours)
await mcp.call("store_temp", {
    "data": processed_data,
    "ttl": 3600  # 1 hour
})

# Long-lived data (days)
await mcp.call("store_persistent", {
    "data": final_result,
    "ttl": 86400  # 24 hours
})
```

## Troubleshooting

### Problem: Resource Not Found

```python
try:
    content = await mcp.get_resource(uri)
except ResourceNotFoundError:
    # Resource expired or doesn't exist
    # Regenerate or use fallback
    content = await regenerate_resource()
```

### Problem: Memory Issues

```python
# If execution environment runs out of memory
# Process in smaller chunks

async def process_carefully(data_uri: str):
    metadata = await mcp.call("get_metadata", {"uri": data_uri})

    if metadata["size_bytes"] > 100_000_000:  # > 100MB
        # Too large, chunk it
        return await process_in_chunks(data_uri)
    else:
        # Safe to load fully
        data = await mcp.get_resource(data_uri)
        return process(data)
```

### Problem: Slow Resource Access

```python
# If fetching resources is slow, cache them

resource_cache = {}

async def get_resource_cached(uri: str):
    if uri in resource_cache:
        return resource_cache[uri]

    content = await mcp.get_resource(uri)
    resource_cache[uri] = content
    return content
```

## Summary

**Key Principles**:

1. **Keep large data in execution environment**, not context
2. **Use resource URIs** for data > 1KB
3. **Include metadata** with resource references
4. **Clean up resources** when done
5. **Chunk very large datasets** to manage memory

**Benefits**:

- **98-99% reduction** in token usage
- **Faster execution** (no context overhead)
- **Can process gigabytes** of data
- **More reliable** (avoid context limits)

**Remember**: Every byte in context counts. When in doubt, use resources!
