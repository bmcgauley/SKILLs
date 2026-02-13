# Resource Management in MCPs

**Last Updated**: 2025-11-09

## Overview

Resource management is the practice of storing large data outside the conversation context and providing agents with URIs to access that data when needed. This keeps context windows small while still giving agents access to large datasets.

## The Resource Pattern

### Traditional Approach (Anti-Pattern)

```python
@mcp.tool("scrape_url")
async def scrape_url(url: str) -> str:
    """Scrape a URL and return full content."""
    html = fetch_url(url)  # 50KB of HTML

    return json.dumps({
        "url": url,
        "content": html,  # 50KB in context!
        "size": len(html)
    })
```

**Problems**:
- Large data flows through context
- Same data returned even if agent doesn't need it
- Can't reuse data without re-transmission
- Wastes tokens

### Resource-Based Approach (Correct)

```python
from datetime import datetime, timedelta
import uuid

# Storage (in-memory for demo, use Redis/S3 in production)
RESOURCE_STORE = {}

@mcp.tool("scrape_url")
async def scrape_url(url: str) -> str:
    """Scrape a URL and return resource reference."""
    html = fetch_url(url)  # 50KB of HTML

    # Store content
    resource_id = uuid.uuid4().hex
    RESOURCE_STORE[resource_id] = {
        "data": html,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=1),
        "metadata": {
            "url": url,
            "size_bytes": len(html),
            "content_type": "text/html"
        }
    }

    # Return reference (small)
    return json.dumps({
        "resource_id": resource_id,
        "resource_uri": f"webscrape://{resource_id}/content",
        "preview": html[:500],  # Small preview
        "metadata": {
            "url": url,
            "size_bytes": len(html),
            "content_type": "text/html",
            "expires_in_seconds": 3600
        }
    })

@mcp.resource("webscrape://{resource_id}/content")
async def get_content(resource_id: str) -> str:
    """Retrieve full content by resource ID."""
    if resource_id not in RESOURCE_STORE:
        raise Exception(f"Resource {resource_id} not found or expired")

    resource = RESOURCE_STORE[resource_id]

    # Check expiration
    if datetime.utcnow() > resource["expires_at"]:
        del RESOURCE_STORE[resource_id]
        raise Exception(f"Resource {resource_id} has expired")

    return resource["data"]
```

**Benefits**:
- Only metadata in context (~1KB vs 50KB)
- Agent accesses data in execution environment
- Can reuse data without re-transmission
- Supports expiration and cleanup

## Storage Strategies

### 1. In-Memory Storage

**Best for**: Development, small datasets, short-lived resources

```python
from collections import OrderedDict
from datetime import datetime, timedelta

class InMemoryResourceStore:
    def __init__(self, max_size: int = 1000):
        self.store = OrderedDict()
        self.max_size = max_size

    def set(self, key: str, data: any, ttl_seconds: int = 3600):
        """Store data with TTL."""
        # Evict oldest if at capacity
        if len(self.store) >= self.max_size:
            self.store.popitem(last=False)

        self.store[key] = {
            "data": data,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds)
        }

    def get(self, key: str):
        """Retrieve data if not expired."""
        if key not in self.store:
            return None

        resource = self.store[key]

        # Check expiration
        if datetime.utcnow() > resource["expires_at"]:
            del self.store[key]
            return None

        return resource["data"]

    def delete(self, key: str):
        """Delete resource."""
        if key in self.store:
            del self.store[key]

    def cleanup_expired(self):
        """Remove all expired resources."""
        now = datetime.utcnow()
        expired = [
            k for k, v in self.store.items()
            if now > v["expires_at"]
        ]
        for key in expired:
            del self.store[key]

# Usage
resource_store = InMemoryResourceStore(max_size=1000)
```

### 2. Redis Storage

**Best for**: Production, distributed systems, automatic expiration

```python
import redis
import json
from typing import Optional

class RedisResourceStore:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.client = redis.from_url(redis_url)

    def set(self, key: str, data: any, ttl_seconds: int = 3600):
        """Store data with TTL."""
        serialized = json.dumps(data)
        self.client.setex(key, ttl_seconds, serialized)

    def get(self, key: str) -> Optional[any]:
        """Retrieve data."""
        data = self.client.get(key)
        if data is None:
            return None
        return json.loads(data)

    def delete(self, key: str):
        """Delete resource."""
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Check if resource exists."""
        return self.client.exists(key) > 0

    def get_ttl(self, key: str) -> int:
        """Get remaining TTL in seconds."""
        return self.client.ttl(key)

# Usage
resource_store = RedisResourceStore()
resource_store.set("abc123", {"content": "..."}, ttl_seconds=3600)
```

