# Migration Example: Legacy to Progressive MCP

This example demonstrates how to migrate an existing MCP from traditional patterns to progressive disclosure architecture.

## Overview

Shows the complete migration process:
1. **Before**: Legacy MCP with all tools registered upfront
2. **Migration Steps**: Incremental changes (non-breaking)
3. **After**: Modern progressive MCP

## Directory Structure

```
migration-example/
├── before/
│   └── legacy_server.py       # Original MCP
├── migration_steps/
│   ├── step1_add_discovery.py
│   ├── step2_add_resources.py
│   ├── step3_add_types.py
│   └── step4_deprecate_old.py
├── after/
│   └── modern_server.py       # Fully migrated
├── MIGRATION_GUIDE.md         # Detailed steps
└── README.md
```

## The Problem (Before)

### Legacy MCP Issues

```python
# legacy_server.py - ALL tools registered upfront

@mcp.tool("scrape")
async def scrape(url: str) -> str:
    html = fetch(url)  # 50KB
    return json.dumps({"html": html})  # All in context!

@mcp.tool("parse")
async def parse(html: str) -> str:
    data = parse_html(html)  # 25KB
    return json.dumps({"data": data})  # All in context!

# ... 20 more tools
```

**Problems**:
- 150KB+ of schemas loaded into every context
- Large data flowing through context
- No discovery mechanism
- No TypeScript definitions
- Poor error messages

**Impact**:
- ~40,000 tokens per conversation
- Slow initialization
- Can't scale beyond ~20 tools

## Migration Steps

### Step 1: Add Discovery (Non-Breaking)

```python
# step1_add_discovery.py
# Keep existing tools, add discovery alongside

# Existing tools remain registered
@mcp.tool("scrape")
async def scrape(url: str):
    # ... existing implementation

# NEW: Add discovery endpoints
@mcp.tool("legacy_list_tools")
async def list_tools(detail_level: str = "minimal"):
    # Return tool information
    pass

@mcp.tool("legacy_search_tools")
async def search_tools(query: str):
    # Search functionality
    pass
```

**Benefits**:
- Backward compatible
- New clients can use discovery
- Old clients still work

### Step 2: Add Resources (Non-Breaking)

```python
# step2_add_resources.py
# Add resource storage alongside existing returns

RESOURCE_STORE = {}

@mcp.tool("scrape")
async def scrape(url: str):
    html = fetch(url)

    # NEW: Store as resource
    resource_id = uuid.uuid4().hex
    RESOURCE_STORE[resource_id] = html

    # Return BOTH old and new formats
    return json.dumps({
        "html": html,  # OLD: For backward compatibility
        "resource_id": resource_id,  # NEW: For new clients
        "resource_uri": f"legacy://{resource_id}/content"
    })

@mcp.resource("legacy://{resource_id}/content")
async def get_resource(resource_id: str):
    return RESOURCE_STORE.get(resource_id)
```

**Benefits**:
- Backward compatible
- New clients get resource references
- Old clients get full data

### Step 3: Add TypeScript Definitions

```typescript
// tools/scrape.ts
// NEW: Add type definitions

export interface ScrapeInput {
  url: string;
}

export interface ScrapeOutput {
  resource_uri: string;
  preview: string;
  metadata: {
    size_bytes: number;
    url: string;
  };
}

// DEPRECATED: Old format
export interface LegacyScrapeOutput {
  html: string;
}
```

**Benefits**:
- Type safety for new clients
- Documentation
- Gradual adoption

### Step 4: Deprecate Old Patterns

```python
# step4_deprecate_old.py
# Add warnings, prepare for removal

@mcp.tool("scrape")
async def scrape(url: str, use_resources: bool = True):
    html = fetch(url)

    if use_resources:
        # NEW: Resource-based (recommended)
        resource_id = store_resource(html)
        return json.dumps({
            "resource_id": resource_id,
            "resource_uri": f"legacy://{resource_id}/content",
            "preview": html[:500]
        })
    else:
        # OLD: Direct return (deprecated)
        warnings.warn(
            "Direct HTML return is deprecated. "
            "Use use_resources=True for better performance.",
            DeprecationWarning
        )
        return json.dumps({"html": html})
```

**Benefits**:
- Gradual migration
- Clear deprecation path
- Metrics on adoption

### Step 5: Remove Legacy (Breaking)

```python
# after/modern_server.py
# Remove old patterns completely

# Discovery tools ONLY registered upfront
@mcp.tool("modern_list_tools")
async def list_tools(): pass

@mcp.tool("modern_search_tools")
async def search_tools(): pass

# Actual tools available via discovery
@mcp.tool("modern_scrape")  # Renamed
async def scrape(url: str):
    # Resource-only return
    resource_id = store_resource(html)
    return json.dumps({
        "resource_uri": f"modern://{resource_id}/content",
        "preview": html[:500]
    })
```

