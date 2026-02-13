# TypeScript Type Definitions for MCP Tools

**Last Updated**: 2025-11-09

## Overview

TypeScript type definitions serve as both documentation and enforceable contracts for MCP tools. Well-defined types help agents understand tool interfaces, generate correct code, and catch errors before execution.

## Why TypeScript for MCPs

Even if your MCP is written in Python, TypeScript definitions provide:

1. **Rich Type Information**: More expressive than JSON Schema
2. **IDE Support**: Autocomplete and type checking when writing agent code
3. **Documentation**: Types serve as inline documentation
4. **Code Generation**: Agents can generate correctly-typed code
5. **Validation**: Types can be compiled to JSON Schema for runtime validation

## File Organization

### Directory Structure

```
mcp-name/
├── server.py (or index.ts)
├── tools/
│   ├── index.ts              # Tool registry and discovery
│   ├── scrape_url.ts         # Individual tool definitions
│   ├── extract_links.ts
│   └── types/
│       ├── common.ts         # Shared types
│       └── resources.ts      # Resource-related types
└── README.md
```

### Index File Pattern

```typescript
// tools/index.ts

/**
 * MCP Tool Registry
 *
 * This file exports all available tools and provides
 * discovery functionality.
 */

export * from './scrape_url';
export * from './extract_links';

/**
 * Tool Categories
 */
export const TOOL_CATEGORIES = {
  scraping: 'Tools for fetching web content',
  parsing: 'Tools for parsing and extracting data',
  analysis: 'Tools for analyzing content',
  storage: 'Tools for saving and retrieving data'
} as const;

/**
 * All available tools
 */
export const AVAILABLE_TOOLS = [
  'webscrape_scrape_url',
  'webscrape_extract_links',
  'webscrape_crawl_site'
] as const;

export type ToolName = typeof AVAILABLE_TOOLS[number];
```

## Type Definition Pattern

### Basic Tool Type

```typescript
/**
 * Scrape content from a URL.
 *
 * This tool fetches a web page and returns its content in the specified format.
 * Best for static HTML pages. For JavaScript-rendered pages, use scrape_with_js.
 *
 * @example
 * ```typescript
 * const result = await scrapeUrl({
 *   url: "https://example.com",
 *   format: "markdown"
 * });
 *
 * // Access content via resource
 * const content = await getResource(result.resource_uri);
 * ```
 */

/**
 * Input parameters for scrape_url tool
 */
export interface ScrapeUrlInput {
  /**
   * URL to scrape (must be valid HTTP/HTTPS URL)
   * @example "https://example.com"
   */
  url: string;

  /**
   * Output format for scraped content
   * @default "markdown"
   */
  format?: "html" | "markdown" | "text";

  /**
   * Include images in the output
   * @default false
   */
  include_images?: boolean;

  /**
   * Include links in the output
   * @default false
   */
  include_links?: boolean;
}

/**
 * Output from scrape_url tool
 */
export interface ScrapeUrlOutput {
  /**
   * Unique resource identifier
   */
  resource_id: string;

  /**
   * Resource URI for accessing full content
   * @example "webscrape://abc123/content"
   */
  resource_uri: string;

  /**
   * Small preview of content (first 500 chars)
   */
  preview: string;

  /**
   * Metadata about the scraped content
   */
  metadata: {
    /**
     * Source URL that was scraped
     */
    url: string;

    /**
     * Size of scraped content in bytes
     */
    size_bytes: number;

    /**
     * Timestamp when content was scraped (ISO 8601)
     */
    scraped_at: string;

    /**
     * HTTP status code
     */
    status_code: number;

    /**
     * Content type from HTTP response
     */
    content_type: string;

    /**
     * TTL for resource in seconds
     */
    expires_in_seconds: number;
  };
}

/**
 * Error response from scrape_url tool
 */
export interface ScrapeUrlError {
  error: string;
  url: string;
  status_code?: number;
  suggestions?: string[];
}
```

## Advanced Patterns

### Union Types for Multiple Return Types

```typescript
/**
 * Result can be either success or error
 */
export type ScrapeUrlResult = ScrapeUrlOutput | ScrapeUrlError;

/**
 * Type guard to check if result is an error
 */
export function isScrapeUrlError(
  result: ScrapeUrlResult
): result is ScrapeUrlError {
  return 'error' in result;
}

// Usage in agent code:
const result = await scrapeUrl({ url: "https://example.com" });

if (isScrapeUrlError(result)) {
  console.error(`Scraping failed: ${result.error}`);
} else {
  console.log(`Scraped ${result.metadata.size_bytes} bytes`);
}
```