### 3. S3 Storage

**Best for**: Large files, long-term storage, binary data

```python
import boto3
from datetime import datetime, timedelta
from typing import Optional

class S3ResourceStore:
    def __init__(self, bucket_name: str):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name

    def set(self, key: str, data: bytes, ttl_seconds: int = 3600):
        """Store data with expiration tag."""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            Metadata={
                'expires_at': expires_at.isoformat()
            }
        )

    def get(self, key: str) -> Optional[bytes]:
        """Retrieve data if not expired."""
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)

            # Check expiration
            expires_at = response['Metadata'].get('expires_at')
            if expires_at:
                expires_dt = datetime.fromisoformat(expires_at)
                if datetime.utcnow() > expires_dt:
                    self.delete(key)
                    return None

            return response['Body'].read()

        except self.s3.exceptions.NoSuchKey:
            return None

    def delete(self, key: str):
        """Delete resource."""
        self.s3.delete_object(Bucket=self.bucket, Key=key)

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for direct access."""
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=expiration
        )

# Usage
resource_store = S3ResourceStore(bucket_name="mcp-resources")
```

## Resource URI Patterns

### Standard Format

```
{mcp_name}://{resource_id}/{resource_type}
```

**Examples**:
```
webscrape://abc123/content
webscrape://abc123/metadata
midi://xyz789/audio
midi://xyz789/notation
fileanalysis://def456/summary
```

### URI Components

1. **Scheme**: MCP name (identifies which MCP owns the resource)
2. **Resource ID**: Unique identifier (UUID, hash, or custom)
3. **Resource Type**: Type of data (content, metadata, etc.)

### Implementation

```python
from urllib.parse import urlparse

def parse_resource_uri(uri: str) -> dict:
    """Parse resource URI into components."""
    parsed = urlparse(uri)

    return {
        "mcp_name": parsed.scheme,
        "resource_id": parsed.netloc,
        "resource_type": parsed.path.lstrip('/'),
        "full_uri": uri
    }

# Example
uri = "webscrape://abc123/content"
components = parse_resource_uri(uri)
# {
#     "mcp_name": "webscrape",
#     "resource_id": "abc123",
#     "resource_type": "content",
#     "full_uri": "webscrape://abc123/content"
# }

@mcp.resource("webscrape://{resource_id}/{resource_type}")
async def get_resource(resource_id: str, resource_type: str) -> str:
    """Handle resource access with type."""
    resource = RESOURCE_STORE.get(resource_id)

    if not resource:
        raise Exception(f"Resource {resource_id} not found")

    if resource_type == "content":
        return resource["data"]
    elif resource_type == "metadata":
        return json.dumps(resource["metadata"])
    else:
        raise Exception(f"Unknown resource type: {resource_type}")
```

## Expiration Strategies

### 1. Time-Based Expiration (TTL)

```python
@mcp.tool("generate_data")
async def generate_data(ttl_minutes: int = 60) -> str:
    """Generate data with configurable TTL."""
    data = expensive_operation()
    resource_id = uuid.uuid4().hex

    ttl_seconds = ttl_minutes * 60
    resource_store.set(resource_id, data, ttl_seconds=ttl_seconds)

    return json.dumps({
        "resource_id": resource_id,
        "resource_uri": f"myapp://{resource_id}/data",
        "expires_in_seconds": ttl_seconds,
        "expires_at": (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()
    })
```

### 2. Access-Based Expiration

```python
class AccessTrackingStore:
    def __init__(self):
        self.store = {}

    def set(self, key: str, data: any, max_accesses: int = 10):
        """Store with access limit."""
        self.store[key] = {
            "data": data,
            "accesses_remaining": max_accesses
        }

    def get(self, key: str):
        """Retrieve and decrement access count."""
        if key not in self.store:
            return None

        resource = self.store[key]
        resource["accesses_remaining"] -= 1

        if resource["accesses_remaining"] <= 0:
            data = resource["data"]
            del self.store[key]
            return data

        return resource["data"]
```

### 3. Size-Based Eviction (LRU)

