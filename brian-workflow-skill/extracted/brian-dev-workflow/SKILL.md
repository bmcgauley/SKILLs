---
name: brian-dev-workflow
description: Full-stack development workflow for Next.js 15 + React 19 + Supabase projects AND MCP development with progressive disclosure. Use when Brian requests help with web development, new features, debugging, testing, project setup, architecture decisions, OR creating/refactoring Model Context Protocol servers.
license: MIT
---

# Brian's Development Workflow

## Overview

Brian builds Next.js + React + Supabase applications AND Model Context Protocol (MCP) servers following rigorous senior-level workflows. This skill guides:
- **Web Development**: Project initialization, feature development, testing, deployment
- **MCP Development**: Progressive disclosure architecture, code execution patterns, token optimization

**Core principle**: Research before coding. Validate before committing. Test everything.

## Workflow Decision Tree

### Starting New Web Project
Use "Project Initialization" workflow

### Starting New MCP
Use "MCP Development Workflow" (see MCP section below)

### Adding Feature or Fixing Bug
Use "Feature Development" workflow

### Refactoring Existing MCP
Use "MCP Refactoring Workflow" (see MCP section below)

### Need Current Documentation
Use "Research Phase" workflow (ALWAYS before coding)

### Writing Tests
See [`testing-guide.md`](references/testing-guide.md) for patterns

### Code Quality Issues
See [`standards.md`](references/standards.md) for rules

### MCP Architecture Questions
See [`mcp-development.md`](references/mcp-development.md) for patterns

## Project Initialization

**ALWAYS** start with spec-kit for new projects:

```bash
git clone https://github.com/github/spec-kit.git project-name
cd project-name
rm -rf .git
git init
```

### Required Files

Create these immediately:
- `spec.md` - Technical specification (from spec-kit template)
- `plan.md` - Implementation phases and milestones
- `tasks.md` - Task tracking (synced with GitHub Issues)

### Specification Process

1. **Generate initial spec** from spec-kit template
2. **Ask clarifying questions** for ALL ambiguous items (CRITICAL: be thorough but concise)
3. **Document decisions** with clear acceptance criteria
4. **Create implementation plan** broken into phases
5. **Initialize task tracking** with GitHub Issues integration

Format for `tasks.md`:
```markdown
## In Progress
- [ ] Task description (#issue-number)

## Backlog
- [ ] Task description (#issue-number)

## Completed
- [x] Task description (#issue-number)
```

## Feature Development Workflow

### Phase 1: Research (MANDATORY before coding)

**NEVER skip this phase. NEVER trust assumptions.**

1. **Check for MCPs and Skills**
   ```bash
   # ALWAYS check available tools first
   # List available MCPs and skills before proceeding
   ```

2. **Research Current Best Practices**
   - Search web for latest official documentation
   - Verify patterns for exact versions in use
   - Check [`tech-versions.md`](references/tech-versions.md) for current stack
   - Use available documentation skills/MCPs

3. **Technology-Specific Research**
   - Next.js 15: App Router, Server Components, Server Actions
   - React 19: Actions, use() hook, optimistic updates
   - Supabase: Latest client patterns, RLS policies
   - See [`tech-versions.md`](references/tech-versions.md) for details

### Phase 2: Implementation

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/descriptive-name
   ```
   **NEVER push directly to main/master**

2. **Write Code Following Standards**
   - TypeScript strict mode (no `any` types)
   - Proper type safety and error handling
   - See [`standards.md`](references/standards.md) for patterns

3. **Write Tests FIRST or ALONGSIDE**
   - Unit tests (Vitest) for all business logic
   - Component tests (Testing Library) for UI
   - E2E tests (Playwright) for critical paths
   - See [`testing-guide.md`](references/testing-guide.md) for examples

4. **Validate Continuously**
   ```bash
   pnpm type-check
   pnpm lint
   pnpm test
   ```

### Phase 3: Quality Assurance

**Before committing, ALWAYS run:**

```bash
pnpm test:all  # Runs: type-check + lint + test + test:e2e
```

**Commit only when:**
- ✅ All tests pass
- ✅ No TypeScript errors
- ✅ No ESLint warnings
- ✅ Build succeeds locally

### Phase 4: Git Workflow

1. **Commit with Conventional Commits**
   ```bash
   git add .
   git commit -m "feat: descriptive message"
   ```
   Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`

