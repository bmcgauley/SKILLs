# Error Handling and Resilience Patterns

**Last Updated**: 2025-11-09

## Overview

Agent code that calls MCP tools must handle errors gracefully. Network failures, rate limits, invalid inputs, and unexpected responses are common. This guide provides patterns for building resilient agent code.

## Types of Errors

### 1. Network Errors

- Connection timeouts
- DNS resolution failures
- Network unreachable
- Connection refused

### 2. MCP Tool Errors

- Tool not found
- Invalid parameters
- Rate limiting
- Tool-specific business logic errors

### 3. Resource Errors

- Resource not found (expired or never existed)
- Resource access denied
- Resource too large

### 4. Data Errors

- Malformed responses
- Unexpected data types
- Missing required fields
- Data validation failures

### 5. Execution Errors

- Out of memory
- Timeout exceeded
- Infinite loops
- Stack overflow

## Basic Error Handling

### Try-Except Pattern

```python
async def basic_error_handling(url: str):
    try:
        result = await mcp.call("webscrape_scrape_url", {
            "url": url,
            "response_format": "markdown"
        })

        # Check for errors in response
        if "error" in result:
            raise Exception(result["error"])

        return result

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {
            "error": str(e),
            "url": url,
            "success": False
        }
```

### Specific Exception Handling

```python
async def specific_error_handling(url: str):
    try:
        result = await mcp.call("webscrape_scrape_url", {"url": url})
        return result

    except ConnectionError as e:
        # Network issues
        print(f"Network error: {e}")
        return {"error": "network_error", "retryable": True}

    except ValueError as e:
        # Invalid data
        print(f"Data error: {e}")
        return {"error": "data_error", "retryable": False}

    except TimeoutError as e:
        # Timeout
        print(f"Timeout: {e}")
        return {"error": "timeout", "retryable": True}

    except Exception as e:
        # Catch-all
        print(f"Unexpected error: {e}")
        return {"error": "unknown", "retryable": False}
```

## Retry Patterns

### Pattern 1: Simple Retry

```python
async def simple_retry(url: str, max_attempts: int = 3):
    for attempt in range(max_attempts):
        try:
            result = await mcp.call("webscrape_scrape_url", {"url": url})

            if "error" not in result:
                return result  # Success

        except Exception as e:
            if attempt == max_attempts - 1:
                # Final attempt failed
                raise

        # Wait before retry
        await asyncio.sleep(1)

    return None
```

### Pattern 2: Exponential Backoff

```python
async def exponential_backoff_retry(url: str, max_attempts: int = 5):
    for attempt in range(max_attempts):
        try:
            result = await mcp.call("webscrape_scrape_url", {"url": url})

            if "error" not in result:
                print(f"Success on attempt {attempt + 1}")
                return result

        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"Failed after {max_attempts} attempts")
                return {
                    "error": str(e),
                    "attempts": max_attempts,
                    "failed": True
                }

            # Exponential backoff: 1s, 2s, 4s, 8s, 16s
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

    return None
```

### Pattern 3: Retry with Jitter

```python
import random

async def retry_with_jitter(url: str, max_attempts: int = 5):
    """Adds randomness to prevent thundering herd problem"""
    for attempt in range(max_attempts):
        try:
            result = await mcp.call("webscrape_scrape_url", {"url": url})

            if "error" not in result:
                return result

        except Exception as e:
            if attempt == max_attempts - 1:
                return {"error": str(e), "failed": True}

            # Exponential backoff with jitter
            base_wait = 2 ** attempt
            jitter = random.uniform(0, base_wait * 0.3)
            wait_time = base_wait + jitter

            print(f"Retry in {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)

    return None
```

### Pattern 4: Conditional Retry