### Generic Resource Types

```typescript
// tools/types/resources.ts

/**
 * Base resource response structure
 */
export interface ResourceResponse<T = any> {
  /**
   * Unique resource identifier
   */
  resource_id: string;

  /**
   * Resource URI for accessing data
   */
  resource_uri: string;

  /**
   * Small preview of data
   */
  preview: string;

  /**
   * Type-specific metadata
   */
  metadata: T;
}

/**
 * Scrape-specific metadata
 */
export interface ScrapeMetadata {
  url: string;
  size_bytes: number;
  scraped_at: string;
  status_code: number;
  content_type: string;
  expires_in_seconds: number;
}

/**
 * Type-safe scrape response
 */
export type ScrapeUrlOutput = ResourceResponse<ScrapeMetadata>;
```

### Enums for Constrained Values

```typescript
/**
 * Supported output formats
 */
export enum OutputFormat {
  HTML = "html",
  Markdown = "markdown",
  Text = "text",
  JSON = "json"
}

/**
 * Tool detail levels for discovery
 */
export enum DetailLevel {
  Minimal = "minimal",
  Brief = "brief",
  Full = "full"
}

/**
 * Tool categories
 */
export enum ToolCategory {
  Scraping = "scraping",
  Parsing = "parsing",
  Analysis = "analysis",
  Storage = "storage"
}

// Usage in tool definition:
export interface ListToolsInput {
  detail_level?: DetailLevel;
  category?: ToolCategory;
}
```

### Literal Types for Constants

```typescript
/**
 * HTTP methods
 */
export type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";

/**
 * Match modes for tag filtering
 */
export type MatchMode = "any" | "all";

/**
 * Sorting orders
 */
export type SortOrder = "asc" | "desc";

// Usage:
export interface SearchToolsInput {
  query: string;
  sort_by?: "relevance" | "name" | "category";
  sort_order?: SortOrder;
}
```

## Discovery Tool Types

### List Tools

```typescript
/**
 * Input for list_tools endpoint
 */
export interface ListToolsInput {
  /**
   * Level of detail to return
   * - minimal: Tool names only
   * - brief: Names and descriptions
   * - full: Complete schemas
   * @default "minimal"
   */
  detail_level?: DetailLevel;

  /**
   * Filter by category
   */
  category?: ToolCategory;

  /**
   * Filter by tags
   */
  tags?: string[];

  /**
   * Tag matching mode
   * @default "any"
   */
  match_mode?: MatchMode;

  /**
   * Page number for pagination (1-indexed)
   * @default 1
   */
  page?: number;

  /**
   * Results per page
   * @default 50
   */
  page_size?: number;
}

/**
 * Minimal tool information
 */
export interface MinimalToolInfo {
  name: string;
}

/**
 * Brief tool information
 */
export interface BriefToolInfo {
  name: string;
  description: string;
  category: ToolCategory;
}

/**
 * Full tool information
 */
export interface FullToolInfo extends BriefToolInfo {
  tags: string[];
  schema: {
    parameters: Record<string, ParameterSchema>;
    returns: Record<string, any>;
  };
  examples?: ToolExample[];
  related_tools?: string[];
}

/**
 * Parameter schema definition
 */
export interface ParameterSchema {
  type: "string" | "number" | "boolean" | "array" | "object";
  description: string;
  required?: boolean;
  default?: any;
  enum?: any[];
  pattern?: string;
  min?: number;
  max?: number;
}

/**
 * Tool usage example
 */
export interface ToolExample {
  description: string;
  input: Record<string, any>;
  output: Record<string, any>;
}

/**
 * List tools output (depends on detail level)
 */
export type ListToolsOutput =
  | MinimalToolInfo[]
  | BriefToolInfo[]
  | FullToolInfo[];

/**
 * Paginated list tools output
 */
export interface PaginatedListToolsOutput<T> {
  tools: T[];
  pagination: {
    page: number;
    page_size: number;
    total_tools: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}
```

### Search Tools

