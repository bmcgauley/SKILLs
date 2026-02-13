# Simple Discovery MCP Example

A minimal MCP demonstrating progressive disclosure patterns.

## Features

- **Tool Discovery**: `simple_list_tools` and `simple_search_tools` endpoints
- **Resource Management**: Store data as resources, return references
- **TypeScript Definitions**: See `tools/` directory
- **Simple Testing**: Run `python server.py` to test

## Structure

```
simple-discovery-mcp/
├── server.py           # Main MCP implementation
├── tools/
│   ├── greet.ts       # Type definitions for greet tool
│   └── generate_data.ts
├── tests/
│   └── test_discovery.py
└── README.md
```

## Tools

### Discovery Tools

1. **simple_list_tools**: List available tools
   - `detail_level`: minimal, brief, or full
   - `category`: optional filter

2. **simple_search_tools**: Search tools by keyword
   - `query`: search term
   - `detail_level`: brief or full

### Functional Tools

3. **simple_greet**: Return a greeting
   - `name`: name to greet

4. **simple_generate_data**: Generate sample data
   - `size`: number of items (default 10)
   - Returns resource reference

## Usage

### Running the Server

```bash
python server.py
```

### Testing Discovery

```python
# List all tools (minimal)
result = await list_tools(detail_level="minimal")
# ["simple_greet", "simple_generate_data"]

# Search for data tools
result = await search_tools(query="data", detail_level="brief")
# [{"name": "simple_generate_data", "description": "...", "relevance": 50}]

# Get full schema
result = await search_tools(query="generate_data", detail_level="full")
```

### Using Resource Pattern

```python
# Generate data (returns reference)
result = await generate_data(size=10)
# {
#   "resource_id": "abc123",
#   "resource_uri": "simple://abc123/data",
#   "preview": "[{\"id\": 0, ...}]...",
#   "metadata": {"item_count": 10, "size_bytes": 500}
# }

# Access full data via resource
data = await get_resource("abc123")
# Full data array
```

## Key Patterns Demonstrated

1. **Progressive Disclosure**: Tools discoverable via endpoints, not all loaded upfront
2. **Detail Levels**: Minimal → Brief → Full schemas
3. **Resource References**: Large data stored, references returned
4. **Metadata-First**: Preview + metadata without full data
5. **Relevance Scoring**: Search results ranked by relevance

## Token Comparison

### Traditional Approach
```python
# All tools registered upfront: ~5KB
# Total context: ~5000 tokens
```

### Progressive Approach
```python
# Discovery endpoints only: ~500 bytes
# Load tools on demand: ~1KB per tool
# Total context (using 1 tool): ~1500 tokens
# Savings: 70%
```

## Next Steps

See `full-featured-mcp/` for:
- Multiple categories
- Tag-based filtering
- Advanced resource management
- Comprehensive testing
- Performance benchmarks
