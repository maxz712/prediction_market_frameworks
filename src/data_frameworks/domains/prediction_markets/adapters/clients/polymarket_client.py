from typing import List, Dict, Any, Optional
from py_clob_client.clob_types import ApiCreds, OrderBookSummary

from .gamma_client import GammaClient
from .clob_client import ClobClient
from ..configs.polymarket_configs import PolymarketConfig
from ...core.models.event import Event
from ...core.models.market import Market
from ...core.models.order_book import OrderBook


class PolymarketClient:
    """
    Unified client for accessing all Polymarket APIs.
    Wraps both Gamma API (events/markets) and CLOB API (trading/order books).
    """
    
    def __init__(self, config: Optional[PolymarketConfig] = None):
        """
        Initialize the unified Polymarket client.
        
        Args:
            config: PolymarketConfig instance. If None, loads from environment variables.
        """
        if config is None:
            config = PolymarketConfig.from_env()
        
        self.config = config
        self.gamma_client = GammaClient(config.hosts["gamma"])
        self.clob_client = ClobClient(
            host=config.hosts["clob"],
            key=config.pk,
            chain_id=config.chain_id,
            creds=ApiCreds(
                api_key=config.api_key,
                api_secret=config.api_secret,
                api_passphrase=config.api_passphrase
            )
        )
    
    # Event-related methods (Gamma API)
    def get_events(self, active: bool = True, closed: bool = False,
                   end_date_min: str = None, limit: int = 100, 
                   offset: int = 0) -> List[Event]:
        """Get events from Gamma API."""
        return self.gamma_client.get_events(
            active=active, closed=closed, end_date_min=end_date_min,
            limit=limit, offset=offset
        )
    
    def get_active_events(self, limit: int = 100) -> List[Event]:
        """Get currently active events."""
        return self.get_events(active=True, closed=False, limit=limit)
    
    # Market-related methods
    def get_market(self, condition_id: str) -> Market:
        """Get market data from CLOB API."""
        market_data = self.clob_client.get_market(condition_id)
        return Market.model_validate(market_data)
    
    def get_markets(self, market_id: str = None) -> Dict[str, Any]:
        """Get market data from Gamma API (skeleton - to be implemented)."""
        return self.gamma_client.get_markets(market_id)
    
    # Order book and trading methods (CLOB API)
    def get_order_book(self, token_id: str) -> OrderBook:
        """Get order book for a token."""
        summary = self.clob_client.get_order_book(token_id)
        return OrderBook.from_raw_data(
            market_id=summary.market,
            asset_id=summary.asset_id,
            timestamp=int(summary.timestamp),
            hash=summary.hash,
            raw_bids=summary.bids,
            raw_asks=summary.asks
        )
    
    def get_order_book_raw(self, token_id: str) -> OrderBookSummary:
        """Get raw order book summary."""
        return self.clob_client.get_order_book(token_id)
    
    def get_market_depth(self, token_id: str, depth: int = 10) -> Dict[str, Any]:
        """Get detailed market depth."""
        return self.clob_client.get_market_depth(token_id, depth)
    
    # Trading methods (CLOB API)
    def get_trades(self, market: str, **kwargs) -> Dict[str, Any]:
        """Get trades for a market."""
        return self.clob_client.get_trades(market, **kwargs)
    
    def get_market_trades_history(self, market_id: str, limit: int = 100,
                                 offset: int = 0) -> Dict[str, Any]:
        """Get comprehensive trade history."""
        return self.clob_client.get_market_trades_history(market_id, limit, offset)
    
    def get_orders(self, **kwargs) -> Dict[str, Any]:
        """Get orders."""
        return self.clob_client.get_orders(**kwargs)
    
    def post_order(self, order_args: Dict[str, Any]) -> Dict[str, Any]:
        """Post an order."""
        return self.clob_client.post_order(order_args)
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order."""
        return self.clob_client.cancel_order(order_id)
    
    def cancel_orders(self, order_ids: list) -> Dict[str, Any]:
        """Cancel multiple orders."""
        return self.clob_client.cancel_orders(order_ids)
    
    def cancel_all_orders(self) -> Dict[str, Any]:
        """Cancel all orders."""
        return self.clob_client.cancel_all()
    
    # Trading execution methods
    def submit_market_order(self, token_id: str, side: str, size: float) -> Dict[str, Any]:
        """Submit a market order for immediate execution."""
        return self.clob_client.submit_market_order(token_id, side, size)
    
    def submit_limit_order_gtc(self, token_id: str, side: str, size: float, price: float) -> Dict[str, Any]:
        """Submit a limit order that is good till cancellation (GTC)."""
        return self.clob_client.submit_limit_order_gtc(token_id, side, size, price)
    
    def get_open_orders(self, market: Optional[str] = None) -> Dict[str, Any]:
        """Get current open orders for the authenticated user."""
        return self.clob_client.get_open_orders(market)
    
    def get_current_user_position(self, market: Optional[str] = None) -> Dict[str, Any]:
        """Get current user position."""
        return self.clob_client.get_current_user_position(market)
    
    # Analytics and statistics methods (CLOB API)
    def get_market_statistics(self, market_id: str) -> Dict[str, Any]:
        """Get market statistics."""
        return self.clob_client.get_market_statistics(market_id)
    
    def get_user_positions(self, user_address: str) -> Dict[str, Any]:
        """Get user positions."""
        return self.clob_client.get_user_positions(user_address)
    
    def get_market_candles(self, market_id: str, interval: str = "1h",
                          limit: int = 100) -> Dict[str, Any]:
        """Get candlestick data."""
        return self.clob_client.get_market_candles(market_id, interval, limit)
    
    # Access to underlying clients for advanced usage
    @property
    def gamma(self) -> GammaClient:
        """Direct access to Gamma client."""
        return self.gamma_client
    
    @property
    def clob(self) -> ClobClient:
        """Direct access to CLOB client."""
        return self.clob_client