```typescript
/**
 * Input for search_tools endpoint
 */
export interface SearchToolsInput {
  /**
   * Search query (searches name, description, tags)
   */
  query: string;

  /**
   * Filter by category
   */
  category?: ToolCategory;

  /**
   * Level of detail to return
   * @default "brief"
   */
  detail_level?: Exclude<DetailLevel, "minimal">;

  /**
   * Maximum results to return
   * @default 10
   */
  max_results?: number;

  /**
   * Minimum relevance score (0-100)
   * @default 0
   */
  min_relevance?: number;
}

/**
 * Search result with relevance score
 */
export interface SearchResult<T> {
  tool: T;
  relevance: number;
}

/**
 * Search tools output
 */
export type SearchToolsOutput =
  | SearchResult<BriefToolInfo>[]
  | SearchResult<FullToolInfo>[];
```

## Common Types

### Shared Types File

```typescript
// tools/types/common.ts

/**
 * ISO 8601 timestamp string
 */
export type Timestamp = string;

/**
 * Resource URI following pattern: {mcp}://{id}/{type}
 */
export type ResourceUri = string;

/**
 * UUID v4 string
 */
export type UUID = string;

/**
 * URL string
 */
export type Url = string;

/**
 * Pagination parameters
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

/**
 * Pagination metadata
 */
export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

/**
 * Standard error response
 */
export interface ErrorResponse {
  error: string;
  error_code?: string;
  suggestions?: string[];
  details?: Record<string, any>;
}

/**
 * Standard success response wrapper
 */
export interface SuccessResponse<T> {
  success: true;
  data: T;
}

/**
 * Standard result type (success or error)
 */
export type Result<T> = SuccessResponse<T> | ErrorResponse;
```

## Documentation Best Practices

### 1. JSDoc Comments

```typescript
/**
 * Scrape content from a URL.
 *
 * This tool fetches web pages and returns content in various formats.
 * It handles static HTML pages efficiently. For JavaScript-rendered
 * pages, use `scrape_with_js` instead.
 *
 * **Rate Limits**: 10 requests per minute
 * **Caching**: Results cached for 5 minutes
 *
 * @category Scraping
 * @tags web, html, http
 *
 * @example
 * ```typescript
 * // Basic usage
 * const result = await scrapeUrl({
 *   url: "https://example.com"
 * });
 *
 * // With custom format
 * const result = await scrapeUrl({
 *   url: "https://example.com",
 *   format: "markdown",
 *   include_links: true
 * });
 * ```
 *
 * @see scrape_with_js for JavaScript-rendered pages
 * @see extract_links for link extraction
 */
export interface ScrapeUrlInput {
  // ...
}
```

### 2. Parameter Documentation

```typescript
export interface ToolInput {
  /**
   * URL to process
   *
   * Must be a valid HTTP or HTTPS URL. Relative URLs are not supported.
   *
   * @example "https://example.com/page"
   * @pattern ^https?://
   */
  url: string;

  /**
   * Number of retry attempts
   *
   * If the request fails, it will be retried up to this many times
   * with exponential backoff.
   *
   * @default 3
   * @minimum 0
   * @maximum 10
   */
  max_retries?: number;

  /**
   * Request timeout in seconds
   *
   * @default 30
   * @minimum 1
   * @maximum 300
   */
  timeout?: number;
}
```

### 3. Complex Type Documentation

```typescript
/**
 * Crawl configuration options
 *
 * Controls how the crawler traverses a website.
 */
export interface CrawlConfig {
  /**
   * Maximum depth to crawl
   *
   * - 0: Only the starting URL
   * - 1: Starting URL + direct links
   * - 2: Starting URL + links + links from those pages
   *
   * @default 2
   * @minimum 0
   * @maximum 5
   */
  max_depth?: number;

  /**
   * Maximum pages to crawl
   *
   * Crawling stops when this limit is reached, even if max_depth
   * hasn't been exhausted.
   *
   * @default 100
   * @minimum 1
   * @maximum 1000
   */
  max_pages?: number;

  /**
   * Only crawl URLs from the same domain
   *
   * When true, links to external domains are ignored.
   *
   * @default true
   */
  same_domain_only?: boolean;

  /**
   * URL patterns to exclude
   *
   * URLs matching any of these regex patterns will be skipped.
   *
   * @example ["^https://example\\.com/admin/", "\\.pdf$"]
   */
  exclude_patterns?: string[];
}
```

## Generating JSON Schema

### Convert TypeScript to JSON Schema