```python
def is_retryable(error: Exception) -> bool:
    """Determine if error is worth retrying"""
    retryable_errors = [
        ConnectionError,
        TimeoutError,
        "rate_limit",
        "server_error",
        "503",  # Service unavailable
        "429",  # Too many requests
    ]

    error_str = str(error).lower()
    return any(
        isinstance(error, err) if isinstance(err, type) else err in error_str
        for err in retryable_errors
    )

async def conditional_retry(url: str, max_attempts: int = 3):
    for attempt in range(max_attempts):
        try:
            result = await mcp.call("webscrape_scrape_url", {"url": url})

            if "error" not in result:
                return result

            # Check if error is retryable
            if not is_retryable(Exception(result["error"])):
                print("Non-retryable error, giving up")
                return result

        except Exception as e:
            if not is_retryable(e):
                print(f"Non-retryable error: {e}")
                return {"error": str(e), "retryable": False}

            if attempt == max_attempts - 1:
                return {"error": str(e), "attempts": max_attempts}

        await asyncio.sleep(2 ** attempt)

    return None
```

## Timeout Patterns

### Pattern 1: Simple Timeout

```python
import asyncio

async def with_timeout(url: str, timeout_seconds: int = 10):
    try:
        result = await asyncio.wait_for(
            mcp.call("webscrape_scrape_url", {"url": url}),
            timeout=timeout_seconds
        )
        return result

    except asyncio.TimeoutError:
        print(f"Operation timed out after {timeout_seconds}s")
        return {
            "error": "timeout",
            "timeout_seconds": timeout_seconds
        }
```

### Pattern 2: Timeout with Fallback

```python
async def timeout_with_fallback(url: str):
    try:
        # Try with short timeout first (fast path)
        result = await asyncio.wait_for(
            mcp.call("webscrape_scrape_url", {"url": url}),
            timeout=5
        )
        return result

    except asyncio.TimeoutError:
        print("Fast path timed out, trying slower method...")

        try:
            # Fall back to longer timeout
            result = await asyncio.wait_for(
                mcp.call("webscrape_scrape_with_js", {"url": url}),
                timeout=30
            )
            return result

        except asyncio.TimeoutError:
            return {
                "error": "timeout",
                "tried": ["scrape_url", "scrape_with_js"]
            }
```

### Pattern 3: Per-Operation Timeout

```python
async def multi_operation_timeout(urls: List[str]):
    """Each operation gets its own timeout"""
    async def fetch_with_timeout(url: str):
        try:
            return await asyncio.wait_for(
                mcp.call("webscrape_scrape_url", {"url": url}),
                timeout=10  # Per-URL timeout
            )
        except asyncio.TimeoutError:
            return {"error": "timeout", "url": url}

    # Overall timeout for entire batch
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*[fetch_with_timeout(url) for url in urls]),
            timeout=60  # Total timeout
        )
        return results

    except asyncio.TimeoutError:
        return {"error": "batch_timeout", "url_count": len(urls)}
```

## Fallback Patterns

### Pattern 1: Simple Fallback

```python
async def with_fallback(url: str):
    # Try primary method
    try:
        result = await mcp.call("webscrape_scrape_url", {"url": url})
        if "error" not in result:
            return result
    except Exception as e:
        print(f"Primary method failed: {e}")

    # Fall back to secondary method
    try:
        result = await mcp.call("webscrape_scrape_with_js", {"url": url})
        return result
    except Exception as e:
        print(f"Fallback also failed: {e}")
        return {"error": "all_methods_failed"}
```

### Pattern 2: Cascading Fallbacks

```python
async def cascading_fallbacks(url: str):
    """Try multiple methods in order of preference"""
    methods = [
        ("webscrape_scrape_url", {"url": url}),
        ("webscrape_scrape_with_js", {"url": url, "wait_seconds": 2}),
        ("webscrape_screenshot_url", {"url": url, "full_page": True}),
    ]

    errors = []

    for method_name, params in methods:
        try:
            print(f"Trying {method_name}...")
            result = await mcp.call(method_name, params)

            if "error" not in result:
                print(f"Success with {method_name}")
                return result

            errors.append({"method": method_name, "error": result["error"]})

        except Exception as e:
            errors.append({"method": method_name, "error": str(e)})
            continue

    # All methods failed
    return {
        "error": "all_methods_failed",
        "tried": errors
    }
```