```python
from collections import OrderedDict

class LRUResourceStore:
    def __init__(self, max_size_mb: int = 100):
        self.store = OrderedDict()
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.current_size_bytes = 0

    def set(self, key: str, data: bytes):
        """Store with LRU eviction."""
        data_size = len(data)

        # Evict oldest until there's space
        while self.current_size_bytes + data_size > self.max_size_bytes:
            if not self.store:
                raise Exception("Data too large for store")

            oldest_key, oldest_data = self.store.popitem(last=False)
            self.current_size_bytes -= len(oldest_data)

        self.store[key] = data
        self.current_size_bytes += data_size

    def get(self, key: str):
        """Retrieve and mark as recently used."""
        if key not in self.store:
            return None

        # Move to end (most recent)
        self.store.move_to_end(key)
        return self.store[key]
```

## Resource Lifecycle

### Complete Lifecycle Example

```python
class ResourceManager:
    def __init__(self, store):
        self.store = store
        self.metadata = {}

    async def create_resource(self, data: any, metadata: dict = None) -> dict:
        """Create new resource."""
        resource_id = uuid.uuid4().hex
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(hours=1)

        # Store data
        self.store.set(resource_id, data, ttl_seconds=3600)

        # Store metadata separately
        self.metadata[resource_id] = {
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "size_bytes": len(str(data)),
            "access_count": 0,
            **(metadata or {})
        }

        return {
            "resource_id": resource_id,
            "resource_uri": f"myapp://{resource_id}/data",
            "metadata": self.metadata[resource_id]
        }

    async def access_resource(self, resource_id: str) -> any:
        """Access resource and update metadata."""
        data = self.store.get(resource_id)

        if data is None:
            raise Exception(f"Resource {resource_id} not found or expired")

        # Update access count
        if resource_id in self.metadata:
            self.metadata[resource_id]["access_count"] += 1
            self.metadata[resource_id]["last_accessed"] = datetime.utcnow().isoformat()

        return data

    async def delete_resource(self, resource_id: str):
        """Explicitly delete resource."""
        self.store.delete(resource_id)
        if resource_id in self.metadata:
            del self.metadata[resource_id]

    async def refresh_resource(self, resource_id: str, ttl_seconds: int = 3600):
        """Extend resource lifetime."""
        data = self.store.get(resource_id)

        if data is None:
            raise Exception(f"Resource {resource_id} not found")

        # Re-store with new TTL
        self.store.set(resource_id, data, ttl_seconds=ttl_seconds)

        # Update metadata
        if resource_id in self.metadata:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self.metadata[resource_id]["expires_at"] = expires_at.isoformat()

    async def list_resources(self) -> list:
        """List all active resources."""
        return [
            {
                "resource_id": rid,
                "resource_uri": f"myapp://{rid}/data",
                **meta
            }
            for rid, meta in self.metadata.items()
            if self.store.get(rid) is not None
        ]
```

## Preview Generation

### Text Previews

```python
def generate_text_preview(text: str, max_length: int = 500) -> dict:
    """Generate preview for text content."""
    preview = text[:max_length]

    if len(text) > max_length:
        preview += "..."

    return {
        "preview": preview,
        "preview_length": len(preview),
        "total_length": len(text),
        "is_truncated": len(text) > max_length
    }
```

### Structured Data Previews

```python
def generate_json_preview(data: dict, max_keys: int = 10) -> dict:
    """Generate preview for JSON data."""
    if isinstance(data, dict):
        keys = list(data.keys())[:max_keys]
        preview = {k: data[k] for k in keys}

        return {
            "preview": preview,
            "total_keys": len(data),
            "preview_keys": len(keys),
            "is_truncated": len(data) > max_keys,
            "remaining_keys": list(data.keys())[max_keys:]
        }
    elif isinstance(data, list):
        return {
            "preview": data[:max_keys],
            "total_items": len(data),
            "is_truncated": len(data) > max_keys
        }
    else:
        return {"preview": str(data)[:500]}
```

### Binary Data Previews

```python
import base64

def generate_binary_preview(data: bytes) -> dict:
    """Generate preview for binary data."""
    return {
        "size_bytes": len(data),
        "preview_base64": base64.b64encode(data[:100]).decode('utf-8'),
        "mime_type": detect_mime_type(data),
        "is_binary": True
    }

def detect_mime_type(data: bytes) -> str:
    """Detect MIME type from binary data."""
    # Check magic numbers
    if data.startswith(b'\x89PNG'):
        return "image/png"
    elif data.startswith(b'\xff\xd8\xff'):
        return "image/jpeg"
    elif data.startswith(b'%PDF'):
        return "application/pdf"
    else:
        return "application/octet-stream"
```

