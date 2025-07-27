#!/usr/bin/env python3
"""
Example showing how to use structured logging with the Polymarket client.
"""

import os
import sys

# Add the src directory to Python path for the example
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from polymarket_client import get_logger, setup_logging


def main():
    """Demonstrate logging setup and usage."""

    # Example 1: Setup structured JSON logging
    setup_logging(
        level="INFO",
        format_type="structured",
        enable_console=True
    )

    logger = get_logger("example")
    logger.info("Client initialized with structured logging")

    # Example 2: Setup simple human-readable logging
    setup_logging(
        level="DEBUG",
        format_type="simple",
        enable_console=True
    )

    logger = get_logger("example")
    logger.debug("Debug message with simple format")
    logger.info("Info message with simple format")
    logger.warning("Warning message with simple format")

    # Example 3: Log to file as well
    setup_logging(
        level="INFO",
        format_type="structured",
        enable_console=True,
        log_file="polymarket_client.log"
    )

    logger = get_logger("example")
    logger.info("This message will be logged to both console and file")

    # Example 4: Using structured logging in practice

    # Simulate typical client usage with logging
    logger.info(
        "Starting market analysis",
        extra={
            "market_id": "0x1234567890abcdef",
            "analysis_type": "price_trend",
            "time_period": "24h"
        }
    )

    # Simulate an API call
    logger.info(
        "Fetching market data",
        extra={
            "endpoint": "/events",
            "filters": {"active": True, "limit": 50}
        }
    )

    # Simulate order placement
    logger.info(
        "Placing limit order",
        extra={
            "order_type": "LIMIT",
            "side": "BUY",
            "size": "100.0",
            "price": "0.55",
            "market": "presidential-election-2024"
        }
    )

    # Simulate error handling
    try:
        # This would be actual client code
        msg = "Invalid order size"
        raise ValueError(msg)
    except ValueError as e:
        logger.error(
            "Order placement failed",
            extra={
                "error_type": "validation_error",
                "error_details": str(e)
            },
            exc_info=True
        )



if __name__ == "__main__":
    main()
