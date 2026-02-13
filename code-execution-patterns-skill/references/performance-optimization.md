# Performance Optimization for Agent Code

**Last Updated**: 2025-11-09

## Overview

Optimizing agent code that uses MCPs involves minimizing token usage, reducing execution time, and efficiently using resources. This guide provides techniques for building high-performance agent workflows.

## Token Usage Optimization

### Principle: Minimize Context Window Usage

Every token in the conversation context has a cost. The goal is to keep large data in the execution environment.

### Measurement

```python
def estimate_tokens(text: str) -> int:
    """Rough estimate: 1 token ≈ 4 characters"""
    return len(text) // 4

def measure_context_usage(func):
    """Decorator to measure token usage"""
    async def wrapper(*args, **kwargs):
        # Capture conversation before
        before_context = get_conversation_context()
        before_tokens = estimate_tokens(str(before_context))

        # Execute function
        result = await func(*args, **kwargs)

        # Capture conversation after
        after_context = get_conversation_context()
        after_tokens = estimate_tokens(str(after_context))

        tokens_used = after_tokens - before_tokens

        print(f"{func.__name__} used ~{tokens_used:,} tokens")

        return result

    return wrapper

@measure_context_usage
async def my_workflow(url: str):
    # Implementation
    pass
```

### Technique 1: Use Resource URIs

**Impact**: 98-99% token reduction for large data

```python
# ❌ BAD - 50KB in context
result = await mcp.call("scrape_url", {"url": url})
content = result["content"]  # 50KB flows through context
# Token cost: ~12,500 tokens

# ✅ GOOD - ~200 bytes in context
result = await mcp.call("scrape_url", {"url": url})
content = await mcp.get_resource(result["resource_uri"])  # In exec env
# Token cost: ~50 tokens
# Savings: 99.6%
```

### Technique 2: Progressive Tool Discovery

**Impact**: 90-95% reduction in discovery phase

```python
# ❌ BAD - Load all schemas (100KB)
all_tools = await mcp.call("list_tools", {"detail_level": "full"})
# Token cost: ~25,000 tokens

# ✅ GOOD - Load names only (5KB)
tool_names = await mcp.call("list_tools", {"detail_level": "minimal"})
# Token cost: ~1,250 tokens

# Then load specific schema when needed (2KB)
schema = await mcp.call("search_tools", {
    "query": "scrape_url",
    "detail_level": "full"
})
# Token cost: ~500 tokens
# Total: ~1,750 tokens vs 25,000 tokens
# Savings: 93%
```

### Technique 3: Process Data Locally

**Impact**: Eliminates tokens for intermediate processing

```python
# ❌ BAD - Multiple round trips through context
html = await mcp.call("scrape", {"url": url})  # 25,000 tokens
links = await mcp.call("extract_links", {"html": html})  # 25,000 tokens again
filtered = await mcp.call("filter_links", {"links": links})  # 5,000 tokens
# Total: 55,000 tokens

# ✅ GOOD - Process in execution environment
ref = await mcp.call("scrape", {"url": url})  # 50 tokens
html = await mcp.get_resource(ref["resource_uri"])  # 0 tokens (exec env)
links = extract_links_locally(html)  # 0 tokens (exec env)
filtered = filter_links_locally(links)  # 0 tokens (exec env)
# Total: 50 tokens
# Savings: 99.9%
```

### Technique 4: Batch Reference Returns

**Impact**: Minimize per-item overhead

```python
# ❌ BAD - Return each item separately
results = []
for url in urls:
    result = await mcp.call("scrape", {"url": url})
    results.append(result)
# Each result: ~200 tokens overhead
# 10 URLs: ~2,000 tokens overhead

# ✅ GOOD - Return batch of references
refs = await mcp.call("scrape_batch", {"urls": urls})
# Single response: ~500 tokens total overhead
# Savings: 75%
```

## Execution Time Optimization

### Principle: Maximize Parallelism

Most MCP calls are I/O-bound (network, disk), making them perfect for parallel execution.

### Measurement

```python
import time
import asyncio

def measure_time(func):
    """Decorator to measure execution time"""
    async def wrapper(*args, **kwargs):
        start = time.time()

        result = await func(*args, **kwargs)

        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f}s")

        return result

    return wrapper

@measure_time
async def my_workflow(urls: List[str]):
    # Implementation
    pass
```

### Technique 1: Parallel MCP Calls

**Impact**: 10-100x speedup for independent operations

