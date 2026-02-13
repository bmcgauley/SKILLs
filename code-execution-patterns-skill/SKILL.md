# Code Execution Patterns Skill

**Version**: 1.0.0
**Last Updated**: 2025-11-09
**License**: MIT

## Overview

This skill teaches agents how to write effective code that uses MCP (Model Context Protocol) tools efficiently. It focuses on keeping large data outside the context window, composing tools together, handling errors gracefully, and optimizing performance.

## Purpose

Modern agent workflows can execute code directly, allowing them to call MCP tools and process data in their execution environment rather than in the conversation context. This dramatically reduces token usage and enables more sophisticated data processing pipelines.

**Key Benefits**:
- **98-99% reduction in token usage** for data-heavy operations
- **Parallel execution** of independent operations
- **Secure PII handling** through tokenization
- **Composable tools** that work together seamlessly
- **Resilient error handling** with automatic retries

## When to Use This Skill

Invoke this skill when you need to:

1. **Write agent code** that calls MCP tools
2. **Compose multiple MCP calls** into a pipeline
3. **Manage large datasets** (>1KB) between tool calls
4. **Handle sensitive data** (PII, credentials, etc.)
5. **Optimize performance** of agent scripts
6. **Test agent code** with mocks or integration tests
7. **Debug token usage** issues in workflows

## Core Concepts

### 1. Data Outside Context

The fundamental principle: **keep large data in the execution environment, not in the conversation context**.

**Why?** Every byte in the conversation context counts toward your token limit. By keeping data in the execution environment and only passing references through context, you can work with massive datasets while using minimal tokens.

**How?** MCP tools return resource URIs instead of full data:
```python
# Tool returns reference
result = await mcp.call("scrape_url", {"url": url})
# result = {"resource_uri": "scrape://abc123/content", "preview": "..."}

# Fetch full data into execution environment
content = await mcp.get_resource(result["resource_uri"])
# content is now in execution env, NOT in context
```

### 2. Progressive Discovery

Don't assume which tools are available. Discover them programmatically:

1. **List** available tools (minimal detail)
2. **Search** for relevant tools by keyword
3. **Load** full schema only when implementing
4. **Execute** the tool with proper parameters

This approach minimizes token usage during exploration and ensures your code adapts to available tools.

### 3. Tool Composition

Design tools to be composable—each tool does one thing well, and agent code chains them together:

```python
# Composable workflow
scrape_result = await scrape_url(url)
content = await get_resource(scrape_result["resource_uri"])
links = extract_links(content)  # Local processing
filtered = filter_links(links)  # Local processing
results = await scrape_multiple(filtered)  # Parallel execution
```

### 4. Parallel Execution

Use `asyncio.gather()` to run independent operations concurrently:

```python
tasks = [scrape_url(url) for url in urls]
results = await asyncio.gather(*tasks)
```

This can reduce execution time from minutes to seconds when processing multiple items.

### 5. Error Resilience

Always handle errors gracefully with retries and fallbacks:

```python
try:
    result = await mcp.call("tool", params)
    if "error" in result:
        handle_error(result["error"])
except Exception as e:
    # Retry with exponential backoff
    # Or use fallback approach
```

## Design Patterns

### Pattern 1: Progressive Tool Discovery

**Use Case**: Before implementing a workflow, discover what tools are available.

**Implementation**:
```python
async def discover_and_use_tools():
    # 1. List all tools (minimal detail)
    tools = await mcp.call("webscrape_list_tools", {
        "detail_level": "minimal"
    })
    print(f"Available tools: {tools}")

    # 2. Search for specific functionality
    crawl_tools = await mcp.call("webscrape_search_tools", {
        "query": "crawl",
        "category": "scraping"
    })

    # 3. Load full schema when ready to implement
    schema = await mcp.call("webscrape_search_tools", {
        "query": "crawl_site",
        "detail_level": "full"
    })

    # 4. Now call the tool
    result = await mcp.call("webscrape_crawl_site", {
        "url": "https://example.com",
        "max_depth": 2
    })

    return result
```

