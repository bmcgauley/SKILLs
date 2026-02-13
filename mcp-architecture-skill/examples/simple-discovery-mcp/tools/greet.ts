/**
 * Greet Tool
 *
 * Returns a greeting message with timestamp.
 *
 * @category utility
 * @tags simple, example
 *
 * @example
 * ```typescript
 * const result = await simpleGreet({ name: "Alice" });
 * console.log(result.greeting); // "Hello, Alice!"
 * ```
 */

/**
 * Input parameters for simple_greet tool
 */
export interface GreetInput {
  /**
   * Name to greet
   * @example "Alice"
   */
  name: string;
}

/**
 * Output from simple_greet tool
 */
export interface GreetOutput {
  /**
   * Greeting message
   * @example "Hello, Alice!"
   */
  greeting: string;

  /**
   * Timestamp when greeting was generated (ISO 8601)
   * @example "2025-11-09T12:00:00Z"
   */
  timestamp: string;
}
