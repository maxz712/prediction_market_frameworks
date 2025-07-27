# Polymarket Client API Documentation

A comprehensive Python SDK for the Polymarket prediction market platform, providing unified access to both Gamma API (events/markets) and CLOB API (trading/order books).

## Installation

```bash
pip install polymarket-client
```

## Quick Start

```python
from polymarket_client import PolymarketClient

# Initialize with default configuration (loads from environment)
client = PolymarketClient()

# Or with custom configuration
from polymarket_client import PolymarketConfig
config = PolymarketConfig(
    gamma_endpoint="https://gamma-api.polymarket.com",
    clob_endpoint="https://clob.polymarket.com",
    data_api_endpoint="https://data-api.polymarket.com",
    pk="your_private_key",
    # ... other config options
)
client = PolymarketClient(config)
```

## Configuration

### Environment Variables

Set the following environment variables for automatic configuration:

- `GAMMA_ENDPOINT`: Gamma API endpoint URL
- `CLOB_ENDPOINT`: CLOB API endpoint URL 
- `DATA_API_ENDPOINT`: Data API endpoint URL
- `PK`: Private key for authentication
- `WALLET_PROXY_ADDRESS`: Proxy wallet address (optional)
- `API_CREDS`: API credentials (optional)
- `CHAIN_ID`: Blockchain chain ID (default: 137)

### PolymarketConfig Class

```python
from polymarket_client import PolymarketConfig

config = PolymarketConfig(
    gamma_endpoint="https://gamma-api.polymarket.com",
    clob_endpoint="https://clob.polymarket.com", 
    data_api_endpoint="https://data-api.polymarket.com",
    pk="your_private_key",
    wallet_proxy_address="0x...",  # Optional
    api_creds={},  # Optional
    chain_id=137,
    timeout=30,
    max_retries=3,
    default_limit=100,
    auto_paginate=True
)
```

## Core Client

### PolymarketClient

The main client class that provides unified access to all Polymarket APIs.

```python
class PolymarketClient:
    def __init__(self, config: PolymarketConfig | None = None) -> None
```

## Event Management (Gamma API)

### Get Events

```python
def get_events(
    self,
    # Pagination parameters
    limit: int | None = None,
    offset: int = 0,
    auto_paginate: bool | None = None,
    # Sorting parameters
    order: str | None = None,
    ascending: bool = True,
    # ID and slug filters
    event_id: int | list[int] | None = None,
    slug: str | list[str] | None = None,
    # Status filters
    archived: bool | None = None,
    active: bool | None = True,
    closed: bool | None = False,
    # Volume and liquidity filters
    liquidity_min: float | None = None,
    liquidity_max: float | None = None,
    volume_min: float | None = None,
    volume_max: float | None = None,
    # Date filters
    start_date_min: str | None = None,
    start_date_max: str | None = None,
    end_date_min: str | None = None,
    end_date_max: str | None = None,
    # Tag filters
    tag: str | list[str] | None = None,
    tag_id: int | list[int] | None = None,
    related_tags: bool | None = None,
    tag_slug: str | list[str] | None = None
) -> EventList
```

**Examples:**

```python
# Get all active events
events = client.get_events(active=True, closed=False)

# Get events with high liquidity
high_liquidity_events = client.get_events(
    active=True,
    liquidity_min=10000
)

# Get events by specific tags
crypto_events = client.get_events(
    tag=["crypto", "bitcoin"],
    active=True
)

# Get events with pagination
events = client.get_events(limit=50, offset=0)
```

### Get Events with Pagination Metadata

```python
def get_events_paginated(
    # Same parameters as get_events()
) -> PaginatedResponse[Event]
```

**Example:**

```python
# Get events with pagination metadata
response = client.get_events_paginated(limit=10)
print(f"Total events: {response.meta.total}")
print(f"Current page events: {len(response.data)}")

# Check if more pages are available
if response.meta.has_next:
    next_response = client.get_events_paginated(
        limit=10, 
        offset=response.meta.next_offset
    )
```

### Iterate Through Events

```python
def iter_events(
    # Same parameters as get_events() except limit becomes page_size
    page_size: int | None = None,
    # ... other parameters
) -> Generator[Event, None, None]
```

**Example:**

```python
# Process all active events one by one (memory efficient)
for event in client.iter_events(active=True, page_size=50):
    print(f"Processing event: {event.title}")
    if event.volume > 10000:
        print(f"High volume event: {event.title}")
```

### Convenience Methods

```python
# Get active events
def get_active_events(self, limit: int = 100) -> EventList

# Get events by slug
def get_events_by_slug(
    self,
    slug: str | list[str],
    limit: int | None = None,
    active: bool | None = None,
    closed: bool | None = None,
    **kwargs
) -> EventList
```

**Examples:**

```python
# Get active events
active_events = client.get_active_events(limit=50)

# Get events by slug
events = client.get_events_by_slug("presidential-election-2024")

# Get multiple events by slug with filters
events = client.get_events_by_slug(
    ["event1-slug", "event2-slug"], 
    active=True,
    liquidity_min=1000
)
```

