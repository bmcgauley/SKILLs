"""
Legacy MCP Example (Before Migration)

This represents a traditional MCP implementation before progressive disclosure:
- All tools registered upfront
- Large data returned directly
- No discovery mechanism
- No TypeScript definitions
- Minimal error handling
"""

import json
import asyncio
from typing import List

# Simulated MCP framework
class LegacyMCP:
    def __init__(self):
        self.tools = {}

    def tool(self, name: str):
        def decorator(func):
            self.tools[name] = func
            print(f"Registered tool: {name}")  # All tools loaded upfront!
            return func
        return decorator

mcp = LegacyMCP()


# Problem 1: All tools registered upfront (loads all schemas into context)
@mcp.tool("scrape_url")
async def scrape_url(url: str) -> str:
    """Scrape a URL and return HTML."""
    # Simulate fetching
    html = f"<html><body>Content from {url}</body></html>" * 100  # ~5KB

    # Problem 2: Return large data directly
    return json.dumps({
        "url": url,
        "html": html,  # All 5KB in context!
        "size": len(html)
    })


@mcp.tool("parse_html")
async def parse_html(html: str) -> str:
    """Parse HTML and extract data."""
    # Simulate parsing
    data = {
        "title": "Sample Title",
        "paragraphs": ["Paragraph 1", "Paragraph 2"] * 50,  # Large data
        "links": [f"https://example.com/link{i}" for i in range(100)]
    }

    # Problem 2: Return large parsed data
    return json.dumps(data)  # Several KB in context


@mcp.tool("analyze_text")
async def analyze_text(text: str) -> str:
    """Analyze text content."""
    # Simulate analysis
    analysis = {
        "word_count": len(text.split()),
        "char_count": len(text),
        "sentences": text.split("."),  # Could be large
        "words": text.split()  # Duplicate of input!
    }

    return json.dumps(analysis)


@mcp.tool("fetch_multiple")
async def fetch_multiple(urls: List[str]) -> str:
    """Fetch multiple URLs."""
    # Problem 3: No composability - monolithic operation
    results = []
    for url in urls:
        html = f"<html>Content from {url}</html>" * 100
        results.append({
            "url": url,
            "html": html  # All data in one response!
        })

    return json.dumps(results)  # Potentially huge response


@mcp.tool("summarize")
async def summarize(text: str) -> str:
    """Summarize text."""
    # Simulate summarization
    summary = {
        "original_text": text,  # Problem: Echoes input
        "summary": text[:100] + "...",
        "key_points": ["Point 1", "Point 2", "Point 3"]
    }

    return json.dumps(summary)


# Problem 4: No discovery mechanism
# Agent must know all tool names upfront
# Can't browse or search for tools

# Problem 5: No error handling
# Errors not helpful or actionable

# Problem 6: No TypeScript definitions
# No type safety or documentation


async def main():
    """Demonstrate legacy MCP."""
    print("=== Legacy MCP Demo ===\n")

    print("Problem 1: All tools loaded upfront")
    print(f"Total tools registered: {len(mcp.tools)}")
    print("Each tool schema loaded into every context!\n")

    print("Problem 2: Large data in responses")
    result = await scrape_url("https://example.com")
    data = json.loads(result)
    print(f"Response size: {len(result)} bytes")
    print(f"HTML in context: {len(data['html'])} chars\n")

    print("Problem 3: Monolithic operations")
    result = await fetch_multiple([
        "https://example.com",
        "https://example.org"
    ])
    print(f"Batch response size: {len(result)} bytes")
    print("All data must flow through context!\n")

    print("Problem 4: No discovery")
    print("Agent must know all tool names upfront")
    print("Cannot search or browse available tools\n")

    print("=== Problems Summary ===")
    print("1. All schemas loaded (~150KB)")
    print("2. Large data in context (~50KB+ per call)")
    print("3. Monolithic, non-composable tools")
    print("4. No discovery mechanism")
    print("5. Poor error handling")
    print("6. No type definitions")
    print("\nSee migration steps to fix these issues!")


if __name__ == "__main__":
    asyncio.run(main())
