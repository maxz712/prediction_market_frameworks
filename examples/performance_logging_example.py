#!/usr/bin/env python3
"""
Example demonstrating performance metrics logging in the Polymarket client.

This example shows how to:
1. Configure performance logging
2. Use the measure_performance context manager
3. Use the PerformanceMetrics class for detailed tracking
4. Log memory usage statistics

Run this example with:
    python examples/performance_logging_example.py
"""

import asyncio
import random
import time
from typing import Any

from polymarket_client.logger import (
    create_performance_logger,
    log_memory_usage,
    measure_performance,
    setup_logging,
)


def simulate_api_call(duration_ms: float = 100.0) -> dict[str, Any]:
    """Simulate an API call with configurable duration."""
    time.sleep(duration_ms / 1000)
    return {
        "status": "success",
        "data": {"market_id": "0x123", "price": 0.55},
        "timestamp": time.time(),
    }


def simulate_database_operation(operation: str, records: int = 100) -> dict[str, Any]:
    """Simulate a database operation."""
    # Simulate variable processing time based on record count
    processing_time = (records / 1000) + random.uniform(0.01, 0.05)
    time.sleep(processing_time)

    return {
        "operation": operation,
        "records_processed": records,
        "success": True,
    }


async def simulate_async_operation(delay_ms: float = 50.0) -> str:
    """Simulate an async operation."""
    await asyncio.sleep(delay_ms / 1000)
    return f"Async operation completed after {delay_ms}ms"


def main() -> None:
    """Main example function."""

    # 1. Setup performance logging
    setup_logging(
        level="INFO",
        format_type="structured",  # Use structured JSON logging
        enable_console=True,
        log_file="performance_metrics.log"  # Also log to file
    )

    # 2. Create a performance logger and metrics collector
    logger, metrics = create_performance_logger("example")

    # 3. Example 1: Using the measure_performance context manager

    for i in range(3):
        with measure_performance(
            logger,
            "api_call",
            metadata={"endpoint": "/markets", "attempt": i + 1}
        ):
            result = simulate_api_call(random.uniform(50, 200))

    # 4. Example 2: Using PerformanceMetrics class for detailed tracking

    operations = [
        ("fetch_markets", 150, {"query": "active"}),
        ("fetch_positions", 75, {"user_id": "0xabc"}),
        ("place_order", 300, {"market_id": "0x123", "amount": 100}),
        ("cancel_order", 50, {"order_id": "order_456"}),
    ]

    for operation, base_duration, metadata in operations:
        # Simulate variable duration
        duration = base_duration + random.uniform(-20, 50)
        success = random.random() > 0.1  # 90% success rate

        # Record the operation
        metrics.record_operation(operation, duration, success, metadata)


    # 5. Example 3: Measuring database operations

    db_operations = [
        ("SELECT", 500),
        ("INSERT", 200),
        ("UPDATE", 150),
        ("SELECT", 1000),  # Larger query
        ("DELETE", 50),
    ]

    for operation, record_count in db_operations:
        start_time = time.perf_counter()

        try:
            result = simulate_database_operation(operation, record_count)
            duration_ms = (time.perf_counter() - start_time) * 1000

            metrics.record_operation(
                f"db_{operation.lower()}",
                duration_ms,
                result["success"],
                {"records": record_count}
            )


        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            metrics.record_operation(
                f"db_{operation.lower()}",
                duration_ms,
                False,
                {"records": record_count, "error": str(e)}
            )

    # 6. Example 4: Async operations (requires some manual timing)

    async def run_async_examples():
        for i in range(2):
            start_time = time.perf_counter()

            try:
                await simulate_async_operation(random.uniform(30, 100))
                duration_ms = (time.perf_counter() - start_time) * 1000

                metrics.record_operation(
                    "async_operation",
                    duration_ms,
                    True,
                    {"iteration": i + 1}
                )


            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                metrics.record_operation(
                    "async_operation",
                    duration_ms,
                    False,
                    {"iteration": i + 1, "error": str(e)}
                )

    # Run async examples
    asyncio.run(run_async_examples())

    # 7. Example 5: Memory usage logging

    # Log memory before heavy operation
    log_memory_usage(logger, "before_heavy_operation")

    # Simulate memory-intensive operation
    large_data = []
    for i in range(10000):
        large_data.append({"id": i, "data": "x" * 100})

    # Log memory after heavy operation
    log_memory_usage(logger, "after_heavy_operation", {"data_size": len(large_data)})

    # Clean up
    del large_data

    # 8. Generate operation summaries

    all_operations = [
        "api_call", "fetch_markets", "fetch_positions", "place_order", "cancel_order",
        "db_select", "db_insert", "db_update", "db_delete", "async_operation"
    ]

    for operation in all_operations:
        stats = metrics.get_operation_stats(operation)
        if stats:

            # Log summary to structured logs
            metrics.log_operation_summary(operation)

    # 9. Final memory usage
    log_memory_usage(logger, "example_completion")



if __name__ == "__main__":
    main()
