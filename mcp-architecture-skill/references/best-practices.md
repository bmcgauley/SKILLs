# MCP Architecture Best Practices

**Last Updated**: 2025-11-09

## Overview

This guide covers performance optimization, security considerations, reliability patterns, and operational best practices for production MCP deployments.

## Performance Optimization

### 1. Token Usage Optimization

#### Minimize Context Overhead

```python
# ❌ Bad: Large responses
@mcp.tool("get_data")
async def get_data(id: str):
    data = fetch_large_data(id)  # 50KB
    return json.dumps({"data": data})  # All in context!

# ✅ Good: Resource-based responses
@mcp.tool("get_data")
async def get_data(id: str):
    data = fetch_large_data(id)  # 50KB
    resource_id = store_resource(data)
    return json.dumps({
        "resource_id": resource_id,
        "resource_uri": f"myapp://{resource_id}/data",
        "preview": data[:500],  # Small preview only
        "size_bytes": len(data)
    })  # ~1KB in context
```

**Impact**: 98% reduction in context size for large data

#### Progressive Detail Loading

```python
# ❌ Bad: Always return full schemas
@mcp.tool("list_tools")
async def list_tools():
    return all_tools_with_full_schemas()  # 150KB

# ✅ Good: Configurable detail levels
@mcp.tool("list_tools")
async def list_tools(detail_level: str = "minimal"):
    if detail_level == "minimal":
        return tool_names_only()  # 2KB
    elif detail_level == "brief":
        return tools_with_descriptions()  # 10KB
    else:
        return tools_with_full_schemas()  # 150KB
```

**Impact**: 90%+ reduction in discovery overhead

### 2. Caching Strategies

#### Tool Discovery Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class ToolRegistry:
    def __init__(self):
        self._cache = None
        self._cache_time = None
        self._cache_ttl = timedelta(minutes=5)

    def get_tools(self):
        """Get tools with caching."""
        now = datetime.utcnow()

        if (self._cache is None or
            self._cache_time is None or
            now - self._cache_time > self._cache_ttl):

            self._cache = self._build_tool_registry()
            self._cache_time = now

        return self._cache

    @lru_cache(maxsize=100)
    def search_tools(self, query: str):
        """Cache search results."""
        tools = self.get_tools()
        return [t for t in tools if query.lower() in t['name'].lower()]
```

#### Resource Caching

```python
import redis

class CachedResourceStore:
    def __init__(self):
        self.redis = redis.Redis()
        self.local_cache = {}

    async def get(self, key: str):
        """Two-level cache: local + Redis."""
        # Check local cache first (fastest)
        if key in self.local_cache:
            return self.local_cache[key]

        # Check Redis (fast)
        data = self.redis.get(key)
        if data:
            self.local_cache[key] = data
            return data

        # Not found
        return None

    async def set(self, key: str, data: any, ttl: int = 3600):
        """Store in both caches."""
        self.local_cache[key] = data
        self.redis.setex(key, ttl, data)
```

### 3. Parallel Operations

#### Concurrent Resource Creation

```python
import asyncio

