"""
Tests for Simple Discovery MCP

Run with: pytest test_discovery.py
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import list_tools, search_tools, greet, generate_data, get_resource


@pytest.mark.asyncio
async def test_list_tools_minimal():
    """Test list_tools with minimal detail."""
    result = await list_tools(detail_level="minimal")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert len(tools) == 2
    assert "simple_greet" in tools
    assert "simple_generate_data" in tools


@pytest.mark.asyncio
async def test_list_tools_brief():
    """Test list_tools with brief detail."""
    result = await list_tools(detail_level="brief")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert len(tools) == 2

    # Check structure
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "category" in tool


@pytest.mark.asyncio
async def test_list_tools_full():
    """Test list_tools with full detail."""
    result = await list_tools(detail_level="full")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert len(tools) == 2

    # Check full schema present
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "category" in tool
        assert "tags" in tool
        assert "schema" in tool


@pytest.mark.asyncio
async def test_list_tools_category_filter():
    """Test list_tools with category filter."""
    result = await list_tools(detail_level="brief", category="data")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert len(tools) == 1
    assert tools[0]["name"] == "simple_generate_data"


@pytest.mark.asyncio
async def test_search_tools():
    """Test search_tools functionality."""
    result = await search_tools(query="data", detail_level="brief")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert len(tools) > 0
    assert tools[0]["name"] == "simple_generate_data"
    assert "relevance" in tools[0]
    assert tools[0]["relevance"] > 0


@pytest.mark.asyncio
async def test_search_tools_no_results():
    """Test search with no matches."""
    result = await search_tools(query="nonexistent", detail_level="brief")
    tools = json.loads(result)

    assert isinstance(tools, list)
    assert len(tools) == 0


@pytest.mark.asyncio
async def test_greet_tool():
    """Test greet tool."""
    result = await greet(name="World")
    data = json.loads(result)

    assert "greeting" in data
    assert data["greeting"] == "Hello, World!"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_generate_data_tool():
    """Test generate_data tool."""
    result = await generate_data(size=5)
    data = json.loads(result)

    # Check response structure
    assert "resource_id" in data
    assert "resource_uri" in data
    assert "preview" in data
    assert "metadata" in data

    # Check metadata
    assert data["metadata"]["item_count"] == 5
    assert "size_bytes" in data["metadata"]
    assert "created_at" in data["metadata"]
    assert "expires_in_seconds" in data["metadata"]


@pytest.mark.asyncio
async def test_resource_access():
    """Test resource creation and access."""
    # Generate data
    result = await generate_data(size=3)
    data = json.loads(result)

    resource_id = data["resource_id"]

    # Access resource
    resource_data = await get_resource(resource_id)
    items = json.loads(resource_data)

    # Verify data
    assert isinstance(items, list)
    assert len(items) == 3

    for i, item in enumerate(items):
        assert item["id"] == i
        assert item["value"] == f"Item {i}"
        assert "timestamp" in item


@pytest.mark.asyncio
async def test_resource_not_found():
    """Test accessing non-existent resource."""
    with pytest.raises(Exception) as exc_info:
        await get_resource("nonexistent123")

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_progressive_disclosure_flow():
    """Test complete progressive disclosure workflow."""
    # 1. List tools (minimal)
    tools_minimal = json.loads(await list_tools(detail_level="minimal"))
    assert len(tools_minimal) == 2

    # 2. Search for specific tool
    search_result = json.loads(
        await search_tools(query="generate", detail_level="brief")
    )
    assert len(search_result) > 0
    tool_name = search_result[0]["name"]

    # 3. Get full schema
    full_schema = json.loads(
        await search_tools(query=tool_name, detail_level="full")
    )
    assert "schema" in full_schema[0]

    # 4. Use the tool
    result = await generate_data(size=5)
    assert json.loads(result)["metadata"]["item_count"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
