from abc import ABC, abstractmethod
from typing import Dict, List, Any
from src.data_frameworks.ports.base_port import BasePort


class FinancialDataPort(BasePort, ABC):
    """Interface for financial data providers."""
    
    @abstractmethod
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol."""
        pass
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data for a symbol."""
        pass
    
    @abstractmethod
    def get_historical_prices(self, symbol: str, **kwargs) -> List[Dict[str, Any]]:
        """Get historical price data."""
        pass