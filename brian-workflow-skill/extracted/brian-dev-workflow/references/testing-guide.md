# Testing Guide

Test patterns and examples for the stack.

## Test Strategy

```
E2E (Playwright)      - Critical user paths only
Integration (Vitest)  - Component interactions
Unit (Vitest)         - Business logic, utils, hooks
```

## Unit Testing

### Utilities
```typescript
// src/utils/formatDate.ts
export function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US');
}

// tests/utils/formatDate.test.ts
import { describe, it, expect } from 'vitest';
import { formatDate } from '@/utils/formatDate';

describe('formatDate', () => {
  it('formats date correctly', () => {
    const date = new Date('2024-01-15');
    expect(formatDate(date)).toBe('1/15/2024');
  });
});
```

### Custom Hooks
```typescript
// tests/hooks/useDebounce.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { useDebounce } from '@/hooks/useDebounce';

describe('useDebounce', () => {
  it('debounces value changes', async () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    expect(result.current).toBe('initial');
    rerender({ value: 'updated', delay: 500 });
    
    await waitFor(() => {
      expect(result.current).toBe('updated');
    }, { timeout: 600 });
  });
});
```

### API Routes
```typescript
// tests/api/users.test.ts
import { GET } from '@/app/api/users/route';

vi.mock('@/lib/database', () => ({
  getUsers: vi.fn(() => Promise.resolve([{ id: '1', name: 'John' }]))
}));

describe('GET /api/users', () => {
  it('returns users list', async () => {
    const response = await GET();
    const data = await response.json();
    
    expect(response.status).toBe(200);
    expect(data.users).toHaveLength(1);
  });
});
```

## Component Testing

### Basic Component
```typescript
// tests/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Button } from '@/components/Button';

describe('Button', () => {
  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    
    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Form Component
```typescript
// tests/components/LoginForm.test.tsx
describe('LoginForm', () => {
  it('validates email format', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);
    
    await userEvent.type(screen.getByPlaceholderText('Email'), 'invalid');
    await userEvent.click(screen.getByRole('button'));
    
    await waitFor(() => {
      expect(screen.getByText('Invalid email')).toBeInTheDocument();
    });
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('submits valid form', async () => {
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);
    
    await userEvent.type(screen.getByPlaceholderText('Email'), 'test@example.com');
    await userEvent.type(screen.getByPlaceholderText('Password'), 'password123');
    await userEvent.click(screen.getByRole('button'));
    
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });
  });
});
```

### Zustand Store
```typescript
// tests/stores/counter.test.tsx
import { renderHook, act } from '@testing-library/react';
import { useCounterStore } from '@/stores/counter';

describe('useCounterStore', () => {
  beforeEach(() => {
    useCounterStore.getState().reset();
  });

  it('increments count', () => {
    const { result } = renderHook(() => useCounterStore());
    
    act(() => {
      result.current.increment();
    });
    
    expect(result.current.count).toBe(1);
  });
});
```

## E2E Testing

### Authentication Flow
```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test('user can sign up', async ({ page }) => {
  await page.goto('/signup');
  
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  await expect(page).toHaveURL('/dashboard');
});
```

### API Mocking
```typescript
// tests/e2e/dashboard.spec.ts
test('displays user data', async ({ page }) => {
  await page.route('**/api/user', async (route) => {
    await route.fulfill({
      status: 200,
      body: JSON.stringify({ name: 'John Doe' })
    });
  });
  
  await page.goto('/dashboard');
  await expect(page.locator('text=John Doe')).toBeVisible();
});
```

### Accessibility Testing
```typescript
// tests/e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage has no violations', async ({ page }) => {
  await page.goto('/');
  
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

## Mocking Supabase

```typescript
// tests/mocks/supabase.ts
vi.mock('@/lib/supabase/client', () => ({
  createClient: vi.fn(() => ({
    from: vi.fn(() => ({
      select: vi.fn(() => Promise.resolve({
        data: [{ id: '1', name: 'Test' }],
        error: null
      })),
      insert: vi.fn(() => Promise.resolve({
        data: { id: '2', name: 'New' },
        error: null
      }))
    }))
  }))
}));
```

## Coverage

```bash
pnpm test:coverage
```

**Target thresholds:**
- Lines: 80%
- Functions: 80%
- Branches: 80%
- Statements: 80%

## Best Practices

1. **Test behavior, not implementation**
2. **Use Arrange-Act-Assert pattern**
3. **Prefer semantic queries** (`getByRole` over `getByTestId`)
4. **Mock external dependencies**
5. **Test error states**
6. **Keep tests isolated**
7. **Test accessibility**
