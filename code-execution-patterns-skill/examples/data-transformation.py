"""
Large Data Transformation Pipeline

This example demonstrates processing large datasets efficiently:
- Loading data via resources (not into context)
- Processing in execution environment
- Chunking for very large datasets
- Memory-efficient transformations
- Minimal token usage

Author: Code Execution Patterns Skill
License: MIT
"""

import asyncio
import json
import hashlib
from typing import List, Dict, Any, Iterator
from dataclasses import dataclass


@dataclass
class DataChunk:
    """Represents a chunk of data"""
    chunk_id: str
    data: Any
    size_bytes: int
    index: int


# Simulated MCP client
class MCPClient:
    """Simulated MCP client for demonstration"""

    def __init__(self):
        self.storage = {}  # Simulated resource storage

    async def call(self, tool_name: str, params: dict) -> dict:
        """Call an MCP tool"""
        print(f"[MCP] {tool_name}")

        # Simulate different tool responses
        if "get_metadata" in tool_name:
            return {
                "size_bytes": params.get("size", 10_000_000),
                "format": "json",
                "record_count": 100_000
            }
        elif "load_file" in tool_name:
            # Return reference, not data
            resource_id = hashlib.md5(params["path"].encode()).hexdigest()
            return {
                "resource_uri": f"file://{resource_id}",
                "metadata": {
                    "size_bytes": 10_000_000,
                    "path": params["path"]
                }
            }
        elif "chunk_data" in tool_name:
            # Return chunk references
            chunk_ids = [f"chunk_{i}" for i in range(10)]
            return {
                "chunk_ids": chunk_ids,
                "chunk_count": len(chunk_ids),
                "chunk_size": params.get("chunk_size", 1_000_000)
            }
        elif "save_file" in tool_name:
            return {"success": True, "path": params["path"]}

        return {"success": True}

    async def get_resource(self, uri: str) -> Any:
        """Fetch resource by URI"""
        print(f"[MCP] Fetching: {uri}")

        # Simulate large dataset
        if uri.startswith("chunk_"):
            # Return simulated chunk data
            chunk_id = uri.split("_")[1]
            return self._generate_chunk_data(int(chunk_id), 1000)

        # Return simulated full dataset
        return self._generate_chunk_data(0, 10000)

    def _generate_chunk_data(self, start_id: int, count: int) -> List[Dict]:
        """Generate simulated data records"""
        return [
            {
                "id": start_id + i,
                "name": f"Record_{start_id + i}",
                "value": (start_id + i) * 10,
                "category": "A" if i % 2 == 0 else "B",
                "metadata": {
                    "created_at": f"2025-11-{(i % 28) + 1:02d}",
                    "updated_at": f"2025-11-{(i % 28) + 1:02d}"
                }
            }
            for i in range(count)
        ]


# Initialize MCP client
mcp = MCPClient()


async def get_data_metadata(data_uri: str) -> Dict[str, Any]:
    """
    Get metadata about dataset without loading it

    Key pattern: Check size before deciding how to process
    """
    print("\n=== Getting Data Metadata ===")

    metadata = await mcp.call("get_metadata", {"uri": data_uri})

    print(f"Size: {metadata['size_bytes']:,} bytes")
    print(f"Format: {metadata.get('format', 'unknown')}")
    print(f"Records: {metadata.get('record_count', 'unknown')}")

    return metadata


