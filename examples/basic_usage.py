"""Basic usage examples for the Prediction Market Frameworks SDK."""

import os

from src.polymarket_client import (
    PolymarketClient,
    PolymarketConfig,
    PolymarketError,
    PolymarketRateLimitError,
)


def main():
    """Demonstrate basic SDK usage."""

    # Method 1: Simple initialization (uses environment variables)
    try:
        client = PolymarketClient()
    except PolymarketError:
        return

    # Method 2: Explicit configuration
    config = PolymarketConfig(
        api_key=os.getenv("POLYMARKET_API_KEY", "your_api_key"),
        api_secret=os.getenv("POLYMARKET_API_SECRET", "your_api_secret"),
        api_passphrase=os.getenv("POLYMARKET_API_PASSPHRASE", "your_passphrase"),
        pk=os.getenv("POLYMARKET_PRIVATE_KEY", "your_private_key"),
        # Optional: customize settings
        timeout=60,
        max_retries=5,
        default_page_size=50,
    )
    client = PolymarketClient(config)

    # Example 1: Get active events
    try:
        events = client.get_active_events(limit=5)
        for _event in events[:3]:  # Show first 3
            pass
    except PolymarketRateLimitError as e:
        if e.retry_after:
            pass
    except PolymarketError:
        pass

    # Example 2: Get market data
    try:
        # This would work with a real condition_id
        # market = client.get_market("some_condition_id")
        # print(f"📊 Market: {market.question}")
        pass
    except PolymarketError:
        pass

    # Example 3: Health check
    try:
        health = client.gamma.health_check()
        if health["status"] == "healthy":
            pass
    except Exception:
        pass

    # Example 4: Configuration info


if __name__ == "__main__":
    main()