**Benefits**:
- Clean architecture
- No technical debt
- Optimal performance

## Migration Checklist

### Phase 1: Preparation (Week 1)
- [ ] Audit existing tools
- [ ] Identify large data responses
- [ ] Plan resource URI scheme
- [ ] Create TypeScript definitions
- [ ] Write migration guide

### Phase 2: Add Discovery (Week 2)
- [ ] Implement list_tools endpoint
- [ ] Implement search_tools endpoint
- [ ] Add category tagging
- [ ] Test discovery endpoints
- [ ] Document discovery usage

### Phase 3: Add Resources (Week 3)
- [ ] Implement resource storage
- [ ] Add resource endpoints
- [ ] Update tools to return resources
- [ ] Maintain backward compatibility
- [ ] Test resource access

### Phase 4: Deploy & Monitor (Week 4)
- [ ] Deploy to staging
- [ ] Monitor adoption metrics
- [ ] Collect feedback
- [ ] Fix issues
- [ ] Deploy to production

### Phase 5: Deprecation (Week 6-8)
- [ ] Add deprecation warnings
- [ ] Notify users
- [ ] Provide migration support
- [ ] Monitor old pattern usage
- [ ] Prepare for removal

### Phase 6: Cleanup (Week 10)
- [ ] Remove old patterns
- [ ] Remove backward compatibility code
- [ ] Update documentation
- [ ] Celebrate! 🎉

## Performance Comparison

### Before Migration

```
Initial context: 150KB (40,000 tokens)
Average conversation: 50,000 tokens
Tools: 20 (all upfront)
Discovery: None
Resources: None
```

### After Migration

```
Initial context: 2KB (500 tokens)
Average conversation: 3,000 tokens (94% reduction!)
Tools: 20 (via discovery)
Discovery: Yes (4 endpoints)
Resources: Yes (all large data)
```

## Code Examples

### Before: Direct Data Return

```python
@mcp.tool("scrape")
async def scrape(url: str):
    html = fetch(url)  # 50KB
    return json.dumps({"html": html})  # 50KB in context
```

### After: Resource Reference

```python
@mcp.tool("scrape")
async def scrape(url: str):
    html = fetch(url)  # 50KB
    resource_id = store_resource(html)
    return json.dumps({
        "resource_uri": f"mcp://{resource_id}/content",
        "preview": html[:500],  # Only 500 chars
        "size_bytes": len(html)
    })  # ~1KB in context
```

## Testing Migration

### Test Backward Compatibility

```python
def test_backward_compatibility():
    # Old clients should still work
    result = await scrape(url="https://example.com")
    assert "html" in result  # Old format
    assert "resource_uri" in result  # New format
```

### Test Progressive Migration

```python
def test_progressive_migration():
    # New clients use resources
    result = await scrape(url="https://example.com", use_resources=True)
    assert "resource_uri" in result
    assert "html" not in result  # No full data
```

### Test Discovery

```python
def test_discovery():
    # Discovery available
    tools = await list_tools()
    assert len(tools) > 0

    # Old tools findable
    results = await search_tools(query="scrape")
    assert len(results) > 0
```

## Common Migration Challenges

### Challenge 1: Existing Clients Break

**Solution**: Maintain backward compatibility for 3-6 months
```python
# Return both old and new formats
return json.dumps({
    "html": html,  # OLD
    "resource_uri": uri  # NEW
})
```

### Challenge 2: Performance During Migration

**Solution**: Gradual rollout with feature flags
```python
if feature_flag("use_resources"):
    return resource_format()
else:
    return legacy_format()
```

### Challenge 3: Large Codebase

**Solution**: Migrate tool-by-tool
```python
# Week 1: Migrate 5 most-used tools
# Week 2: Migrate next 5 tools
# Week 3: Migrate remaining tools
```

## Success Metrics

Track these metrics during migration:

1. **Token usage**: Should decrease 80-95%
2. **Resource adoption**: % of requests using resources
3. **Discovery usage**: % of clients using discovery
4. **Error rate**: Should remain constant
5. **Response time**: Should remain constant or improve

## Timeline

Typical migration timeline:
- **Small MCP** (5-10 tools): 2-4 weeks
- **Medium MCP** (10-20 tools): 4-6 weeks
- **Large MCP** (20+ tools): 6-12 weeks

## Resources

- **Full code examples**: See `before/` and `after/` directories
- **Step-by-step guide**: See `MIGRATION_GUIDE.md`
- **Migration scripts**: See `migration_steps/`

## Support

Questions about migration?
1. Review this example
2. Check the main skill documentation
3. Review `best-practices.md`
4. Test in staging environment first