2. **Push to Feature Branch**
   ```bash
   git push origin feature/descriptive-name
   ```

3. **Update Task Tracking**
   - Mark tasks complete in `tasks.md`
   - Update related GitHub Issues
   - Keep both in sync

4. **Create Pull Request**
   - Clear description referencing issues
   - Request review from Brian (Human In Loop)
   - **Wait for approval before merging**

## MCP Development Workflow

**IMPORTANT**: Creating an MCP is fundamentally different from web development. MCPs provide tools and resources to AI agents, requiring progressive disclosure architecture for optimal performance (98-99% token reduction).

### When to Create an MCP vs Skill

**Create MCP when:**
- Building reusable tools for AI agents
- Integrating with external services/APIs
- Processing data that agents need access to
- Creating composable operations (scraping, file processing, etc.)
- Tools share state or caching requirements

**Create Skill when:**
- Teaching workflow or methodology
- Documenting best practices
- Providing decision trees and checklists
- Guiding implementation approach
- No code execution needed

### MCP Research Phase (CRITICAL - NEVER SKIP)

**Study patterns before designing ANY MCP:**

1. **Study MCP Architecture**
   - Read `c:/github/mcps/MCP-REFACTORING-GUIDE.md` (comprehensive guide)
   - Review [`mcp-development.md`](references/mcp-development.md) (patterns reference)
   - Study webscrape_mcp refactoring example (real-world implementation)

2. **Check for Existing MCPs**
   - Search for similar functionality
   - Evaluate whether to extend existing MCP vs create new
   - Review MCP registry if available

3. **Plan Progressive Disclosure Architecture**
   - How will agents discover tools? (list/search endpoints)
   - What categories make sense?
   - Which responses will be large? (need resources)
   - What data needs caching? (TTL strategy)

4. **Design for Code Execution**
   - Can tools be composed in agent scripts?
   - Are tools atomic (single responsibility)?
   - Do tools return references vs full data?
   - Can operations run in parallel?

### MCP Design Phase

1. **Define Tool Interface**
   - List all tools needed
   - Define input/output schemas
   - Plan tool naming: `{mcp_name}_{tool_name}`
   - Categorize tools (scraping, extraction, analysis, etc.)

2. **Plan Resource Architecture**
   ```
   Tool Response Pattern (REQUIRED for data >1KB):
   {
     "success": true,
     "resource_id": "abc123",
     "resource_uri": "mcp://abc123/content",
     "preview": "First 500 chars...",
     "metadata": { "size": 25000, "created_at": "..." },
     "expires_in_seconds": 3600
   }
   ```

3. **Design Discovery Endpoints**
   - `{mcp_name}_list_tools` with detail levels (minimal/brief/full)
   - `{mcp_name}_search_tools` with query and category filters
   - Tool metadata structure with categories and descriptions

4. **Plan Caching Strategy**
   - What data to cache (scraped content, generated files, etc.)
   - Cache TTL (typically 1 hour = 3600 seconds)
   - Cache cleanup mechanism
   - Storage backend (in-memory for dev, Redis for production)

### MCP Implementation Phase

1. **Setup Project Structure**
   ```
   mcp-name/
   ├── server.py (or index.ts)
   ├── tools/
   │   ├── tool1.ts              # TypeScript definitions
   │   ├── tool2.ts
   │   └── index.ts              # Discovery helpers
   ├── tests/
   │   ├── test_discovery.py
   │   ├── test_resources.py
   │   └── test_integration.py
   ├── examples/
   │   └── agent_usage.py        # Code execution examples
   ├── README.md
   ├── ARCHITECTURE.md           # Progressive disclosure docs
   └── requirements.txt (or package.json)
   ```

