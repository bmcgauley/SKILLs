# Skills Development Guide: Code Execution & MCP Architecture

**Last Updated**: 2025-11-09
**Related**: See `c:/github/mcps/MCP-REFACTORING-GUIDE.md`

## Executive Summary

This guide outlines the new skills needed to support **code execution with MCP** architecture. These skills will teach Claude Code best practices for building progressive disclosure MCPs and using code execution patterns effectively.

---

## Current Skills Inventory

### brian-dev-workflow
**Location**: `c:/github/skills/brian-workflow-skill/`
**Purpose**: Full-stack development workflow for Next.js 15 + React 19 + Supabase
**Status**: Active, needs MCP section

### expert-systems
**Location**: `c:/github/skills/expert-systems/`
**Purpose**: Expert systems design and implementation guidance
**Status**: Active

---

## Required New Skills

### 1. mcp-architecture-skill

**Location**: `c:/github/skills/mcp-architecture-skill/`
**Purpose**: Teach progressive disclosure architecture patterns for MCP development
**Priority**: HIGH

#### Structure
```
mcp-architecture-skill/
├── mcp-architecture.skill       # Main skill file
├── SKILL.md                     # Detailed documentation
├── references/
│   ├── progressive-disclosure.md
│   ├── tool-discovery-patterns.md
│   ├── resource-management.md
│   ├── type-definitions.md
│   └── best-practices.md
└── examples/
    ├── simple-discovery-mcp/    # Minimal example
    ├── full-featured-mcp/       # Complete example
    └── migration-example/       # Refactoring example
```

#### Skill Content (.skill file)
```markdown
---
name: mcp-architecture
description: Guide for building MCPs with progressive disclosure, code execution support, and resource-based data access. Use when designing new MCPs or refactoring existing ones for better token efficiency.
license: MIT
---

# MCP Architecture Skill

## When to Use This Skill
- Designing a new MCP server
- Refactoring existing MCP for code execution
- Implementing tool discovery endpoints
- Creating resource-based data access
- Defining TypeScript interfaces for tools

## Core Principles

### Progressive Disclosure
Expose tools through discoverable structure, not upfront loading.

**Anti-Pattern**:
```python
# All tools loaded into context (150KB)
@mcp.tool("tool1")
@mcp.tool("tool2")
@mcp.tool("tool3")
# ... 50 more tools
```

**Correct Pattern**:
```python
@mcp.tool("list_tools")
async def list_tools(detail_level: str = "minimal"):
    """Agents discover tools on-demand"""

@mcp.tool("search_tools")
async def search_tools(query: str):
    """Agents search for relevant tools"""
```

### Resource-Based Data Access
Return references, not full data.

**Anti-Pattern**:
```python
return json.dumps({"content": large_25kb_content})
```

**Correct Pattern**:
```python
store_data(data_id, large_content)
return json.dumps({
    "data_id": data_id,
    "resource_uri": f"mcp://{data_id}/content",
    "preview": large_content[:500]
})
```

### Tool Design for Code Composition
Design tools to work in agent-written scripts.

**Anti-Pattern**:
```python
# Requires multiple model calls
@mcp.tool("scrape_and_save")
# Monolithic, no flexibility
```

**Correct Pattern**:
```python
@mcp.tool("scrape_url")  # Composable
@mcp.tool("save_content")  # Composable
# Agent can: content = scrape_url(url); save_content(content)
```

## Implementation Checklist

### Minimum Viable Progressive MCP
- [ ] `list_tools` endpoint with detail levels
- [ ] `search_tools` endpoint with query support
- [ ] TypeScript definitions in `tools/` directory
- [ ] At least one resource-based endpoint
- [ ] Clear naming convention: `{mcp_name}_{tool_name}`

### Full-Featured Progressive MCP
- [ ] All minimum viable features
- [ ] Category tagging for all tools
- [ ] Resource URIs with TTL/expiration
- [ ] Metadata-first responses
- [ ] Error handling with helpful messages
- [ ] Example scripts for code execution
- [ ] Performance benchmarks (token usage)

### Migration from Legacy MCP
- [ ] Add discovery endpoints (non-breaking)
- [ ] Create TypeScript definitions
- [ ] Add resource access (parallel to existing)
- [ ] Update responses to include references
- [ ] Deprecation warnings on old patterns
- [ ] Remove legacy patterns after adoption

## Architecture Patterns

### Pattern 1: Discovery Endpoint
```python
@mcp.tool(name="{mcp_name}_list_tools")
async def list_tools(
    detail_level: Literal["minimal", "brief", "full"] = "minimal",
    category: Optional[str] = None
) -> str:
    """
    List available tools with configurable detail.

    Args:
        detail_level:
            - minimal: Names only (fastest, for exploration)
            - brief: Names + descriptions (for searching)
            - full: Complete schemas (for implementation)
        category: Filter by category (e.g., "scraping", "analysis")

    Returns:
        JSON with tool information at requested detail level
    """
    pass
