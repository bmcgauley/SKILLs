# MCP Architecture Skill

**Version**: 1.0.0
**Last Updated**: 2025-11-09
**License**: MIT

## Overview

The MCP Architecture Skill teaches Claude Code best practices for designing and implementing Model Context Protocol (MCP) servers with progressive disclosure, code execution support, and resource-based data access. This skill is essential for building token-efficient MCPs that enable agents to write code that composes multiple tool calls together.

## Purpose

Modern MCP architecture has evolved beyond traditional tool registration patterns. With code execution capabilities, agents can now:

1. **Discover tools on-demand** instead of loading all tools upfront
2. **Keep large data in execution environments** instead of passing through context
3. **Compose multiple tool calls** in agent-written scripts
4. **Access data via resources** instead of returning full payloads

This skill provides the patterns, examples, and best practices needed to implement these capabilities effectively.

## When to Use This Skill

Invoke this skill when you need to:

- **Design a new MCP server** from scratch
- **Refactor an existing MCP** for code execution support
- **Implement tool discovery endpoints** for progressive disclosure
- **Create resource-based data access** patterns
- **Define TypeScript interfaces** for tool inputs/outputs
- **Migrate from legacy MCP patterns** to modern architecture
- **Optimize token usage** in MCP implementations
- **Enable agent code composition** with your tools

## Key Concepts

### Progressive Disclosure

Instead of registering all tools upfront (which loads all schemas into context), MCPs should expose discovery endpoints that let agents find tools on-demand.

**Benefits**:
- Reduces initial context size by 90%+
- Enables dynamic tool discovery
- Supports large tool catalogs (50+ tools)
- Allows category-based browsing

### Resource-Based Data Access

Instead of returning large data directly in tool responses, MCPs should store data and return resource URIs that agents can access when needed.

**Benefits**:
- Keeps large data out of context
- Enables data reuse without re-transmission
- Supports streaming and partial access
- Allows data expiration and cleanup

### Code Composition

Tools should be atomic and composable, allowing agents to write scripts that chain multiple operations together.

**Benefits**:
- Reduces number of model calls needed
- Enables complex workflows
- Supports parallel operations
- Allows data transformation in execution environment

## Architecture Patterns

The skill covers four essential patterns:

### 1. Discovery Endpoint Pattern

Every MCP should implement `{mcp_name}_list_tools` with configurable detail levels:
- **Minimal**: Tool names only (fastest)
- **Brief**: Names + descriptions (for searching)
- **Full**: Complete schemas (for implementation)

### 2. Search Endpoint Pattern

Every MCP should implement `{mcp_name}_search_tools` for keyword-based tool discovery with:
- Query parameter for search terms
- Category filtering
- Relevance scoring

### 3. Resource Access Pattern

Tools that generate/fetch large data should:
- Store data with unique IDs
- Return resource URIs instead of full data
- Provide small previews for context
- Support expiration and cleanup

### 4. TypeScript Definition Pattern

All tools should have TypeScript interfaces defining:
- Input parameters with descriptions
- Output structure with metadata
- Usage examples
- Best practices

## Implementation Checklist

The skill provides three implementation levels:

### Minimum Viable Progressive MCP
Essential features for basic progressive disclosure.

### Full-Featured Progressive MCP
Complete implementation with all recommended features.

### Migration from Legacy MCP
Step-by-step guide for refactoring existing MCPs.

## Testing Requirements

The skill includes testing patterns for:
- Discovery endpoint verification
- Resource lifecycle testing
- Code execution simulation
- Token usage measurement

## Common Pitfalls

The skill identifies and corrects common mistakes:
- Returning large data directly
- No discovery mechanism
- Monolithic (non-composable) tools
- Missing TypeScript definitions
- Poor error messages

## Decision Trees

The skill provides decision frameworks for:
- When to create a new MCP vs. extend existing
- What detail level to use for different scenarios
- When to use resources vs. direct returns

## Directory Structure

```
mcp-architecture-skill/
├── mcp-architecture.skill       # Main skill file
├── SKILL.md                     # This documentation
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

## Reference Documents

### progressive-disclosure.md
Deep dive into progressive disclosure architecture, including:
- Why progressive disclosure matters
- Context window optimization
- Discovery vs. registration patterns
- Performance benchmarks

### tool-discovery-patterns.md
Detailed implementation guide for discovery endpoints:
- List tools implementation
- Search tools implementation
- Category management
- Filtering and sorting

### resource-management.md
Complete guide to resource-based data access:
- Storage strategies (in-memory, Redis, S3)
- Resource URI patterns
- Expiration and cleanup
- Access control

### type-definitions.md
TypeScript best practices for MCP tools:
- Interface design patterns
- Documentation conventions
- Example generation
- Type safety

### best-practices.md
Performance, security, and reliability guidelines:
- Token usage optimization
- Error handling patterns
- Rate limiting
- Security considerations

## Examples

### simple-discovery-mcp
A minimal working MCP demonstrating:
- Basic discovery endpoints
- Simple resource access
- TypeScript definitions
- Testing setup

**Use when**: Learning the fundamentals or building a simple MCP.

### full-featured-mcp
A complete MCP implementation with:
- All discovery patterns
- Advanced resource management
- Multiple categories
- Comprehensive testing
- Performance benchmarks

**Use when**: Building a production MCP or reference implementation.

### migration-example
A before/after example showing:
- Legacy MCP structure
- Migration steps
- Backward compatibility
- Deprecation strategy

**Use when**: Refactoring an existing MCP to modern patterns.

## Usage Examples

### Invoking the Skill

```
/skill mcp-architecture
```

### Example Tasks

**Design a new MCP**:
```
"Design a new file-analysis MCP with progressive disclosure"
```

**Implement discovery**:
```
"Implement the list_tools endpoint for my MCP"
```

**Add resource access**:
```
"Refactor my scraping tool to use resources instead of returning full HTML"
```

**Create TypeScript definitions**:
```
"Create TypeScript interfaces for my MCP tools"
```

## Integration with Other Skills

### brian-dev-workflow
The brian-dev-workflow skill includes MCP development guidelines that reference this skill for architecture patterns.

### code-execution-patterns
The code-execution-patterns skill teaches agents how to write code that uses MCPs built with these patterns.

## Success Metrics

Skills are effective when they:
- Reduce MCP implementation time by 50%+
- Ensure consistent architecture across MCPs
- Prevent common implementation mistakes
- Enable 90%+ token usage reduction
- Provide actionable code examples

## Maintenance and Updates

### Update Triggers
- MCP specification changes
- New patterns discovered
- Common issues identified
- Performance improvements found
- Community feedback

### Version History
- **1.0.0** (2025-11-09): Initial release

## Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **Code Execution Blog**: https://www.anthropic.com/engineering/code-execution-with-mcp
- **FastMCP Library**: https://github.com/jlowin/fastmcp
- **MCP Refactoring Guide**: `c:/github/mcps/MCP-REFACTORING-GUIDE.md`

## Contributing

To improve this skill:
1. Test with real MCP implementations
2. Document new patterns discovered
3. Add examples from production use
4. Share performance benchmarks
5. Provide feedback on clarity and completeness

## License

MIT License - Free to use, modify, and distribute.
