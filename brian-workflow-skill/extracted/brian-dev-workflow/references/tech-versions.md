# Technology Stack Versions

Current versions and key patterns for Brian's stack.

## Core Framework

### Next.js 15.5.6
**App Router patterns:**
```typescript
// Server Component (default)
export default async function Page() {
  const data = await fetchData();
  return <div>{data}</div>;
}

// Client Component
'use client';
export function ClientComponent() {
  const [state, setState] = useState();
  return <button onClick={() => setState(1)}>Click</button>;
}

// Server Action
async function submitAction(formData: FormData) {
  'use server';
  // Server-side logic
}
```

### React 19.2.0
**New patterns:**
```typescript
// Actions
<form action={serverAction}>...</form>

// use() hook
const data = use(promise);

// Optimistic updates
const [optimisticState, setOptimistic] = useOptimistic(state);
```

### TypeScript 5.3.3
**Strict config required:**
```json
{
  "strict": true,
  "noImplicitAny": true,
  "strictNullChecks": true,
  "noUncheckedIndexedAccess": true
}
```

## Backend

### Supabase (@supabase/supabase-js v2.39.0)
```typescript
// Server-side (preferred)
import { createClient } from '@/lib/supabase/server';
const supabase = createClient();

// Queries
const { data, error } = await supabase
  .from('table')
  .select('*, related(*)')
  .eq('column', 'value')
  .single();

// Mutations
const { data, error } = await supabase
  .from('table')
  .insert({ ... })
  .select();
```

### Payload CMS 3.61.1
```typescript
// payload.config.ts
import { buildConfig } from 'payload/config';
import { postgresAdapter } from '@payloadcms/db-postgres';

export default buildConfig({
  collections: [],
  db: postgresAdapter({
    pool: { connectionString: process.env.DATABASE_URL }
  })
});
```

## State & Forms

### Zustand 4.5.0
```typescript
import { create } from 'zustand';

interface Store {
  count: number;
  increment: () => void;
}

export const useStore = create<Store>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 }))
}));
```

### React Hook Form + Zod
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email()
});

type FormData = z.infer<typeof schema>;

const { register, handleSubmit } = useForm<FormData>({
  resolver: zodResolver(schema)
});
```

## UI

### Tailwind CSS 3.4.1
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  plugins: [require('tailwindcss-animate')]
};
```

### Radix UI + Framer Motion
```typescript
import * as Dialog from '@radix-ui/react-dialog';
import { motion } from 'framer-motion';

<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
  <Dialog.Root>...</Dialog.Root>
</motion.div>
```

## Testing

### Vitest
```typescript
// vitest.config.ts
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './tests/setup.ts'
  }
});
```

### Playwright
```typescript
// playwright.config.ts
export default defineConfig({
  testDir: './tests/e2e',
  use: { baseURL: 'http://localhost:3000' }
});
```

## Deployment

### Vercel
```json
// vercel.json
{
  "buildCommand": "pnpm build",
  "framework": "nextjs",
  "installCommand": "pnpm install"
}
```

**Environment variables:**
- Set in Vercel dashboard
- Prefix `NEXT_PUBLIC_` for client access
- Never commit `.env.local`

## Breaking Changes

**Next.js 14 → 15:**
- `next/image` optimization changes
- `next/link` no longer wraps `<a>`
- Dynamic imports syntax updated

**React 18 → 19:**
- Actions introduced
- New hooks: `use()`, `useOptimistic()`
- Concurrent rendering default

## MCP Development

### FastMCP (Python)
**Latest Version**: 0.4.0+
**Repository**: https://github.com/jlowin/fastmcp

**Installation**:
```bash
pip install fastmcp
```

**Basic Pattern**:
```python
from fastmcp import FastMCP

mcp = FastMCP("mcp-name")

@mcp.tool(name="mcp_tool_name")
async def tool_name(param: str) -> str:
    """Tool description"""
    return json.dumps({"result": "data"})

# Resource decorator
@mcp.resource("mcp://{resource_id}/content")
async def get_content(resource_id: str) -> str:
    return CACHE[resource_id]["data"]
```

### MCP SDK (TypeScript)
**Package**: @modelcontextprotocol/sdk
**Latest Version**: Check npm registry

**Installation**:
```bash
npm install @modelcontextprotocol/sdk
```

**Basic Pattern**:
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";

const server = new Server({
  name: "mcp-name",
  version: "1.0.0"
});

server.tool("mcp_tool_name", async (params) => {
  return { result: "data" };
});
```

### Model Context Protocol
**Specification**: https://spec.modelcontextprotocol.io/
**Current Version**: 2024-11-05

**Key Features**:
- Tools (function calling)
- Resources (data access)
- Prompts (templates)
- Sampling (LLM requests)

### Breaking Changes

**FastMCP 0.3 → 0.4**:
- Resource decorator syntax updated
- Tool response format standardized
- Async/await required for all tools

**MCP Spec 2024-10 → 2024-11**:
- Resource URIs now required format
- Discovery endpoints recommended
- Progressive disclosure patterns added
