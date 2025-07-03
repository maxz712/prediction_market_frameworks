from typing import List, Optional

from ..configs.polymarket_configs import PolymarketConfig
from ..clients.polymarket_client import PolymarketClient

from ...core.models.order_book import OrderBook
from ...core.models.event import Event
from ...core.models.market import Market
from ...ports.data_port import DataPort


class PolymarketDataAdapter(DataPort):
    def __init__(self, config: Optional[PolymarketConfig] = None):
        self.client = PolymarketClient(config)
        self._connected = False

    def connect(self):
        """Connect to Polymarket APIs."""
        self._connected = True

    def disconnect(self):
        """Disconnect from Polymarket APIs."""
        self._connected = False

    def health_check(self) -> bool:
        """Check if the adapter is healthy and connected."""
        return self._connected and self.client is not None

    def get_market(self, condition_id: str) -> Market:
        return self.client.get_market(condition_id)

    def get_order_book(self, token_id: str) -> OrderBook:
        return self.client.get_order_book(token_id)

    def get_active_events(self, limit: int = 100) -> List[Event]:
        """
        Retrieves all currently *ongoing* events: active=true & closed=false, optionally filtering by future end dates.
        """
        return self.client.get_active_events(limit=limit)