2. **Implement Core Infrastructure**
   ```python
   # Cache setup
   from datetime import datetime, timedelta
   import hashlib
   import time

   CACHE_TTL_SECONDS = 3600  # 1 hour
   PREVIEW_LENGTH = 500      # Preview size
   RESOURCE_CACHE = {}

   def _generate_resource_id(data: str) -> str:
       """Generate unique ID for cached resource"""
       return hashlib.md5(data.encode()).hexdigest()

   def _store_in_cache(resource_id: str, data: Any, metadata: dict):
       """Store data with TTL"""
       RESOURCE_CACHE[resource_id] = {
           "data": data,
           "metadata": metadata,
           "created_at": datetime.utcnow(),
           "expires_at": datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS)
       }

   def _clean_expired_cache():
       """Remove expired cache entries"""
       now = datetime.utcnow()
       expired = [k for k, v in RESOURCE_CACHE.items() if v["expires_at"] < now]
       for key in expired:
           del RESOURCE_CACHE[key]
   ```

3. **Implement Discovery Tools**
   ```python
   @mcp.tool(name="{mcp_name}_list_tools")
   async def list_tools(
       detail_level: str = "minimal",
       category: Optional[str] = None
   ) -> str:
       """
       List available tools with configurable detail.

       Args:
           detail_level: "minimal" (names only), "brief" (names + descriptions),
                        "full" (complete schemas)
           category: Optional filter (e.g., "scraping", "analysis")

       Returns:
           JSON with tool information
       """
       tools = {
           "tool1": {
               "name": "{mcp_name}_tool1",
               "description": "Tool description",
               "category": "category_name"
           },
           # ... other tools
       }

       if category:
           tools = {k: v for k, v in tools.items() if v.get("category") == category}

       if detail_level == "minimal":
           return json.dumps(list(tools.keys()))
       elif detail_level == "brief":
           return json.dumps([{k: v for k, v in t.items() if k != "schema"}
                             for t in tools.values()])
       else:  # full
           return json.dumps(tools, indent=2)

   @mcp.tool(name="{mcp_name}_search_tools")
   async def search_tools(query: str, category: Optional[str] = None) -> str:
       """
       Search for tools by keyword.

       Args:
           query: Search term (searches name, description, tags)
           category: Optional category filter

       Returns:
           JSON array of matching tools
       """
       # Implementation: search by query in tool metadata
       pass
   ```

4. **Implement Resource Endpoints**
   ```python
   @mcp.resource("{mcp_name}://{resource_id}/content")
   async def get_resource_content(resource_id: str) -> str:
       """Retrieve full content by resource ID"""
       _clean_expired_cache()

       if resource_id not in RESOURCE_CACHE:
           raise Exception(
               f"Resource {resource_id} not found or expired. "
               f"Resources expire after {CACHE_TTL_SECONDS} seconds."
           )

       return RESOURCE_CACHE[resource_id]["data"]

   @mcp.resource("{mcp_name}://{resource_id}/metadata")
   async def get_resource_metadata(resource_id: str) -> str:
       """Retrieve metadata without full content"""
       _clean_expired_cache()

       if resource_id not in RESOURCE_CACHE:
           raise Exception(f"Resource {resource_id} not found or expired")

       entry = RESOURCE_CACHE[resource_id]
       return json.dumps({
           "resource_id": resource_id,
           "metadata": entry["metadata"],
           "created_at": entry["created_at"].isoformat(),
           "expires_at": entry["expires_at"].isoformat()
       })
   ```