```typescript
// Use typescript-json-schema or similar tool

import { createGenerator } from 'typescript-json-schema';
import * as fs from 'fs';

const settings = {
  required: true,
  noExtraProps: true
};

const program = TJS.getProgramFromFiles(
  ['tools/scrape_url.ts'],
  {}
);

const generator = createGenerator(program, settings);

// Generate schema for input
const inputSchema = generator.getSchemaForSymbol('ScrapeUrlInput');
fs.writeFileSync(
  'schemas/scrape_url_input.json',
  JSON.stringify(inputSchema, null, 2)
);

// Generate schema for output
const outputSchema = generator.getSchemaForSymbol('ScrapeUrlOutput');
fs.writeFileSync(
  'schemas/scrape_url_output.json',
  JSON.stringify(outputSchema, null, 2)
);
```

### Use JSON Schema for Validation

```python
import json
from jsonschema import validate

# Load generated schema
with open('schemas/scrape_url_input.json') as f:
    schema = json.load(f)

# Validate input
def scrape_url(params: dict):
    # Validate params against schema
    validate(instance=params, schema=schema)

    # Process valid params
    url = params['url']
    format = params.get('format', 'markdown')
    # ...
```

## Testing Types

### Type Tests with TypeScript

```typescript
// tools/__tests__/types.test.ts

import { expectType, expectError } from 'tsd';
import { ScrapeUrlInput, ScrapeUrlOutput } from '../scrape_url';

// Test valid input
expectType<ScrapeUrlInput>({
  url: "https://example.com",
  format: "markdown"
});

// Test invalid input (should error)
expectError<ScrapeUrlInput>({
  url: "https://example.com",
  format: "invalid"  // Not a valid format
});

// Test output type
const output: ScrapeUrlOutput = {
  resource_id: "abc123",
  resource_uri: "webscrape://abc123/content",
  preview: "Preview...",
  metadata: {
    url: "https://example.com",
    size_bytes: 1024,
    scraped_at: "2025-11-09T12:00:00Z",
    status_code: 200,
    content_type: "text/html",
    expires_in_seconds: 3600
  }
};

expectType<ScrapeUrlOutput>(output);
```

## Complete Example

```typescript
// tools/scrape_url.ts

import {
  ResourceResponse,
  Url,
  Timestamp,
  ErrorResponse
} from './types/common';

/**
 * Scrape content from a URL and return as resource.
 *
 * @category Scraping
 */

/**
 * Output format options
 */
export type ScrapeFormat = "html" | "markdown" | "text";

/**
 * Input for scrape_url tool
 */
export interface ScrapeUrlInput {
  /** URL to scrape */
  url: Url;

  /** Output format @default "markdown" */
  format?: ScrapeFormat;

  /** Include images @default false */
  include_images?: boolean;
}

/**
 * Metadata for scraped content
 */
export interface ScrapeMetadata {
  url: Url;
  size_bytes: number;
  scraped_at: Timestamp;
  status_code: number;
  content_type: string;
  expires_in_seconds: number;
}

/**
 * Output from scrape_url tool
 */
export type ScrapeUrlOutput = ResourceResponse<ScrapeMetadata>;

/**
 * Error from scrape_url tool
 */
export interface ScrapeUrlError extends ErrorResponse {
  url: Url;
  status_code?: number;
}

/**
 * Result type (success or error)
 */
export type ScrapeUrlResult = ScrapeUrlOutput | ScrapeUrlError;

/**
 * Type guard for error checking
 */
export function isScrapeUrlError(
  result: ScrapeUrlResult
): result is ScrapeUrlError {
  return 'error' in result;
}
```

## Best Practices Summary

1. **Use descriptive names**: `ScrapeUrlInput` not `Input`
2. **Document everything**: JSDoc for all types and properties
3. **Provide examples**: Show typical usage in comments
4. **Use strict types**: Avoid `any`, use specific types
5. **Share common types**: Extract reusable types to `common.ts`
6. **Include type guards**: Helper functions for type checking
7. **Generate schemas**: Convert to JSON Schema for validation
8. **Test types**: Use type testing tools like `tsd`
9. **Version types**: Include version in type comments if needed
10. **Export everything**: Make all types available to consumers

## Conclusion

Well-defined TypeScript types:
- Improve agent code generation accuracy
- Provide inline documentation
- Enable IDE autocomplete and type checking
- Serve as source of truth for tool interfaces
- Can be compiled to JSON Schema for validation