async def batch_scrape_urls(urls: list):
    """Scrape multiple URLs in parallel."""
    # ❌ Bad: Sequential
    # results = []
    # for url in urls:
    #     result = await scrape_url(url)
    #     results.append(result)

    # ✅ Good: Parallel
    tasks = [scrape_url(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [r for r in results if not isinstance(r, Exception)]
```

#### Rate Limiting with Concurrency

```python
from asyncio import Semaphore

class RateLimitedScraper:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = Semaphore(max_concurrent)

    async def scrape_url(self, url: str):
        """Scrape with concurrency limit."""
        async with self.semaphore:
            return await self._do_scrape(url)

    async def batch_scrape(self, urls: list):
        """Scrape multiple URLs with rate limiting."""
        tasks = [self.scrape_url(url) for url in urls]
        return await asyncio.gather(*tasks)
```

### 4. Memory Management

#### Resource Cleanup

```python
from datetime import datetime, timedelta
import asyncio

class ResourceManager:
    def __init__(self):
        self.resources = {}
        self.cleanup_interval = 300  # 5 minutes

        # Start cleanup task
        asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Periodically clean up expired resources."""
        while True:
            await asyncio.sleep(self.cleanup_interval)
            await self._cleanup_expired()

    async def _cleanup_expired(self):
        """Remove expired resources."""
        now = datetime.utcnow()
        expired = [
            rid for rid, r in self.resources.items()
            if now > r.get('expires_at', now)
        ]

        for rid in expired:
            del self.resources[rid]

        if expired:
            print(f"Cleaned up {len(expired)} expired resources")
```

#### Size-Based Eviction

```python
from collections import OrderedDict

class SizeLimitedStore:
    def __init__(self, max_size_mb: int = 100):
        self.store = OrderedDict()
        self.max_bytes = max_size_mb * 1024 * 1024
        self.current_bytes = 0

    def set(self, key: str, data: bytes):
        """Store with size-based eviction."""
        data_size = len(data)

        # Evict oldest until there's space
        while self.current_bytes + data_size > self.max_bytes:
            if not self.store:
                raise ValueError("Data too large for store")

            oldest_key, oldest_data = self.store.popitem(last=False)
            self.current_bytes -= len(oldest_data)

        self.store[key] = data
        self.current_bytes += data_size

        return {
            "stored": True,
            "size_bytes": data_size,
            "store_usage_percent": (self.current_bytes / self.max_bytes) * 100
        }
```

## Security Best Practices

### 1. Input Validation

```python
from urllib.parse import urlparse
import re

def validate_url(url: str) -> tuple[bool, str]:
    """Validate URL input."""
    # Check format
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL format: {e}"

    # Check scheme
    if parsed.scheme not in ['http', 'https']:
        return False, "Only HTTP/HTTPS URLs allowed"

    # Check for localhost/private IPs (SSRF prevention)
    hostname = parsed.hostname
    if hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
        return False, "Local URLs not allowed"

    # Check for private IP ranges
    if re.match(r'^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)', hostname):
        return False, "Private IP ranges not allowed"

    return True, ""

@mcp.tool("scrape_url")
async def scrape_url(url: str):
    """Scrape with validation."""
    valid, error = validate_url(url)
    if not valid:
        return json.dumps({"error": error})

    # Proceed with scraping
    return await _do_scrape(url)
```

### 2. Resource Access Control

```python
import hmac
import hashlib
from datetime import datetime, timedelta

class SecureResourceStore:
    def __init__(self, secret_key: str):
        self.secret = secret_key.encode()
        self.resources = {}

    def create_resource(self, data: any, owner_id: str):
        """Create resource with signed token."""
        resource_id = uuid.uuid4().hex
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Create signed token
        message = f"{resource_id}:{owner_id}:{expires_at.isoformat()}"
        signature = hmac.new(
            self.secret,
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        token = f"{resource_id}:{signature}"

        # Store resource
        self.resources[resource_id] = {
            "data": data,
            "owner_id": owner_id,
            "expires_at": expires_at
        }

        return {
            "resource_id": resource_id,
            "access_token": token,
            "expires_at": expires_at.isoformat()
        }

    def get_resource(self, resource_id: str, token: str, requester_id: str):
        """Get resource with token verification."""
        if resource_id not in self.resources:
            raise ValueError("Resource not found")

        resource = self.resources[resource_id]

        # Verify token
        expected_message = f"{resource_id}:{resource['owner_id']}:{resource['expires_at'].isoformat()}"
        expected_sig = hmac.new(
            self.secret,
            expected_message.encode(),
            hashlib.sha256
        ).hexdigest()

        provided_rid, provided_sig = token.split(':', 1)

        if provided_rid != resource_id or provided_sig != expected_sig:
            raise ValueError("Invalid access token")

        # Check expiration
        if datetime.utcnow() > resource['expires_at']:
            del self.resources[resource_id]
            raise ValueError("Resource expired")

        # Check ownership (optional)
        if resource['owner_id'] != requester_id:
            raise ValueError("Access denied")

        return resource['data']
```

### 3. Rate Limiting

```python
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self.window = timedelta(minutes=1)
        self.requests = defaultdict(list)

    async def check_limit(self, identifier: str) -> tuple[bool, dict]:
        """Check if request is within rate limit."""
        now = datetime.utcnow()
        cutoff = now - self.window

        # Clean old requests
        self.requests[identifier] = [
            t for t in self.requests[identifier]
            if t > cutoff
        ]

        # Check limit
        current_count = len(self.requests[identifier])

        if current_count >= self.limit:
            return False, {
                "error": "Rate limit exceeded",
                "limit": self.limit,
                "window_seconds": int(self.window.total_seconds()),
                "retry_after_seconds": int(
                    (self.requests[identifier][0] + self.window - now).total_seconds()
                )
            }

        # Record request
        self.requests[identifier].append(now)

        return True, {
            "allowed": True,
            "remaining": self.limit - current_count - 1,
            "reset_at": (cutoff + self.window).isoformat()
        }

# Usage
rate_limiter = RateLimiter(requests_per_minute=10)

@mcp.tool("scrape_url")
async def scrape_url(url: str, user_id: str):
    """Scrape with rate limiting."""
    allowed, info = await rate_limiter.check_limit(user_id)

    if not allowed:
        return json.dumps(info)

    # Proceed with scraping
    return await _do_scrape(url)
```

### 4. Sanitization

```python
import bleach
from html import escape

def sanitize_html(html: str, allowed_tags: list = None) -> str:
    """Sanitize HTML content."""
    if allowed_tags is None:
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'code', 'pre'
        ]

    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt']
    }

    return bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )

def sanitize_text(text: str) -> str:
    """Escape special characters in text."""
    return escape(text)
```

## Reliability Patterns

### 1. Error Handling

```python
from enum import Enum

class ErrorCode(Enum):
    INVALID_INPUT = "INVALID_INPUT"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    NETWORK_ERROR = "NETWORK_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class MCPError(Exception):
    """Base MCP error."""
    def __init__(self, code: ErrorCode, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self):
        """Convert to JSON-serializable dict."""
        return {
            "error": self.message,
            "error_code": self.code.value,
            "details": self.details,
            "suggestions": self._get_suggestions()
        }

    def _get_suggestions(self) -> list:
        """Get helpful suggestions based on error type."""
        suggestions = {
            ErrorCode.INVALID_INPUT: [
                "Check that all required parameters are provided",
                "Verify parameter types match the schema"
            ],
            ErrorCode.RESOURCE_NOT_FOUND: [
                "Verify the resource ID is correct",
                "Check if the resource has expired"
            ],
            ErrorCode.NETWORK_ERROR: [
                "Verify the URL is accessible",
                "Check your network connection",
                "Try again later"
            ],
            ErrorCode.RATE_LIMIT: [
                "Wait before making more requests",
                "Consider reducing request frequency"
            ]
        }
        return suggestions.get(self.code, [])

@mcp.tool("scrape_url")
async def scrape_url(url: str):
    """Scrape with comprehensive error handling."""
    try:
        # Validate input
        valid, error = validate_url(url)
        if not valid:
            raise MCPError(
                ErrorCode.INVALID_INPUT,
                error,
                {"url": url}
            )

        # Attempt scraping
        result = await _do_scrape(url)
        return json.dumps(result)

    except MCPError as e:
        return json.dumps(e.to_dict())

    except aiohttp.ClientError as e:
        error = MCPError(
            ErrorCode.NETWORK_ERROR,
            f"Failed to fetch URL: {str(e)}",
            {"url": url}
        )
        return json.dumps(error.to_dict())

    except Exception as e:
        error = MCPError(
            ErrorCode.INTERNAL_ERROR,
            "An unexpected error occurred",
            {"error_type": type(e).__name__}
        )
        return json.dumps(error.to_dict())
```

### 2. Retry Logic

```python
import asyncio
from functools import wraps

def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retry logic with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise

                    # Log retry
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")

                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)

        return wrapper
    return decorator

# Usage
@retry_with_backoff(
    max_attempts=3,
    exceptions=(aiohttp.ClientError, asyncio.TimeoutError)
)
async def fetch_url(url: str):
    """Fetch with automatic retries."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=30) as response:
            return await response.text()
```

### 3. Circuit Breaker

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Too many failures, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: timedelta = timedelta(minutes=1),
        expected_exceptions: tuple = (Exception,)
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exceptions = expected_exceptions

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker."""
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if datetime.utcnow() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)

            # Success - reset if half-open
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0

            return result

        except self.expected_exceptions as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise

# Usage
scraping_circuit = CircuitBreaker(
    failure_threshold=5,
    timeout=timedelta(minutes=2),
    expected_exceptions=(aiohttp.ClientError,)
)

@mcp.tool("scrape_url")
async def scrape_url(url: str):
    """Scrape with circuit breaker."""
    try:
        return await scraping_circuit.call(_do_scrape, url)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "circuit_state": scraping_circuit.state.value
        })
```

## Monitoring and Observability

### 1. Metrics Collection

```python
from collections import Counter, defaultdict
from datetime import datetime
import time

class MetricsCollector:
    def __init__(self):
        self.counters = Counter()
        self.histograms = defaultdict(list)
        self.gauges = {}

    def increment(self, metric: str, value: int = 1):
        """Increment counter."""
        self.counters[metric] += value

    def record_timing(self, metric: str, duration_ms: float):
        """Record timing histogram."""
        self.histograms[metric].append(duration_ms)

    def set_gauge(self, metric: str, value: float):
        """Set gauge value."""
        self.gauges[metric] = value

    def get_stats(self) -> dict:
        """Get current statistics."""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                metric: {
                    "count": len(values),
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "avg": sum(values) / len(values) if values else 0
                }
                for metric, values in self.histograms.items()
            }
        }

# Global metrics
metrics = MetricsCollector()

def track_metrics(metric_name: str):
    """Decorator to track metrics."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            metrics.increment(f"{metric_name}.calls")

            try:
                result = await func(*args, **kwargs)
                metrics.increment(f"{metric_name}.success")
                return result

            except Exception as e:
                metrics.increment(f"{metric_name}.errors")
                raise

            finally:
                duration_ms = (time.time() - start) * 1000
                metrics.record_timing(f"{metric_name}.duration_ms", duration_ms)

        return wrapper
    return decorator

# Usage
@track_metrics("scrape_url")
@mcp.tool("scrape_url")
async def scrape_url(url: str):
    return await _do_scrape(url)

# Get metrics
@mcp.tool("get_metrics")
async def get_metrics():
    return json.dumps(metrics.get_stats(), indent=2)
```

### 2. Structured Logging

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log(self, level: str, message: str, **kwargs):
        """Log structured data."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }

        log_func = getattr(self.logger, level.lower())
        log_func(json.dumps(log_entry))

# Usage
logger = StructuredLogger("mcp.webscrape")

@mcp.tool("scrape_url")
async def scrape_url(url: str):
    logger.log("info", "Starting scrape", url=url)

    try:
        result = await _do_scrape(url)
        logger.log("info", "Scrape completed",
                   url=url,
                   size_bytes=len(result))
        return result

    except Exception as e:
        logger.log("error", "Scrape failed",
                   url=url,
                   error=str(e),
                   error_type=type(e).__name__)
        raise
```

## Testing Best Practices

### Integration Tests

```python
import pytest

@pytest.mark.asyncio
async def test_scrape_and_resource_access():
    """Test complete workflow."""
    # Scrape URL
    result = await scrape_url("https://example.com")
    assert "resource_uri" in result

    # Access resource
    content = await get_resource(result["resource_uri"])
    assert len(content) > 0

    # Verify metadata
    assert result["metadata"]["url"] == "https://example.com"
    assert result["metadata"]["size_bytes"] == len(content)

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limits are enforced."""
    # Make requests up to limit
    for i in range(10):
        result = await scrape_url(f"https://example.com/page{i}")
        assert "error" not in result

    # Next request should be rate limited
    result = await scrape_url("https://example.com/page11")
    assert "error" in result
    assert "rate limit" in result["error"].lower()
```

## Deployment Checklist

- [ ] Input validation on all tools
- [ ] Rate limiting configured
- [ ] Resource expiration implemented
- [ ] Error messages are helpful
- [ ] Metrics collection enabled
- [ ] Structured logging configured
- [ ] Circuit breakers for external services
- [ ] Retry logic with backoff
- [ ] Resource cleanup task running
- [ ] Security headers configured
- [ ] CORS settings appropriate
- [ ] Environment variables used for secrets
- [ ] Health check endpoint available
- [ ] Documentation complete
- [ ] Tests passing

## Conclusion

Production-ready MCPs require:
- Comprehensive error handling
- Security best practices
- Performance optimization
- Reliability patterns
- Monitoring and observability
- Thorough testing
