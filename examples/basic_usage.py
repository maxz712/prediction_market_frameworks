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
    print("=== Method 1: Simple Initialization ===")
    try:
        client = PolymarketClient()
        print("✅ Client initialized from environment variables")
    except PolymarketError as e:
        print(f"❌ Failed to initialize: {e}")
        print("💡 Make sure to set POLYMARKET_API_KEY, POLYMARKET_API_SECRET, etc.")
        return

    # Method 2: Explicit configuration
    print("\n=== Method 2: Explicit Configuration ===")
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
    print("✅ Client initialized with custom configuration")

    # Example 1: Get active events
    print("\n=== Example 1: Get Active Events ===")
    try:
        events = client.get_active_events(limit=5)
        print(f"📅 Found {len(events)} active events:")
        for event in events[:3]:  # Show first 3
            print(f"   • {event.title}")
    except PolymarketRateLimitError as e:
        print(f"⏱️ Rate limited: {e}")
        if e.retry_after:
            print(f"   Retry after {e.retry_after} seconds")
    except PolymarketError as e:
        print(f"❌ Error fetching events: {e}")

    # Example 2: Get market data
    print("\n=== Example 2: Get Market Data ===")
    try:
        # This would work with a real condition_id
        # market = client.get_market("some_condition_id")
        # print(f"📊 Market: {market.question}")
        print("📊 Market data example (requires valid condition_id)")
    except PolymarketError as e:
        print(f"❌ Error fetching market: {e}")

    # Example 3: Health check
    print("\n=== Example 3: Health Check ===")
    try:
        health = client.gamma.health_check()
        print(f"🏥 Gamma API Status: {health['status']}")
        if health["status"] == "healthy":
            print(f"   Response time: {health['response_time_ms']:.2f}ms")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    # Example 4: Configuration info
    print("\n=== Example 4: Configuration Info ===")
    print(f"🔧 SDK Version: {client.config.sdk_version}")
    print(f"🔧 Default Page Size: {client.config.default_page_size}")
    print(f"🔧 Max Page Size: {client.config.max_page_size}")
    print(f"🔧 Auto Pagination: {client.config.enable_auto_pagination}")
    print(f"🔧 Timeout: {client.config.timeout}s")
    print(f"🔧 Max Retries: {client.config.max_retries}")


if __name__ == "__main__":
    main()