```

### Pattern 2: Search Endpoint
```python
@mcp.tool(name="{mcp_name}_search_tools")
async def search_tools(
    query: str,
    category: Optional[str] = None,
    max_results: int = 10
) -> str:
    """
    Search for tools by keyword.

    Args:
        query: Search term (searches name, description, tags)
        category: Optional category filter
        max_results: Limit results (default 10)

    Returns:
        JSON array of matching tools with relevance scores
    """
    pass
```

### Pattern 3: Resource Access
```python
# Storage (use Redis/cache in production)
RESOURCE_STORE = {}

@mcp.tool(name="generate_data")
async def generate_data(params: Params) -> str:
    # Generate/fetch large data
    data = expensive_operation(params)

    # Store with expiration
    resource_id = uuid.uuid4().hex
    RESOURCE_STORE[resource_id] = {
        "data": data,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }

    # Return reference
    return json.dumps({
        "resource_id": resource_id,
        "resource_uri": f"{MCP_NAME}://{resource_id}/data",
        "preview": str(data)[:500],
        "size_bytes": len(str(data)),
        "expires_in_seconds": 3600
    })

@mcp.resource("{MCP_NAME}://{resource_id}/data")
async def get_data(resource_id: str) -> str:
    """Retrieve full data by resource ID"""
    if resource_id not in RESOURCE_STORE:
        raise Exception(f"Resource {resource_id} not found or expired")
    return RESOURCE_STORE[resource_id]["data"]
```

### Pattern 4: TypeScript Definitions
Create `tools/{tool_name}.ts` for each tool:

```typescript
/**
 * [Tool description]
 *
 * Best for:
 * - Use case 1
 * - Use case 2
 *
 * @example
 * const result = await toolName({ param: "value" });
 */

export interface ToolNameInput {
  /** Description of required parameter */
  requiredParam: string;

  /** Description of optional parameter */
  optionalParam?: number;
}

export interface ToolNameOutput {
  /** Unique identifier */
  id: string;

  /** Resource URI for full data access */
  resource_uri: string;

  /** Small preview for context */
  preview: string;

  /** Metadata without full data */
  metadata: {
    size_bytes: number;
    created_at: string;
    [key: string]: any;
  };
}
```

## Testing Requirements

### Discovery Tests
```python
def test_list_tools_minimal():
    result = await list_tools(detail_level="minimal")
    assert isinstance(json.loads(result), list)

def test_search_tools():
    result = await search_tools(query="scrape")
    tools = json.loads(result)
    assert all("scrape" in t["name"].lower() for t in tools)
```

### Resource Tests
```python
async def test_resource_lifecycle():
    # Generate resource
    result = await generate_data(params)
    data = json.loads(result)

    # Access resource
    content = await get_resource(data["resource_uri"])
    assert content is not None

    # Check expiration (mock time if needed)