**Benefits**:
- Adapts to available tools
- Minimizes token usage during exploration
- Self-documenting code

### Pattern 2: Data Outside Context

**Use Case**: Processing large datasets (scraped content, files, API responses).

**Implementation**:
```python
async def process_large_data(url: str):
    # Get reference (small, ~100 bytes)
    scrape_ref = await mcp.call("scrape_url", {"url": url})

    # Fetch into execution environment (NOT context)
    content = await mcp.get_resource(scrape_ref["resource_uri"])

    # Process locally (outside context)
    processed = transform_data(content)  # 1MB stays out of context
    cleaned = clean_data(processed)
    analyzed = analyze_data(cleaned)

    # Save result (transformed data never enters context)
    return await mcp.call("save_result", {"data": analyzed})
```

**Benefits**:
- 98-99% reduction in token usage
- Can process gigabytes of data
- Faster execution (no context overhead)

### Pattern 3: Tool Composition

**Use Case**: Building multi-step workflows.

**Implementation**:
```python
async def scrape_and_analyze_pipeline(url: str):
    # Step 1: Scrape main page
    page_ref = await mcp.call("webscrape_scrape_url", {
        "url": url,
        "response_format": "markdown"
    })

    # Step 2: Get content into execution env
    page_content = await mcp.get_resource(page_ref["resource_uri"])

    # Step 3: Extract links locally (no MCP call needed)
    links = extract_links_from_markdown(page_content)

    # Step 4: Filter links locally
    external_links = [
        link for link in links
        if not is_same_domain(link, url)
    ]

    # Step 5: Scrape external links in parallel
    link_tasks = [
        mcp.call("webscrape_scrape_url", {"url": link})
        for link in external_links[:10]
    ]
    link_refs = await asyncio.gather(*link_tasks)

    # Step 6: Analyze all content
    link_contents = [
        await mcp.get_resource(ref["resource_uri"])
        for ref in link_refs
    ]

    # Step 7: Generate insights
    insights = generate_insights(page_content, link_contents)

    return insights
```

**Benefits**:
- Clear, readable pipeline
- Mix of MCP calls and local processing
- Parallel execution where possible

### Pattern 4: Parallel Execution

**Use Case**: Processing multiple independent items.

**Implementation**:
```python
async def scrape_multiple_urls(urls: List[str]):
    # Create tasks for all URLs
    tasks = [
        mcp.call("webscrape_scrape_url", {"url": url})
        for url in urls
    ]

    # Execute in parallel (not sequential)
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Separate successes from failures
    successful = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    print(f"Successful: {len(successful)}, Failed: {len(failed)}")

    return {
        "successful": successful,
        "failed": failed,
        "success_rate": len(successful) / len(urls)
    }
```

**Benefits**:
- 10-100x faster than sequential processing
- Built-in error handling
- Efficient resource usage

### Pattern 5: PII Tokenization

**Use Case**: Processing data that contains PII (emails, phone numbers, SSNs, etc.).

**Implementation**:
```python
async def process_user_data_safely(user_text: str):
    # Step 1: Tokenize PII BEFORE any context interaction
    tokenized = await mcp.call("helper_tokenize_pii", {
        "text": user_text,
        "pii_types": ["email", "phone", "ssn", "credit_card"]
    })

    token_map_id = tokenized["token_map_id"]
    safe_text = tokenized["tokenized_text"]
    # safe_text = "Contact [EMAIL_1] at [PHONE_1]"

    # Step 2: Process tokenized text (no PII in context)
    analysis = await analyze_sentiment(safe_text)
    entities = await extract_entities(safe_text)

    # Step 3: Detokenize only if needed for final output
    if user_wants_original:
        final_text = await mcp.call("helper_detokenize_pii", {
            "text": analysis["summary"],
            "token_map_id": token_map_id
        })
    else:
        # Keep it tokenized for security
        final_text = analysis["summary"]

    return {
        "analysis": analysis,
        "entities": entities,
        "text": final_text
    }
```