```python
# ❌ SLOW - Sequential execution (10s for 10 URLs)
results = []
for url in urls:  # 10 URLs
    result = await mcp.call("scrape", {"url": url})  # 1s each
    results.append(result)
# Total: 10 seconds

# ✅ FAST - Parallel execution (1s for 10 URLs)
results = await asyncio.gather(*[
    mcp.call("scrape", {"url": url})
    for url in urls  # 10 URLs
])
# Total: 1 second (all at once)
# Speedup: 10x
```

### Technique 2: Limit Concurrency

**Impact**: Prevent overwhelming servers or hitting rate limits

```python
from asyncio import Semaphore

async def scrape_with_limit(urls: List[str], max_concurrent: int = 5):
    """Limit concurrent requests"""
    semaphore = Semaphore(max_concurrent)

    async def scrape_one(url: str):
        async with semaphore:
            return await mcp.call("scrape", {"url": url})

    results = await asyncio.gather(*[
        scrape_one(url) for url in urls
    ])

    return results

# Process 100 URLs, 5 at a time
# Total time: ~20s (100 URLs / 5 concurrent = 20 batches of 1s each)
# vs 100s sequential
```

### Technique 3: Early Termination

**Impact**: Stop as soon as goal is achieved

```python
# ❌ SLOW - Process all items
async def find_in_all(urls: List[str], pattern: str):
    results = await asyncio.gather(*[
        mcp.call("scrape", {"url": url})
        for url in urls  # Process all 100
    ])

    for result in results:
        content = await mcp.get_resource(result["resource_uri"])
        if pattern in content:
            return result  # Found, but processed everything

# ✅ FAST - Stop when found
async def find_first(urls: List[str], pattern: str):
    for url in urls:
        result = await mcp.call("scrape", {"url": url})
        content = await mcp.get_resource(result["resource_uri"])

        if pattern in content:
            return result  # Stop immediately

    return None

# If pattern is in URL #5, we only process 5 instead of 100
# Speedup: 20x
```

### Technique 4: Caching

**Impact**: Eliminate redundant operations

```python
from functools import lru_cache
import hashlib

# In-memory cache
cache = {}

async def scrape_with_cache(url: str, ttl: int = 3600):
    """Cache scrape results"""
    cache_key = hashlib.md5(url.encode()).hexdigest()

    # Check cache
    if cache_key in cache:
        cached = cache[cache_key]
        age = time.time() - cached["timestamp"]

        if age < ttl:
            print(f"Cache hit: {url}")
            return cached["result"]  # Instant return

    # Cache miss
    print(f"Cache miss: {url}")
    result = await mcp.call("scrape", {"url": url})  # 1s

    # Store in cache
    cache[cache_key] = {
        "result": result,
        "timestamp": time.time()
    }

    return result

# First call: 1s
# Subsequent calls within TTL: 0.001s
# Speedup: 1000x for cached items
```

### Technique 5: Prefetching

**Impact**: Reduce latency by predicting needs

```python
async def prefetch_resources(refs: List[dict]):
    """Fetch resources in parallel before needed"""
    # Start fetching all resources
    fetch_tasks = [
        mcp.get_resource(ref["resource_uri"])
        for ref in refs
    ]

    # Wait for all to complete
    contents = await asyncio.gather(*fetch_tasks)

    # Build lookup
    resource_cache = {
        ref["resource_uri"]: content
        for ref, content in zip(refs, contents)
    }

    return resource_cache

# Usage
refs = await mcp.call("scrape_batch", {"urls": urls})

# Prefetch all resources while doing other work
resource_cache = await prefetch_resources(refs)

# Now all resources are already loaded
for ref in refs:
    content = resource_cache[ref["resource_uri"]]  # Instant access
    process(content)
```

## Memory Optimization

### Principle: Process in Chunks

For very large datasets, process in manageable chunks to avoid memory issues.

### Technique 1: Streaming Processing

```python
async def process_large_file_streaming(file_uri: str):
    """Process file in chunks"""
    # Get metadata
    metadata = await mcp.call("get_metadata", {"uri": file_uri})

    if metadata["size_bytes"] > 100_000_000:  # > 100MB
        # Request chunking
        chunk_info = await mcp.call("chunk_file", {
            "uri": file_uri,
            "chunk_size": 10_000_000  # 10MB chunks
        })

        # Process one chunk at a time
        results = []
        for chunk_id in chunk_info["chunk_ids"]:
            # Load chunk
            chunk = await mcp.get_resource(f"chunk://{chunk_id}")

            # Process chunk
            chunk_result = process_chunk(chunk)
            results.append(chunk_result)

            # chunk goes out of scope, memory freed

        return combine_results(results)
    else:
        # Small enough to process in one go
        data = await mcp.get_resource(file_uri)
        return process_data(data)
```

