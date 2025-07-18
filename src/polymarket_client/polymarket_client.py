from typing import List, Dict, Any, Optional, Generator, Union
from py_clob_client.clob_types import OrderBookSummary

from .gamma_client import GammaClient
from .clob_client import ClobClient
from .configs.polymarket_configs import PolymarketConfig
from .models.event import Event
from .models.market import Market
from .models.order_book import OrderBook
from .models.pagination import PaginatedResponse
from .exceptions import PolymarketConfigurationError


class PolymarketClient:
    """
    Unified client for accessing all Polymarket APIs.
    Wraps both Gamma API (events/markets) and CLOB API (trading/order books).
    """
    
    def __init__(self, config: Optional[PolymarketConfig] = None) -> None:
        """
        Initialize the unified Polymarket client.
        
        Args:
            config: PolymarketConfig instance. If None, loads from environment variables.
        """
        if config is None:
            try:
                config = PolymarketConfig.from_env()
            except Exception as e:
                raise PolymarketConfigurationError(
                    "Failed to load configuration from environment variables. "
                    "Please provide a config object or set the required environment variables."
                ) from e
        
        self.config = config
        self.gamma_client = GammaClient(config)
        self.clob_client = ClobClient(config)
    
    # Event-related methods (Gamma API)
    def get_events(
        self, 
        # Pagination parameters
        limit: Optional[int] = None,
        offset: int = 0,
        auto_paginate: Optional[bool] = None,
        # Sorting parameters
        order: Optional[str] = None,
        ascending: bool = True,
        # ID and slug filters
        event_id: Optional[Union[int, List[int]]] = None,
        slug: Optional[Union[str, List[str]]] = None,
        # Status filters
        archived: Optional[bool] = None,
        active: Optional[bool] = True,
        closed: Optional[bool] = False,
        # Volume and liquidity filters
        liquidity_min: Optional[float] = None,
        liquidity_max: Optional[float] = None,
        volume_min: Optional[float] = None,
        volume_max: Optional[float] = None,
        # Date filters
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        end_date_min: Optional[str] = None,
        end_date_max: Optional[str] = None,
        # Tag filters
        tag: Optional[Union[str, List[str]]] = None,
        tag_id: Optional[Union[int, List[int]]] = None,
        related_tags: Optional[bool] = None,
        tag_slug: Optional[Union[str, List[str]]] = None
    ) -> List[Event]:
        """Get events from Gamma API with comprehensive filtering options.
        
        Args:
            limit: Maximum number of events to return total (uses config default if None)
            offset: Offset for pagination
            auto_paginate: Whether to automatically paginate through all results (uses config default if None)
            order: Key to sort by
            ascending: Sort direction, defaults to True (requires order parameter)
            event_id: ID of a single event to query, can be int or list of ints
            slug: Slug of a single event to query, can be string or list of strings
            archived: Filter by archived status
            active: Filter for active events
            closed: Filter for closed events
            liquidity_min: Filter by minimum liquidity
            liquidity_max: Filter by maximum liquidity
            volume_min: Filter by minimum volume
            volume_max: Filter by maximum volume
            start_date_min: Filter by minimum start date (ISO format)
            start_date_max: Filter by maximum start date (ISO format)
            end_date_min: Minimum end date filter (ISO format)
            end_date_max: Filter by maximum end date (ISO format)
            tag: Filter by tag labels, can be string or list of strings
            tag_id: Filter by tag ID, can be int or list of ints
            related_tags: Include events with related tags (requires tag_id parameter)
            tag_slug: Filter by tag slug, can be string or list of strings
        """
        return self.gamma_client.get_events(
            limit=limit,
            offset=offset,
            auto_paginate=auto_paginate,
            order=order,
            ascending=ascending,
            event_id=event_id,
            slug=slug,
            archived=archived,
            active=active,
            closed=closed,
            liquidity_min=liquidity_min,
            liquidity_max=liquidity_max,
            volume_min=volume_min,
            volume_max=volume_max,
            start_date_min=start_date_min,
            start_date_max=start_date_max,
            end_date_min=end_date_min,
            end_date_max=end_date_max,
            tag=tag,
            tag_id=tag_id,
            related_tags=related_tags,
            tag_slug=tag_slug
        )
    
    def get_events_paginated(
        self, 
        # Pagination parameters
        limit: Optional[int] = None,
        offset: int = 0,
        auto_paginate: Optional[bool] = None,
        # Sorting parameters
        order: Optional[str] = None,
        ascending: bool = True,
        # ID and slug filters
        event_id: Optional[Union[int, List[int]]] = None,
        slug: Optional[Union[str, List[str]]] = None,
        # Status filters
        archived: Optional[bool] = None,
        active: Optional[bool] = True,
        closed: Optional[bool] = False,
        # Volume and liquidity filters
        liquidity_min: Optional[float] = None,
        liquidity_max: Optional[float] = None,
        volume_min: Optional[float] = None,
        volume_max: Optional[float] = None,
        # Date filters
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        end_date_min: Optional[str] = None,
        end_date_max: Optional[str] = None,
        # Tag filters
        tag: Optional[Union[str, List[str]]] = None,
        tag_id: Optional[Union[int, List[int]]] = None,
        related_tags: Optional[bool] = None,
        tag_slug: Optional[Union[str, List[str]]] = None
    ) -> PaginatedResponse[Event]:
        """Get events from Gamma API with pagination metadata and comprehensive filtering options."""
        return self.gamma_client.get_events_paginated(
            limit=limit,
            offset=offset,
            auto_paginate=auto_paginate,
            order=order,
            ascending=ascending,
            event_id=event_id,
            slug=slug,
            archived=archived,
            active=active,
            closed=closed,
            liquidity_min=liquidity_min,
            liquidity_max=liquidity_max,
            volume_min=volume_min,
            volume_max=volume_max,
            start_date_min=start_date_min,
            start_date_max=start_date_max,
            end_date_min=end_date_min,
            end_date_max=end_date_max,
            tag=tag,
            tag_id=tag_id,
            related_tags=related_tags,
            tag_slug=tag_slug
        )
    
    def iter_events(
        self, 
        # Pagination parameters
        page_size: Optional[int] = None,
        offset: int = 0,
        # Sorting parameters
        order: Optional[str] = None,
        ascending: bool = True,
        # ID and slug filters
        event_id: Optional[Union[int, List[int]]] = None,
        slug: Optional[Union[str, List[str]]] = None,
        # Status filters
        archived: Optional[bool] = None,
        active: Optional[bool] = True,
        closed: Optional[bool] = False,
        # Volume and liquidity filters
        liquidity_min: Optional[float] = None,
        liquidity_max: Optional[float] = None,
        volume_min: Optional[float] = None,
        volume_max: Optional[float] = None,
        # Date filters
        start_date_min: Optional[str] = None,
        start_date_max: Optional[str] = None,
        end_date_min: Optional[str] = None,
        end_date_max: Optional[str] = None,
        # Tag filters
        tag: Optional[Union[str, List[str]]] = None,
        tag_id: Optional[Union[int, List[int]]] = None,
        related_tags: Optional[bool] = None,
        tag_slug: Optional[Union[str, List[str]]] = None
    ) -> Generator[Event, None, None]:
        """Iterator for events that yields events one page at a time (memory efficient)."""
        return self.gamma_client.iter_events(
            page_size=page_size,
            offset=offset,
            order=order,
            ascending=ascending,
            event_id=event_id,
            slug=slug,
            archived=archived,
            active=active,
            closed=closed,
            liquidity_min=liquidity_min,
            liquidity_max=liquidity_max,
            volume_min=volume_min,
            volume_max=volume_max,
            start_date_min=start_date_min,
            start_date_max=start_date_max,
            end_date_min=end_date_min,
            end_date_max=end_date_max,
            tag=tag,
            tag_id=tag_id,
            related_tags=related_tags,
            tag_slug=tag_slug
        )
    
    def get_active_events(self, limit: int = 100) -> List[Event]:
        """Get currently active events."""
        return self.get_events(active=True, closed=False, limit=limit)
    
    def get_events_by_slug(
        self, 
        slug: Union[str, List[str]],
        limit: Optional[int] = None,
        active: Optional[bool] = None,
        closed: Optional[bool] = None,
        **kwargs
    ) -> List[Event]:
        """Get events by their slug(s) - convenience function.
        
        Args:
            slug: Event slug(s) to search for. Can be a single string or list of strings.
            limit: Maximum number of events to return (uses config default if None)
            active: Filter for active events (None = no filter)
            closed: Filter for closed events (None = no filter)
            **kwargs: Additional filtering parameters (e.g., liquidity_min, volume_min, etc.)
            
        Returns:
            List of Event objects matching the slug(s)
            
        Examples:
            # Get single event by slug
            events = client.get_events_by_slug("presidential-election-2024")
            
            # Get multiple events by slug
            events = client.get_events_by_slug(["event1-slug", "event2-slug"])
            
            # Get events by slug with additional filters
            events = client.get_events_by_slug(
                "sports-event", 
                active=True, 
                liquidity_min=1000
            )
        """
        return self.get_events(
            slug=slug,
            limit=limit,
            active=active,
            closed=closed,
            **kwargs
        )
    
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
    
    # Access to underlying src for advanced usage
    @property
    def gamma(self) -> GammaClient:
        """Direct access to Gamma client."""
        return self.gamma_client
    
    @property
    def clob(self) -> ClobClient:
        """Direct access to CLOB client."""
        return self.clob_client