## Market Data (CLOB API)

### Get Market Data

```python
def get_market(self, condition_id: str) -> Market
```

**Example:**

```python
# Get market data for a specific condition
market = client.get_market("0x1234...")
print(f"Market ID: {market.condition_id}")
print(f"Market status: {market.active}")
```

### Get Order Book

```python
def get_order_book(self, token_id: str) -> OrderBook
```

**Example:**

```python
# Get order book for a token
order_book = client.get_order_book("0x1234...")

# Analyze the spread
best_bid = order_book.bids[0] if order_book.bids else None
best_ask = order_book.asks[0] if order_book.asks else None

if best_bid and best_ask:
    spread = float(best_ask.price) - float(best_bid.price)
    print(f"Current spread: {spread}")
```

### Get Price History

```python
def get_prices_history(
    self,
    market: str,
    start_ts: int | None = None,
    end_ts: int | None = None,
    interval: str | None = None,
    fidelity: int | None = None
) -> PricesHistory
```

**Examples:**

```python
# Get all available price history
history = client.get_prices_history("0x1234...")

# Get price history for the last week
history = client.get_prices_history("0x1234...", interval="1w")

# Get price history between specific timestamps
history = client.get_prices_history(
    market="0x1234...",
    start_ts=1640995200,  # Jan 1, 2022
    end_ts=1672531200     # Jan 1, 2023
)

# Get hourly price data (60-minute fidelity)
history = client.get_prices_history("0x1234...", fidelity=60)
```

## Trading Operations

### Submit Limit Orders

```python
def submit_limit_order(self, request: LimitOrderRequest) -> OrderResponse
```

**Example:**

```python
from polymarket_client import LimitOrderRequest, OrderSide, OrderType

# Create a limit order request
order_request = LimitOrderRequest(
    token_id="0x1234...",
    price=0.55,
    size=100.0,
    side=OrderSide.BUY,
    order_type=OrderType.GTC,  # Good Till Cancelled
    funder="0x5678..."  # Optional: specify funder address
)

# Submit the order
response = client.submit_limit_order(order_request)
print(f"Order ID: {response.order_id}")
print(f"Status: {response.status}")
```

### Cancel Orders

```python
# Cancel a single order
def cancel_order(self, order_id: str) -> CancelResponse

# Cancel multiple orders
def cancel_orders(self, order_ids: list[str]) -> CancelResponse

# Cancel all orders
def cancel_all_orders(self) -> CancelResponse
```

**Examples:**

```python
# Cancel a specific order
cancel_response = client.cancel_order("0xabc123...")

# Cancel multiple orders
cancel_response = client.cancel_orders(["0xabc123...", "0xdef456..."])

# Cancel all open orders
cancel_response = client.cancel_all_orders()

print(f"Cancelled orders: {cancel_response.cancelled}")
```

### Get Open Orders

```python
def get_open_orders(self, market: str | None = None) -> OrderList
```

**Example:**

```python
# Get all open orders
open_orders = client.get_open_orders()

# Get open orders for a specific market
market_orders = client.get_open_orders(market="0x1234...")

for order in open_orders.orders:
    print(f"Order {order.id}: {order.side} {order.size} @ {order.price}")
```

## Position Management

### Get User Positions

```python
# Get positions for a specific user
def get_user_position(
    self, 
    proxy_wallet_address: str, 
    market: str | None = None
) -> UserPositions

# Get current user's positions
def get_current_user_position(self, market: str | None = None) -> UserPositions
```

**Examples:**

```python
# Get current user's positions
positions = client.get_current_user_position()

# Get positions for a specific market
market_positions = client.get_current_user_position(market="0x1234...")

# Get positions for another user
user_positions = client.get_user_position(
    proxy_wallet_address="0x5678...",
    market="0x1234..."
)

for position in positions.positions:
    print(f"Market: {position.market}")
    print(f"Size: {position.size}")
    print(f"Value: {position.value}")
```

## Activity and History

### Get Trade History

```python
def get_user_market_trades_history(
    self, 
    token_id: str, 
    limit: int = 100,
    offset: int = 0
) -> TradeHistory
```

**Example:**

```python
# Get recent trades for a token
trades = client.get_user_market_trades_history("0x1234...", limit=50)

# Get next page of trades
more_trades = client.get_user_market_trades_history(
    token_id="0x1234...",
    limit=50,
    offset=50
)

# Calculate total volume
total_volume = sum(float(trade.size) for trade in trades.history)
print(f"Total trade volume: {total_volume}")
```

### Get User Activity

```python
def get_user_activity(
    self,
    proxy_wallet_address: str,
    limit: int = 100,
    offset: int = 0,
    market: str | None = None,
    activity_type: str | None = None,
    start: int | None = None,
    end: int | None = None,
    side: str | None = None,
    sort_by: str = "TIMESTAMP",
    sort_direction: str = "DESC"
) -> UserActivity

def get_current_user_activity(
    # Same parameters except proxy_wallet_address
) -> UserActivity
```

**Examples:**

