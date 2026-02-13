# Testing Agent Code: Strategies and Best Practices

**Last Updated**: 2025-11-09

## Overview

Testing agent code that uses MCP tools requires different approaches than traditional software testing. This guide covers unit testing with mocks, integration testing with real MCPs, and performance testing for token usage and execution time.

## Types of Tests

### 1. Unit Tests
- Test individual functions in isolation
- Mock MCP calls
- Fast execution
- Run frequently during development

### 2. Integration Tests
- Test with real MCP servers
- Verify end-to-end behavior
- Slower execution
- Run before deployment

### 3. Performance Tests
- Measure token usage
- Measure execution time
- Measure memory usage
- Verify optimization goals

### 4. Property-Based Tests
- Test with generated inputs
- Find edge cases automatically
- Verify invariants

## Unit Testing with Mocks

### Basic Mock Pattern

```python
import pytest
from unittest.mock import AsyncMock, Mock, patch

@pytest.mark.asyncio
async def test_scrape_url_basic():
    # Create mock MCP client
    mock_mcp = Mock()
    mock_mcp.call = AsyncMock()

    # Setup mock response
    mock_mcp.call.return_value = {
        "resource_uri": "scrape://test123/content",
        "metadata": {
            "size_bytes": 5000,
            "content_type": "text/html",
            "url": "https://example.com"
        },
        "preview": "Example Domain..."
    }

    # Call function with mock
    result = await scrape_url("https://example.com", mcp=mock_mcp)

    # Assertions
    assert mock_mcp.call.called
    assert mock_mcp.call.call_count == 1
    assert result["resource_uri"] == "scrape://test123/content"

    # Verify correct parameters
    call_args = mock_mcp.call.call_args
    assert call_args[0][0] == "webscrape_scrape_url"
    assert call_args[1]["url"] == "https://example.com"
```

### Mocking Resources

```python
@pytest.mark.asyncio
async def test_scrape_and_process():
    # Mock both call and get_resource
    mock_mcp = Mock()
    mock_mcp.call = AsyncMock()
    mock_mcp.get_resource = AsyncMock()

    # Setup mocks
    mock_mcp.call.return_value = {
        "resource_uri": "scrape://abc123/content"
    }
    mock_mcp.get_resource.return_value = "<html>Test content</html>"

    # Test function
    result = await scrape_and_process("https://example.com", mcp=mock_mcp)

    # Verify both methods called
    assert mock_mcp.call.called
    assert mock_mcp.get_resource.called

    # Verify get_resource called with correct URI
    mock_mcp.get_resource.assert_called_with("scrape://abc123/content")

    # Verify processing occurred
    assert "processed" in result
```

### Mocking Errors

```python
@pytest.mark.asyncio
async def test_scrape_error_handling():
    mock_mcp = Mock()
    mock_mcp.call = AsyncMock()

    # Mock error response
    mock_mcp.call.return_value = {
        "error": "Connection timeout",
        "url": "https://example.com"
    }

    # Test error handling
    result = await scrape_url("https://example.com", mcp=mock_mcp)

    # Verify error handled gracefully
    assert "error" in result
    assert result["error"] == "Connection timeout"
```

### Mocking Side Effects

```python
@pytest.mark.asyncio
async def test_retry_behavior():
    mock_mcp = Mock()
    mock_mcp.call = AsyncMock()

    # First two calls fail, third succeeds
    mock_mcp.call.side_effect = [
        Exception("Network error"),
        Exception("Network error"),
        {"resource_uri": "scrape://success/content"}
    ]

    # Test with retries
    result = await scrape_with_retry("https://example.com", mcp=mock_mcp)

    # Verify retried 3 times
    assert mock_mcp.call.call_count == 3

    # Verify success on third attempt
    assert "resource_uri" in result
```

## Integration Testing

### Testing with Real MCP

```python
import pytest
import os

# Skip if MCP server not available
@pytest.mark.skipif(
    not os.getenv("MCP_SERVER_URL"),
    reason="MCP server not available"
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_scraping():
    """Test with actual MCP server"""
    # Use real MCP client
    mcp = create_mcp_client()

    # Test with real URL
    result = await mcp.call("webscrape_scrape_url", {
        "url": "https://example.com",
        "response_format": "markdown"
    })

    # Verify structure
    assert "resource_uri" in result
    assert "metadata" in result
    assert result["metadata"]["size_bytes"] > 0

    # Verify resource accessible
    content = await mcp.get_resource(result["resource_uri"])
    assert len(content) > 0
    assert "Example Domain" in content
```

### Fixture for MCP Client

