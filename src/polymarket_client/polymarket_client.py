from collections.abc import Generator

from .clob_client import _ClobClient
from .configs.polymarket_configs import PolymarketConfig
from .exceptions import PolymarketConfigurationError
from .gamma_client import _GammaClient
from .logger import get_logger, log_user_action
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
    PricesHistory,
    TradeHistory,
    UserActivity,
    UserPositions,
)
from .sanitization import InputSanitizer


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
                msg = (
                    "Failed to load configuration from environment variables. "
                    "Please provide a config object or set the required environment variables."
                )
                raise PolymarketConfigurationError(msg) from e

        self.config = config
        self.gamma_client = _GammaClient(config)
        self.clob_client = _ClobClient(config)
        self._logger = get_logger("polymarket_client")

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
        tag_slug: str | list[str] | None = None,
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
            tag_slug=tag_slug,
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
        tag_slug: str | list[str] | None = None,
    ) -> PaginatedResponse[Event]:
        """Get events from Gamma API with pagination metadata and comprehensive filtering options.

        This method returns the same data as get_events() but wrapped in a PaginatedResponse
        that includes metadata about pagination such as total count, current offset, and
        whether there are more pages available.

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

        Returns:
            PaginatedResponse[Event]: Paginated response containing events and metadata

        Examples:
            # Get first 10 events with pagination metadata
            response = client.get_events_paginated(limit=10)
            print(f"Total events: {response.meta.total}")
            print(f"Current page events: {len(response.data)}")

            # Check if more pages are available
            if response.meta.has_next:
                next_response = client.get_events_paginated(
                    limit=10,
                    offset=response.meta.next_offset
                )
        """
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
            tag_slug=tag_slug,
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
        tag_slug: str | list[str] | None = None,
    ) -> Generator[Event]:
        """Iterator for events that yields events one page at a time (memory efficient).

        This method is useful when you need to process a large number of events without
        loading them all into memory at once. It automatically handles pagination and
        yields individual Event objects as they are retrieved.

        Args:
            page_size: Number of events to fetch per API request (uses config default if None)
            offset: Starting offset for pagination
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

        Yields:
            Event: Individual Event objects one at a time

        Examples:
            # Process all active events one by one
            for event in client.iter_events(active=True):
                print(f"Processing event: {event.title}")
                # Process event without loading all events into memory

            # Process events with specific filters
            for event in client.iter_events(
                active=True,
                liquidity_min=1000,
                page_size=50  # Fetch 50 events per API call
            ):
                if event.volume > 10000:
                    print(f"High volume event: {event.title}")
        """
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
            tag_slug=tag_slug,
        )

    def get_active_events(self, limit: int = 100) -> EventList:
        """Get currently active events.

        This is a convenience method that filters for events that are both active
        and not closed. It's equivalent to calling get_events(active=True, closed=False).

        Args:
            limit: Maximum number of active events to return (default 100)

        Returns:
            EventList: A list of active Event objects

        Examples:
            # Get the first 50 active events
            active_events = client.get_active_events(limit=50)

            # Get all active events (up to default limit)
            all_active = client.get_active_events()

            for event in active_events:
                print(f"Active event: {event.title}")
        """
        return self.get_events(active=True, closed=False, limit=limit)

    def get_events_by_slug(
        self,
        slug: str | list[str],
        limit: int | None = None,
        active: bool | None = None,
        closed: bool | None = None,
        **kwargs,
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
            slug=slug, limit=limit, active=active, closed=closed, **kwargs
        )

    # Market-related methods
    def get_market(self, condition_id: str) -> Market:
        """Get market data from CLOB API.

        Args:
            condition_id: The condition ID of the market to retrieve

        Returns:
            Market: A Market model instance with the market data
        """
        sanitized_condition_id = InputSanitizer.sanitize_token_id(condition_id)
        if sanitized_condition_id is None:
            msg = "Invalid condition_id format"
            raise ValueError(msg)
        return self.clob_client.get_market(sanitized_condition_id)

    # Order book and trading methods (CLOB API)
    def get_order_book(self, token_id: str) -> OrderBook:
        """Get order book for a token.

        Retrieves the current order book showing all active buy and sell orders
        for a specific token/market. The order book provides price and quantity
        information for market making and trading decisions.

        Args:
            token_id: The CLOB token ID to get the order book for

        Returns:
            OrderBook: Order book data containing bids and asks

        Examples:
            # Get order book for a specific token
            order_book = client.get_order_book("0x1234...")

            # Analyze the spread
            best_bid = order_book.bids[0] if order_book.bids else None
            best_ask = order_book.asks[0] if order_book.asks else None

            if best_bid and best_ask:
                spread = float(best_ask.price) - float(best_bid.price)
                print(f"Current spread: {spread}")
        """
        sanitized_token_id = InputSanitizer.sanitize_token_id(token_id)
        if sanitized_token_id is None:
            msg = "Invalid token_id format"
            raise ValueError(msg)
        return self.clob_client.get_order_book(sanitized_token_id)

    def get_user_market_trades_history(
        self, token_id: str, limit: int = 100, offset: int = 0
    ) -> TradeHistory:
        """Get comprehensive trade history for a specific token/market.

        Retrieves the trade history for the authenticated user in a specific market.
        This includes all completed trades with details like price, quantity, timestamp,
        and trade direction.

        Args:
            token_id: The CLOB token ID to get trade history for
            limit: Maximum number of trades to return (default 100)
            offset: Pagination offset for retrieving more trades (default 0)

        Returns:
            TradeHistory: Trade history data containing list of trades

        Examples:
            # Get recent trades for a token
            trades = client.get_user_market_trades_history("0x1234...", limit=50)

            # Get next page of trades
            more_trades = client.get_user_market_trades_history(
                token_id="0x1234...",
                limit=50,
                offset=50
            )

            # Calculate total volume
            total_volume = sum(float(trade.size) for trade in trades.history)
            print(f"Total trade volume: {total_volume}")
        """
        return self.clob_client.get_user_market_trades_history(token_id, limit, offset)

    def get_prices_history(
        self,
        market: str,
        start_ts: int | None = None,
        end_ts: int | None = None,
        interval: str | None = None,
        fidelity: int | None = None,
    ) -> PricesHistory:
        """
        Get price history for a specific market.

        Args:
            market: The CLOB token ID for which to fetch price history
            start_ts: Start time as Unix timestamp in UTC (optional)
            end_ts: End time as Unix timestamp in UTC (optional)
            interval: Duration ending at current time, options: 1m, 1w, 1d, 6h, 1h, max (optional)
            fidelity: Data resolution in minutes (optional)

        Returns:
            PricesHistory: Custom data model containing price history

        Examples:
            # Get all available price history
            history = client.get_prices_history("0x1234...")

            # Get price history for the last week
            history = client.get_prices_history("0x1234...", interval="1w")

            # Get price history between specific timestamps
            history = client.get_prices_history(
                market="0x1234...",
                start_ts=1640995200,  # Jan 1, 2022
                end_ts=1672531200     # Jan 1, 2023
            )

            # Get hourly price data
            history = client.get_prices_history("0x1234...", fidelity=60)
        """
        return self.clob_client.get_prices_history(
            market=market,
            start_ts=start_ts,
            end_ts=end_ts,
            interval=interval,
            fidelity=fidelity,
        )

    def cancel_order(self, order_id: str) -> CancelResponse:
        """Cancel an order.

        Args:
            order_id: The order ID to cancel

        Returns:
            CancelResponse: Response with cancellation results
        """
        sanitized_order_id = InputSanitizer.sanitize_order_id(order_id)
        if sanitized_order_id is None:
            msg = "Invalid order_id format"
            raise ValueError(msg)
        log_user_action(self._logger, "cancel_order", order_id=sanitized_order_id)
        return self.clob_client.cancel_order(sanitized_order_id)

    def cancel_orders(self, order_ids: list[str]) -> CancelResponse:
        """Cancel multiple orders.

        Args:
            order_ids: List of order IDs to cancel

        Returns:
            CancelResponse: Response with cancellation results
        """
        log_user_action(
            self._logger,
            "cancel_orders",
            additional_data={"order_count": len(order_ids), "order_ids": order_ids},
        )
        return self.clob_client.cancel_orders(order_ids)

    def cancel_all_orders(self) -> CancelResponse:
        """Cancel all orders.

        Returns:
            CancelResponse: Response with cancellation results
        """
        log_user_action(self._logger, "cancel_all_orders")
        return self.clob_client.cancel_all()

    def submit_limit_order(self, request: LimitOrderRequest) -> OrderResponse:
        """
        Submit a limit order with specified order type.

        Args:
            request: LimitOrderRequest containing order details including order_type

        Returns:
            OrderResponse: Response with order submission details
        """
        log_user_action(
            self._logger,
            "submit_limit_order",
            market_id=getattr(request, "token_id", None),
            additional_data={
                "order_type": getattr(request, "order_type", None),
                "side": getattr(request, "side", None),
                "size": getattr(request, "size", None),
                "price": getattr(request, "price", None),
            },
        )
        return self.clob_client.submit_limit_order(request)

    def get_open_orders(self, market: str | None = None) -> OrderList:
        """Get current open orders for the authenticated user.

        Args:
            market: Optional market filter

        Returns:
            OrderList: A custom data model containing the list of open orders
        """
        return self.clob_client.get_open_orders(market)

    def get_user_position(
        self, proxy_wallet_address: str, market: str | None = None
    ) -> UserPositions:
        """Get user position.

        Args:
            proxy_wallet_address: The proxy wallet address to get positions for
            market: Optional market filter

        Returns:
            UserPositions: User positions data model
        """
        sanitized_address = InputSanitizer.sanitize_hex_address(proxy_wallet_address)
        if sanitized_address is None:
            msg = "Invalid proxy_wallet_address format"
            raise ValueError(msg)
        sanitized_market = InputSanitizer.sanitize_token_id(market) if market else None
        return self.clob_client.get_user_position(sanitized_address, sanitized_market)

    def get_current_user_position(self, market: str | None = None) -> UserPositions:
        """Get current user position.

        Args:
            market: Optional market filter

        Returns:
            UserPositions: User positions data model
        """
        return self.clob_client.get_current_user_position(market)

    def get_user_activity(
        self,
        proxy_wallet_address: str,
        limit: int = 100,
        offset: int = 0,
        market: str | None = None,
        activity_type: str | None = None,
        start: int | None = None,
        end: int | None = None,
        side: str | None = None,
        sort_by: str = "TIMESTAMP",
        sort_direction: str = "DESC",
    ) -> UserActivity:
        """Get user's on-chain activity history.

        Args:
            proxy_wallet_address: The proxy wallet address to get activity for
            limit: Maximum number of activities to return (max 500, default 100)
            offset: Pagination offset (default 0)
            market: Comma-separated market condition IDs to filter by
            activity_type: Activity types to filter by (TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION)
            start: Start timestamp (Unix seconds)
            end: End timestamp (Unix seconds)
            side: Trade side filter (BUY or SELL)
            sort_by: Sort field (TIMESTAMP, TOKENS, CASH) (default TIMESTAMP)
            sort_direction: Sort order (ASC or DESC) (default DESC)

        Returns:
            UserActivity: Custom data model containing activity history

        Examples:
            # Get recent activity
            activity = client.get_user_activity("0x1234...", limit=50)

            # Get only trades
            trades = client.get_user_activity("0x1234...", activity_type="TRADE")

            # Get activity for a specific market
            market_activity = client.get_user_activity(
                proxy_wallet_address="0x1234...",
                market="0x5678...",
                limit=100
            )

            # Get buy trades only
            buy_trades = client.get_user_activity(
                proxy_wallet_address="0x1234...",
                activity_type="TRADE",
                side="BUY"
            )
        """
        return self.clob_client.get_user_activity(
            proxy_wallet_address=proxy_wallet_address,
            limit=limit,
            offset=offset,
            market=market,
            activity_type=activity_type,
            start=start,
            end=end,
            side=side,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    def get_current_user_activity(
        self,
        limit: int = 100,
        offset: int = 0,
        market: str | None = None,
        activity_type: str | None = None,
        start: int | None = None,
        end: int | None = None,
        side: str | None = None,
        sort_by: str = "TIMESTAMP",
        sort_direction: str = "DESC",
    ) -> UserActivity:
        """Get current user's on-chain activity history.

        Args:
            limit: Maximum number of activities to return (max 500, default 100)
            offset: Pagination offset (default 0)
            market: Comma-separated market condition IDs to filter by
            activity_type: Activity types to filter by (TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION)
            start: Start timestamp (Unix seconds)
            end: End timestamp (Unix seconds)
            side: Trade side filter (BUY or SELL)
            sort_by: Sort field (TIMESTAMP, TOKENS, CASH) (default TIMESTAMP)
            sort_direction: Sort order (ASC or DESC) (default DESC)

        Returns:
            UserActivity: Custom data model containing activity history

        Examples:
            # Get recent activity
            activity = client.get_current_user_activity(limit=50)

            # Get only trades
            trades = client.get_current_user_activity(activity_type="TRADE")

            # Get activity for a specific market
            market_activity = client.get_current_user_activity(
                market="0x1234...",
                limit=100
            )

            # Get buy trades only
            buy_trades = client.get_current_user_activity(
                activity_type="TRADE",
                side="BUY"
            )
        """
        return self.clob_client.get_current_user_activity(
            limit=limit,
            offset=offset,
            market=market,
            activity_type=activity_type,
            start=start,
            end=end,
            side=side,
            sort_by=sort_by,
            sort_direction=sort_direction,
        )

    # Convenience methods
    def get_user_address(self) -> str:
        """Get the Ethereum address of the authenticated user.

        Returns:
            str: The user's Ethereum address
        """
        return self.clob_client.get_user_address()

    # Access to underlying src for advanced usage
    @property
    def gamma(self) -> _GammaClient:
        """Direct access to Gamma client for advanced usage.

        Provides direct access to the underlying Gamma API client for operations
        not exposed through the unified interface. Use this for advanced functionality
        or when you need to access Gamma-specific methods.

        Returns:
            _GammaClient: The underlying Gamma API client instance

        Examples:
            # Access gamma-specific methods
            gamma_client = client.gamma
            # Use gamma client methods directly
        """
        return self.gamma_client

    @property
    def clob(self) -> _ClobClient:
        """Direct access to CLOB client for advanced usage.

        Provides direct access to the underlying CLOB API client for trading
        operations not exposed through the unified interface. Use this for
        advanced trading functionality or when you need CLOB-specific methods.

        Returns:
            _ClobClient: The underlying CLOB API client instance

        Examples:
            # Access CLOB-specific methods
            clob_client = client.clob
            # Use CLOB client methods directly
        """
        return self.clob_client