5. **Update Tools to Return Resources**
   ```python
   @mcp.tool(name="{mcp_name}_process_data")
   async def process_data(params: ProcessDataInput) -> str:
       """Process data and return resource reference"""

       # Perform operation (scraping, generation, etc.)
       full_data = perform_operation(params)

       # Generate ID and store
       resource_id = _generate_resource_id(str(full_data))
       _store_in_cache(
           resource_id,
           full_data,
           metadata={"size": len(full_data), "format": params.format}
       )

       # Return reference (NOT full data)
       return json.dumps({
           "success": True,
           "resource_id": resource_id,
           "resource_uri": f"{MCP_NAME}://{resource_id}/content",
           "metadata_uri": f"{MCP_NAME}://{resource_id}/metadata",
           "preview": str(full_data)[:PREVIEW_LENGTH] + "...",
           "content_length": len(full_data),
           "expires_at": (
               datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS)
           ).isoformat()
       })
   ```

6. **Create TypeScript Definitions**
   ```typescript
   // tools/tool_name.ts
   /**
    * Process data with specified parameters
    *
    * Best for:
    * - Use case 1
    * - Use case 2
    *
    * @example
    * const result = await processData({ param: "value" });
    * const content = await getResource(result.resource_uri);
    */
   export interface ProcessDataInput {
     /** Required parameter description */
     param: string;

     /** Optional parameter with default */
     format?: "json" | "text" | "markdown";
   }

   export interface ProcessDataOutput {
     /** Operation success status */
     success: boolean;

     /** Unique identifier for this resource */
     resource_id: string;

     /** URI to fetch full content */
     resource_uri: string;

     /** URI to fetch metadata only */
     metadata_uri: string;

     /** Preview of content (first 500 chars) */
     preview: string;

     /** Total content length in bytes */
     content_length: number;

     /** ISO timestamp when resource expires */
     expires_at: string;
   }
   ```

### MCP Testing Phase

1. **Unit Tests**
   ```python
   import pytest
   import json

   def test_list_tools_minimal():
       result = await list_tools(detail_level="minimal")
       tools = json.loads(result)
       assert isinstance(tools, list)
       assert len(tools) > 0
       assert all(isinstance(t, str) for t in tools)

   def test_search_tools():
       result = await search_tools(query="process")
       tools = json.loads(result)
       assert len(tools) > 0
       assert all("process" in t["name"].lower() for t in tools)
   ```

2. **Resource Tests**
   ```python
   async def test_resource_lifecycle():
       # Generate resource
       result = await process_data(ProcessDataInput(param="test"))
       data = json.loads(result)

       # Verify reference returned (not full data)
       assert "resource_uri" in data
       assert "preview" in data
       assert len(json.dumps(data)) < 2000  # Response under 2KB

       # Access resource
       content = await get_resource_content(data["resource_id"])
       assert len(content) > len(data["preview"])

       # Verify metadata access
       metadata = await get_resource_metadata(data["resource_id"])
       assert "created_at" in metadata
   ```

3. **Token Usage Measurement**
   ```python
   async def test_token_efficiency():
       # Execute tool
       result = await process_data(params)
       response_size = len(json.dumps(result))

       # Resource-based response should be <2KB
       assert response_size < 2000

       # Calculate savings vs returning full data
       full_data_size = 25000  # Example large data
       savings_percent = ((full_data_size - response_size) / full_data_size) * 100

       # Target: 98%+ reduction
       assert savings_percent >= 98
   ```

4. **Integration Tests**
   ```python
   async def test_code_execution_pattern():
       # Simulate complete agent workflow
       # 1. Discover tools
       tools = await list_tools(detail_level="minimal")
       assert len(json.loads(tools)) > 0

       # 2. Search for relevant tool
       search = await search_tools(query="process")
       assert len(json.loads(search)) > 0

       # 3. Execute tool
       result = await process_data(params)
       data = json.loads(result)

       # 4. Access data via resource
       content = await get_resource_content(data["resource_id"])
       assert content is not None

       # Verify minimal context usage
       total_bytes = len(json.dumps(tools)) + len(json.dumps(result))
       assert total_bytes < 5000  # Total workflow under 5KB
   ```