```python
@pytest.fixture
async def mcp_client():
    """Fixture providing real MCP client"""
    client = create_mcp_client()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_with_fixture(mcp_client):
    """Test using fixture"""
    result = await mcp_client.call("webscrape_scrape_url", {
        "url": "https://example.com"
    })

    assert "resource_uri" in result
```

### Testing Tool Discovery

```python
@pytest.mark.asyncio
async def test_tool_discovery():
    mcp = create_mcp_client()

    # Test list_tools
    tools = await mcp.call("webscrape_list_tools", {
        "detail_level": "minimal"
    })

    assert isinstance(tools, list)
    assert len(tools) > 0

    # Test search_tools
    scrape_tools = await mcp.call("webscrape_search_tools", {
        "query": "scrape"
    })

    assert len(scrape_tools) > 0
    assert all("scrape" in t["name"].lower() for t in scrape_tools)
```

### End-to-End Pipeline Test

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_full_pipeline():
    """Test complete workflow"""
    mcp = create_mcp_client()

    # 1. Discover tools
    tools = await mcp.call("webscrape_list_tools", {
        "detail_level": "minimal"
    })
    assert "webscrape_scrape_url" in [t["name"] for t in tools]

    # 2. Scrape URL
    result = await mcp.call("webscrape_scrape_url", {
        "url": "https://example.com"
    })
    assert "resource_uri" in result

    # 3. Fetch resource
    content = await mcp.get_resource(result["resource_uri"])
    assert len(content) > 0

    # 4. Process content
    links = extract_links(content)
    assert len(links) > 0

    # 5. Verify complete
    assert True  # Pipeline completed successfully
```

## Performance Testing

### Token Usage Testing

```python
def estimate_tokens(data: any) -> int:
    """Estimate token count"""
    return len(str(data)) // 4

@pytest.mark.asyncio
async def test_token_usage():
    """Verify token usage is optimized"""
    mcp = create_mock_mcp()

    # Measure tokens before
    before = estimate_tokens(get_conversation_context())

    # Run workflow
    result = await scrape_and_process("https://example.com", mcp=mcp)

    # Measure tokens after
    after = estimate_tokens(get_conversation_context())

    tokens_used = after - before

    # Verify token usage is reasonable
    assert tokens_used < 5000, f"Used {tokens_used} tokens, expected < 5000"

    # Verify using resources, not direct data
    assert "resource_uri" in result
```

### Execution Time Testing

```python
import time

@pytest.mark.asyncio
async def test_execution_time():
    """Verify performance targets met"""
    mcp = create_mock_mcp()

    start = time.time()

    # Run workflow
    result = await scrape_multiple_urls(
        ["https://example.com"] * 10,
        mcp=mcp
    )

    elapsed = time.time() - start

    # Should complete in under 2 seconds
    assert elapsed < 2.0, f"Took {elapsed:.2f}s, expected < 2.0s"

    # Verify all completed
    assert len(result) == 10
```

### Memory Usage Testing

```python
import psutil
import os

@pytest.mark.asyncio
async def test_memory_usage():
    """Verify memory usage is reasonable"""
    process = psutil.Process(os.getpid())

    # Measure before
    before_mb = process.memory_info().rss / 1024 / 1024

    # Process large dataset
    result = await process_large_dataset(
        data_uri="large://dataset",
        mcp=create_mock_mcp()
    )

    # Measure after
    after_mb = process.memory_info().rss / 1024 / 1024

    increase_mb = after_mb - before_mb

    # Should not increase memory by more than 100MB
    assert increase_mb < 100, f"Memory increased by {increase_mb:.2f}MB"
```

### Parallel Execution Testing

```python
@pytest.mark.asyncio
async def test_parallel_speedup():
    """Verify parallel execution is faster than sequential"""
    mcp = create_mock_mcp()
    urls = ["https://example.com"] * 10

    # Sequential execution
    start = time.time()
    for url in urls:
        await mcp.call("scrape", {"url": url})
    sequential_time = time.time() - start

    # Parallel execution
    start = time.time()
    await asyncio.gather(*[
        mcp.call("scrape", {"url": url})
        for url in urls
    ])
    parallel_time = time.time() - start

    # Parallel should be significantly faster
    speedup = sequential_time / parallel_time
    assert speedup > 5, f"Speedup only {speedup:.2f}x, expected > 5x"
