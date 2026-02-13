# Coding Standards

TypeScript and code quality standards.

## TypeScript Rules

### Strict Configuration (REQUIRED)
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### Never Use `any`
```typescript
// ❌ Bad
function process(data: any) {
  return data.value;
}

// ✅ Good
interface Data {
  value: string;
}
function process(data: Data): string {
  return data.value;
}

// ✅ Good (when type unknown)
function process(data: unknown): string {
  if (typeof data === 'object' && data !== null && 'value' in data) {
    return String(data.value);
  }
  throw new Error('Invalid data');
}
```

### Explicit Return Types
```typescript
// ❌ Bad
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// ✅ Good
interface Item {
  price: number;
}
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

### Discriminated Unions
```typescript
// ✅ Good for state management
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function handleState<T>(state: RequestState<T>) {
  switch (state.status) {
    case 'success':
      return <div>{state.data}</div>; // TypeScript knows data exists
    case 'error':
      return <Error message={state.error.message} />;
    // ...
  }
}
```

## Component Patterns

### Function Component
```typescript
// src/components/UserCard.tsx
import { FC } from 'react';

interface UserCardProps {
  user: {
    id: string;
    name: string;
    email: string;
  };
  onEdit: (userId: string) => void;
}

export const UserCard: FC<UserCardProps> = ({ user, onEdit }) => {
  return (
    <div className="rounded-lg border p-4">
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <button onClick={() => onEdit(user.id)}>Edit</button>
    </div>
  );
};
```

### Server vs Client Components
```typescript
// Server Component (default) - app/users/page.tsx
import { getUsers } from '@/lib/api';

export default async function UsersPage() {
  const users = await getUsers(); // Direct async
  return <UserList users={users} />;
}

// Client Component - app/users/UserList.tsx
'use client';
import { useState } from 'react';

export function UserList({ users }: { users: User[] }) {
  const [filter, setFilter] = useState('');
  return (
    <div>
      <input value={filter} onChange={(e) => setFilter(e.target.value)} />
      {users.filter(u => u.name.includes(filter)).map(...)}
    </div>
  );
}
```

### Custom Hooks
```typescript
// src/hooks/useAsync.ts
import { useState, useEffect } from 'react';

interface AsyncState<T> {
  data: T | null;
  error: Error | null;
  loading: boolean;
}

export function useAsync<T>(
  asyncFn: () => Promise<T>
): AsyncState<T> & { execute: () => Promise<void> } {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    error: null,
    loading: false
  });

  const execute = async () => {
    setState(prev => ({ ...prev, loading: true }));
    try {
      const data = await asyncFn();
      setState({ data, error: null, loading: false });
    } catch (error) {
      setState({
        data: null,
        error: error instanceof Error ? error : new Error('Unknown'),
        loading: false
      });
    }
  };

  useEffect(() => { execute(); }, []);
  return { ...state, execute };
}
```

## API Routes

### Error Handling
```typescript
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const paramsSchema = z.object({
  id: z.string().uuid()
});

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = paramsSchema.parse(params);
    const user = await getUserById(id);

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ user });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### Request Validation
```typescript
// app/api/users/route.ts
const createUserSchema = z.object({
  name: z.string().min(2).max(50),
  email: z.string().email(),
  role: z.enum(['admin', 'user'])
});

type CreateUserBody = z.infer<typeof createUserSchema>;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = createUserSchema.parse(body);
    const user = await createUser(validatedData);

    return NextResponse.json({ user }, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', details: error.errors },
        { status: 400 }
      );
    }
    return NextResponse.json({ error: 'Failed' }, { status: 500 });
  }
}
```

## Database Patterns

### Supabase Queries
```typescript
// lib/api/users.ts
import { createClient } from '@/lib/supabase/server';

interface User {
  id: string;
  name: string;
  email: string;
}

export async function getUsers(): Promise<User[]> {
  const supabase = createClient();
  
  const { data, error } = await supabase
    .from('users')
    .select('id, name, email')
    .order('created_at', { ascending: false });

  if (error) throw new Error(`Failed: ${error.message}`);
  return data;
}

export async function getUserById(id: string): Promise<User | null> {
  const supabase = createClient();
  
  const { data, error } = await supabase
    .from('users')
    .select('*')
    .eq('id', id)
    .maybeSingle();

  if (error) throw new Error(`Failed: ${error.message}`);
  return data;
}
```

## File Organization