```

### Code Execution Simulation
```python
async def test_code_execution_pattern():
    # 1. Discover
    tools = await list_tools(detail_level="minimal")

    # 2. Search
    matches = await search_tools(query="relevant")

    # 3. Execute
    result = await tool_name(params)

    # 4. Access data
    data = await get_resource(result["resource_uri"])

    # Verify minimal context usage
    assert total_tokens_used < 5000
```

## Common Pitfalls

### ❌ Returning Large Data Directly
```python
# BAD
return json.dumps({"content": large_content})
```

### ✅ Returning References
```python
# GOOD
return json.dumps({
    "resource_uri": f"mcp://{id}/content",
    "preview": large_content[:500]
})
```

### ❌ No Discovery Mechanism
```python
# BAD - Agent must know all tool names upfront
```

### ✅ Searchable Tools
```python
# GOOD
@mcp.tool("list_tools")
@mcp.tool("search_tools")
```

### ❌ Monolithic Tools
```python
# BAD - Can't compose
@mcp.tool("fetch_process_and_save")
```

### ✅ Composable Tools
```python
# GOOD - Agent can mix and match
@mcp.tool("fetch")
@mcp.tool("process")
@mcp.tool("save")
```

## Decision Trees

### Should I create a new MCP or add to existing?

**Create new MCP if**:
- Different domain/category
- Different dependencies
- Independent lifecycle
- Different update cadence

**Add to existing MCP if**:
- Same domain
- Related functionality
- Shared dependencies
- Tools often used together

### What detail level for list_tools?

**Minimal** (names only):
- Initial exploration
- Counting/listing
- Quick checks

**Brief** (names + descriptions):
- Search/filter operations
- Discovery phase
- Category browsing

**Full** (complete schemas):
- Implementation
- Code generation
- Type checking

### When to use resources vs. direct returns?

**Use resources when**:
- Data > 1KB
- Data reused multiple times
- Want to keep data out of context
- Binary/large files

**Direct return when**:
- Data < 1KB
- Metadata/status
- One-time use
- Simple values

## References

See detailed guides in `references/`:
- `progressive-disclosure.md` - Deep dive on architecture
- `tool-discovery-patterns.md` - Discovery implementation
- `resource-management.md` - Resource handling
- `type-definitions.md` - TypeScript best practices
- `best-practices.md` - Performance & security

## Examples

See working examples in `examples/`:
- `simple-discovery-mcp/` - Minimal viable implementation
- `full-featured-mcp/` - All patterns implemented
- `migration-example/` - Refactoring legacy MCP
```

---

### 2. code-execution-patterns-skill

**Location**: `c:/github/skills/code-execution-patterns-skill/`
**Purpose**: Teach agents how to write code that effectively uses MCPs
**Priority**: HIGH

#### Structure
```
code-execution-patterns-skill/
├── code-execution-patterns.skill
├── SKILL.md
├── references/
│   ├── data-management.md
│   ├── pii-handling.md
│   ├── error-handling.md
│   ├── performance-optimization.md
│   └── testing-agent-code.md
└── examples/
    ├── scraping-pipeline.py      # Multi-step scraping
    ├── data-transformation.py    # Processing large data
    ├── pii-tokenization.py       # Handling sensitive data
    └── parallel-operations.py    # Concurrent execution
```

#### Skill Content (.skill file)
```markdown
---
name: code-execution-patterns
description: Patterns for writing agent code that effectively uses MCPs with code execution. Covers data management, tool composition, error handling, and performance optimization. Use when writing code that calls MCP tools.
license: MIT
---

# Code Execution Patterns Skill

## When to Use This Skill
- Writing agent code that calls MCP tools
- Composing multiple MCP calls together
- Managing large data between tool calls
- Handling PII or sensitive data
- Optimizing performance in agent scripts

## Core Patterns

### Pattern 1: Progressive Tool Discovery

**Before coding, discover tools**:
```python
# 1. List available tools
tools_list = await mcp.call("webscrape_list_tools", {
    "detail_level": "minimal"
})

# 2. Search for relevant tools
relevant_tools = await mcp.call("webscrape_search_tools", {
    "query": "crawl",
    "category": "scraping"
})