**Benefits**:
- PII never enters conversation context
- Compliant with privacy regulations
- Reversible tokenization when needed

### Pattern 6: Chunking Large Data

**Use Case**: Processing datasets too large to fit in memory.

**Implementation**:
```python
async def process_large_dataset(data_uri: str):
    # Step 1: Get metadata without loading data
    metadata = await mcp.call("get_data_metadata", {"uri": data_uri})

    if metadata["size_bytes"] > 1_000_000:  # > 1MB
        # Step 2: Chunk the data
        chunk_result = await mcp.call("helper_chunk_data", {
            "data_uri": data_uri,
            "chunk_size": 100_000,  # 100KB chunks
            "overlap": 1000  # For context across chunks
        })

        # Step 3: Process each chunk
        results = []
        for chunk_id in chunk_result["chunk_ids"]:
            chunk_data = await mcp.get_resource(f"chunk://{chunk_id}")
            processed = process_chunk(chunk_data)
            results.append(processed)

        # Step 4: Combine results
        return combine_chunk_results(results)
    else:
        # Small enough to process directly
        data = await mcp.get_resource(data_uri)
        return process_data(data)
```

**Benefits**:
- Process arbitrarily large datasets
- Controlled memory usage
- Parallelizable across chunks

### Pattern 7: Error Handling with Retries

**Use Case**: Handling network errors, rate limits, transient failures.

**Implementation**:
```python
async def resilient_scrape(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            result = await mcp.call("webscrape_scrape_url", {
                "url": url,
                "response_format": "markdown"
            })

            # Check for errors in result
            if "error" in result:
                raise Exception(result["error"])

            print(f"Success on attempt {attempt + 1}")
            return result

        except Exception as e:
            if attempt == max_retries - 1:
                # Final attempt failed, return error info
                print(f"Failed after {max_retries} attempts: {e}")
                return {
                    "error": str(e),
                    "url": url,
                    "attempts": max_retries,
                    "failed": True
                }

            # Wait before retry (exponential backoff)
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

    return None
```

**Benefits**:
- Graceful failure handling
- Exponential backoff prevents hammering
- Detailed error information

### Pattern 8: Caching & Memoization

**Use Case**: Avoiding redundant tool calls for expensive operations.

**Implementation**:
```python
from functools import lru_cache
import hashlib

# Cache tool schemas (rarely change)
@lru_cache(maxsize=100)
async def get_tool_schema(mcp_name: str, tool_name: str):
    return await mcp.call(f"{mcp_name}_search_tools", {
        "query": tool_name,
        "detail_level": "full"
    })

# Cache scraped content by URL
scraped_cache = {}

async def scrape_with_cache(url: str, ttl: int = 3600):
    cache_key = hashlib.md5(url.encode()).hexdigest()

    # Check cache
    if cache_key in scraped_cache:
        cached_result = scraped_cache[cache_key]
        age = time.time() - cached_result["timestamp"]

        if age < ttl:
            print(f"Cache hit for {url} (age: {age:.0f}s)")
            return cached_result["data"]
        else:
            print(f"Cache expired for {url}")

    # Cache miss or expired
    print(f"Cache miss for {url}, fetching...")
    result = await mcp.call("webscrape_scrape_url", {"url": url})

    # Store in cache
    scraped_cache[cache_key] = {
        "data": result,
        "timestamp": time.time()
    }

    return result
```

**Benefits**:
- Avoid redundant network requests
- Faster execution
- Reduced costs

## Testing Strategies

### Unit Testing with Mocks

**Purpose**: Test your code logic without calling real MCP tools.