```
src/
├── app/                # Next.js app directory
│   ├── (auth)/        # Route groups
│   ├── api/           # API routes
│   └── dashboard/     # Pages
├── components/        # React components
│   ├── ui/           # Base UI
│   └── features/     # Feature-specific
├── hooks/            # Custom hooks
├── lib/              # Utils, integrations
├── stores/           # Zustand stores
├── types/            # TypeScript types
└── middleware.ts     # Middleware
```

## Naming Conventions

- Components: `PascalCase` (UserCard.tsx)
- Hooks: `camelCase` (useUser.ts)
- Utils: `camelCase` (formatDate.ts)
- Types: `PascalCase` (User, UserRole)
- Constants: `UPPER_SNAKE` (MAX_RETRIES)
- Files (non-tsx): `kebab-case` (user-api.ts)

## ESLint Configuration

```javascript
// .eslintrc.js
module.exports = {
  extends: ['next/core-web-vitals'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/no-explicit-any': 'error',
    'prefer-const': 'error',
    'no-console': ['warn', { allow: ['warn', 'error'] }]
  }
};
```

## Performance

### Memoization
```typescript
import { useMemo, useCallback } from 'react';

function Component({ data }: { data: Item[] }) {
  const sorted = useMemo(() => 
    data.sort((a, b) => a.value - b.value),
    [data]
  );

  const handleClick = useCallback((id: string) => {
    console.log(id);
  }, []);

  return <div>{/* ... */}</div>;
}
```

### Dynamic Imports
```typescript
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <div>Loading...</div>,
  ssr: false
});
```

## Error Boundaries

```typescript
// components/ErrorBoundary.tsx
'use client';
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong</div>;
    }
    return this.props.children;
  }
}
```

## Git Commits

**Format:** `<type>: <description>`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `test`: Tests
- `refactor`: Code refactor
- `docs`: Documentation
- `chore`: Maintenance
- `perf`: Performance

**Examples:**
```
feat: add user authentication
fix: resolve dashboard loading issue
test: add tests for user API
refactor: simplify auth logic
```

## MCP Development Standards

### Naming Conventions

**Tool Names** (REQUIRED):
```python
# Good - includes MCP prefix
@mcp.tool(name="webscrape_scrape_url")
@mcp.tool(name="midi_convert_audio")

# Bad - no prefix
@mcp.tool(name="scrape")
@mcp.tool(name="convert")
```

**Resource URI Patterns** (REQUIRED):
```
Format: {mcp_name}://{resource_id}/{resource_type}

Examples:
- webscrape://abc123/content
- webscrape://abc123/metadata
- midi://def456/file
```

**File Structure**:
```
mcp-name/              # kebab-case
├── server.py          # snake_case
├── tools/
│   ├── tool_name.ts   # snake_case
│   └── index.ts
├── tests/
│   └── test_*.py      # test_ prefix
```

### Cache Configuration

**Constants** (REQUIRED):
```python
CACHE_TTL_SECONDS = 3600     # 1 hour
PREVIEW_LENGTH = 500         # Preview size
MAX_CACHE_SIZE_MB = 100      # Cache limit
MAX_CACHE_ENTRIES = 1000     # Entry limit
```

**TTL Guidelines**:
- Screenshots: 1800s (30 min)
- Scraped content: 3600s (1 hour)
- Generated files: 7200s (2 hours)
- Max: 86400s (24 hours)

### TypeScript Definition Standards

**Required Fields**:
```typescript
export interface ToolOutput {
  success: boolean;           // Status
  resource_id: string;        // ID
  resource_uri: string;       // URI
  preview: string;            // Preview (max 500 chars)
  content_length: number;     // Size
  expires_at: string;         // Expiration
}
```

### Response Format Standards

**Resource-Based** (data >1KB):
```python
return json.dumps({
    "success": True,
    "resource_id": resource_id,
    "resource_uri": f"{MCP_NAME}://{resource_id}/content",
    "preview": data[:500],
    "content_length": len(data),
    "expires_at": expires_at.isoformat()
})
```

**Direct Response** (data <1KB):
```python
return json.dumps({
    "status": "completed",
    "count": 42
})
```

### Performance Requirements

**Response Size Limits**:
- Discovery (minimal): <500 bytes
- Discovery (brief): <2KB
- Tool response: <2KB
- Error message: <500 bytes

**Token Reduction Targets**:
- Discovery: 99%+ reduction
- Single operation: 98%+ reduction
- Multi-step workflow: 97%+ reduction