### Pattern 3: Conditional Fallback

```python
async def conditional_fallback(url: str, require_js: bool = None):
    """Choose fallback based on conditions"""

    # Try primary method
    result = await mcp.call("webscrape_scrape_url", {"url": url})

    # Check if we need to fall back
    if "error" in result:
        # Network error - retry same method
        if "network" in result["error"]:
            await asyncio.sleep(2)
            return await mcp.call("webscrape_scrape_url", {"url": url})

        # Content issue - try JS rendering
        if "empty" in result["error"] or "dynamic" in result["error"]:
            return await mcp.call("webscrape_scrape_with_js", {"url": url})

    # Check if content suggests JS needed
    if result.get("metadata", {}).get("size_bytes", 0) < 100:
        print("Content too small, likely needs JS rendering")
        return await mcp.call("webscrape_scrape_with_js", {"url": url})

    return result
```

## Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Prevents repeated calls to failing service"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def is_open(self) -> bool:
        if self.state == "open":
            # Check if timeout expired
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                return False
            return True
        return False

    def record_success(self):
        self.failures = 0
        self.state = "closed"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = "open"

# Usage
breaker = CircuitBreaker(failure_threshold=3, timeout=30)

async def with_circuit_breaker(url: str):
    if breaker.is_open():
        return {
            "error": "circuit_breaker_open",
            "message": "Service is currently unavailable"
        }

    try:
        result = await mcp.call("webscrape_scrape_url", {"url": url})

        if "error" in result:
            breaker.record_failure()
            return result

        breaker.record_success()
        return result

    except Exception as e:
        breaker.record_failure()
        return {"error": str(e)}
```

## Validation and Defensive Programming

### Input Validation

```python
def validate_url(url: str) -> bool:
    """Validate URL before making request"""
    if not url:
        raise ValueError("URL cannot be empty")

    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    if len(url) > 2048:
        raise ValueError("URL too long (max 2048 characters)")

    return True

async def safe_scrape(url: str):
    try:
        # Validate input
        validate_url(url)

        # Make request
        result = await mcp.call("webscrape_scrape_url", {"url": url})

        # Validate output
        if not isinstance(result, dict):
            raise ValueError("Expected dict response")

        if "resource_uri" not in result and "error" not in result:
            raise ValueError("Missing required fields in response")

        return result

    except ValueError as e:
        return {"error": "validation_error", "message": str(e)}
```

### Response Validation

```python
async def validate_response(result: dict) -> dict:
    """Validate MCP tool response"""
    required_fields = ["resource_uri", "metadata"]

    # Check structure
    if not isinstance(result, dict):
        raise ValueError("Response must be a dictionary")

    # Check for error
    if "error" in result:
        return result

    # Check required fields
    missing = [f for f in required_fields if f not in result]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # Validate metadata
    metadata = result.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary")

    if metadata.get("size_bytes", 0) < 0:
        raise ValueError("Invalid size_bytes")

    return result

# Usage
async def scrape_with_validation(url: str):
    result = await mcp.call("webscrape_scrape_url", {"url": url})

    try:
        validated = await validate_response(result)
        return validated
    except ValueError as e:
        return {"error": "validation_failed", "message": str(e)}