```

## Property-Based Testing

### Using Hypothesis

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=1000))
@pytest.mark.asyncio
async def test_tokenization_reversible(text):
    """Property: tokenization should be reversible"""
    mcp = create_mock_mcp()

    # Mock tokenization
    mcp.call.return_value = {
        "tokenized_text": "[TOKEN_1]",
        "token_map_id": "test123"
    }
    mcp.get_resource.return_value = text

    # Tokenize
    tokenized = await mcp.call("helper_tokenize_pii", {"text": text})

    # Detokenize
    detokenized = await mcp.get_resource(tokenized["token_map_id"])

    # Should get original back
    assert detokenized == text

@given(st.lists(st.text(alphabet=st.characters(min_codepoint=65, max_codepoint=90), min_size=10, max_size=100), min_size=1, max_size=100))
@pytest.mark.asyncio
async def test_batch_processing_invariants(urls):
    """Property: batch processing should handle any list of URLs"""
    mcp = create_mock_mcp()

    result = await process_batch(urls, mcp=mcp)

    # Invariants
    assert len(result["successful"]) + len(result["failed"]) == len(urls)
    assert 0 <= result["success_rate"] <= 1.0
```

## Test Fixtures and Helpers

### Reusable Mock MCP

```python
@pytest.fixture
def mock_mcp():
    """Fixture providing mock MCP client"""
    mcp = Mock()
    mcp.call = AsyncMock()
    mcp.get_resource = AsyncMock()

    # Default responses
    mcp.call.return_value = {
        "resource_uri": "test://resource",
        "metadata": {"size_bytes": 1000}
    }
    mcp.get_resource.return_value = "test content"

    return mcp

@pytest.mark.asyncio
async def test_with_mock(mock_mcp):
    """Use fixture"""
    result = await scrape_url("https://example.com", mcp=mock_mcp)
    assert "resource_uri" in result
```

### Test Data Builders

```python
def build_scrape_response(
    content: str = "test content",
    size: int = 1000,
    url: str = "https://example.com"
) -> dict:
    """Build test scrape response"""
    return {
        "resource_uri": f"scrape://{hash(content)}/content",
        "metadata": {
            "size_bytes": size,
            "url": url,
            "content_type": "text/html"
        },
        "preview": content[:100]
    }

@pytest.mark.asyncio
async def test_with_builder(mock_mcp):
    # Use builder for consistent test data
    mock_mcp.call.return_value = build_scrape_response(
        content="<html>Custom test content</html>",
        size=5000
    )

    result = await scrape_url("https://example.com", mcp=mock_mcp)
    assert result["metadata"]["size_bytes"] == 5000
```

### Parameterized Tests

```python
@pytest.mark.parametrize("url,expected_error", [
    ("", "URL cannot be empty"),
    ("not-a-url", "Invalid URL format"),
    ("ftp://example.com", "Protocol not supported"),
    ("https://" + "x" * 3000, "URL too long"),
])
@pytest.mark.asyncio
async def test_url_validation(url, expected_error):
    """Test various invalid URLs"""
    with pytest.raises(ValueError, match=expected_error):
        validate_url(url)

@pytest.mark.parametrize("max_retries,expected_attempts", [
    (1, 1),
    (3, 3),
    (5, 5),
])
@pytest.mark.asyncio
async def test_retry_attempts(max_retries, expected_attempts, mock_mcp):
    """Test retry behavior with different max_retries"""
    # Mock always fails
    mock_mcp.call.side_effect = Exception("Network error")

    result = await scrape_with_retry(
        "https://example.com",
        max_retries=max_retries,
        mcp=mock_mcp
    )

    # Verify correct number of attempts
    assert mock_mcp.call.call_count == expected_attempts
    assert "error" in result
```

## Testing Error Handling

### Test Retry Logic

```python
@pytest.mark.asyncio
async def test_retry_on_transient_error(mock_mcp):
    """Test retries on transient errors"""
    # Fail twice, then succeed
    mock_mcp.call.side_effect = [
        Exception("Connection timeout"),
        Exception("Connection timeout"),
        {"resource_uri": "scrape://success/content"}
    ]

    result = await scrape_with_retry(
        "https://example.com",
        max_retries=3,
        mcp=mock_mcp
    )

    assert mock_mcp.call.call_count == 3
    assert "resource_uri" in result
    assert result["resource_uri"] == "scrape://success/content"

@pytest.mark.asyncio
async def test_no_retry_on_permanent_error(mock_mcp):
    """Test no retry on permanent errors"""
    # Permanent error
    mock_mcp.call.side_effect = Exception("Invalid parameter")

    result = await scrape_with_conditional_retry(
        "https://example.com",
        mcp=mock_mcp
    )

    # Should only try once
    assert mock_mcp.call.call_count == 1
    assert "error" in result
```

### Test Timeout Handling

