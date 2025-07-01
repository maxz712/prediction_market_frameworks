# src/prediction_market_frameworks/core/models.py

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Iterator

@dataclass(frozen=True)
class BookLevel:
    price: float
    volume: float
    total: float  # cumulative volume at or before this level

    def __post_init__(self):
        if self.price < 0 or self.volume < 0 or self.total < 0:
            raise ValueError("Price, volume, and total must be non-negative")

@dataclass(frozen=True)
class OrderBook:
    market_id: str
    asset_id: str
    timestamp: int
    hash: str
    bids: List[BookLevel]
    asks: List[BookLevel]

    def best_bid(self) -> Optional[BookLevel]:
        """Return the highest bid, or None if no bids."""
        return self.bids[0] if self.bids else None

    def best_ask(self) -> Optional[BookLevel]:
        """Return the lowest ask, or None if no asks."""
        return self.asks[0] if self.asks else None

    def spread(self) -> Optional[float]:
        """Return the bid-ask spread, or None if incomplete book."""
        bb, ba = self.best_bid(), self.best_ask()
        return None if bb is None or ba is None else ba.price - bb.price

    def mid_price(self) -> Optional[float]:
        """Return the mid-price, or None if incomplete book."""
        bb, ba = self.best_bid(), self.best_ask()
        return None if bb is None or ba is None else (bb.price + ba.price) / 2

    def total_depth(self, side: str) -> float:
        """
        Compute total volume on given side ('bids' or 'asks').
        """
        levels = self.bids if side == "bids" else self.asks
        if side not in ("bids", "asks"):
            raise ValueError("side must be 'bids' or 'asks'")
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
            raise ValueError("side must be 'bids' or 'asks'")
