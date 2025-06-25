from connectors.abstract_connector import Connector
from abc import ABC, abstractmethod

class DataConnector(Connector, ABC):
    """Interface for data sources (market, news)."""

    @abstractmethod
    def get_market_data(self):
        """Return fresh market data (price, orderbook, etc.)."""
        pass