def transform_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a single record (local processing)

    This runs in execution environment - no tokens consumed.
    """
    # Example transformations
    transformed = {
        "id": record["id"],
        "name": record["name"].upper(),  # Uppercase names
        "value": record["value"] * 2,  # Double values
        "category": record["category"],
        "computed_field": record["value"] + record["id"],  # Add computed field
        "metadata": record["metadata"]
    }

    return transformed


def transform_chunk(chunk_data: List[Dict]) -> List[Dict]:
    """
    Transform a chunk of records (local processing)

    All processing happens in execution environment.
    """
    print(f"Transforming {len(chunk_data)} records...")

    transformed = [transform_record(record) for record in chunk_data]

    return transformed


def filter_records(records: List[Dict], criteria: Dict[str, Any]) -> List[Dict]:
    """
    Filter records based on criteria (local processing)

    Example: filter by category, value range, etc.
    """
    print(f"Filtering {len(records)} records...")

    filtered = []

    for record in records:
        # Check each criterion
        match = True

        if "category" in criteria:
            if record.get("category") != criteria["category"]:
                match = False

        if "min_value" in criteria:
            if record.get("value", 0) < criteria["min_value"]:
                match = False

        if "max_value" in criteria:
            if record.get("value", 0) > criteria["max_value"]:
                match = False

        if match:
            filtered.append(record)

    print(f"Filtered to {len(filtered)} records")
    return filtered


def aggregate_records(records: List[Dict]) -> Dict[str, Any]:
    """
    Aggregate statistics from records (local processing)

    Calculate sums, averages, counts, etc.
    """
    print(f"Aggregating {len(records)} records...")

    if not records:
        return {
            "count": 0,
            "total_value": 0,
            "avg_value": 0,
            "categories": {}
        }

    total_value = sum(r.get("value", 0) for r in records)
    categories = {}

    for record in records:
        cat = record.get("category", "unknown")
        if cat not in categories:
            categories[cat] = {"count": 0, "total_value": 0}

        categories[cat]["count"] += 1
        categories[cat]["total_value"] += record.get("value", 0)

    # Calculate averages
    for cat in categories:
        categories[cat]["avg_value"] = (
            categories[cat]["total_value"] / categories[cat]["count"]
        )

    return {
        "count": len(records),
        "total_value": total_value,
        "avg_value": total_value / len(records) if records else 0,
        "categories": categories
    }


async def process_small_dataset(data_uri: str) -> Dict[str, Any]:
    """
    Process dataset that fits in memory (< 10MB)

    Pattern: Load once, process in execution environment
    """
    print("\n=== Processing Small Dataset ===")

    # Get reference
    file_ref = await mcp.call("load_file", {"path": data_uri})

    # Fetch into execution environment
    data = await mcp.get_resource(file_ref["resource_uri"])
    print(f"Loaded {len(data)} records into execution environment")

    # Transform (local processing - no tokens)
    transformed = transform_chunk(data)

    # Filter (local processing - no tokens)
    filtered = filter_records(transformed, {
        "category": "A",
        "min_value": 100
    })

    # Aggregate (local processing - no tokens)
    stats = aggregate_records(filtered)

    return {
        "original_count": len(data),
        "transformed_count": len(transformed),
        "filtered_count": len(filtered),
        "statistics": stats
    }


async def process_large_dataset_chunked(data_uri: str, chunk_size: int = 1_000_000) -> Dict[str, Any]:
    """
    Process very large dataset in chunks

    Pattern: Process one chunk at a time to manage memory
    This allows processing datasets larger than available RAM
    """
    print("\n=== Processing Large Dataset (Chunked) ===")

    # Request chunking
    chunk_info = await mcp.call("chunk_data", {
        "uri": data_uri,
        "chunk_size": chunk_size,
        "overlap": 0
    })

    chunk_ids = chunk_info["chunk_ids"]
    print(f"Dataset split into {len(chunk_ids)} chunks")

    # Process chunks one at a time
    all_stats = []
    total_records = 0
    total_filtered = 0

    for i, chunk_id in enumerate(chunk_ids):
        print(f"\nProcessing chunk {i + 1}/{len(chunk_ids)}")

        # Load chunk into execution environment
        chunk_data = await mcp.get_resource(chunk_id)
        print(f"  Loaded {len(chunk_data)} records")

        # Transform chunk
        transformed = transform_chunk(chunk_data)

        # Filter chunk
        filtered = filter_records(transformed, {
            "category": "A",
            "min_value": 50
        })

        # Aggregate chunk
        chunk_stats = aggregate_records(filtered)
        all_stats.append(chunk_stats)

        total_records += len(chunk_data)
        total_filtered += len(filtered)

        # Chunk goes out of scope here - memory freed automatically
        print(f"  Chunk {i + 1} complete")

    # Combine chunk statistics
    print("\n=== Combining Results ===")
    combined_stats = combine_chunk_stats(all_stats)

    return {
        "chunks_processed": len(chunk_ids),
        "total_records": total_records,
        "total_filtered": total_filtered,
        "combined_statistics": combined_stats
    }


def combine_chunk_stats(chunk_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Combine statistics from multiple chunks (local processing)

    Merge aggregations from chunks to get overall statistics
    """
    print("Combining statistics from chunks...")

    if not chunk_stats:
        return {
            "count": 0,
            "total_value": 0,
            "avg_value": 0,
            "categories": {}
        }

    # Sum counts and totals
    total_count = sum(s["count"] for s in chunk_stats)
    total_value = sum(s["total_value"] for s in chunk_stats)

    # Combine category stats
    combined_categories = {}

    for stats in chunk_stats:
        for cat, cat_stats in stats.get("categories", {}).items():
            if cat not in combined_categories:
                combined_categories[cat] = {"count": 0, "total_value": 0}

            combined_categories[cat]["count"] += cat_stats["count"]
            combined_categories[cat]["total_value"] += cat_stats["total_value"]

    # Calculate combined averages
    for cat in combined_categories:
        combined_categories[cat]["avg_value"] = (
            combined_categories[cat]["total_value"] /
            combined_categories[cat]["count"]
        )

    return {
        "count": total_count,
        "total_value": total_value,
        "avg_value": total_value / total_count if total_count else 0,
        "categories": combined_categories
    }