## Performance Optimization

### 1. Lazy Loading

```python
class LazyResource:
    """Resource that loads data only when accessed."""

    def __init__(self, resource_id: str, store):
        self.resource_id = resource_id
        self.store = store
        self._data = None

    @property
    def data(self):
        """Load data on first access."""
        if self._data is None:
            self._data = self.store.get(self.resource_id)
        return self._data
```

### 2. Streaming Access

```python
@mcp.resource("myapp://{resource_id}/stream")
async def stream_resource(resource_id: str):
    """Stream large resource in chunks."""
    data = RESOURCE_STORE.get(resource_id)

    if data is None:
        raise Exception(f"Resource {resource_id} not found")

    # Yield chunks
    chunk_size = 1024 * 1024  # 1MB chunks
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]
```

### 3. Compression

```python
import gzip

def store_compressed(key: str, data: str, store):
    """Store data compressed."""
    compressed = gzip.compress(data.encode('utf-8'))
    store.set(key, compressed)

    return {
        "original_size": len(data),
        "compressed_size": len(compressed),
        "compression_ratio": len(compressed) / len(data)
    }

def get_compressed(key: str, store):
    """Retrieve and decompress data."""
    compressed = store.get(key)
    if compressed is None:
        return None

    return gzip.decompress(compressed).decode('utf-8')
```

## Security Considerations

### 1. Access Control

```python
class SecureResourceStore:
    def __init__(self):
        self.store = {}
        self.access_tokens = {}

    def create_resource(self, data: any, owner_id: str) -> dict:
        """Create resource with access token."""
        resource_id = uuid.uuid4().hex
        access_token = uuid.uuid4().hex

        self.store[resource_id] = data
        self.access_tokens[resource_id] = {
            "token": access_token,
            "owner_id": owner_id
        }

        return {
            "resource_id": resource_id,
            "access_token": access_token
        }

    def get_resource(self, resource_id: str, access_token: str):
        """Retrieve resource with token verification."""
        if resource_id not in self.access_tokens:
            raise Exception("Resource not found")

        if self.access_tokens[resource_id]["token"] != access_token:
            raise Exception("Invalid access token")

        return self.store.get(resource_id)
```

### 2. Resource Limits

```python
class LimitedResourceStore:
    def __init__(self, max_size_per_resource_mb: int = 10):
        self.store = {}
        self.max_size_bytes = max_size_per_resource_mb * 1024 * 1024

    def set(self, key: str, data: any):
        """Store with size limit."""
        data_size = len(str(data))

        if data_size > self.max_size_bytes:
            raise Exception(
                f"Resource too large: {data_size} bytes "
                f"(max: {self.max_size_bytes} bytes)"
            )

        self.store[key] = data
```

## Testing

### Resource Lifecycle Tests

```python
import pytest

@pytest.mark.asyncio
async def test_resource_lifecycle():
    """Test complete resource lifecycle."""
    manager = ResourceManager(InMemoryResourceStore())

    # Create
    result = await manager.create_resource("test data", {"type": "test"})
    resource_id = result["resource_id"]

    # Access
    data = await manager.access_resource(resource_id)
    assert data == "test data"

    # Refresh
    await manager.refresh_resource(resource_id, ttl_seconds=7200)

    # Delete
    await manager.delete_resource(resource_id)

    # Verify deleted
    with pytest.raises(Exception):
        await manager.access_resource(resource_id)

@pytest.mark.asyncio
async def test_resource_expiration():
    """Test resource expiration."""
    store = InMemoryResourceStore()
    store.set("test", "data", ttl_seconds=1)

    # Should exist immediately
    assert store.get("test") == "data"

    # Wait for expiration
    await asyncio.sleep(2)

    # Should be expired
    assert store.get("test") is None
```

## Best Practices

1. **Always provide previews**: Give agents a small preview of data
2. **Use appropriate TTLs**: Balance between reuse and memory usage
3. **Include metadata**: Size, type, expiration info
4. **Clear resource URIs**: Use consistent, parseable formats
5. **Handle expiration gracefully**: Return helpful error messages
6. **Optimize storage**: Use compression, streaming for large data
7. **Monitor resource usage**: Track creation, access, deletion metrics
8. **Clean up expired resources**: Run periodic cleanup tasks

## Conclusion

Effective resource management enables:
- Token-efficient MCPs (90%+ reduction in context usage)
- Large data handling without context limits
- Data reuse across multiple tool calls
- Flexible expiration and cleanup strategies
