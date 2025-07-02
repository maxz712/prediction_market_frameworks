from typing import List, Optional

from src.prediction_market_frameworks.adapters.configs.polymarket_configs import PolymarketConfig
from src.prediction_market_frameworks.adapters.clients.polymarket_client import PolymarketClient

from src.prediction_market_frameworks.core.models.order_book import OrderBook
from src.prediction_market_frameworks.core.models.event import Event
from src.prediction_market_frameworks.core.models.market import Market
from src.prediction_market_frameworks.ports.data_port import DataPort


class PolymarketDataAdapter(DataPort):
    def __init__(self, config: Optional[PolymarketConfig] = None):
        self.client = PolymarketClient(config)

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_market(self, condition_id: str) -> Market:
        return self.client.get_market(condition_id)

    def get_order_book(self, token_id: str) -> OrderBook:
        return self.client.get_order_book(token_id)

    def get_active_events(self, limit: int = 100) -> List[Event]:
        """
        Retrieves all currently *ongoing* events: active=true & closed=false, optionally filtering by future end dates.
        """
        return self.client.get_active_events(limit=limit)
