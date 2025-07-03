
from abc import ABC, abstractmethod
from typing import List

from src.data_frameworks.ports.base_port import BasePort


class DataPort(BasePort, ABC):
    """Interface for prediction market data sources."""

    @abstractmethod
    def get_order_book(self, token_id: str):
        """Get order book for a specific token."""
        pass
    
    @abstractmethod
    def get_market(self, condition_id: str):
        """Get market data for a specific condition."""
        pass
    
    @abstractmethod
    def get_active_events(self, limit: int = 100):
        """Get currently active events."""
        pass
