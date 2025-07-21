"""Example of using the unified pagination system."""

import asyncio
from typing import Any

from src.polymarket_client import PolymarketClient
from src.polymarket_client.configs import PolymarketConfig
from src.polymarket_client.models import Event
from src.polymarket_client.pagination import create_offset_paginator


def demonstrate_unified_pagination():
    """Demonstrate the unified pagination approach."""
    
    # Initialize client
    config = PolymarketConfig(
        api_key="your_api_key",
        api_secret="your_api_secret",
        api_passphrase="your_api_passphrase",
        pk="your_private_key",
        default_page_size=50,
        max_page_size=200,
        enable_auto_pagination=True
    )
    
    client = PolymarketClient(config)
    
    # Example 1: Using the built-in pagination (existing approach)
    print("=== Example 1: Built-in Pagination ===")
    
    # Get events with auto-pagination
    events = client.get_events(limit=150, auto_paginate=True)
    print(f"Fetched {len(events.events)} events total")
    
    # Get paginated response with metadata
    paginated = client.get_events_paginated(limit=100)
    print(f"Page info: Page {paginated.pagination.page}, Has next: {paginated.pagination.has_next}")
    
    # Iterate through events efficiently
    print("\n=== Example 2: Streaming Events ===")
    count = 0
    for event in client.iter_events(page_size=25):
        count += 1
        if count <= 3:  # Show first 3
            print(f"Event: {event.title}")
        if count >= 100:  # Stop after 100
            break
    print(f"Processed {count} events")
    
    # Example 3: Direct use of unified paginator
    print("\n=== Example 3: Direct Paginator Usage ===")
    
    # Create a custom fetch function
    def fetch_active_events(**kwargs) -> list[dict[str, Any]]:
        """Custom fetch function for active events."""
        # This would make the actual API call
        # For demo purposes, we'll use the gamma client
        url = f"{client.gamma.base_url}/events"
        params = {
            "active": "true",
            "closed": "false",
            **kwargs
        }
        resp = client.gamma._session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
    
    # Create paginator
    paginator = create_offset_paginator(
        fetch_func=fetch_active_events,
        model_class=Event,
        config=config
    )
    
    # Fetch all with limit
    active_events = paginator.fetch_all(limit=75)
    print(f"Fetched {len(active_events)} active events")
    
    # Get paginated response
    paginated_active = paginator.fetch_paginated(limit=50)
    print(f"Paginated: {len(paginated_active.data)} events, has_next: {paginated_active.pagination.has_next}")
    
    # Stream events
    print("\n=== Example 4: Streaming with Paginator ===")
    stream_count = 0
    for event in paginator.iter_pages(page_size=10):
        stream_count += 1
        if stream_count >= 30:
            break
    print(f"Streamed {stream_count} events")
    
    # Example 5: Custom pagination for CLOB data
    print("\n=== Example 5: CLOB Trade History Pagination ===")
    
    # For CLOB endpoints that support pagination
    def fetch_trades(market_id: str, **kwargs) -> list[dict[str, Any]]:
        """Fetch trades for a market."""
        url = f"{client.clob.config.get_endpoint('clob')}/trade-history"
        params = {
            "market": market_id,
            **kwargs
        }
        resp = client.clob._session.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        # Assuming the API returns trades in a 'trades' field
        return data.get("trades", data) if isinstance(data, dict) else data
    
    # Create a simple trade model for demo
    from pydantic import BaseModel
    
    class Trade(BaseModel):
        id: str
        price: float
        size: float
        side: str
        timestamp: int
    
    # Create paginator for trades
    market_id = "0x1234..."  # Example market ID
    trade_paginator = create_offset_paginator(
        fetch_func=lambda **kw: fetch_trades(market_id, **kw),
        model_class=Trade,
        config=config
    )
    
    # Fetch trades
    # trades = trade_paginator.fetch_all(limit=100)
    # print(f"Fetched {len(trades)} trades")


def demonstrate_pagination_patterns():
    """Demonstrate common pagination patterns."""
    
    config = PolymarketConfig.from_env()
    client = PolymarketClient(config)
    
    print("=== Common Pagination Patterns ===\n")
    
    # Pattern 1: Get first page only
    print("1. First Page Only:")
    first_page = client.get_events(limit=20, auto_paginate=False)
    print(f"   Got {len(first_page.events)} events from first page")
    
    # Pattern 2: Get specific page
    print("\n2. Specific Page (offset-based):")
    page_3 = client.get_events(limit=20, offset=40, auto_paginate=False)
    print(f"   Got {len(page_3.events)} events from page 3")
    
    # Pattern 3: Process in batches
    print("\n3. Batch Processing:")
    total_processed = 0
    for event in client.iter_events(page_size=50):
        # Process event
        total_processed += 1
        if total_processed >= 150:
            break
    print(f"   Processed {total_processed} events in batches of 50")
    
    # Pattern 4: Get all with reasonable limit
    print("\n4. Get All with Limit:")
    all_events = client.get_events(limit=200, auto_paginate=True)
    print(f"   Got {len(all_events.events)} events total")
    
    # Pattern 5: Check pagination metadata
    print("\n5. Pagination Metadata:")
    response = client.get_events_paginated(limit=30)
    print(f"   Current page: {response.pagination.page}")
    print(f"   Items per page: {response.pagination.per_page}")
    print(f"   Has next page: {response.pagination.has_next}")
    print(f"   Has previous page: {response.pagination.has_previous}")


if __name__ == "__main__":
    # Run the demonstrations
    try:
        demonstrate_unified_pagination()
        print("\n" + "="*50 + "\n")
        demonstrate_pagination_patterns()
    except Exception as e:
        print(f"Error in demonstration: {e}")
        print("Make sure to set up your configuration properly!")