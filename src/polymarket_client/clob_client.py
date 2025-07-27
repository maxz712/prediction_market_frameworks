from typing import Any

import requests
from py_clob_client.client import ClobClient as PyClobClient
from py_clob_client.clob_types import (
    BalanceAllowanceParams,
    MarketOrderArgs,
    OrderArgs,
    OrderType,
)
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .configs.polymarket_configs import PolymarketConfig
from .models import (
    CancelResponse,
    LimitOrderRequest,
    Market,
    OrderBook,
    OrderList,
    OrderResponse,
    PricesHistory,
    TradeHistory,
    UserActivity,
    UserPositions,
)
from .models.order import OrderType as PMOrderType
from .rate_limiter import create_rate_limited_session


class _ClobClient:
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
        # For proxy setups, use signature_type=2 and funder parameter
        if config.wallet_proxy_address:
            self._py_client = PyClobClient(
                host=config.get_endpoint("clob"),
                key=config.pk,  # EOA private key
                chain_id=config.chain_id,
                signature_type=1,
                funder=config.wallet_proxy_address,
            )
            # Set API credentials for proxy setup
            self._py_client.set_api_creds(self._py_client.create_or_derive_api_creds())
        else:
            self._py_client = PyClobClient(
                host=config.get_endpoint("clob"),
                key=config.pk,  # Private key should match the trading address
                chain_id=config.chain_id,
                creds=config.api_creds,
            )

        # Initialize session for direct API calls
        self._session = self._init_session()

    @classmethod
    def from_config_dict(cls, config_dict: dict[str, Any]) -> "_ClobClient":
        """Create ClobClient from configuration dictionary.

        Args:
            config_dict: Dictionary containing configuration parameters

        Returns:
            _ClobClient: New CLOB client instance
        """
        config = PolymarketConfig(**config_dict)
        return cls(config)

    @classmethod
    def from_env(cls) -> "_ClobClient":
        """Create ClobClient from environment variables.

        Loads configuration from environment variables and creates a new client.

        Returns:
            _ClobClient: New CLOB client instance

        Raises:
            PolymarketConfigurationError: If required environment variables are missing
        """
        config = PolymarketConfig.from_env()
        return cls(config)

    def _init_session(self) -> requests.Session:
        """Initialize session with retry strategy and rate limiting for direct API calls.

        Sets up retry strategy, rate limiting, and timeouts for HTTP requests to CLOB API endpoints.

        Returns:
            requests.Session: Configured session with retry strategy and rate limiting
        """
        if self.config.enable_rate_limiting:
            # Create rate limited session with config parameters
            session = create_rate_limited_session(
                rate_limiter_type=self.config.rate_limiter_type,
                requests_per_second=self.config.requests_per_second,
                burst_capacity=self.config.burst_capacity,
                requests_per_window=self.config.requests_per_window,
                window_size_seconds=self.config.window_size_seconds,
                per_host=self.config.rate_limit_per_host,
                timeout_on_rate_limit=self.config.rate_limit_timeout,
                max_retries=Retry(
                    total=self.config.max_retries,
                    backoff_factor=0.3,
                    status_forcelist=[429, 500, 502, 503, 504],
                ),
            )
        else:
            # Create regular session without rate limiting
            session = requests.Session()
            retry = Retry(
                total=self.config.max_retries,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

        session.timeout = self.config.timeout
        return session

    # Delegate existing methods to the underlying py_clob_client
    def get_market(self, token_id: str) -> Market:
        """Get market data for a given condition ID.

        Args:
            token_id: The condition ID of the market to retrieve

        Returns:
            Market: A Market model instance with the market data
        """
        market_data = self._py_client.get_market(token_id)
        return Market.model_validate(market_data)

    def get_order_book(self, token_id: str) -> OrderBook:
        """Get order book for a given token ID.

        Args:
            token_id: The token ID to get the order book for

        Returns:
            OrderBook: The order book data model with bids, asks, and metadata
        """
        summary = self._py_client.get_order_book(token_id)
        return OrderBook.from_raw_data(
            market_id=summary.market,
            asset_id=summary.asset_id,
            timestamp=int(summary.timestamp),
            hash=summary.hash,
            raw_bids=summary.bids,
            raw_asks=summary.asks,
        )

    def post_order(self, order_args: dict[str, Any]) -> dict[str, Any]:
        """Post an order using OrderArgs.

        Args:
            order_args: Dictionary containing order parameters (token_id, price, size, side)

        Returns:
            dict: Raw response from the order submission
        """
        # Convert dict to OrderArgs and use create_and_post_order
        order_args_obj = OrderArgs(
            token_id=order_args["token_id"],
            price=float(order_args["price"]),
            size=float(order_args["size"]),
            side=order_args["side"],
        )
        return self._py_client.create_and_post_order(order_args_obj)

    def cancel_order(self, order_id: str) -> CancelResponse:
        """Cancel an order.

        Args:
            order_id: The order ID to cancel

        Returns:
            CancelResponse: Response with cancellation results
        """
        raw_response = self._py_client.cancel(order_id)
        return CancelResponse.from_raw_response(raw_response)

    def cancel_orders(self, order_ids: list[str]) -> CancelResponse:
        """Cancel multiple orders.

        Args:
            order_ids: List of order IDs to cancel

        Returns:
            CancelResponse: Response with cancellation results
        """
        raw_response = self._py_client.cancel_orders(order_ids)
        return CancelResponse.from_raw_response(raw_response)

    def cancel_all(self) -> CancelResponse:
        """Cancel all orders.

        Returns:
            CancelResponse: Response with cancellation results
        """
        raw_response = self._py_client.cancel_all()
        return CancelResponse.from_raw_response(raw_response)

    # Extended functionality - additional CLOB API endpoints
    def get_user_market_trades_history(
        self, token_id: str, limit: int = 100, offset: int = 0
    ) -> TradeHistory:
        """
        Get comprehensive trade history for a market.

        Note: This method uses the py_clob_client get_trades method to fetch trade history.
        The market_id parameter is used for filtering if possible, but the py_clob_client
        get_trades method returns all trades for the authenticated user.

        Args:
            token_id: Market identifier (used for documentation, actual filtering depends on API)
            limit: Maximum number of trades to return
            offset: Offset for pagination (converted to cursor if needed)

        Returns:
            TradeHistory: Custom data model containing trade history
        """
        try:
            # Use py_clob_client's get_trades method which returns user's trade history
            # Note: py_clob_client doesn't have market-specific filtering in get_trades
            raw_trades = self._py_client.get_trades()

            # If we have trades and a token_id filter, filter client-side
            if token_id and isinstance(raw_trades, list):
                # Filter trades by token_id if provided
                filtered_trades = [
                    trade for trade in raw_trades if trade.get("market") == token_id
                ]
                raw_trades = filtered_trades

            # Apply limit if specified
            if isinstance(raw_trades, list) and limit:
                raw_trades = raw_trades[:limit]

            # Convert to our custom model
            if isinstance(raw_trades, list):
                return TradeHistory.from_raw_trades(raw_trades)
            # In case py_clob_client returns a different format
            return TradeHistory.from_raw_trades([])

        except Exception:
            # Fallback: return empty trade history if there's an error
            return TradeHistory.from_raw_trades([])

    def get_user_positions(self, user_address: str) -> dict[str, Any]:
        """
        Get user positions across all markets.

        Extended endpoint for position tracking that retrieves all positions
        for a given user address across different markets.

        Args:
            user_address: The Ethereum address to get positions for

        Returns:
            dict: Raw positions data from the API

        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        url = f"{self.config.get_endpoint('data_api')}/positions"
        params = {"user": user_address}

        response = self._session.get(url, params=params)
        response.raise_for_status()
        return response.json()

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
        """
        Get user's on-chain activity history.

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

        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        url = f"{self.config.get_endpoint('data_api')}/activity"

        params = {
            "user": proxy_wallet_address,
            "limit": min(limit, 500),  # Ensure we don't exceed API limit
            "offset": offset,
            "sortBy": sort_by,
            "sortDirection": sort_direction,
        }

        # Add optional filters
        if market:
            params["market"] = market
        if activity_type:
            params["type"] = activity_type
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if side:
            params["side"] = side.upper()

        response = self._session.get(url, params=params)
        response.raise_for_status()

        activity_data = response.json()
        return UserActivity.from_raw_data(activity_data)

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
        """
        Get current user's on-chain activity history.

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

        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        user_address = self.get_user_address()
        return self.get_user_activity(
            proxy_wallet_address=user_address,
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

    # Trading execution methods
    def submit_market_order(
        self, token_id: str, side: str, size: float
    ) -> dict[str, Any]:
        """
        Submit a market order for immediate execution.

        Args:
            token_id: The token ID to trade
            side: 'BUY' or 'SELL'
            size: Size of the order
        """
        # Create MarketOrderArgs and use create_market_order + post_order
        market_order_args = MarketOrderArgs(
            token_id=token_id, amount=size, side=side.upper()
        )
        order = self._py_client.create_market_order(market_order_args)
        return self._py_client.post_order(order)

    def submit_limit_order(self, request: LimitOrderRequest) -> OrderResponse:
        """
        Submit a limit order with specified order type.

        Args:
            request: LimitOrderRequest containing order details including order_type

        Returns:
            OrderResponse: Response with order submission details
        """
        # Validate GTD orders have expiration
        if request.order_type == PMOrderType.GTD and request.expires_at is None:
            msg = "expires_at must be set for GTD orders"
            raise ValueError(msg)

        # Build order args based on order type
        order_args_dict = {
            "token_id": request.token_id,
            "price": request.price,
            "size": request.size,
            "side": request.side.value.upper(),
        }

        # Add expiration for GTD orders
        if request.order_type == PMOrderType.GTD:
            order_args_dict["expiration"] = request.expires_at

        order_args = OrderArgs(**order_args_dict)
        order = self._py_client.create_order(order_args)

        # Map our OrderType enum to py_clob_client's OrderType
        order_type_map = {
            PMOrderType.GTC: OrderType.GTC,
            PMOrderType.FOK: OrderType.FOK,
            PMOrderType.FAK: OrderType.FAK,
            PMOrderType.GTD: OrderType.GTD,
        }

        py_order_type = order_type_map[request.order_type]
        raw_response = self._py_client.post_order(order, py_order_type)
        return OrderResponse.from_raw_response(raw_response)

    def get_open_orders(self, market: str | None = None) -> OrderList:
        """
        Get current open orders for the authenticated user.

        Args:
            market: Optional market filter

        Returns:
            OrderList: A custom data model containing the list of open orders
        """
        if market:
            raw_response = self._py_client.get_orders(market=market)
        else:
            raw_response = self._py_client.get_orders()

        return OrderList.from_raw_response(raw_response)

    def get_user_position(
        self, proxy_wallet_address: str, market: str | None = None
    ) -> UserPositions:
        """
        Get user position.

        Args:
            proxy_wallet_address: The proxy wallet address to get positions for
            market: Optional market filter

        Returns:
            UserPositions: User positions data model
        """
        positions_data = self.get_user_positions(proxy_wallet_address)

        # Convert to UserPositions model
        user_positions = UserPositions.from_raw_data(positions_data)

        # Filter by token_id if specified (the market parameter represents a token_id for filtering)
        if market:
            filtered = [
                pos for pos in user_positions.positions if pos.token_id == market
            ]
            return UserPositions(positions=filtered)

        return user_positions

    def get_current_user_position(self, market: str | None = None) -> UserPositions:
        """
        Get current user position.

        Args:
            market: Optional market filter

        Returns:
            UserPositions: User positions data model
        """
        # Get user address from the py_clob_client
        user_address = self._py_client.get_address()
        return self.get_user_position(proxy_wallet_address=user_address, market=market)

    # Balance and Allowance Methods
    def get_balance_allowance(
        self, asset_type: str = "COLLATERAL", token_id: str | None = None
    ) -> dict[str, Any]:
        """
        Get the current balance and allowance for USDC (collateral) or conditional tokens.

        Args:
            asset_type: "COLLATERAL" for USDC or "CONDITIONAL" for conditional tokens
            token_id: Required for CONDITIONAL asset type, optional for COLLATERAL

        Returns:
            Dictionary with balance and allowance information
        """
        params = BalanceAllowanceParams(
            asset_type="COLLATERAL" if asset_type == "COLLATERAL" else "CONDITIONAL",
            token_id=token_id,
            signature_type=-1,  # Will be set automatically by the client
        )
        return self._py_client.get_balance_allowance(params)

    def update_balance_allowance(
        self, asset_type: str = "COLLATERAL", token_id: str | None = None
    ) -> dict[str, Any]:
        """
        Update (refresh) the balance and allowance information.

        Args:
            asset_type: "COLLATERAL" for USDC or "CONDITIONAL" for conditional tokens
            token_id: Required for CONDITIONAL asset type, optional for COLLATERAL

        Returns:
            Dictionary with updated balance and allowance information
        """
        params = BalanceAllowanceParams(
            asset_type="COLLATERAL" if asset_type == "COLLATERAL" else "CONDITIONAL",
            token_id=token_id,
            signature_type=-1,  # Will be set automatically by the client
        )
        return self._py_client.update_balance_allowance(params)

    def get_usdc_balance_allowance(self) -> dict[str, Any]:
        """
        Convenience method to get USDC (collateral) balance and allowance.

        Returns:
            Dictionary with USDC balance and allowance information
        """
        return self.get_balance_allowance(asset_type="COLLATERAL")

    def update_usdc_balance_allowance(self) -> dict[str, Any]:
        """
        Convenience method to update USDC (collateral) balance and allowance.

        Returns:
            Dictionary with updated USDC balance and allowance information
        """
        return self.update_balance_allowance(asset_type="COLLATERAL")

    def check_usdc_allowance_sufficient(self, required_amount: float) -> bool:
        """
        Check if the current USDC allowance is sufficient for a given amount.

        Args:
            required_amount: The amount of USDC needed (in USDC units, not wei)

        Returns:
            True if allowance is sufficient, False otherwise
        """
        try:
            balance_info = self.get_usdc_balance_allowance()
            # The exact field names may vary, adjust based on actual response
            current_allowance = float(balance_info.get("allowance", 0))
            return current_allowance >= required_amount
        except Exception:
            return False

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

        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        url = f"{self.config.get_endpoint('clob')}/prices-history"

        params = {"market": market}

        # Add optional parameters
        if start_ts is not None:
            params["startTs"] = start_ts
        if end_ts is not None:
            params["endTs"] = end_ts
        if interval is not None:
            params["interval"] = interval
        if fidelity is not None:
            params["fidelity"] = fidelity

        response = self._session.get(url, params=params)
        response.raise_for_status()

        raw_data = response.json()
        return PricesHistory.from_raw_data(
            raw_data=raw_data,
            market=market,
            start_ts=start_ts,
            end_ts=end_ts,
            interval=interval,
            fidelity=fidelity,
        )

    # Convenience methods
    def get_user_address(self) -> str:
        """Get the Ethereum address of the authenticated user.

        Returns:
            str: The user's Ethereum address
        """
        return self._py_client.get_address()

    # Expose the underlying client for any methods not explicitly wrapped
    @property
    def py_client(self) -> PyClobClient:
        """Access to the underlying py_clob_client for advanced usage.

        Provides direct access to the py_clob_client instance for operations
        not exposed through this wrapper interface.

        Returns:
            PyClobClient: The underlying py_clob_client instance
        """
        return self._py_client