```python
# Get recent activity for current user
activity = client.get_current_user_activity(limit=50)

# Get only trades
trades = client.get_current_user_activity(activity_type="TRADE")

# Get activity for a specific market
market_activity = client.get_current_user_activity(
    market="0x1234...",
    limit=100
)

# Get buy trades only
buy_trades = client.get_current_user_activity(
    activity_type="TRADE",
    side="BUY"
)

# Get activity for another user
user_activity = client.get_user_activity(
    proxy_wallet_address="0x5678...",
    activity_type="TRADE",
    start=1640995200,  # Start timestamp
    end=1672531200     # End timestamp
)
```

## Data Models

### Event

```python
class Event:
    id: int
    title: str
    description: str
    slug: str
    active: bool
    closed: bool
    archived: bool
    start_date: str
    end_date: str
    volume: float
    liquidity: float
    tags: list[Tag]
    markets: list[EventMarket]
```

### Market

```python
class Market:
    condition_id: str
    question: str
    active: bool
    closed: bool
    tokens: list[dict]
    # ... other market fields
```

### OrderBook

```python
class OrderBook:
    market_id: str
    asset_id: str
    timestamp: int
    hash: str
    bids: list[BookLevel]
    asks: list[BookLevel]
```

### BookLevel

```python
class BookLevel:
    price: str
    size: str
```

### Order Types and Enums

```python
class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    GTC = "GTC"  # Good Till Cancelled
    FOK = "FOK"  # Fill or Kill
    FAK = "FAK"  # Fill and Kill
    GTD = "GTD"  # Good Till Date

class OrderStatus(Enum):
    LIVE = "LIVE"
    CANCELED = "CANCELED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"
```

### LimitOrderRequest

```python
class LimitOrderRequest:
    token_id: str
    price: float
    size: float
    side: OrderSide
    order_type: OrderType = OrderType.GTC
    funder: str | None = None
    expires_at: int | None = None  # Required for GTD orders
```

## Advanced Usage

### Direct Client Access

For advanced operations, you can access the underlying clients directly:

```python
# Access Gamma client directly
gamma_client = client.gamma
# Use gamma-specific methods

# Access CLOB client directly  
clob_client = client.clob
# Use CLOB-specific methods

# Access underlying py_clob_client
py_clob_client = client.clob.py_client
# Use py_clob_client methods directly
```

### Utility Methods

```python
# Get user's Ethereum address
user_address = client.get_user_address()

# Input sanitization (used internally)
from polymarket_client import InputSanitizer
sanitized_id = InputSanitizer.sanitize_token_id("0x1234...")
sanitized_address = InputSanitizer.sanitize_hex_address("0x5678...")
```

## Error Handling

The client provides comprehensive error handling with specific exception types:

```python
from polymarket_client import (
    PolymarketError,
    PolymarketAPIError,
    PolymarketAuthenticationError,
    PolymarketNetworkError,
    PolymarketValidationError,
    # ... other exception types
)

try:
    events = client.get_events(active=True)
except PolymarketAuthenticationError:
    print("Authentication failed - check your credentials")
except PolymarketNetworkError:
    print("Network error - check your connection")
except PolymarketAPIError as e:
    print(f"API error: {e}")
except PolymarketError as e:
    print(f"General Polymarket error: {e}")
```

## Logging

The client includes comprehensive logging capabilities:

```python
from polymarket_client import setup_logging, get_logger

# Setup logging with custom configuration
setup_logging(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="polymarket.log"
)

# Get a logger for your application
logger = get_logger("my_app")
logger.info("Starting application")

# The client automatically logs API requests and user actions
```

## Rate Limiting

The client handles rate limiting automatically with exponential backoff and retry logic. Configure retry behavior through the PolymarketConfig:

```python
config = PolymarketConfig(
    max_retries=5,
    timeout=30,
    # ... other config
)
```

## Complete Example

```python
from polymarket_client import PolymarketClient, LimitOrderRequest, OrderSide, OrderType

# Initialize client
client = PolymarketClient()

# Get active events
events = client.get_active_events(limit=10)
print(f"Found {len(events)} active events")

# Get market data for first event's first market
if events and events[0].markets:
    market_id = events[0].markets[0].condition_id
    
    # Get order book
    order_book = client.get_order_book(market_id)
    print(f"Order book has {len(order_book.bids)} bids and {len(order_book.asks)} asks")
    
    # Submit a limit order
    order_request = LimitOrderRequest(
        token_id=market_id,
        price=0.45,
        size=10.0,
        side=OrderSide.BUY,
        order_type=OrderType.GTC
    )
    
    order_response = client.submit_limit_order(order_request)
    print(f"Order submitted: {order_response.order_id}")
    
    # Get user positions
    positions = client.get_current_user_position()
    print(f"User has {len(positions.positions)} positions")
    
    # Get user activity
    activity = client.get_current_user_activity(limit=20)
    print(f"User has {len(activity.activity)} recent activities")
```

This documentation covers the main functionality of the Polymarket Client SDK. For more advanced usage and detailed parameter descriptions, refer to the inline documentation and examples in the codebase.