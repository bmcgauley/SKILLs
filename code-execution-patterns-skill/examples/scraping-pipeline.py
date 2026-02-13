"""
Multi-Step Web Scraping Pipeline

This example demonstrates a complete web scraping workflow using MCP tools
with code execution patterns. It shows:
- Progressive tool discovery
- Data kept outside context using resources
- Parallel execution for multiple URLs
- Error handling with retries
- Local data processing

Author: Code Execution Patterns Skill
License: MIT
"""

import asyncio
import re
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse


# Simulated MCP client interface
class MCPClient:
    """Simulated MCP client for demonstration"""

    async def call(self, tool_name: str, params: dict) -> dict:
        """Call an MCP tool"""
        print(f"[MCP] Calling {tool_name} with {params}")
        # Simulated responses would come from real MCP
        return {"resource_uri": f"scrape://{hash(str(params))}/content"}

    async def get_resource(self, uri: str) -> str:
        """Fetch resource by URI"""
        print(f"[MCP] Fetching resource: {uri}")
        # Simulated content
        return "<html><body>Example content with <a href='/link1'>Link 1</a></body></html>"


# Initialize MCP client
mcp = MCPClient()


async def discover_scraping_tools() -> Dict[str, Any]:
    """
    Step 1: Discover available scraping tools

    Uses progressive discovery to minimize token usage:
    1. List all tools (minimal detail)
    2. Search for scraping tools
    3. Load full schema only when needed
    """
    print("\n=== Tool Discovery Phase ===")

    # List all available tools (minimal detail)
    print("Listing all tools...")
    tools_list = await mcp.call("webscrape_list_tools", {
        "detail_level": "minimal"
    })
    print(f"Found tools: {tools_list}")

    # Search for relevant tools
    print("\nSearching for scraping tools...")
    scraping_tools = await mcp.call("webscrape_search_tools", {
        "query": "scrape",
        "category": "scraping"
    })
    print(f"Scraping tools: {scraping_tools}")

    # Load full schema for the tool we'll use
    print("\nLoading full schema for scrape_url...")
    schema = await mcp.call("webscrape_search_tools", {
        "query": "scrape_url",
        "detail_level": "full"
    })

    return schema


async def scrape_single_url(url: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Step 2: Scrape a single URL with error handling

    Returns a resource reference, NOT the full content.
    This keeps large data out of the conversation context.
    """
    print(f"\n=== Scraping: {url} ===")

    for attempt in range(max_retries):
        try:
            # Call MCP tool - returns reference, not full content
            result = await mcp.call("webscrape_scrape_url", {
                "url": url,
                "response_format": "markdown"
            })

            # Check for errors in response
            if "error" in result:
                raise Exception(result["error"])

            print(f"✓ Scrape successful (attempt {attempt + 1})")
            return result

        except Exception as e:
            if attempt == max_retries - 1:
                print(f"✗ Failed after {max_retries} attempts: {e}")
                return {
                    "error": str(e),
                    "url": url,
                    "failed": True
                }

            # Exponential backoff
            wait_time = 2 ** attempt
            print(f"⚠ Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

    return {"error": "unknown", "failed": True}


async def scrape_multiple_urls(urls: List[str], max_concurrent: int = 5) -> List[Dict[str, Any]]:
    """
    Step 3: Scrape multiple URLs in parallel with concurrency limit

    Uses asyncio.gather for parallel execution.
    Semaphore prevents overwhelming the server.
    """
    print(f"\n=== Scraping {len(urls)} URLs (max {max_concurrent} concurrent) ===")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def scrape_with_limit(url: str) -> Dict[str, Any]:
        async with semaphore:
            return await scrape_single_url(url)

    # Execute all scrapes in parallel (with concurrency limit)
    results = await asyncio.gather(*[
        scrape_with_limit(url)
        for url in urls
    ])

    # Separate successes and failures
    successful = [r for r in results if "error" not in r]
    failed = [r for r in results if "error" in r]

    print(f"\n✓ Successful: {len(successful)}")
    print(f"✗ Failed: {len(failed)}")

    return results


def extract_links_from_html(html: str, base_url: str) -> List[str]:
    """
    Step 4: Extract links from HTML (local processing)

    This runs in the execution environment, NOT through MCP.
    No tokens consumed for this processing.
    """
    print("\n=== Extracting Links (Local Processing) ===")

    # Simple regex to find links (in production, use BeautifulSoup or lxml)
    link_pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"')
    links = link_pattern.findall(html)

    # Convert relative URLs to absolute
    absolute_links = []
    for link in links:
        if link.startswith('http'):
            absolute_links.append(link)
        else:
            absolute_links.append(urljoin(base_url, link))

    print(f"Found {len(absolute_links)} links")
    return absolute_links


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from the same domain (local processing)"""
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    return domain1 == domain2


def filter_links(links: List[str], base_url: str, same_domain_only: bool = True) -> List[str]:
    """
    Step 5: Filter links (local processing)

    All filtering happens in execution environment.
    No MCP calls needed, no tokens consumed.
    """
    print("\n=== Filtering Links (Local Processing) ===")

    filtered = []

    for link in links:
        # Skip anchors
        if '#' in link:
            continue

        # Filter by domain if requested
        if same_domain_only and not is_same_domain(link, base_url):
            continue

        # Skip duplicates
        if link in filtered:
            continue

        filtered.append(link)

    print(f"Filtered to {len(filtered)} links")
    return filtered


async def process_scraped_content(content: str) -> Dict[str, Any]:
    """
    Step 6: Process content (local processing)

    All processing happens in execution environment.
    Content never enters conversation context.
    """
    print("\n=== Processing Content (Local Processing) ===")

    # Calculate statistics
    word_count = len(content.split())
    line_count = len(content.split('\n'))
    char_count = len(content)

    # Extract headings (simple regex, use proper parser in production)
    headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)

    # Extract code blocks
    code_blocks = re.findall(r'```[\s\S]*?```', content)

    return {
        "statistics": {
            "words": word_count,
            "lines": line_count,
            "characters": char_count
        },
        "headings": headings,
        "code_blocks_count": len(code_blocks),
        "has_code": len(code_blocks) > 0
    }