```python
import pytest
from unittest.mock import AsyncMock, Mock

@pytest.mark.asyncio
async def test_scrape_and_analyze():
    # Create mock MCP client
    mock_mcp = Mock()
    mock_mcp.call = AsyncMock()
    mock_mcp.get_resource = AsyncMock()

    # Setup mock responses
    mock_mcp.call.return_value = {
        "resource_uri": "scrape://test123/content",
        "preview": "Test content...",
        "size_bytes": 5000
    }
    mock_mcp.get_resource.return_value = "<html>Test content</html>"

    # Test your function
    result = await scrape_and_analyze("https://example.com", mcp=mock_mcp)

    # Assertions
    assert mock_mcp.call.called
    assert mock_mcp.call.call_count == 1
    assert "resource_uri" in result

    # Verify correct parameters
    call_args = mock_mcp.call.call_args
    assert call_args[0][0] == "webscrape_scrape_url"
    assert call_args[1]["url"] == "https://example.com"
```

### Integration Testing

**Purpose**: Test with real MCP tools to verify end-to-end behavior.

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_scraping_pipeline():
    # Use real MCP (requires server running)
    result = await scrape_and_analyze("https://example.com")

    # Verify structure
    assert "resource_uri" in result
    assert result["preview"]
    assert result["size_bytes"] > 0

    # Verify data is accessible
    content = await mcp.get_resource(result["resource_uri"])
    assert len(content) > 0
    assert "html" in content.lower() or "markdown" in content.lower()

    # Verify processing worked
    assert "analysis" in result
    assert "links" in result["analysis"]
```

### Performance Testing

**Purpose**: Measure token usage and execution time.

```python
import time

def measure_performance(func):
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        start_tokens = get_context_size()

        result = await func(*args, **kwargs)

        end_time = time.time()
        end_tokens = get_context_size()

        execution_time = end_time - start_time
        tokens_used = end_tokens - start_tokens

        print(f"Function: {func.__name__}")
        print(f"Execution time: {execution_time:.2f}s")
        print(f"Tokens used: {tokens_used}")
        print(f"Tokens/second: {tokens_used/execution_time:.2f}")

        return result

    return wrapper

@measure_performance
async def scraping_pipeline(urls: List[str]):
    # Your implementation
    pass
```

## Performance Optimization

### Token Usage Optimization

**Goal**: Minimize tokens in conversation context.

**Techniques**:

1. **Use resources, not direct returns**
   ```python
   # ❌ Bad: 50KB in context
   data = await mcp.call("get_data", {"id": 123})

   # ✅ Good: ~100 bytes in context
   ref = await mcp.call("get_data", {"id": 123})
   data = await mcp.get_resource(ref["resource_uri"])
   ```

2. **Progressive discovery**
   ```python
   # ❌ Bad: Load all schemas (100KB)
   all_tools = await mcp.call("list_tools", {"detail_level": "full"})

   # ✅ Good: Load names only (5KB)
   tools = await mcp.call("list_tools", {"detail_level": "minimal"})
   # Then get specific schema when needed (2KB)
   schema = await mcp.call("search_tools", {
       "query": "crawl_site",
       "detail_level": "full"
   })
   ```

3. **Process data locally**
   ```python
   # ❌ Bad: Process through MCP calls
   links = await mcp.call("extract_links", {"html": html})
   filtered = await mcp.call("filter_links", {"links": links})

   # ✅ Good: Process in execution environment
   links = extract_links_local(html)
   filtered = filter_links_local(links)
   ```

### Execution Time Optimization

**Goal**: Minimize wall-clock time.

**Techniques**:

1. **Parallel execution**
   ```python
   # ❌ Slow: Sequential (10s total for 10 URLs)
   results = []
   for url in urls:
       result = await scrape_url(url)  # 1s each
       results.append(result)

   # ✅ Fast: Parallel (1s total for 10 URLs)
   results = await asyncio.gather(*[
       scrape_url(url) for url in urls
   ])
   ```

2. **Caching**
   ```python
   # Cache expensive operations
   cache = {}

   async def cached_operation(key):
       if key in cache:
           return cache[key]

       result = await expensive_operation(key)
       cache[key] = result
       return result
   ```

3. **Early termination**
   ```python
   # Stop as soon as you find what you need
   async def find_first_match(urls, pattern):
       for url in urls:
           content = await scrape_url(url)
           if pattern in content:
               return url  # Stop early
       return None
   ```

## Common Pitfalls and Solutions

### Pitfall 1: Loading Full Data Into Context

**Problem**: Large data flows through conversation context.

**Bad**:
```python
data = await mcp.call("get_data", {"id": 123})
process(data["content"])  # 500KB in context!
```

**Good**:
```python
ref = await mcp.call("get_data", {"id": 123})
content = await mcp.get_resource(ref["resource_uri"])
process(content)  # In execution env
```

### Pitfall 2: No Error Handling

**Problem**: One failure breaks entire pipeline.

**Bad**:
```python
result = await mcp.call("tool", params)
# What if it fails? Unhandled exception!
```

**Good**:
```python
try:
    result = await mcp.call("tool", params)
    if "error" in result:
        handle_error(result["error"])
