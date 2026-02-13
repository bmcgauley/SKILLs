"""
Parallel Operations and Concurrent Execution

This example demonstrates:
- Parallel MCP calls with asyncio.gather
- Concurrency limiting with Semaphore
- Error handling in parallel execution
- Performance comparison (sequential vs parallel)
- Fan-out/fan-in patterns
- Circuit breaker for failing services

Author: Code Execution Patterns Skill
License: MIT
"""

import asyncio
import time
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Circuit breaker to prevent cascading failures"""
    failure_threshold: int = 5
    timeout: int = 60
    failures: int = 0
    last_failure_time: Optional[float] = None
    state: CircuitState = CircuitState.CLOSED

    def is_open(self) -> bool:
        """Check if circuit is open"""
        if self.state == CircuitState.OPEN:
            # Check if timeout expired
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                return False
            return True
        return False

    def record_success(self):
        """Record successful call"""
        self.failures = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        """Record failed call"""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"⚠ Circuit breaker OPEN (failures: {self.failures})")


# Global circuit breaker
circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)


class MCPClient:
    """Simulated MCP client"""

    def __init__(self, failure_rate: float = 0.1):
        self.failure_rate = failure_rate
        self.call_count = 0

    async def call(self, tool_name: str, params: dict) -> dict:
        """Call an MCP tool (with simulated latency and failures)"""
        self.call_count += 1

        # Simulate network latency
        await asyncio.sleep(random.uniform(0.1, 0.5))

        # Simulate occasional failures
        if random.random() < self.failure_rate:
            raise Exception(f"Network error in {tool_name}")

        # Simulate response
        return {
            "resource_uri": f"resource://{hash(str(params))}",
            "metadata": {
                "size_bytes": random.randint(1000, 50000),
                "url": params.get("url", "unknown")
            }
        }

    async def get_resource(self, uri: str) -> str:
        """Fetch resource (with simulated latency)"""
        await asyncio.sleep(random.uniform(0.05, 0.2))
        return f"Content for {uri}"


# Initialize MCP client
mcp = MCPClient(failure_rate=0.1)


async def scrape_url_sequential(urls: List[str]) -> Dict[str, Any]:
    """
    ❌ SLOW: Sequential execution

    Each URL is scraped one after another.
    Total time = sum of individual times.
    """
    print("\n=== Sequential Execution ===")
    start_time = time.time()

    results = []

    for i, url in enumerate(urls):
        print(f"Scraping {i + 1}/{len(urls)}: {url}")
        try:
            result = await mcp.call("scrape_url", {"url": url})
            results.append(result)
        except Exception as e:
            print(f"✗ Failed: {e}")
            results.append({"error": str(e), "url": url})

    elapsed = time.time() - start_time

    return {
        "results": results,
        "successful": len([r for r in results if "error" not in r]),
        "failed": len([r for r in results if "error" in r]),
        "elapsed_seconds": elapsed,
        "urls_per_second": len(urls) / elapsed if elapsed > 0 else 0
    }


async def scrape_url_parallel(urls: List[str]) -> Dict[str, Any]:
    """
    ✅ FAST: Parallel execution

    All URLs scraped concurrently.
    Total time ≈ max of individual times (not sum).
    """
    print("\n=== Parallel Execution ===")
    start_time = time.time()

    # Create tasks for all URLs
    tasks = [
        mcp.call("scrape_url", {"url": url})
        for url in urls
    ]

    # Execute all in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Separate successes and failures
    successful = []
    failed = []

    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            failed.append({"error": str(result), "url": url})
        else:
            successful.append(result)

    elapsed = time.time() - start_time

    print(f"✓ Successful: {len(successful)}")
    print(f"✗ Failed: {len(failed)}")
    print(f"⏱ Time: {elapsed:.2f}s")

    return {
        "successful": successful,
        "failed": failed,
        "elapsed_seconds": elapsed,
        "urls_per_second": len(urls) / elapsed if elapsed > 0 else 0
    }


async def scrape_url_with_concurrency_limit(urls: List[str], max_concurrent: int = 5) -> Dict[str, Any]:
    """
    ✅ CONTROLLED: Parallel with concurrency limit

    Prevents overwhelming the server with too many concurrent requests.
    Good for respecting rate limits.
    """
    print(f"\n=== Parallel with Concurrency Limit ({max_concurrent}) ===")
    start_time = time.time()

    # Semaphore limits concurrent operations
    semaphore = asyncio.Semaphore(max_concurrent)

    async def scrape_with_limit(url: str) -> dict:
        async with semaphore:
            print(f"  Scraping: {url}")
            return await mcp.call("scrape_url", {"url": url})

    # Create tasks
    tasks = [scrape_with_limit(url) for url in urls]

    # Execute with limit
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    successful = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    elapsed = time.time() - start_time

    print(f"✓ Successful: {len(successful)}")
    print(f"✗ Failed: {len(failed)}")
    print(f"⏱ Time: {elapsed:.2f}s")

    return {
        "successful": successful,
        "failed": failed,
        "elapsed_seconds": elapsed,
        "urls_per_second": len(urls) / elapsed if elapsed > 0 else 0
    }


async def scrape_with_retry(url: str, max_retries: int = 3) -> dict:
    """
    Retry failed operations with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            result = await mcp.call("scrape_url", {"url": url})
            return result

        except Exception as e:
            if attempt == max_retries - 1:
                # Final attempt failed
                return {"error": str(e), "url": url, "attempts": max_retries}

            # Exponential backoff
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)

    return {"error": "max_retries_exceeded"}


