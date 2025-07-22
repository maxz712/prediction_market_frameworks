from collections.abc import Generator
from typing import Any

from .clob_client import _ClobClient
from .configs.polymarket_configs import PolymarketConfig
from .exceptions import PolymarketConfigurationError
from .gamma_client import _GammaClient
from .models import (
    CancelResponse,
    Event,
    EventList,
    LimitOrderRequest,
    Market,
    OrderBook,
    OrderList,
    OrderResponse,
    PaginatedResponse,
    TradeHistory,
)


class PolymarketClient:
    """
    Unified client for accessing all Polymarket APIs.
    Wraps both Gamma API (events/markets) and CLOB API (trading/order books).
    """

    def __init__(self, config: PolymarketConfig | None = None) -> None:
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
        self.gamma_client = _GammaClient(config)
        self.clob_client = _ClobClient(config)

    # Event-related methods (Gamma API)
    def get_events(
        self,
        # Pagination parameters
        limit: int | None = None,
        offset: int = 0,
        auto_paginate: bool | None = None,
        # Sorting parameters
        order: str | None = None,
        ascending: bool = True,
        # ID and slug filters
        event_id: int | list[int] | None = None,
        slug: str | list[str] | None = None,
        # Status filters
        archived: bool | None = None,
        active: bool | None = True,
        closed: bool | None = False,
        # Volume and liquidity filters
        liquidity_min: float | None = None,
        liquidity_max: float | None = None,
        volume_min: float | None = None,
        volume_max: float | None = None,
        # Date filters
        start_date_min: str | None = None,
        start_date_max: str | None = None,
        end_date_min: str | None = None,
        end_date_max: str | None = None,
        # Tag filters
        tag: str | list[str] | None = None,
        tag_id: int | list[int] | None = None,
        related_tags: bool | None = None,
        tag_slug: str | list[str] | None = None
    ) -> EventList:
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
        limit: int | None = None,
        offset: int = 0,
        auto_paginate: bool | None = None,
        # Sorting parameters
        order: str | None = None,
        ascending: bool = True,
        # ID and slug filters
        event_id: int | list[int] | None = None,
        slug: str | list[str] | None = None,
        # Status filters
        archived: bool | None = None,
        active: bool | None = True,
        closed: bool | None = False,
        # Volume and liquidity filters
        liquidity_min: float | None = None,
        liquidity_max: float | None = None,
        volume_min: float | None = None,
        volume_max: float | None = None,
        # Date filters
        start_date_min: str | None = None,
        start_date_max: str | None = None,
        end_date_min: str | None = None,
        end_date_max: str | None = None,
        # Tag filters
        tag: str | list[str] | None = None,
        tag_id: int | list[int] | None = None,
        related_tags: bool | None = None,
        tag_slug: str | list[str] | None = None
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
        page_size: int | None = None,
        offset: int = 0,
        # Sorting parameters
        order: str | None = None,
        ascending: bool = True,
        # ID and slug filters
        event_id: int | list[int] | None = None,
        slug: str | list[str] | None = None,
        # Status filters
        archived: bool | None = None,
        active: bool | None = True,
        closed: bool | None = False,
        # Volume and liquidity filters
        liquidity_min: float | None = None,
        liquidity_max: float | None = None,
        volume_min: float | None = None,
        volume_max: float | None = None,
        # Date filters
        start_date_min: str | None = None,
        start_date_max: str | None = None,
        end_date_min: str | None = None,
        end_date_max: str | None = None,
        # Tag filters
        tag: str | list[str] | None = None,
        tag_id: int | list[int] | None = None,
        related_tags: bool | None = None,
        tag_slug: str | list[str] | None = None
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

    def get_active_events(self, limit: int = 100) -> EventList:
        """Get currently active events."""
        return self.get_events(active=True, closed=False, limit=limit)

    def get_events_by_slug(
        self,
        slug: str | list[str],
        limit: int | None = None,
        active: bool | None = None,
        closed: bool | None = None,
        **kwargs
    ) -> EventList:
        """Get events by their slug(s) - convenience function.
        
        Args:
            slug: Event slug(s) to search for. Can be a single string or list of strings.
            limit: Maximum number of events to return (uses config default if None)
            active: Filter for active events (None = no filter)
            closed: Filter for closed events (None = no filter)
            **kwargs: Additional filtering parameters (e.g., liquidity_min, volume_min, etc.)
            
        Returns:
            EventList containing Event objects matching the slug(s)
            
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
        """Get market data from CLOB API.
        
        Args:
            condition_id: The condition ID of the market to retrieve
            
        Returns:
            Market: A Market model instance with the market data
        """
        return self.clob_client.get_market(condition_id)

    # Order book and trading methods (CLOB API)
    def get_order_book(self, token_id: str) -> OrderBook:
        """Get order book for a token."""
        return self.clob_client.get_order_book(token_id)

    def get_user_market_trades_history(self, token_id: str, limit: int = 100,
                                 offset: int = 0) -> TradeHistory:
        """Get comprehensive trade history."""
        return self.clob_client.get_user_market_trades_history(token_id, limit, offset)

    def cancel_order(self, order_id: str) -> CancelResponse:
        """Cancel an order.
        
        Args:
            order_id: The order ID to cancel
            
        Returns:
            CancelResponse: Response with cancellation results
        """
        return self.clob_client.cancel_order(order_id)

    def cancel_orders(self, order_ids: list[str]) -> CancelResponse:
        """Cancel multiple orders.
        
        Args:
            order_ids: List of order IDs to cancel
            
        Returns:
            CancelResponse: Response with cancellation results
        """
        return self.clob_client.cancel_orders(order_ids)

    def cancel_all_orders(self) -> CancelResponse:
        """Cancel all orders.
        
        Returns:
            CancelResponse: Response with cancellation results
        """
        return self.clob_client.cancel_all()

    def submit_limit_order(self, request: LimitOrderRequest) -> OrderResponse:
        """
        Submit a limit order with specified order type.
        
        Args:
            request: LimitOrderRequest containing order details including order_type
            
        Returns:
            OrderResponse: Response with order submission details
        """
        return self.clob_client.submit_limit_order(request)

    def get_open_orders(self, market: str | None = None) -> OrderList:
        """Get current open orders for the authenticated user.
        
        Args:
            market: Optional market filter
            
        Returns:
            OrderList: A custom data model containing the list of open orders
        """
        return self.clob_client.get_open_orders(market)

    def get_current_user_position(self, market: str | None = None) -> dict[str, Any]:
        """Get current user position."""
        return self.clob_client.get_current_user_position(market)

    # Analytics and statistics methods (CLOB API)
    def get_market_statistics(self, market_id: str) -> dict[str, Any]:
        """Get market statistics."""
        return self.clob_client.get_market_statistics(market_id)

    def get_user_positions(self, user_address: str) -> dict[str, Any]:
        """Get user positions."""
        return self.clob_client.get_user_positions(user_address)

    def get_market_candles(self, market_id: str, interval: str = "1h",
                          limit: int = 100) -> dict[str, Any]:
        """Get candlestick data."""
        return self.clob_client.get_market_candles(market_id, interval, limit)

    # Access to underlying src for advanced usage
    @property
    def gamma(self) -> _GammaClient:
        """Direct access to Gamma client."""
        return self.gamma_client

    @property
    def clob(self) -> _ClobClient:
        """Direct access to CLOB client."""
        return self.clob_client