# 3. Load full schema only when needed
schema = await mcp.call("webscrape_search_tools", {
    "query": "crawl_site",
    "detail_level": "full"
})

# 4. Now implement
result = await mcp.call("webscrape_crawl_site", params)
```

### Pattern 2: Data Outside Context

**Keep large data in execution environment**:
```python
# ❌ BAD - Loads data into context
scraped_data = await mcp.call("scrape_url", {"url": url})
# scraped_data is 25KB in context

processed = process_large_data(scraped_data)  # In context!

await mcp.call("save_data", {"data": processed})  # Back through context


# ✅ GOOD - Data stays in execution environment
scrape_result = await mcp.call("scrape_url", {"url": url})
# Returns reference: {"resource_uri": "scrape://abc123/content"}

# Fetch data into execution environment
content = await mcp.get_resource(scrape_result["resource_uri"])
# Now content is in execution env, NOT context

# Process in execution environment
processed = process_large_data(content)  # Outside context

# Save directly
await mcp.call("save_data", {"data": processed})
```

### Pattern 3: Tool Composition

**Chain tools together in code**:
```python
# Multi-step workflow
async def scrape_and_analyze(url: str):
    # Step 1: Scrape
    scrape_result = await mcp.call("webscrape_scrape_url", {
        "url": url,
        "response_format": "markdown"
    })

    # Step 2: Get content
    content = await mcp.get_resource(scrape_result["resource_uri"])

    # Step 3: Extract links (in execution env)
    links = extract_links_from_markdown(content)

    # Step 4: Filter links (in execution env)
    external_links = [l for l in links if not is_same_domain(l, url)]

    # Step 5: Process each link
    results = []
    for link in external_links[:10]:  # Limit to 10
        link_result = await mcp.call("webscrape_scrape_url", {"url": link})
        results.append(link_result)

    return results
```

### Pattern 4: Parallel Execution

**Run independent operations concurrently**:
```python
import asyncio

async def scrape_multiple_urls(urls: List[str]):
    # Create tasks for parallel execution
    tasks = [
        mcp.call("webscrape_scrape_url", {"url": url})
        for url in urls
    ]

    # Execute in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    successful = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    return {
        "successful": len(successful),
        "failed": len(failed),
        "results": successful
    }
```

### Pattern 5: PII Tokenization

**Keep sensitive data out of context**:
```python
async def process_user_data(text_with_pii: str):
    # Tokenize PII before any context interaction
    tokenized = await mcp.call("helper_tokenize_pii", {
        "text": text_with_pii,
        "pii_types": ["email", "phone", "ssn"]
    })

    # Now safe to process in context
    token_map_id = tokenized["token_map_id"]
    safe_text = tokenized["tokenized_text"]

    # Analyze tokenized text
    analysis = analyze_text(safe_text)  # No PII in context

    # Detokenize only final results if needed
    if needs_original_data:
        final = await mcp.call("helper_detokenize_pii", {
            "text": analysis["result"],
            "token_map_id": token_map_id
        })
    else:
        final = analysis["result"]

    return final
```

### Pattern 6: Chunking Large Data

**Process large datasets in chunks**:
```python
async def process_large_dataset(data_uri: str):
    # Get dataset metadata without loading full data
    metadata = await mcp.call("get_data_metadata", {"uri": data_uri})

    if metadata["size_bytes"] > 1_000_000:  # > 1MB
        # Chunk the data
        chunk_result = await mcp.call("helper_chunk_data", {
            "data_uri": data_uri,
            "chunk_size": 100_000,  # 100KB chunks
            "overlap": 1000
        })

        # Process each chunk
        results = []
        for chunk_id in chunk_result["chunk_ids"]:
            chunk_data = await mcp.get_resource(f"chunk://{chunk_id}")
            processed = process_chunk(chunk_data)
            results.append(processed)

        # Combine results
        return combine_results(results)
    else:
        # Small enough to process directly
        data = await mcp.get_resource(data_uri)
        return process_data(data)
