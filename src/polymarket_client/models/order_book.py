from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, field_validator

if TYPE_CHECKING:
    from collections.abc import Iterator


class BookLevel(BaseModel):
    price: float
    volume: float
    total: float  # cumulative volume at or before this level

    @field_validator("price", "volume", "total")
    @classmethod
    def validate_non_negative(cls, v: float) -> float:
        if v < 0:
            msg = "Price, volume, and total must be non-negative"
            raise ValueError(msg)
        return v

    class Config:
        frozen = True

class OrderBook(BaseModel):
    market_id: str
    asset_id: str
    timestamp: int
    hash: str
    bids: list[BookLevel]
    asks: list[BookLevel]

    def best_bid(self) -> BookLevel | None:
        """Return the highest bid, or None if no bids."""
        return self.bids[0] if self.bids else None

    def best_ask(self) -> BookLevel | None:
        """Return the lowest ask, or None if no asks."""
        return self.asks[0] if self.asks else None

    def spread(self) -> float | None:
        """Return the bid-ask spread, or None if incomplete book."""
        bb, ba = self.best_bid(), self.best_ask()
        return None if bb is None or ba is None else ba.price - bb.price

    def mid_price(self) -> float | None:
        """Return the mid-price, or None if incomplete book."""
        bb, ba = self.best_bid(), self.best_ask()
        return None if bb is None or ba is None else (bb.price + ba.price) / 2

    def total_depth(self, side: str) -> float:
        """
        Compute total volume on given side ('bids' or 'asks').
        """
        levels = self.bids if side == "bids" else self.asks
        if side not in ("bids", "asks"):
            msg = "side must be 'bids' or 'asks'"
            raise ValueError(msg)
        return sum(l.volume for l in levels)

    def levels(self, side: str) -> Iterator[BookLevel]:
        """
        Iterate through levels on the specified side.
        """
        if side == "bids":
            yield from self.bids
        elif side == "asks":
            yield from self.asks
        else:
            msg = "side must be 'bids' or 'asks'"
            raise ValueError(msg)

    @classmethod
    def from_raw_data(cls, market_id: str, asset_id: str, timestamp: int, hash: str,
                      raw_bids: list[Any], raw_asks: list[Any]) -> OrderBook:
        """Create OrderBook from raw bid/ask data with level conversion."""
        def convert_levels(raw_levels: list[Any], is_bid: bool = False) -> list[dict]:
            parsed = [(float(r.price), float(r.size)) for r in raw_levels]
            sorted_levels = sorted(parsed, key=lambda p: -p[0]) if is_bid else sorted(parsed, key=lambda p: p[0])

            levels = []
            total = 0.0
            for price, vol in sorted_levels:
                total += vol
                levels.append({"price": price, "volume": vol, "total": total})
            return levels

        return cls.model_validate({
            "market_id": market_id,
            "asset_id": asset_id,
            "timestamp": timestamp,
            "hash": hash,
            "bids": convert_levels(raw_bids, is_bid=True),
            "asks": convert_levels(raw_asks, is_bid=False)
        })

    class Config:
        frozen = True