### Technique 2: Lazy Loading

```python
async def lazy_processing(refs: List[dict]):
    """Load resources only when needed"""
    # Don't load all resources upfront
    # ❌ BAD:
    # contents = [await mcp.get_resource(r["resource_uri"]) for r in refs]
    # # All 100 files in memory at once (10GB!)

    # ✅ GOOD: Load one at a time
    for ref in refs:
        content = await mcp.get_resource(ref["resource_uri"])
        result = process(content)
        await save_result(result)
        # content goes out of scope, memory freed
        # Only one file in memory at a time (100MB)
```

### Technique 3: Explicit Memory Management

```python
import gc

async def process_with_gc(uris: List[str]):
    """Explicitly manage memory"""
    for uri in uris:
        # Load data
        data = await mcp.get_resource(uri)

        # Process
        result = process(data)

        # Save
        await save_result(result)

        # Explicitly delete large objects
        del data
        del result

        # Force garbage collection
        gc.collect()
```

## Network Optimization

### Technique 1: Request Batching

```python
# ❌ SLOW - Individual requests
for url in urls:  # 100 URLs
    await mcp.call("scrape", {"url": url})
# 100 separate network round trips

# ✅ FAST - Batch request
await mcp.call("scrape_batch", {
    "urls": urls  # 100 URLs
})
# 1 network round trip
# Speedup: ~100x (less network overhead)
```

### Technique 2: Connection Pooling

```python
# MCP clients should reuse connections
# This is usually handled by the MCP client library
# Just avoid creating multiple clients:

# ❌ BAD
for url in urls:
    client = create_mcp_client()  # New connection each time
    await client.call("scrape", {"url": url})

# ✅ GOOD
client = create_mcp_client()  # One connection
for url in urls:
    await client.call("scrape", {"url": url})  # Reuse connection
```

### Technique 3: Compression

```python
# Request compressed responses
result = await mcp.call("scrape", {
    "url": url,
    "response_format": "markdown",  # More compact than HTML
    "compress": True  # Enable compression
})

# Markdown is ~50% smaller than HTML
# Compression is ~70% smaller
# Combined: ~85% reduction in network transfer
```

## Algorithm Optimization

### Technique 1: Efficient Data Structures

```python
# ❌ SLOW - List lookup (O(n))
urls_seen = []
for url in all_urls:  # 10,000 URLs
    if url not in urls_seen:  # O(n) lookup
        urls_seen.append(url)
# Time complexity: O(n²) = 100,000,000 operations

# ✅ FAST - Set lookup (O(1))
urls_seen = set()
for url in all_urls:  # 10,000 URLs
    if url not in urls_seen:  # O(1) lookup
        urls_seen.add(url)
# Time complexity: O(n) = 10,000 operations
# Speedup: 10,000x
```

### Technique 2: Avoid Redundant Work

```python
# ❌ SLOW - Recompute every time
def process_urls(urls: List[str]):
    for url in urls:
        # Recompute pattern for each URL
        pattern = compile_complex_regex()  # Expensive
        if pattern.match(url):
            process(url)

# ✅ FAST - Compute once
def process_urls(urls: List[str]):
    # Compile pattern once
    pattern = compile_complex_regex()

    for url in urls:
        if pattern.match(url):
            process(url)
```

### Technique 3: Short-Circuit Evaluation

```python
# ❌ SLOW - Check all conditions
if expensive_check_1() and expensive_check_2() and expensive_check_3():
    do_something()
# All three expensive checks run every time

# ✅ FAST - Order by likelihood of failure
if cheap_check() and expensive_check_1() and expensive_check_2():
    do_something()
# If cheap_check() fails, expensive checks never run
```

## Profiling and Monitoring

### Technique 1: Profile Critical Paths

```python
import cProfile
import pstats

async def profile_workflow(urls: List[str]):
    """Profile to find bottlenecks"""
    profiler = cProfile.Profile()
    profiler.enable()

    # Run workflow
    result = await scraping_pipeline(urls)

    profiler.disable()

    # Print stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 slowest functions

    return result
```

### Technique 2: Instrument with Timing

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    """Context manager for timing blocks"""
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{name} took {elapsed:.2f}s")

async def instrumented_workflow(urls: List[str]):
    with timer("Discovery"):
        tools = await mcp.call("list_tools", {"detail_level": "minimal"})

    with timer("Scraping"):
        refs = await asyncio.gather(*[
            mcp.call("scrape", {"url": url})
            for url in urls
        ])

    with timer("Fetching resources"):
        contents = await asyncio.gather(*[
            mcp.get_resource(ref["resource_uri"])
            for ref in refs
        ])

    with timer("Processing"):
        results = [process(c) for c in contents]

    return results