```

### Pattern 7: Error Handling

**Graceful failures with retries**:
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

            return result

        except Exception as e:
            if attempt == max_retries - 1:
                # Final attempt failed
                return {
                    "error": str(e),
                    "url": url,
                    "attempts": max_retries
                }

            # Wait before retry (exponential backoff)
            await asyncio.sleep(2 ** attempt)

    return None
```

### Pattern 8: Caching & Memoization

**Avoid redundant tool calls**:
```python
from functools import lru_cache

# Cache tool schemas
@lru_cache(maxsize=100)
async def get_tool_schema(mcp_name: str, tool_name: str):
    return await mcp.call(f"{mcp_name}_search_tools", {
        "query": tool_name,
        "detail_level": "full"
    })

# Cache scraped content
scraped_cache = {}

async def scrape_with_cache(url: str):
    if url in scraped_cache:
        print(f"Cache hit for {url}")
        return scraped_cache[url]

    result = await mcp.call("webscrape_scrape_url", {"url": url})
    scraped_cache[url] = result
    return result
```

## Before/After Examples

### Example 1: Web Scraping Pipeline

**Before (Inefficient)**:
```python
# All data flows through context
async def analyze_website(url: str):
    # 50KB in context
    page = await mcp.call("scrape", {"url": url})

    # Extract links (50KB still in context)
    links = await mcp.call("extract_links", {"html": page["content"]})

    # Scrape each link (hundreds of KB in context)
    link_contents = []
    for link in links["links"][:5]:
        content = await mcp.call("scrape", {"url": link})
        link_contents.append(content)

    # Analyze (all data in context)
    return analyze(page, link_contents)  # Context explosion!
```

**After (Efficient)**:
```python
# Data stays in execution environment
async def analyze_website(url: str):
    # Get reference (small)
    page_ref = await mcp.call("scrape", {"url": url})

    # Fetch into execution env
    page_content = await mcp.get_resource(page_ref["resource_uri"])

    # Extract links locally (not through context)
    links = extract_links_local(page_content)

    # Scrape links in parallel
    link_tasks = [
        mcp.call("scrape", {"url": link})
        for link in links[:5]
    ]
    link_refs = await asyncio.gather(*link_tasks)

    # Fetch all into execution env
    link_contents = [
        await mcp.get_resource(ref["resource_uri"])
        for ref in link_refs
    ]

    # Analyze locally (outside context)
    return analyze_local(page_content, link_contents)
```

**Token Savings**: 250KB → 5KB (98% reduction)

### Example 2: Data Transformation

**Before (Inefficient)**:
```python
# Transform through context
async def transform_data(input_file: str):
    # Load 1MB into context
    data = await mcp.call("load_file", {"path": input_file})

    # Transform in context
    transformed = await mcp.call("transform", {"data": data})

    # Save through context
    await mcp.call("save_file", {"data": transformed, "path": "output.json"})
```

**After (Efficient)**:
```python
# Transform in execution environment
async def transform_data(input_file: str):
    # Get file reference
    file_ref = await mcp.call("load_file", {"path": input_file})

    # Load into execution env
    data = await mcp.get_resource(file_ref["resource_uri"])

    # Transform locally
    transformed = transform_local(data)

    # Save directly (transformed data never in context)
    await mcp.call("save_file", {
        "data": transformed,
        "path": "output.json"
    })
```

**Token Savings**: 2MB → 2KB (99.9% reduction)

## Testing Agent Code

### Unit Test Pattern
```python
import pytest
from unittest.mock import AsyncMock, Mock

@pytest.mark.asyncio
async def test_scrape_and_analyze():
    # Mock MCP calls
    mock_mcp = Mock()
    mock_mcp.call = AsyncMock()
    mock_mcp.get_resource = AsyncMock()

    # Setup mock responses
    mock_mcp.call.return_value = {
        "resource_uri": "scrape://test123/content",
        "preview": "Test content..."
    }
    mock_mcp.get_resource.return_value = "<html>Test</html>"

    # Test function
    result = await scrape_and_analyze("https://example.com")

    # Assertions
    assert mock_mcp.call.called
    assert "resource_uri" in result
```