```

## Partial Failure Handling

### Pattern: Batch Processing with Failures

```python
async def process_batch_with_failures(urls: List[str]):
    """Process batch, collecting successes and failures"""
    tasks = [
        mcp.call("webscrape_scrape_url", {"url": url})
        for url in urls
    ]

    # Gather with exceptions
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful = []
    failed = []

    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            failed.append({
                "url": url,
                "error": str(result)
            })
        elif "error" in result:
            failed.append({
                "url": url,
                "error": result["error"]
            })
        else:
            successful.append({
                "url": url,
                "result": result
            })

    return {
        "successful": successful,
        "failed": failed,
        "success_rate": len(successful) / len(urls)
    }
```

### Pattern: Retry Failed Items

```python
async def retry_failed_items(urls: List[str]):
    """Process batch, retry failures"""

    # First attempt
    results = await process_batch_with_failures(urls)

    if not results["failed"]:
        return results  # All succeeded

    # Retry failed items
    print(f"Retrying {len(results['failed'])} failed items...")
    failed_urls = [item["url"] for item in results["failed"]]

    retry_results = await process_batch_with_failures(failed_urls)

    # Combine results
    return {
        "successful": results["successful"] + retry_results["successful"],
        "failed": retry_results["failed"],  # Only final failures
        "retried": len(failed_urls)
    }
```

## Logging and Debugging

### Structured Error Logging

```python
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_with_logging(url: str):
    try:
        logger.info(f"Starting scrape: {url}")

        result = await mcp.call("webscrape_scrape_url", {"url": url})

        if "error" in result:
            logger.error(f"Scrape failed: {url}, error: {result['error']}")
            return result

        logger.info(f"Scrape succeeded: {url}, size: {result['metadata']['size_bytes']}")
        return result

    except Exception as e:
        logger.error(
            f"Exception scraping {url}: {e}",
            exc_info=True,  # Include traceback
            extra={
                "url": url,
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )
        return {"error": str(e)}
```

## Best Practices

### 1. Always Handle Errors

```python
# ❌ BAD - No error handling
result = await mcp.call("tool", params)

# ✅ GOOD - Handle errors
try:
    result = await mcp.call("tool", params)
    if "error" in result:
        handle_error(result["error"])
except Exception as e:
    handle_exception(e)
```

### 2. Use Exponential Backoff for Retries

```python
# ❌ BAD - Constant retry delay
for i in range(5):
    try:
        result = await mcp.call("tool", params)
        break
    except:
        await asyncio.sleep(1)  # Always 1s

# ✅ GOOD - Exponential backoff
for i in range(5):
    try:
        result = await mcp.call("tool", params)
        break
    except:
        await asyncio.sleep(2 ** i)  # 1s, 2s, 4s, 8s, 16s
```

### 3. Fail Fast on Non-Retryable Errors

```python
# Don't waste time retrying non-retryable errors
if "invalid_parameter" in error:
    return {"error": error}  # Don't retry

if "rate_limit" in error:
    await asyncio.sleep(60)  # Wait and retry
    return await retry()
```

### 4. Provide Useful Error Messages

```python
# ❌ BAD
return {"error": "failed"}

# ✅ GOOD
return {
    "error": "scrape_failed",
    "message": "Failed to scrape URL after 3 attempts",
    "url": url,
    "attempts": 3,
    "last_error": "Connection timeout",
    "retryable": True
}
```

### 5. Clean Up Resources on Error

```python
async def cleanup_on_error(data_uri: str):
    try:
        data = await mcp.get_resource(data_uri)
        result = await process(data)
        return result

    except Exception as e:
        # Clean up resource even on error
        await mcp.call("delete_resource", {"uri": data_uri})
        raise
```

## Summary

**Key Principles**:

1. **Always handle errors** - Never assume success
2. **Retry with backoff** - Exponential backoff with jitter
3. **Fail fast** - Don't retry non-retryable errors
4. **Validate inputs and outputs** - Defensive programming
5. **Log everything** - Structured logging for debugging
6. **Provide fallbacks** - Multiple methods to accomplish goals
7. **Handle partial failures** - Batch processing with error collection

**Remember**: Errors are not exceptional—they're expected. Design for resilience from the start!
