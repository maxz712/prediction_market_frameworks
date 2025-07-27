from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    GTC = "GTC"  # Good Till Cancelled
    FOK = "FOK"  # Fill or Kill
    FAK = "FAK"  # Fill and Kill
    GTD = "GTD"  # Good Till Date


class OrderStatus(str, Enum):
    OPEN = "OPEN"
    LIVE = "LIVE"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Order(BaseModel):
    """Represents an order in the Polymarket CLOB."""

    order_id: str = Field(..., description="Unique order identifier")
    market: str = Field(..., description="Market identifier")
    token_id: str = Field(..., description="Token identifier")
    side: OrderSide = Field(..., description="Order side (BUY or SELL)")
    order_type: OrderType = Field(..., description="Order type (GTC, FOK, etc.)")
    status: OrderStatus = Field(..., description="Current order status")

    # Price and size information
    price: float = Field(..., description="Price per unit")
    size: float = Field(..., description="Total order size")
    filled_size: float = Field(0.0, description="Amount filled so far")
    remaining_size: float = Field(..., description="Remaining unfilled size")

    # User information
    owner: str = Field(..., description="Address of the order owner")

    # Timestamps
    created_at: datetime = Field(..., description="Order creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    expires_at: datetime | None = Field(
        None, description="Expiration timestamp for GTD orders"
    )

    # Additional metadata
    fee_rate: float | None = Field(None, description="Fee rate for this order")
    nonce: int | None = Field(None, description="Order nonce")
    signature: str | None = Field(None, description="Order signature")

    @staticmethod
    def _parse_timestamp(timestamp_value) -> datetime:
        """Parse timestamp from various formats (Unix timestamp or ISO string)."""
        if timestamp_value is None:
            msg = "Timestamp cannot be None"
            raise ValueError(msg)

        # Handle Unix timestamp (integer or string that represents a number)
        if isinstance(timestamp_value, int | float):
            return datetime.fromtimestamp(timestamp_value)

        # Handle string timestamp (could be Unix timestamp or ISO format)
        if isinstance(timestamp_value, str):
            # Try to parse as Unix timestamp first
            try:
                unix_timestamp = float(timestamp_value)
                return datetime.fromtimestamp(unix_timestamp)
            except ValueError:
                # Try to parse as ISO format
                return datetime.fromisoformat(timestamp_value.replace("Z", "+00:00"))

        msg = f"Unable to parse timestamp: {timestamp_value}"
        raise ValueError(msg)

    @classmethod
    def from_raw_data(cls, raw_order: dict) -> "Order":
        """Create an Order instance from raw API response data."""
        # Map raw fields to our model fields
        return cls(
            order_id=raw_order.get("id", raw_order.get("order_id")),
            market=raw_order.get("market"),
            token_id=raw_order.get("token_id", raw_order.get("asset_id")),
            side=OrderSide(raw_order.get("side", "").upper()),
            order_type=OrderType(raw_order.get("order_type", "GTC").upper()),
            status=OrderStatus(raw_order.get("status", "OPEN").upper()),
            price=float(raw_order.get("price", 0)),
            size=float(raw_order.get("size", raw_order.get("original_size", 0))),
            filled_size=float(
                raw_order.get("filled_size", raw_order.get("size_matched", 0))
            ),
            remaining_size=float(
                raw_order.get(
                    "remaining_size",
                    float(raw_order.get("size", 0))
                    - float(raw_order.get("size_matched", 0)),
                )
            ),
            owner=raw_order.get("owner", raw_order.get("maker", raw_order.get("user"))),
            created_at=cls._parse_timestamp(
                raw_order.get("created_at", raw_order.get("timestamp"))
            ),
            updated_at=cls._parse_timestamp(raw_order.get("updated_at"))
            if raw_order.get("updated_at")
            else None,
            expires_at=cls._parse_timestamp(raw_order.get("expires_at"))
            if raw_order.get("expires_at")
            else None,
            fee_rate=float(
                raw_order.get("fee_rate", raw_order.get("fee_rate_bps", 0)) / 10000
            )
            if raw_order.get("fee_rate") or raw_order.get("fee_rate_bps")
            else None,
            nonce=raw_order.get("nonce"),
            signature=raw_order.get("signature"),
        )

    @property
    def is_buy(self) -> bool:
        """Check if this is a buy order."""
        return self.side == OrderSide.BUY

    @property
    def is_sell(self) -> bool:
        """Check if this is a sell order."""
        return self.side == OrderSide.SELL

    @property
    def is_open(self) -> bool:
        """Check if the order is still open."""
        return self.status in [
            OrderStatus.OPEN,
            OrderStatus.LIVE,
            OrderStatus.PARTIALLY_FILLED,
        ]

    @property
    def is_filled(self) -> bool:
        """Check if the order is completely filled."""
        return self.status == OrderStatus.FILLED

    @property
    def is_cancelled(self) -> bool:
        """Check if the order was cancelled."""
        return self.status == OrderStatus.CANCELLED

    @property
    def fill_percentage(self) -> float:
        """Calculate the fill percentage."""
        if self.size == 0:
            return 0.0
        return (self.filled_size / self.size) * 100

    @property
    def total_value(self) -> float:
        """Calculate the total order value."""
        return self.price * self.size

    @property
    def filled_value(self) -> float:
        """Calculate the filled value."""
        return self.price * self.filled_size


class OrderList(BaseModel):
    """Container for multiple orders with pagination info."""

    orders: list[Order] = Field(default_factory=list, description="List of orders")
    total: int | None = Field(
        None, description="Total number of orders matching the query"
    )
    limit: int | None = Field(None, description="Limit used in the query")
    offset: int | None = Field(None, description="Offset used in the query")

    @classmethod
    def from_raw_response(cls, raw_response: dict) -> "OrderList":
        """Create an OrderList from raw API response."""
        orders = []

        # Handle different response formats
        if isinstance(raw_response, list):
            # Response is just a list of orders
            orders = [Order.from_raw_data(order) for order in raw_response]
            return cls(orders=orders)

        # Response is a dict with orders and possibly pagination info
        raw_orders = raw_response.get("orders", raw_response.get("data", []))
        if isinstance(raw_orders, list):
            orders = [Order.from_raw_data(order) for order in raw_orders]

        return cls(
            orders=orders,
            total=raw_response.get("total", raw_response.get("count")),
            limit=raw_response.get("limit"),
            offset=raw_response.get("offset"),
        )

    def __iter__(self):
        """Make OrderList iterable."""
        return iter(self.orders)

    def __len__(self):
        """Return the number of orders."""
        return len(self.orders)

    def __getitem__(self, index):
        """Allow indexing into the orders list."""
        return self.orders[index]

    def filter_by_status(self, status: OrderStatus) -> list[Order]:
        """Filter orders by status."""
        return [order for order in self.orders if order.status == status]

    def filter_by_side(self, side: OrderSide) -> list[Order]:
        """Filter orders by side."""
        return [order for order in self.orders if order.side == side]

    def filter_by_market(self, market: str) -> list[Order]:
        """Filter orders by market."""
        return [order for order in self.orders if order.market == market]

    @property
    def open_orders(self) -> list[Order]:
        """Get only open orders."""
        return [order for order in self.orders if order.is_open]

    @property
    def buy_orders(self) -> list[Order]:
        """Get only buy orders."""
        return self.filter_by_side(OrderSide.BUY)

    @property
    def sell_orders(self) -> list[Order]:
        """Get only sell orders."""
        return self.filter_by_side(OrderSide.SELL)