### Integration Test Pattern
```python
@pytest.mark.asyncio
async def test_full_pipeline():
    # Use real MCP (requires MCP server running)
    result = await scrape_and_analyze("https://example.com")

    # Verify structure
    assert "resource_uri" in result
    assert result["preview"]

    # Verify data accessible
    content = await mcp.get_resource(result["resource_uri"])
    assert len(content) > 0
```

## Performance Optimization

### Measure Token Usage
```python
def measure_tokens(func):
    async def wrapper(*args, **kwargs):
        start_tokens = get_context_size()

        result = await func(*args, **kwargs)

        end_tokens = get_context_size()
        tokens_used = end_tokens - start_tokens

        print(f"{func.__name__} used {tokens_used} tokens")
        return result

    return wrapper

@measure_tokens
async def my_pipeline(url: str):
    # Implementation
    pass
```

### Optimize Tool Discovery
```python
# ❌ Slow - Loads all schemas
all_tools = await mcp.call("list_tools", {"detail_level": "full"})

# ✅ Fast - Loads names only
tool_names = await mcp.call("list_tools", {"detail_level": "minimal"})
# Then load specific schemas as needed
schema = await mcp.call("search_tools", {
    "query": "specific_tool",
    "detail_level": "full"
})
```

### Batch Operations
```python
# ❌ Slow - Sequential
results = []
for url in urls:
    result = await mcp.call("scrape", {"url": url})
    results.append(result)

# ✅ Fast - Parallel
results = await asyncio.gather(*[
    mcp.call("scrape", {"url": url})
    for url in urls
])
```

## Common Pitfalls

### ❌ Loading Full Data Into Context
```python
# BAD
data = await mcp.call("get_data", {"id": 123})
process(data["content"])  # Large content in context
```

### ✅ Using Resources
```python
# GOOD
ref = await mcp.call("get_data", {"id": 123})
content = await mcp.get_resource(ref["resource_uri"])
process(content)  # In execution env
```

### ❌ No Error Handling
```python
# BAD
result = await mcp.call("tool", params)
# What if it fails?
```

### ✅ Graceful Errors
```python
# GOOD
try:
    result = await mcp.call("tool", params)
    if "error" in result:
        handle_error(result["error"])
except Exception as e:
    fallback_behavior()
```

### ❌ Not Leveraging Discovery
```python
# BAD - Assumes tool exists
await mcp.call("unknown_tool", params)  # May fail
```

### ✅ Discovery First
```python
# GOOD
tools = await mcp.call("list_tools", {"detail_level": "minimal"})
if "target_tool" in tools:
    await mcp.call("target_tool", params)
else:
    use_alternative_approach()
```

## References

See detailed guides in `references/`:
- `data-management.md` - Managing data outside context
- `pii-handling.md` - PII tokenization patterns
- `error-handling.md` - Resilient code patterns
- `performance-optimization.md` - Speed and efficiency
- `testing-agent-code.md` - Testing strategies

## Examples

See working examples in `examples/`:
- `scraping-pipeline.py` - Complete web scraping workflow
- `data-transformation.py` - Large data processing
- `pii-tokenization.py` - Sensitive data handling
- `parallel-operations.py` - Concurrent execution
```

---

### 3. Update brian-dev-workflow Skill

**Location**: `c:/github/skills/brian-workflow-skill/extracted/brian-dev-workflow/SKILL.md`
**Changes**: Add MCP development section

#### Content to Add

Add new section after line 100 (after "Feature Development Workflow"):

```markdown
## MCP Development Workflow

### When to Create an MCP

Create new MCP for:
- Distinct domain/capability (web scraping, audio processing, etc.)
- External service integration
- Reusable tool collection
- Tools that benefit from shared state/cache