async def scrape_url_parallel_with_retry(urls: List[str]) -> Dict[str, Any]:
    """
    ✅ RESILIENT: Parallel execution with automatic retries
    """
    print("\n=== Parallel with Retry ===")
    start_time = time.time()

    # Create tasks with retry logic
    tasks = [scrape_with_retry(url, max_retries=3) for url in urls]

    # Execute in parallel
    results = await asyncio.gather(*tasks)

    # Process results
    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]

    elapsed = time.time() - start_time

    print(f"✓ Successful: {len(successful)}")
    print(f"✗ Failed: {len(failed)}")
    print(f"⏱ Time: {elapsed:.2f}s")

    return {
        "successful": successful,
        "failed": failed,
        "elapsed_seconds": elapsed
    }


async def scrape_with_circuit_breaker(url: str) -> dict:
    """
    Scrape with circuit breaker pattern
    """
    if circuit_breaker.is_open():
        return {
            "error": "circuit_breaker_open",
            "message": "Service temporarily unavailable",
            "url": url
        }

    try:
        result = await mcp.call("scrape_url", {"url": url})
        circuit_breaker.record_success()
        return result

    except Exception as e:
        circuit_breaker.record_failure()
        return {"error": str(e), "url": url}


async def scrape_with_timeout(url: str, timeout_seconds: int = 5) -> dict:
    """
    Scrape with timeout
    """
    try:
        result = await asyncio.wait_for(
            mcp.call("scrape_url", {"url": url}),
            timeout=timeout_seconds
        )
        return result

    except asyncio.TimeoutError:
        return {
            "error": "timeout",
            "message": f"Operation timed out after {timeout_seconds}s",
            "url": url
        }


async def fan_out_fan_in_pattern(urls: List[str]) -> Dict[str, Any]:
    """
    Fan-out/fan-in pattern:
    1. Fan out: Scrape all URLs in parallel
    2. Process: Fetch and process content
    3. Fan in: Aggregate results
    """
    print("\n=== Fan-out/Fan-in Pattern ===")

    # Phase 1: Fan out - scrape all URLs in parallel
    print("Phase 1: Fanning out (scraping URLs)...")
    scrape_tasks = [
        mcp.call("scrape_url", {"url": url})
        for url in urls
    ]
    refs = await asyncio.gather(*scrape_tasks, return_exceptions=True)

    # Filter successful scrapes
    successful_refs = [r for r in refs if not isinstance(r, Exception)]
    print(f"  Scraped {len(successful_refs)}/{len(urls)} URLs")

    # Phase 2: Process - fetch resources in parallel
    print("Phase 2: Processing (fetching resources)...")
    fetch_tasks = [
        mcp.get_resource(ref["resource_uri"])
        for ref in successful_refs
    ]
    contents = await asyncio.gather(*fetch_tasks)

    # Process each content
    processed = [
        process_content(content)
        for content in contents
    ]
    print(f"  Processed {len(processed)} resources")

    # Phase 3: Fan in - aggregate results
    print("Phase 3: Fanning in (aggregating)...")
    aggregated = aggregate_results(processed)

    return {
        "urls_scraped": len(successful_refs),
        "urls_failed": len(urls) - len(successful_refs),
        "total_words": aggregated["total_words"],
        "total_chars": aggregated["total_chars"],
        "average_words": aggregated["total_words"] / len(processed) if processed else 0
    }