```python
@pytest.mark.asyncio
async def test_timeout_handling():
    """Test timeout behavior"""
    async def slow_operation():
        await asyncio.sleep(10)  # Very slow
        return {"result": "data"}

    # Should timeout
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=1)

@pytest.mark.asyncio
async def test_timeout_with_fallback(mock_mcp):
    """Test fallback when timeout occurs"""
    # Primary method times out
    async def timeout_then_succeed(*args, **kwargs):
        await asyncio.sleep(5)
        return {"resource_uri": "slow"}

    mock_mcp.call.side_effect = timeout_then_succeed

    result = await scrape_with_timeout_fallback(
        "https://example.com",
        timeout=1,
        mcp=mock_mcp
    )

    # Should have used fallback
    assert "fallback" in result
```

## Test Organization

### Directory Structure

```
tests/
├── unit/
│   ├── test_scraping.py
│   ├── test_processing.py
│   └── test_error_handling.py
├── integration/
│   ├── test_mcp_integration.py
│   ├── test_pipelines.py
│   └── test_resource_access.py
├── performance/
│   ├── test_token_usage.py
│   ├── test_execution_time.py
│   └── test_memory_usage.py
└── conftest.py  # Shared fixtures
```

### conftest.py

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_mcp():
    """Shared mock MCP fixture"""
    mcp = Mock()
    mcp.call = AsyncMock()
    mcp.get_resource = AsyncMock()
    return mcp

@pytest.fixture
async def real_mcp():
    """Shared real MCP fixture"""
    client = create_mcp_client()
    yield client
    await client.close()

# Markers
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
```

### Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest -m integration

# Run with coverage
pytest --cov=src tests/

# Run performance tests
pytest -m performance

# Run specific test
pytest tests/unit/test_scraping.py::test_scrape_url_basic

# Run with verbose output
pytest -v

# Run and show print statements
pytest -s
```

## Best Practices

### 1. Test Behavior, Not Implementation

```python
# ❌ BAD - Tests implementation details
@pytest.mark.asyncio
async def test_scraping_uses_specific_library():
    assert "requests" in sys.modules

# ✅ GOOD - Tests behavior
@pytest.mark.asyncio
async def test_scraping_returns_content():
    result = await scrape_url("https://example.com")
    assert result["metadata"]["size_bytes"] > 0
```

### 2. Keep Tests Independent

```python
# ❌ BAD - Tests depend on each other
result = None

@pytest.mark.asyncio
async def test_step_1():
    global result
    result = await scrape_url("https://example.com")

@pytest.mark.asyncio
async def test_step_2():
    global result
    content = await process(result)  # Depends on test_step_1

# ✅ GOOD - Tests are independent
@pytest.mark.asyncio
async def test_scraping():
    result = await scrape_url("https://example.com")
    assert result

@pytest.mark.asyncio
async def test_processing():
    mock_result = build_scrape_response()
    content = await process(mock_result)
    assert content
```

### 3. Use Descriptive Test Names

```python
# ❌ BAD
def test_1():
    pass

# ✅ GOOD
def test_scrape_url_returns_resource_uri():
    pass

def test_scrape_url_handles_network_errors_with_retry():
    pass
```

### 4. Test Edge Cases

```python
@pytest.mark.asyncio
async def test_scraping_edge_cases(mock_mcp):
    # Empty response
    mock_mcp.get_resource.return_value = ""
    result = await scrape_and_process("https://example.com", mcp=mock_mcp)
    assert "error" in result

    # Very large response
    mock_mcp.get_resource.return_value = "x" * 10_000_000
    result = await scrape_and_process("https://example.com", mcp=mock_mcp)
    assert result  # Handles large data

    # Malformed response
    mock_mcp.call.return_value = {"unexpected": "structure"}
    result = await scrape_url("https://example.com", mcp=mock_mcp)
    assert "error" in result
```

### 5. Mock at the Right Level

```python
# ❌ BAD - Mock too low-level
@patch("requests.get")
def test_scraping(mock_get):
    # Tests implementation details

# ✅ GOOD - Mock at MCP interface
def test_scraping(mock_mcp):
    # Tests agent code behavior
```

## Summary

**Key Testing Principles**:

1. **Unit tests with mocks** - Fast, isolated, run frequently
2. **Integration tests with real MCPs** - Verify end-to-end behavior
3. **Performance tests** - Measure tokens, time, memory
4. **Property-based tests** - Find edge cases automatically
5. **Test behavior, not implementation** - Refactor-safe tests

**Test Coverage Goals**:
- Core functionality: 100%
- Error handling: 100%
- Edge cases: 80%+
- Performance: Key metrics measured

**Remember**: Good tests give confidence to refactor and optimize!