### Research Phase for MCP Development

**CRITICAL: Research before designing MCP**

1. **Check Existing Patterns**
   - Review `mcp-architecture` skill
   - Study `code-execution-patterns` skill
   - Check MCP-REFACTORING-GUIDE.md in c:/github/mcps
   - Look at existing MCPs for patterns

2. **Plan Progressive Disclosure**
   - How will agents discover tools?
   - What categories make sense?
   - Which tools are commonly used together?
   - What data will be large (needs resources)?

3. **Design Tool Composition**
   - Can tools be chained in agent code?
   - Are tools atomic (single responsibility)?
   - Do tools return useful intermediate results?
   - Can operations run in parallel?

### MCP Architecture Requirements

**MUST HAVE**:
- [ ] Tool discovery endpoint (`{mcp}_list_tools`)
- [ ] Tool search endpoint (`{mcp}_search_tools`)
- [ ] TypeScript interface definitions (`tools/*.ts`)
- [ ] Resource-based data access for large data (>1KB)
- [ ] Clear naming convention: `{mcp_name}_{tool_name}`
- [ ] Category tags on all tools
- [ ] Metadata-first responses
- [ ] README with code execution examples

**SHOULD HAVE**:
- [ ] Caching with TTL for resources
- [ ] Error messages with suggestions
- [ ] Performance benchmarks (token usage)
- [ ] Unit and integration tests
- [ ] Migration guide (if refactoring existing MCP)

**NICE TO HAVE**:
- [ ] Multiple detail levels (minimal/brief/full)
- [ ] Parallel operation support
- [ ] Data chunking for very large datasets
- [ ] PII tokenization support

### MCP File Structure

Standard structure:
```
mcp-name/
├── server.py (or index.ts)        # Main MCP server
├── tools/
│   ├── tool1.ts                   # TypeScript definitions
│   ├── tool2.ts
│   └── index.ts                   # Discovery logic
├── tests/
│   ├── test_discovery.py
│   ├── test_resources.py
│   └── test_code_execution.py
├── examples/
│   └── agent_script.py            # Example usage
├── README.md                      # With code execution examples
└── requirements.txt (or package.json)
```

### Implementation Order

1. **Core Tools First**
   - Implement 1-3 most important tools
   - Add basic error handling
   - Test manually

2. **Add Discovery**
   - Implement `list_tools` endpoint
   - Implement `search_tools` endpoint
   - Create TypeScript definitions
   - Test discovery flow

3. **Add Progressive Disclosure**
   - Identify large data responses
   - Implement resource storage
   - Update tools to return references
   - Test resource access

4. **Testing & Examples**
   - Write unit tests
   - Write integration tests
   - Create agent code examples
   - Measure token usage

5. **Documentation**
   - Update README
   - Add inline documentation
   - Create migration guide (if applicable)

### Code Review Checklist

Before committing MCP code:

- [ ] All tools have `{mcp_name}_` prefix
- [ ] Discovery endpoints implemented
- [ ] TypeScript definitions created
- [ ] Large data uses resources, not direct returns
- [ ] Error messages are helpful
- [ ] Tests pass
- [ ] README has code execution examples
- [ ] Token usage measured and acceptable
- [ ] No secrets or API keys in code

### Testing MCP Code Execution

```bash
# Use MCP inspector
npx @modelcontextprotocol/inspector python server.py

# Or test with agent simulation
python test_code_execution.py
```

### Common MCP Mistakes

**❌ No Discovery**: Agents can't find tools
**❌ Large Responses**: Data in context, not resources
**❌ Monolithic Tools**: Can't compose in agent code
**❌ No TypeScript Defs**: Poor discoverability
**❌ Unclear Errors**: Hard to debug
**❌ No Examples**: Hard to understand usage

### MCP Deployment Checklist