except Exception as e:
    log_error(e)
    use_fallback()
```

### Pitfall 3: Not Using Discovery

**Problem**: Hard-coded tool names that may not exist.

**Bad**:
```python
# Assumes webscrape_crawl_site exists
await mcp.call("webscrape_crawl_site", params)
```

**Good**:
```python
# Verify tool exists first
tools = await mcp.call("webscrape_list_tools", {})
if "webscrape_crawl_site" in tools:
    await mcp.call("webscrape_crawl_site", params)
else:
    use_alternative_approach()
```

### Pitfall 4: Sequential Instead of Parallel

**Problem**: Slow execution due to sequential processing.

**Bad**:
```python
results = []
for url in urls:
    result = await scrape_url(url)  # One at a time
    results.append(result)
```

**Good**:
```python
# All at once
results = await asyncio.gather(*[
    scrape_url(url) for url in urls
])
```

### Pitfall 5: Redundant Tool Calls

**Problem**: Calling same tool multiple times with same parameters.

**Bad**:
```python
schema1 = await get_tool_schema("webscrape", "scrape_url")
# ... later ...
schema2 = await get_tool_schema("webscrape", "scrape_url")  # Duplicate!
```

**Good**:
```python
@lru_cache(maxsize=100)
async def get_tool_schema(mcp_name, tool_name):
    # Cached, only called once per unique input
    return await mcp.call(f"{mcp_name}_search_tools", {
        "query": tool_name,
        "detail_level": "full"
    })
```

## Real-World Examples

See the `examples/` directory for complete, working implementations:

1. **scraping-pipeline.py** - Multi-step web scraping workflow
2. **data-transformation.py** - Large data processing and transformation
3. **pii-tokenization.py** - Secure handling of sensitive data
4. **parallel-operations.py** - Concurrent execution patterns

## Reference Documentation

For deeper dives into specific topics, see:

- **data-management.md** - Detailed guide on managing data outside context
- **pii-handling.md** - PII tokenization and security patterns
- **error-handling.md** - Comprehensive error handling strategies
- **performance-optimization.md** - Advanced optimization techniques
- **testing-agent-code.md** - Testing best practices and patterns

## Related Skills

- **mcp-architecture** - For building MCPs that support code execution
- **brian-dev-workflow** - For integrating MCP development into full-stack workflow

## Version History

- **1.0.0** (2025-11-09) - Initial release
  - Core patterns documented
  - Example implementations
  - Reference documentation
  - Testing strategies

## Contributing

To contribute improvements to this skill:

1. Test patterns with real MCP implementations
2. Document lessons learned
3. Add new examples for common use cases
4. Update performance benchmarks
5. Submit feedback on unclear sections

## License

MIT License - Free to use and modify