### MCP Documentation Phase

1. **README.md Structure**
   ```markdown
   # MCP Name

   ## Overview
   Brief description, purpose, and key features

   ## Installation
   ```bash
   pip install -r requirements.txt
   # Or: npm install
   ```

   ## Tools
   ### Discovery Tools
   - `{mcp_name}_list_tools` - List available tools
   - `{mcp_name}_search_tools` - Search for tools

   ### Core Tools
   - `{mcp_name}_tool1` - Description
   - `{mcp_name}_tool2` - Description

   ## Progressive Disclosure
   This MCP implements progressive disclosure for optimal token efficiency:
   - Tools return resource URIs instead of full data
   - Agents discover tools on-demand via list/search
   - TypeScript definitions available in `tools/` directory
   - Achieves 98%+ token reduction vs direct data returns

   ## Code Execution Examples
   ```python
   # Example 1: Discover and use tools
   tools = await list_tools(detail_level="minimal")
   result = await process_data({"param": "value"})
   content = await get_resource(result["resource_uri"])
   ```

   ## Architecture
   - Resource URI pattern: `{mcp_name}://{resource_id}/{type}`
   - Cache TTL: 3600 seconds (1 hour)
   - Preview length: 500 characters
   - Token savings: 98%+

   ## Performance Metrics
   - Discovery: 200B vs 150KB (99.9% reduction)
   - Tool responses: 500B vs 25KB (98% reduction)
   - Full workflow: 2-5KB vs 175KB (97-99% reduction)
   ```

2. **ARCHITECTURE.md**
   ```markdown
   # Architecture

   ## Progressive Disclosure Pattern
   [Explain resource-based architecture]

   ## Tool Discovery Flow
   [Diagram showing agent discovery workflow]

   ## Resource Management
   [Explain caching, TTL, cleanup]

   ## TypeScript Definitions
   [How agents load type definitions on-demand]
   ```

3. **Integration Examples**
   ```python
   # examples/agent_usage.py
   """
   Example: Complete workflow using {mcp_name}

   This demonstrates:
   - Tool discovery
   - Resource-based data access
   - Token-efficient patterns
   """

   async def example_workflow():
       # 1. Discover tools
       tools = await list_tools(detail_level="minimal")
       print(f"Available tools: {tools}")

       # 2. Search for specific functionality
       relevant = await search_tools(query="process")
       print(f"Found: {relevant}")

       # 3. Execute tool
       result = await process_data({"param": "example"})
       print(f"Result: {result['preview']}")

       # 4. Access full content on-demand
       content = await get_resource(result["resource_uri"])
       print(f"Full content: {len(content)} bytes")

       # 5. Process data locally (outside context)
       processed = analyze_content(content)
       return processed
   ```

### MCP Quality Checklist

**Before Committing:**
- [ ] All tools have `{mcp_name}_` prefix
- [ ] Discovery endpoints implemented (list_tools, search_tools)
- [ ] TypeScript definitions created for all tools
- [ ] Large responses (>1KB) use resources, not direct returns
- [ ] Resource endpoints handle expiration gracefully
- [ ] Error messages are clear and helpful
- [ ] Cache cleanup mechanism implemented
- [ ] Tests pass (unit, integration, token usage)
- [ ] README has code execution examples
- [ ] ARCHITECTURE.md documents patterns
- [ ] Token reduction measured (target: 98%+)
- [ ] No secrets or API keys in code
- [ ] Example scripts in examples/ directory

### Common MCP Pitfalls

**NEVER:**
- ❌ Return large data directly in tool responses
- ❌ Skip discovery endpoints (agents can't find tools)
- ❌ Use monolithic tools (breaks composability)
- ❌ Forget TypeScript definitions (poor discoverability)
- ❌ Skip token usage testing (may not achieve savings)
- ❌ Hardcode cache TTLs without constants
- ❌ Ignore cache cleanup (memory leaks)
- ❌ Use unclear resource URI patterns

**ALWAYS:**
- ✅ Return resource URIs for data >1KB
- ✅ Implement searchable tool discovery
- ✅ Create atomic, composable tools
- ✅ Provide TypeScript interfaces
- ✅ Measure token reduction (target 98%+)
- ✅ Use configurable constants (CACHE_TTL_SECONDS, PREVIEW_LENGTH)
- ✅ Implement cache expiration and cleanup
- ✅ Follow resource URI pattern: `{mcp_name}://{id}/{type}`
- ✅ Include helpful error messages with suggestions