async def save_transformed_data(data: List[Dict], output_path: str) -> Dict[str, Any]:
    """
    Save transformed data

    Pattern: Data is saved directly from execution environment
    No need to pass through context
    """
    print(f"\n=== Saving Results to {output_path} ===")

    # In real implementation, this would save to file system or database
    # Here we just call MCP to save
    result = await mcp.call("save_file", {
        "path": output_path,
        "data": data  # Passed directly, not through context
    })

    print(f"Saved {len(data)} records")
    return result


async def adaptive_processing(data_uri: str, size_threshold: int = 10_000_000) -> Dict[str, Any]:
    """
    Adaptive processing: choose strategy based on data size

    Pattern: Check metadata first, then decide how to process
    - Small data: Load all at once
    - Large data: Process in chunks
    """
    print("\n" + "=" * 60)
    print("ADAPTIVE DATA TRANSFORMATION PIPELINE")
    print("=" * 60)

    # Step 1: Get metadata without loading data
    metadata = await get_data_metadata(data_uri)

    # Step 2: Choose processing strategy based on size
    if metadata["size_bytes"] > size_threshold:
        print(f"\nData is large ({metadata['size_bytes']:,} bytes)")
        print("Using chunked processing...")
        result = await process_large_dataset_chunked(data_uri)
    else:
        print(f"\nData is small ({metadata['size_bytes']:,} bytes)")
        print("Using in-memory processing...")
        result = await process_small_dataset(data_uri)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)

    return result


async def parallel_file_processing(file_paths: List[str]) -> Dict[str, Any]:
    """
    Process multiple files in parallel

    Pattern: Independent operations can run concurrently
    """
    print("\n=== Processing Multiple Files in Parallel ===")

    # Process all files concurrently
    tasks = [
        process_small_dataset(path)
        for path in file_paths
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Separate successes and failures
    successful = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]

    print(f"\n✓ Processed: {len(successful)} files")
    print(f"✗ Failed: {len(failed)} files")

    # Combine all statistics
    if successful:
        combined = {
            "files_processed": len(successful),
            "total_records": sum(r["original_count"] for r in successful),
            "total_filtered": sum(r["filtered_count"] for r in successful)
        }
    else:
        combined = {
            "files_processed": 0,
            "total_records": 0,
            "total_filtered": 0
        }

    return combined


async def main():
    """
    Main entry point demonstrating data transformation patterns
    """
    print("\n" + "=" * 60)
    print("DATA TRANSFORMATION EXAMPLES")
    print("=" * 60)

    # Example 1: Adaptive processing (automatically chooses strategy)
    print("\n--- Example 1: Adaptive Processing ---")
    result1 = await adaptive_processing("data/large_dataset.json")
    print(f"Processed {result1.get('total_records', 'N/A')} records")

    # Example 2: Parallel file processing
    print("\n--- Example 2: Parallel File Processing ---")
    files = ["data/file1.json", "data/file2.json", "data/file3.json"]
    result2 = await parallel_file_processing(files)
    print(f"Total records across files: {result2['total_records']}")

    print("\n" + "=" * 60)
    print("KEY PATTERNS DEMONSTRATED:")
    print("=" * 60)
    print("1. Metadata-first approach (check before loading)")
    print("2. Adaptive processing (strategy based on size)")
    print("3. Chunked processing (for very large data)")
    print("4. Local transformations (outside context)")
    print("5. Parallel processing (multiple files)")
    print("6. Memory-efficient (one chunk at a time)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