def process_content(content: str) -> Dict[str, Any]:
    """Process content (local processing)"""
    return {
        "words": len(content.split()),
        "chars": len(content),
        "lines": len(content.split('\n'))
    }


def aggregate_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate results (local processing)"""
    return {
        "total_words": sum(r["words"] for r in results),
        "total_chars": sum(r["chars"] for r in results),
        "total_lines": sum(r["lines"] for r in results)
    }


async def compare_sequential_vs_parallel(urls: List[str]):
    """
    Compare performance: sequential vs parallel
    """
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)

    # Sequential
    seq_result = await scrape_url_sequential(urls)
    seq_time = seq_result["elapsed_seconds"]
    seq_rate = seq_result["urls_per_second"]

    # Parallel
    par_result = await scrape_url_parallel(urls)
    par_time = par_result["elapsed_seconds"]
    par_rate = par_result["urls_per_second"]

    # Calculate speedup
    speedup = seq_time / par_time if par_time > 0 else 0

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Sequential: {seq_time:.2f}s ({seq_rate:.2f} URLs/s)")
    print(f"Parallel:   {par_time:.2f}s ({par_rate:.2f} URLs/s)")
    print(f"Speedup:    {speedup:.2f}x")
    print("=" * 60)


async def batched_parallel_processing(urls: List[str], batch_size: int = 10):
    """
    Process URLs in batches

    Useful when you have many URLs but want to control memory usage
    """
    print(f"\n=== Batched Processing ({batch_size} per batch) ===")

    all_results = []

    # Process in batches
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(urls) + batch_size - 1) // batch_size

        print(f"\nBatch {batch_num}/{total_batches} ({len(batch)} URLs)")

        # Process batch in parallel
        batch_results = await scrape_url_parallel(batch)
        all_results.extend(batch_results["successful"])

        print(f"  Batch complete: {len(batch_results['successful'])} successful")

    print(f"\nTotal processed: {len(all_results)} URLs")

    return {
        "total_processed": len(all_results),
        "total_urls": len(urls),
        "batches": (len(urls) + batch_size - 1) // batch_size
    }


async def main():
    """
    Main entry point demonstrating parallel execution patterns
    """
    print("\n" + "=" * 60)
    print("PARALLEL OPERATIONS EXAMPLES")
    print("=" * 60)

    # Generate test URLs
    urls = [f"https://example.com/page{i}" for i in range(20)]

    # Example 1: Sequential vs Parallel comparison
    print("\n--- Example 1: Sequential vs Parallel ---")
    await compare_sequential_vs_parallel(urls[:10])

    # Example 2: Concurrency limiting
    print("\n--- Example 2: Concurrency Limiting ---")
    await scrape_url_with_concurrency_limit(urls, max_concurrent=5)

    # Example 3: Parallel with retry
    print("\n--- Example 3: Parallel with Retry ---")
    await scrape_url_parallel_with_retry(urls[:10])

    # Example 4: Fan-out/fan-in pattern
    print("\n--- Example 4: Fan-out/Fan-in Pattern ---")
    result = await fan_out_fan_in_pattern(urls[:10])
    print(f"Total words: {result['total_words']}")

    # Example 5: Batched processing
    print("\n--- Example 5: Batched Processing ---")
    await batched_parallel_processing(urls, batch_size=5)

    print("\n" + "=" * 60)
    print("KEY PATTERNS DEMONSTRATED:")
    print("=" * 60)
    print("1. Parallel execution with asyncio.gather")
    print("2. Concurrency limiting with Semaphore")
    print("3. Error handling in parallel operations")
    print("4. Retry logic with exponential backoff")
    print("5. Circuit breaker pattern")
    print("6. Timeout handling")
    print("7. Fan-out/fan-in pattern")
    print("8. Batched parallel processing")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("PERFORMANCE TIPS:")
    print("=" * 60)
    print("- Use parallel execution for I/O-bound operations")
    print("- Limit concurrency to respect rate limits")
    print("- Add retries for transient failures")
    print("- Use timeouts to prevent hanging")
    print("- Circuit breakers prevent cascading failures")
    print("- Batch processing controls memory usage")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
