from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from py_clob_client.client import ClobClient as PyClobClient
from py_clob_client.clob_types import ApiCreds, OrderBookSummary
from .configs.polymarket_configs import PolymarketConfig
from .exceptions import PolymarketAPIError, PolymarketNetworkError


class ClobClient:
    """
    Wrapper around py_clob_client.ClobClient that extends functionality
    with additional CLOB API endpoints not implemented in the base client.
    """
    
    def __init__(self, config: PolymarketConfig) -> None:
        """Initialize the CLOB client.
        
        Args:
            config: Polymarket configuration containing API credentials and endpoints
        """
        self.config = config
        
        # Initialize the underlying py_clob_client
        self._py_client = PyClobClient(
            host=config.get_endpoint("clob"),
            key=config.api_key,
            chain_id=config.chain_id,
            creds=config.api_creds
        )
        
        # Initialize session for direct API calls
        self._session = self._init_session()
    
    @classmethod
    def from_config_dict(cls, config_dict: Dict[str, Any]) -> 'ClobClient':
        """Create ClobClient from configuration dictionary."""
        config = PolymarketConfig(**config_dict)
        return cls(config)
    
    @classmethod
    def from_env(cls) -> 'ClobClient':
        """Create ClobClient from environment variables."""
        config = PolymarketConfig.from_env()
        return cls(config)
    
    def _init_session(self) -> requests.Session:
        """Initialize session with retry strategy for direct API calls."""
        session = requests.Session()
        retry = Retry(
            total=self.config.max_retries, backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.timeout = self.config.timeout
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
    
    def cancel_orders(self, order_ids: List[str]) -> Dict[str, Any]:
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
        url = f"{self.config.get_endpoint('clob')}/trade-history"
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
        url = f"{self.config.get_endpoint('clob')}/book"
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
        url = f"{self.config.get_endpoint('clob')}/markets/{market_id}/stats"
        
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_user_positions(self, user_address: str) -> Dict[str, Any]:
        """
        Get user positions across all markets.
        Extended endpoint for position tracking.
        """
        url = f"{self.config.get_endpoint('clob')}/positions"
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
        url = f"{self.config.get_endpoint('clob')}/candles"
        params = {
            "market": market_id,
            "interval": interval,
            "limit": limit
        }
        
        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    # Trading execution methods
    def submit_market_order(self, token_id: str, side: str, size: float) -> Dict[str, Any]:
        """
        Submit a market order for immediate execution.
        
        Args:
            token_id: The token ID to trade
            side: 'BUY' or 'SELL'
            size: Size of the order
        """
        order_args = {
            "token_id": token_id,
            "side": side.upper(),
            "type": "MARKET",
            "size": str(size)
        }
        return self.post_order(order_args)
    
    def submit_limit_order_gtc(self, token_id: str, side: str, size: float, price: float) -> Dict[str, Any]:
        """
        Submit a limit order that is good till cancellation (GTC).
        
        Args:
            token_id: The token ID to trade
            side: 'BUY' or 'SELL'
            size: Size of the order
            price: Price per unit
        """
        order_args = {
            "token_id": token_id,
            "side": side.upper(),
            "type": "LIMIT",
            "size": str(size),
            "price": str(price),
            "time_in_force": "GTC"
        }
        return self.post_order(order_args)
    
    def get_open_orders(self, market: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current open orders for the authenticated user.
        
        Args:
            market: Optional market filter
        """
        params = {"status": "OPEN"}
        if market:
            params["market"] = market
        return self.get_orders(**params)
    
    def get_current_user_position(self, market: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current user position.
        
        Args:
            market: Optional market filter
        """
        # Get user address from credentials
        user_address = self.config.api_creds.api_key  # This might need adjustment based on actual API
        positions = self.get_user_positions(user_address)
        
        if market:
            # Filter positions by market if specified
            filtered_positions = []
            for position in positions.get("positions", []):
                if position.get("market") == market:
                    filtered_positions.append(position)
            return {"positions": filtered_positions}
        
        return positions
    
    # Expose the underlying client for any methods not explicitly wrapped
    @property
    def py_client(self) -> PyClobClient:
        """Access to the underlying py_clob_client for advanced usage."""
        return self._py_client