# Output:
# Discovery took 0.25s
# Scraping took 1.50s
# Fetching resources took 0.80s
# Processing took 2.10s
# Total: 4.65s
```

### Technique 3: Monitor Resource Usage

```python
import psutil
import os

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

async def monitored_workflow(urls: List[str]):
    start_memory = get_memory_usage()
    print(f"Starting memory: {start_memory:.2f} MB")

    # Process URLs
    for i, url in enumerate(urls):
        result = await mcp.call("scrape", {"url": url})
        content = await mcp.get_resource(result["resource_uri"])
        process(content)

        if i % 10 == 0:
            current_memory = get_memory_usage()
            print(f"After {i} URLs: {current_memory:.2f} MB")

    end_memory = get_memory_usage()
    print(f"Final memory: {end_memory:.2f} MB")
    print(f"Memory increase: {end_memory - start_memory:.2f} MB")
```

## Optimization Checklist

### Before Optimization
- [ ] Profile to identify bottlenecks
- [ ] Measure current performance (time, memory, tokens)
- [ ] Set optimization goals (e.g., "reduce tokens by 90%")

### Data/Token Optimization
- [ ] Use resource URIs for data > 1KB
- [ ] Progressive tool discovery (minimal → full)
- [ ] Process data locally, not through context
- [ ] Batch operations where possible
- [ ] Include only essential metadata

### Execution Time Optimization
- [ ] Parallelize independent operations
- [ ] Add caching for repeated operations
- [ ] Use early termination when possible
- [ ] Limit concurrency to avoid rate limits
- [ ] Prefetch resources when predictable

### Memory Optimization
- [ ] Process large files in chunks
- [ ] Use lazy loading (load on demand)
- [ ] Explicit cleanup of large objects
- [ ] Monitor memory usage
- [ ] Set appropriate chunk sizes

### After Optimization
- [ ] Measure improvements
- [ ] Document optimizations
- [ ] Add performance tests
- [ ] Monitor in production

## Case Study: Before and After

### Before Optimization

```python
async def analyze_website_slow(url: str):
    # Load page (25KB in context)
    page = await mcp.call("scrape", {"url": url})

    # Extract links (25KB still in context)
    links = await mcp.call("extract_links", {"html": page["content"]})

    # Scrape each link sequentially
    link_contents = []
    for link in links["links"][:10]:
        content = await mcp.call("scrape", {"url": link})
        link_contents.append(content)

    # Process in context
    analysis = await mcp.call("analyze", {
        "page": page,
        "links": link_contents
    })

    return analysis

# Performance:
# - Tokens: ~350,000
# - Time: 10 seconds (sequential)
# - Memory: 500 MB (all in memory)
```

### After Optimization

```python
async def analyze_website_fast(url: str):
    # Get reference (200 bytes in context)
    page_ref = await mcp.call("scrape", {"url": url})

    # Fetch into exec env
    page_content = await mcp.get_resource(page_ref["resource_uri"])

    # Extract links locally
    links = extract_links_local(page_content)

    # Scrape links in parallel (max 5 concurrent)
    semaphore = asyncio.Semaphore(5)

    async def scrape_with_limit(link):
        async with semaphore:
            return await mcp.call("scrape", {"url": link})

    link_refs = await asyncio.gather(*[
        scrape_with_limit(link)
        for link in links[:10]
    ])

    # Fetch into exec env
    link_contents = await asyncio.gather(*[
        mcp.get_resource(ref["resource_uri"])
        for ref in link_refs
    ])

    # Process locally
    analysis = analyze_local(page_content, link_contents)

    return analysis

# Performance:
# - Tokens: ~2,000 (99.4% reduction)
# - Time: 2 seconds (5x faster)
# - Memory: 50 MB (10x less)
```

## Summary

**Key Optimization Principles**:

1. **Token Optimization**: Use resources, not direct returns
2. **Time Optimization**: Parallelize everything possible
3. **Memory Optimization**: Process in chunks, lazy load
4. **Network Optimization**: Batch requests, reuse connections
5. **Algorithm Optimization**: Use efficient data structures

**Measurement is Key**:
- Always profile before optimizing
- Measure token usage, execution time, and memory
- Set specific goals (e.g., "reduce tokens by 90%")
- Verify improvements after optimization

**Remember**: Premature optimization is the root of all evil. Optimize when you have a clear bottleneck and measurable goal!
