/**
 * Generate Data Tool
 *
 * Generates sample data and returns as a resource reference.
 * Demonstrates the resource pattern: large data is stored server-side,
 * and only a small reference is returned.
 *
 * @category data
 * @tags data, resource, example
 *
 * @example
 * ```typescript
 * // Generate data
 * const result = await simpleGenerateData({ size: 10 });
 *
 * // Access via resource
 * const data = await getResource(result.resource_uri);
 * console.log(data.length); // 10
 * ```
 */

/**
 * Input parameters for simple_generate_data tool
 */
export interface GenerateDataInput {
  /**
   * Number of items to generate
   * @default 10
   * @minimum 1
   * @maximum 1000
   */
  size?: number;
}

/**
 * Generated data item structure
 */
export interface DataItem {
  /**
   * Item ID (0-indexed)
   */
  id: number;

  /**
   * Item value
   * @example "Item 0"
   */
  value: string;

  /**
   * Timestamp when item was generated (ISO 8601)
   */
  timestamp: string;
}

/**
 * Metadata for generated data
 */
export interface GenerateDataMetadata {
  /**
   * Number of items generated
   */
  item_count: number;

  /**
   * Size of data in bytes
   */
  size_bytes: number;

  /**
   * When data was created (ISO 8601)
   */
  created_at: string;

  /**
   * TTL for resource in seconds
   */
  expires_in_seconds: number;
}

/**
 * Output from simple_generate_data tool
 */
export interface GenerateDataOutput {
  /**
   * Unique resource identifier
   */
  resource_id: string;

  /**
   * Resource URI for accessing full data
   * @example "simple://abc123/data"
   */
  resource_uri: string;

  /**
   * Small preview of data (first 200 chars)
   */
  preview: string;

  /**
   * Metadata about the generated data
   */
  metadata: GenerateDataMetadata;
}

/**
 * Full resource data (accessed via resource URI)
 */
export type GenerateDataResource = DataItem[];
