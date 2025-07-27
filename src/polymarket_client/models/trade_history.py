"""Trade history data models for Polymarket."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class MakerOrder(BaseModel):
    """Model for a maker order within a trade."""

    model_config = ConfigDict(extra="allow")

    order_id: str
    owner: str
    maker_address: str
    matched_amount: str
    price: str
    fee_rate_bps: str
    asset_id: str
    outcome: str
    side: str


class Trade(BaseModel):
    """Model for a single trade record."""

    model_config = ConfigDict(extra="allow")

    id: str
    taker_order_id: str
    market: str
    asset_id: str
    side: str
    size: str
    fee_rate_bps: str
    price: str
    status: str
    match_time: str
    last_update: str
    outcome: str
    bucket_index: int
    owner: str
    maker_address: str
    transaction_hash: str
    maker_orders: list[MakerOrder]
    trader_side: str


class TradeHistory(BaseModel):
    """Model for trade history response."""

    model_config = ConfigDict(extra="allow")

    trades: list[Trade]
    total_count: int | None = None
    next_cursor: str | None = None

    @classmethod
    def from_raw_trades(
        cls,
        raw_trades: list[dict[str, Any]],
        total_count: int | None = None,
        next_cursor: str | None = None,
    ) -> "TradeHistory":
        """Create TradeHistory from raw trade data."""
        trades = []
        for trade_data in raw_trades:
            # Convert maker_orders
            maker_orders = [
                MakerOrder(**order) for order in trade_data.get("maker_orders", [])
            ]

            # Create trade with maker_orders
            trade_dict = trade_data.copy()
            trade_dict["maker_orders"] = maker_orders
            trades.append(Trade(**trade_dict))

        return cls(trades=trades, total_count=total_count, next_cursor=next_cursor)
