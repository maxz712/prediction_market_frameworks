from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from py_clob_client.client import ClobClient as PyClobClient
from py_clob_client.clob_types import ApiCreds, OrderBookSummary


class ClobClient:
    """
    Wrapper around py_clob_client.ClobClient that extends functionality
    with additional CLOB API endpoints not implemented in the base client.
    """
    
    def __init__(self, host: str, key: str, chain_id: int, creds: ApiCreds):
        self.host = host.rstrip("/")
        self.key = key
        self.chain_id = chain_id
        self.creds = creds
        
        # Initialize the underlying py_clob_client
        self._py_client = PyClobClient(
            host=host,
            key=key,
            chain_id=chain_id,
            creds=creds
        )
        
        # Initialize session for direct API calls
        self._session = self._init_session()
    
    def _init_session(self) -> requests.Session:
        """Initialize session with retry strategy for direct API calls."""
        session = requests.Session()
        retry = Retry(
            total=3, backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
    
    # Delegate existing methods to the underlying py_clob_client
    def get_market(self, condition_id: str) -> Dict[str, Any]:
        """Get market data for a given condition ID."""
        return self._py_client.get_market(condition_id)
    
    def get_order_book(self, token_id: str) -> OrderBookSummary:
        """Get order book summary for a given token ID."""
        return self._py_client.get_order_book(token_id)
    
    def get_trades(self, market: str, **kwargs) -> Dict[str, Any]:
        """Get trades for a market."""
        return self._py_client.get_trades(market, **kwargs)
    
    def get_orders(self, **kwargs) -> Dict[str, Any]:
        """Get orders."""
        return self._py_client.get_orders(**kwargs)
    
    def post_order(self, order_args: Dict[str, Any]) -> Dict[str, Any]:
        """Post an order."""
        return self._py_client.post_order(order_args)
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        return self._py_client.cancel_order(order_id)
    
    def cancel_orders(self, order_ids: list) -> Dict[str, Any]:
        """Cancel multiple orders."""
        return self._py_client.cancel_orders(order_ids)
    
    def cancel_all(self) -> Dict[str, Any]:
        """Cancel all orders."""
        return self._py_client.cancel_all()
    
    # Extended functionality - additional CLOB API endpoints
    def get_market_trades_history(self, market_id: str, limit: int = 100, 
                                 offset: int = 0) -> Dict[str, Any]:
        """
        Get comprehensive trade history for a market.
        Extended endpoint not available in base py_clob_client.
        """
        url = f"{self.host}/trade-history"
        params = {
            "market": market_id,
            "limit": limit,
            "offset": offset
        }
        
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_market_depth(self, token_id: str, depth: int = 10) -> Dict[str, Any]:
        """
        Get market depth with specified number of levels.
        Extended endpoint for more detailed order book data.
        """
        url = f"{self.host}/book"
        params = {
            "token_id": token_id,
            "depth": depth
        }
        
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_market_statistics(self, market_id: str) -> Dict[str, Any]:
        """
        Get comprehensive market statistics.
        Extended endpoint for market analytics.
        """
        url = f"{self.host}/markets/{market_id}/stats"
        
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_user_positions(self, user_address: str) -> Dict[str, Any]:
        """
        Get user positions across all markets.
        Extended endpoint for position tracking.
        """
        url = f"{self.host}/positions"
        params = {"user": user_address}
        
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_market_candles(self, market_id: str, interval: str = "1h", 
                          limit: int = 100) -> Dict[str, Any]:
        """
        Get candlestick data for market price history.
        Extended endpoint for historical price data.
        
        Args:
            market_id: Market identifier
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to return
        """
        url = f"{self.host}/candles"
        params = {
            "market": market_id,
            "interval": interval,
            "limit": limit
        }
        
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    # Expose the underlying client for any methods not explicitly wrapped
    @property
    def py_client(self) -> PyClobClient:
        """Access to the underlying py_clob_client for advanced usage."""
        return self._py_client