### MCP Deployment

1. **Local Testing**
   ```bash
   # Test with MCP inspector
   npx @modelcontextprotocol/inspector python server.py

   # Or test programmatically
   python tests/test_integration.py
   ```

2. **Configuration**
   ```json
   // Claude Code MCP settings
   {
     "mcps": {
       "{mcp_name}": {
         "command": "python",
         "args": ["c:/path/to/server.py"],
         "env": {
           "CACHE_TTL": "3600"
         }
       }
     }
   }
   ```

3. **Monitoring**
   - Track cache hit rates
   - Measure token savings
   - Monitor resource expiration patterns
   - Log error rates and types

### MCP vs Web Development

| Aspect | Web Development | MCP Development |
|--------|----------------|-----------------|
| **Output** | User interfaces | Tools for agents |
| **Architecture** | Components, routes | Progressive disclosure |
| **Data Flow** | Request/response | Resource references |
| **Optimization** | Page load speed | Token efficiency (98%+) |
| **Testing** | UI tests, E2E | Token usage, discovery |
| **Documentation** | User guides | Code execution examples |
| **Caching** | Page caching | Resource caching with TTL |
| **Performance Goal** | <3s load time | <2KB responses |

## Technology Stack

Current versions (see [`tech-versions.md`](references/tech-versions.md) for details):

**Core Framework**
- Next.js 15.5.6 (App Router)
- React 19.2.0
- TypeScript 5.3.3 (strict mode)

**Backend**
- Supabase (PostgreSQL, Auth, Storage)
- Payload CMS 3.61.1

**State & Forms**
- Zustand 4.5.0
- React Hook Form 7.65.0
- Zod 3.25.76

**UI**
- Tailwind CSS 3.4.1
- Radix UI
- Framer Motion 11.0.0

**Testing**
- Vitest (unit/integration)
- Playwright (E2E)
- Testing Library (components)

**Deployment**
- Vercel (hosting)
- Supabase (database)

**MCP Development**
- FastMCP (Python MCPs)
- MCP SDK (@modelcontextprotocol/sdk, TypeScript MCPs)
- Model Context Protocol Specification

## Critical Rules

### NEVER
- ❌ Push directly to main/master
- ❌ Skip tests for new features
- ❌ Use `any` type in TypeScript
- ❌ Trust assumptions without verification
- ❌ Commit code that fails CI
- ❌ Skip research phase
- ❌ Return large data directly in MCP responses
- ❌ Create MCP without discovery endpoints
- ❌ Skip token usage measurement for MCPs

### ALWAYS
- ✅ Create feature branch first
- ✅ Check MCPs/skills before coding
- ✅ Research latest documentation
- ✅ Write tests alongside code
- ✅ Use strict TypeScript
- ✅ Validate locally before commit
- ✅ Ask clarifying questions
- ✅ Sync tasks.md with GitHub Issues
- ✅ Wait for PR approval
- ✅ Use resource URIs for MCP data >1KB
- ✅ Implement progressive disclosure for MCPs
- ✅ Measure token reduction (target 98%+)

## Common Patterns

### Component Structure
```typescript
// src/components/Feature/ComponentName.tsx
import { FC } from 'react';

interface ComponentNameProps {
  prop: string;
}

export const ComponentName: FC<ComponentNameProps> = ({ prop }) => {
  return <div>{prop}</div>;
};
```