async def scraping_pipeline(start_url: str, max_depth: int = 1) -> Dict[str, Any]:
    """
    Complete scraping pipeline demonstrating all patterns

    Pipeline:
    1. Discover tools
    2. Scrape main page (returns reference)
    3. Fetch content into execution environment
    4. Extract and filter links (local processing)
    5. Scrape linked pages in parallel
    6. Process all content locally
    7. Return analysis
    """
    print("\n" + "=" * 60)
    print("SCRAPING PIPELINE STARTED")
    print("=" * 60)

    # Step 1: Discover tools
    tools = await discover_scraping_tools()

    # Step 2: Scrape main page
    main_page_ref = await scrape_single_url(start_url)

    if "error" in main_page_ref:
        return {"error": "Failed to scrape main page", "details": main_page_ref}

    # Step 3: Fetch content into execution environment
    # This is the key pattern: data stays out of context
    print("\n=== Fetching Main Page Content ===")
    main_page_content = await mcp.get_resource(main_page_ref["resource_uri"])
    print(f"Fetched {len(main_page_content)} bytes into execution environment")

    # Step 4: Extract and filter links (local processing - no tokens)
    all_links = extract_links_from_html(main_page_content, start_url)
    filtered_links = filter_links(all_links, start_url, same_domain_only=True)

    # Limit to first 10 for demo
    links_to_scrape = filtered_links[:10]

    # Step 5: Scrape linked pages in parallel
    if max_depth > 0 and links_to_scrape:
        linked_page_refs = await scrape_multiple_urls(links_to_scrape)
    else:
        linked_page_refs = []

    # Step 6: Fetch all linked pages into execution environment
    print("\n=== Fetching Linked Pages ===")
    linked_contents = []
    for ref in linked_page_refs:
        if "error" not in ref:
            content = await mcp.get_resource(ref["resource_uri"])
            linked_contents.append(content)
            print(f"Fetched {len(content)} bytes")

    # Step 7: Process all content locally
    print("\n=== Processing All Content ===")
    main_analysis = await process_scraped_content(main_page_content)

    linked_analyses = []
    for content in linked_contents:
        analysis = await process_scraped_content(content)
        linked_analyses.append(analysis)

    # Step 8: Combine and return results
    result = {
        "main_page": {
            "url": start_url,
            "analysis": main_analysis,
            "links_found": len(all_links),
            "links_filtered": len(filtered_links)
        },
        "linked_pages": {
            "scraped": len(linked_contents),
            "failed": len(linked_page_refs) - len(linked_contents),
            "analyses": linked_analyses
        },
        "totals": {
            "pages_processed": 1 + len(linked_contents),
            "total_words": (
                main_analysis["statistics"]["words"] +
                sum(a["statistics"]["words"] for a in linked_analyses)
            )
        }
    }

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)
    print(f"Pages processed: {result['totals']['pages_processed']}")
    print(f"Total words: {result['totals']['total_words']}")

    return result


async def main():
    """
    Main entry point for the scraping pipeline

    This demonstrates the complete pattern:
    - Minimal token usage (all data in execution environment)
    - Parallel execution where possible
    - Error handling with retries
    - Local data processing
    """
    # Example URL (would be a real URL in production)
    start_url = "https://example.com"

    # Run the pipeline
    result = await scraping_pipeline(start_url, max_depth=1)

    # Display results
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Main page: {result['main_page']['url']}")
    print(f"Links found: {result['main_page']['links_found']}")
    print(f"Linked pages scraped: {result['linked_pages']['scraped']}")
    print(f"Total pages: {result['totals']['pages_processed']}")
    print(f"Total words: {result['totals']['total_words']}")

    return result


if __name__ == "__main__":
    # Run the pipeline
    asyncio.run(main())

    print("\n" + "=" * 60)
    print("KEY PATTERNS DEMONSTRATED:")
    print("=" * 60)
    print("1. Progressive tool discovery (minimal → full)")
    print("2. Resource-based data (not in context)")
    print("3. Parallel execution with concurrency limits")
    print("4. Error handling with exponential backoff")
    print("5. Local data processing (outside context)")
    print("6. Token-efficient workflow")
    print("=" * 60)
