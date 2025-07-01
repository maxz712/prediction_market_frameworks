
from abc import ABC, abstractmethod

from src.prediction_market_frameworks.ports.port import Port


class DataPort(Port, ABC):
    """Interface for data sources (market, news)."""

    @abstractmethod
    def get_order_book(self):
        """Return fresh market data (price, orderbook, etc.)."""
        pass