### API Routes (Next.js 15)
```typescript
// app/api/route/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Logic
    return NextResponse.json({ data });
  } catch (error) {
    return NextResponse.json({ error: 'Message' }, { status: 500 });
  }
}
```

### Supabase Queries
```typescript
import { createClient } from '@/lib/supabase/server';

const supabase = createClient();
const { data, error } = await supabase
  .from('table')
  .select('*')
  .eq('id', id)
  .single();
```

### MCP Tool Pattern
```python
@mcp.tool(name="{mcp_name}_tool_name")
async def tool_name(params: ToolInput) -> str:
    """Tool description for discovery"""
    # Perform operation
    result_data = process(params)

    # Store in cache
    resource_id = _generate_resource_id(result_data)
    _store_in_cache(resource_id, result_data, metadata={})

    # Return reference
    return json.dumps({
        "resource_id": resource_id,
        "resource_uri": f"{MCP_NAME}://{resource_id}/content",
        "preview": str(result_data)[:500]
    })
```

## Package Management

**ALWAYS use pnpm for web projects:**
```bash
pnpm install <package>
pnpm dev
pnpm build
pnpm test
```

**Use pip for Python MCPs:**
```bash
pip install -r requirements.txt
pip install fastmcp
```

## Build Commands

### Web Development
```bash
pnpm dev              # Development server
pnpm build            # Production build
pnpm start            # Production server
pnpm type-check       # TypeScript validation
pnpm lint             # ESLint
pnpm lint:fix         # Auto-fix linting
pnpm format           # Prettier
pnpm test             # Unit tests
pnpm test:watch       # Watch mode
pnpm test:e2e         # E2E tests
pnpm test:all         # Full validation suite
```

### MCP Development
```bash
python server.py                           # Run MCP server
python tests/test_integration.py          # Run tests
npx @modelcontextprotocol/inspector python server.py  # MCP inspector
```

## Reference Files

**Detailed documentation in references directory:**

- [`tech-versions.md`](references/tech-versions.md) - Current versions, breaking changes, patterns
- [`testing-guide.md`](references/testing-guide.md) - Test examples and best practices
- [`standards.md`](references/standards.md) - TypeScript rules, code patterns, style guide
- [`mcp-development.md`](references/mcp-development.md) - MCP architecture patterns, progressive disclosure, code execution

**External References:**
- `c:/github/mcps/MCP-REFACTORING-GUIDE.md` - Comprehensive MCP refactoring guide
- `c:/github/mcps/webscrape_mcp/REFACTORING-COMPLETE.md` - Real-world MCP example

## Senior Developer Mindset

Approach every task as a **senior developer with decades of experience**:

- **Methodical**: Follow the process, don't skip steps
- **Thorough**: Research, validate, test everything
- **Efficient**: Move fast without sacrificing quality
- **Communicative**: Ask questions, explain decisions
- **Pragmatic**: Balance perfection with deadlines

**When time-crunched**: Maintain quality standards but scope intelligently. Better to deliver a fully-tested MVP than a buggy feature-complete product.

**For MCP Development**: Prioritize token efficiency and progressive disclosure. A well-architected MCP with 98% token reduction is worth the extra design effort.

## Environment Variables

### Web Development
Required for all projects:
```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Vercel (auto-injected)
VERCEL_URL=
```

### MCP Development
```env
# MCP Configuration
CACHE_TTL_SECONDS=3600
PREVIEW_LENGTH=500
LOG_LEVEL=INFO
```

## Deployment

### Web Applications
Vercel handles deployment automatically:
1. Push to main branch (after PR approval)
2. Vercel builds and deploys
3. Monitor deployment logs
4. Verify production functionality

### MCP Servers
1. Test locally with MCP inspector
2. Configure in Claude Code MCP settings
3. Monitor cache performance
4. Track token savings metrics