- [ ] Server runs without errors
- [ ] All tools discoverable
- [ ] Resources accessible
- [ ] Tests passing
- [ ] Documentation complete
- [ ] Added to MCP registry (for mcp-discovery-server)
- [ ] Performance benchmarks documented
```

Also add to references section:

```markdown
### MCP Development
- See `mcp-architecture` skill for patterns
- See `code-execution-patterns` skill for agent code
- See `c:/github/mcps/MCP-REFACTORING-GUIDE.md` for implementation details
```

---

## Implementation Plan

### Phase 1: Skills Creation (Week 1)

**Task 1: mcp-architecture-skill**
- Create directory structure
- Write main .skill file
- Create reference documents:
  - `progressive-disclosure.md`
  - `tool-discovery-patterns.md`
  - `resource-management.md`
  - `type-definitions.md`
  - `best-practices.md`
- Create examples (simple, full-featured, migration)
- Test skill with Claude Code

**Task 2: code-execution-patterns-skill**
- Create directory structure
- Write main .skill file
- Create reference documents:
  - `data-management.md`
  - `pii-handling.md`
  - `error-handling.md`
  - `performance-optimization.md`
  - `testing-agent-code.md`
- Create example scripts
- Test skill with Claude Code

**Task 3: Update brian-dev-workflow**
- Add MCP development section
- Update research phase to include MCP patterns
- Add MCP code review checklist
- Add MCP testing guidelines
- Test updated skill

### Phase 2: Validation (Week 2)

- Use skills to refactor existing MCPs
- Collect feedback on skill effectiveness
- Update skills based on real usage
- Add more examples from actual implementations
- Document lessons learned

### Phase 3: Distribution (Week 3)

- Package skills for sharing
- Create quick-start guides
- Add video demonstrations (if applicable)
- Share with community
- Iterate based on feedback

---

## Testing Skills

### How to Test Skills

1. **Invoke skill in Claude Code**:
   ```
   /skill mcp-architecture
   ```

2. **Try a design task**:
   - "Design a new file-analysis MCP with progressive disclosure"
   - Verify skill guides through architecture decisions

3. **Try an implementation task**:
   - "Implement the discovery endpoint for webscrape_mcp"
   - Verify skill provides code templates

4. **Try a refactoring task**:
   - "Refactor midi_mcp to use resources instead of base64"
   - Verify skill guides through migration

### Success Criteria

Skills are successful if they:
- ✅ Reduce time to implement MCPs
- ✅ Ensure consistent architecture patterns
- ✅ Prevent common mistakes
- ✅ Provide actionable code examples
- ✅ Enable agent code execution patterns
- ✅ Improve token efficiency

---

## Maintenance

### When to Update Skills

Update skills when:
- MCP specification changes
- New patterns discovered
- Common issues identified
- Performance improvements found
- Better examples created
- User feedback received

### Versioning

Use semantic versioning:
- **Major**: Breaking changes to skill structure
- **Minor**: New patterns or examples added
- **Patch**: Bug fixes, clarifications

Track version in skill metadata:
```markdown
---
name: mcp-architecture
version: 1.0.0
updated: 2025-11-09
---
```

---

## Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **Code Execution Blog**: https://www.anthropic.com/engineering/code-execution-with-mcp
- **FastMCP Library**: https://github.com/jlowin/fastmcp
- **MCP Refactoring Guide**: `c:/github/mcps/MCP-REFACTORING-GUIDE.md`

---

## Appendix: Skill File Format

### Minimal .skill File
```markdown
---
name: skill-name
description: Brief description of what the skill teaches
license: MIT
---

# Skill Name

## When to Use This Skill
- Scenario 1
- Scenario 2

## Core Concepts

### Concept 1
Explanation and examples

### Concept 2
Explanation and examples

## Patterns

### Pattern 1
Code example

## Common Pitfalls

### ❌ Anti-Pattern
Bad example

### ✅ Correct Pattern
Good example
```

### Full .skill File
Includes:
- Metadata (name, description, version, license)
- When to use section
- Core concepts
- Patterns with code
- Before/after examples
- Testing guidelines
- Common pitfalls
- References to detailed docs
- Decision trees
- Checklists
