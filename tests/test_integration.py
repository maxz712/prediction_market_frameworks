"""Integration tests with mocked API responses."""

from unittest.mock import Mock, patch

import pytest
import requests

from polymarket_client import PolymarketClient
from polymarket_client.configs.polymarket_configs import PolymarketConfig


@pytest.fixture
def integration_config():
    """Create a test configuration for integration tests."""
    return PolymarketConfig(
        api_key="test_integration_key",
        api_secret="test_integration_secret",
        api_passphrase="test_integration_passphrase",
        pk="0x" + "1" * 64,
        endpoints={
            "gamma": "https://gamma-api.polymarket.com",
            "clob": "https://clob.polymarket.com",
            "info": "https://strapi-matic.polymarket.com",
            "neg_risk": "https://neg-risk-api.polymarket.com",
            "data_api": "https://data-api.polymarket.com",
        },
    )


class TestMarketDataIntegration:
    """Integration tests for market data retrieval workflows."""

    @patch("requests.Session.get")
    def test_get_events_and_markets_workflow(self, mock_get, integration_config):
        """Test complete workflow of getting events and their markets."""
        # Mock gamma client events response
        events_response = Mock()
        events_response.json.return_value = [
            {
                "id": "event1",
                "ticker": "ELECTION",
                "title": "2024 Election",
                "description": "Who will win the 2024 election?",
                "slug": "2024-election",
                "startDate": "2024-01-01T00:00:00Z",
                "endDate": "2024-12-31T23:59:59Z",
                "image": "https://example.com/image.png",
                "icon": "https://example.com/icon.png",
                "active": True,
                "closed": False,
                "archived": False,
                "markets": [
                    {
                        "id": "market1",
                        "question": "Will candidate A win?",
                        "tokens": [
                            {"token_id": "token1", "outcome": "Yes", "price": 0.6},
                            {"token_id": "token2", "outcome": "No", "price": 0.4},
                        ],
                    }
                ],
            }
        ]
        events_response.raise_for_status.return_value = None
        mock_get.return_value = events_response

        client = PolymarketClient(integration_config)

        # Test getting events
        events = client.get_events()

        assert len(events) == 1
        assert events[0].ticker == "ELECTION"
        assert events[0].title == "2024 Election"
        assert len(events[0].markets) == 1
        assert events[0].markets[0].question == "Will candidate A win?"

    @patch("requests.Session.get")
    def test_get_event_by_slug_with_markets(self, mock_get, integration_config):
        """Test getting a specific event by slug with market data."""
        # Mock event response
        event_response = Mock()
        event_response.json.return_value = {
            "id": "event1",
            "ticker": "SPORTS",
            "title": "Championship Game",
            "description": "Who will win the championship?",
            "slug": "championship-game",
            "startDate": "2024-06-01T00:00:00Z",
            "endDate": "2024-06-02T00:00:00Z",
            "active": True,
            "markets": [
                {
                    "id": "market1",
                    "question": "Will Team A win?",
                    "tokens": [
                        {"token_id": "token1", "outcome": "Yes", "price": 0.55},
                        {"token_id": "token2", "outcome": "No", "price": 0.45},
                    ],
                }
            ],
        }
        event_response.raise_for_status.return_value = None
        mock_get.return_value = event_response

        client = PolymarketClient(integration_config)

        # Test getting event by slug
        event = client.get_event_by_slug("championship-game")

        assert event.ticker == "SPORTS"
        assert event.title == "Championship Game"
        assert len(event.markets) == 1
        assert event.markets[0].tokens[0].price == 0.55

    @patch("polymarket_client.clob_client._ClobClient.get_market")
    @patch("polymarket_client.clob_client._ClobClient.get_order_book")
    def test_market_and_orderbook_integration(
        self, mock_get_order_book, mock_get_market, integration_config
    ):
        """Test integrated market data and order book retrieval."""
        # Mock market data
        mock_market = Mock()
        mock_market.condition_id = "0x123abc"
        mock_market.question = "Will it rain tomorrow?"
        mock_market.tokens = [
            {"token_id": "token1", "outcome": "Yes"},
            {"token_id": "token2", "outcome": "No"},
        ]
        mock_get_market.return_value = mock_market

        # Mock order book data
        mock_order_book = Mock()
        mock_order_book.market_id = "0x123abc"
        mock_order_book.bids = [{"price": 0.6, "volume": 100}]
        mock_order_book.asks = [{"price": 0.65, "volume": 150}]
        mock_get_order_book.return_value = mock_order_book

        client = PolymarketClient(integration_config)

        # Test getting market
        market = client.get_market("0x123abc")
        assert market.condition_id == "0x123abc"
        assert market.question == "Will it rain tomorrow?"

        # Test getting order book
        order_book = client.get_order_book("token1")
        assert order_book.market_id == "0x123abc"
        assert len(order_book.bids) == 1
        assert len(order_book.asks) == 1


class TestTradingIntegration:
    """Integration tests for trading workflows."""

    @patch("polymarket_client.clob_client._ClobClient.submit_limit_order")
    @patch("polymarket_client.clob_client._ClobClient.get_open_orders")
    @patch("polymarket_client.clob_client._ClobClient.cancel_order")
    def test_order_lifecycle_workflow(
        self, mock_cancel, mock_get_orders, mock_submit, integration_config
    ):
        """Test complete order lifecycle: submit, check status, cancel."""
        # Mock order submission response
        mock_order_response = Mock()
        mock_order_response.order_id = "order123"
        mock_order_response.success = True
        mock_order_response.status = "PENDING"
        mock_submit.return_value = mock_order_response

        # Mock open orders response
        mock_orders_list = Mock()
        mock_orders_list.orders = [
            {
                "id": "order123",
                "market": "0x123abc",
                "side": "BUY",
                "size": "100",
                "price": "0.6",
                "status": "OPEN",
            }
        ]
        mock_get_orders.return_value = mock_orders_list

        # Mock cancel response
        mock_cancel_response = Mock()
        mock_cancel_response.success = True
        mock_cancel_response.cancelled_orders = ["order123"]
        mock_cancel.return_value = mock_cancel_response

        client = PolymarketClient(integration_config)

        # Test order submission
        from polymarket_client.models.limit_order_request import (
            LimitOrderRequest,
            OrderSide,
            OrderType,
        )

        order_request = LimitOrderRequest(
            token_id="token1",
            side=OrderSide.BUY,
            size=100.0,
            price=0.6,
            order_type=OrderType.GTC,
        )

        order_response = client.submit_limit_order(order_request)
        assert order_response.order_id == "order123"
        assert order_response.success is True

        # Test checking open orders
        open_orders = client.get_open_orders()
        assert len(open_orders.orders) == 1
        assert open_orders.orders[0]["id"] == "order123"

        # Test cancelling order
        cancel_response = client.cancel_order("order123")
        assert cancel_response.success is True
        assert "order123" in cancel_response.cancelled_orders

    @patch("polymarket_client.clob_client._ClobClient.get_user_positions")
    @patch("polymarket_client.clob_client._ClobClient.get_user_activity")
    def test_portfolio_tracking_workflow(
        self, mock_get_activity, mock_get_positions, integration_config
    ):
        """Test portfolio tracking: positions and activity history."""
        # Mock positions response
        mock_positions_data = {
            "positions": [
                {
                    "token_id": "token1",
                    "market_id": "0x123abc",
                    "outcome": "Yes",
                    "size": "50.0",
                    "value": "30.0",
                    "avg_price": "0.6",
                }
            ]
        }
        mock_get_positions.return_value = mock_positions_data

        # Mock activity response
        mock_activity = Mock()
        mock_activity.activities = [
            {
                "id": "activity1",
                "type": "TRADE",
                "market_id": "0x123abc",
                "outcome": "Yes",
                "side": "BUY",
                "size": "50.0",
                "price": "0.6",
                "timestamp": "2024-01-01T12:00:00Z",
            }
        ]
        mock_get_activity.return_value = mock_activity

        client = PolymarketClient(integration_config)
        user_address = "0x" + "1" * 40

        # Test getting positions
        positions = client.get_user_positions(user_address)
        assert positions is not None

        # Test getting activity
        activity = client.get_user_activity(user_address)
        assert activity.activities is not None


class TestErrorHandlingIntegration:
    """Integration tests for error handling across different API failures."""

    @patch("requests.Session.get")
    def test_network_error_handling(self, mock_get, integration_config):
        """Test handling of network errors in API calls."""
        # Mock network error
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        client = PolymarketClient(integration_config)

        # Test that network errors are properly handled
        with pytest.raises(requests.exceptions.ConnectionError):
            client.get_events()

    @patch("requests.Session.get")
    def test_api_error_response_handling(self, mock_get, integration_config):
        """Test handling of API error responses."""
        # Mock 400 error response
        error_response = Mock()
        error_response.status_code = 400
        error_response.json.return_value = {
            "error": "Bad Request",
            "message": "Invalid parameter",
        }
        error_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Client Error"
        )
        mock_get.return_value = error_response

        client = PolymarketClient(integration_config)

        # Test that HTTP errors are properly handled
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_events()

    @patch("requests.Session.get")
    def test_rate_limit_error_handling(self, mock_get, integration_config):
        """Test handling of rate limit errors."""
        # Mock 429 rate limit response
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "60"}
        rate_limit_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("429 Too Many Requests")
        )
        mock_get.return_value = rate_limit_response

        client = PolymarketClient(integration_config)

        # Test that rate limit errors are properly handled
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_events()


class TestConfigurationIntegration:
    """Integration tests for different configuration scenarios."""

    def test_client_initialization_with_env_config(self):
        """Test client initialization from environment variables."""
        with patch.dict(
            "os.environ",
            {
                "POLYMARKET_API_KEY": "env_key",
                "POLYMARKET_API_SECRET": "env_secret",
                "POLYMARKET_API_PASSPHRASE": "env_passphrase",
                "POLYMARKET_PRIVATE_KEY": "0x" + "2" * 64,
            },
        ):
            # Test that client can be initialized from environment
            from polymarket_client.configs.polymarket_configs import PolymarketConfig

            config = PolymarketConfig.from_env()
            client = PolymarketClient(config)

            assert client.config.api_key == "env_key"
            assert client.config.api_secret == "env_secret"

    def test_client_with_custom_endpoints(self):
        """Test client with custom API endpoints."""
        custom_config = PolymarketConfig(
            api_key="test_key",
            api_secret="test_secret",
            api_passphrase="test_passphrase",
            pk="0x" + "3" * 64,
            endpoints={
                "gamma": "https://custom-gamma.example.com",
                "clob": "https://custom-clob.example.com",
                "info": "https://custom-info.example.com",
                "neg_risk": "https://custom-neg-risk.example.com",
                "data_api": "https://custom-data-api.example.com",
            },
        )

        client = PolymarketClient(custom_config)

        assert client.config.get_endpoint("gamma") == "https://custom-gamma.example.com"
        assert client.config.get_endpoint("clob") == "https://custom-clob.example.com"

    def test_client_with_rate_limiting_config(self):
        """Test client with rate limiting configuration."""
        rate_limited_config = PolymarketConfig(
            api_key="test_key",
            api_secret="test_secret",
            api_passphrase="test_passphrase",
            pk="0x" + "4" * 64,
            enable_rate_limiting=True,
            requests_per_second=2.0,
            burst_capacity=5,
        )

        client = PolymarketClient(rate_limited_config)

        assert client.config.enable_rate_limiting is True
        assert client.config.requests_per_second == 2.0
        assert client.config.burst_capacity == 5


@pytest.mark.integration
class TestEndToEndWorkflows:
    """End-to-end integration tests for complete user workflows."""

    @patch("requests.Session.get")
    @patch("polymarket_client.clob_client._ClobClient.get_market")
    @patch("polymarket_client.clob_client._ClobClient.submit_limit_order")
    def test_discover_and_trade_workflow(
        self, mock_submit, mock_get_market, mock_get, integration_config
    ):
        """Test complete workflow: discover events -> find market -> place order."""
        # Mock events discovery
        events_response = Mock()
        events_response.json.return_value = [
            {
                "id": "event1",
                "ticker": "TECH",
                "title": "Tech IPO Success",
                "slug": "tech-ipo",
                "active": True,
                "markets": [
                    {
                        "id": "market1",
                        "question": "Will IPO be successful?",
                        "condition_id": "0xabc123",
                        "tokens": [
                            {"token_id": "token_yes", "outcome": "Yes"},
                            {"token_id": "token_no", "outcome": "No"},
                        ],
                    }
                ],
            }
        ]
        events_response.raise_for_status.return_value = None
        mock_get.return_value = events_response

        # Mock market details
        mock_market = Mock()
        mock_market.condition_id = "0xabc123"
        mock_market.question = "Will IPO be successful?"
        mock_market.tokens = [
            {"token_id": "token_yes", "outcome": "Yes"},
            {"token_id": "token_no", "outcome": "No"},
        ]
        mock_get_market.return_value = mock_market

        # Mock order submission
        mock_order_response = Mock()
        mock_order_response.order_id = "order_xyz"
        mock_order_response.success = True
        mock_submit.return_value = mock_order_response

        client = PolymarketClient(integration_config)

        # Step 1: Discover events
        events = client.get_events()
        assert len(events) == 1
        tech_event = events[0]
        assert tech_event.ticker == "TECH"

        # Step 2: Get market details
        market_id = tech_event.markets[0].condition_id
        market = client.get_market(market_id)
        assert market.condition_id == "0xabc123"

        # Step 3: Place order
        from polymarket_client.models.limit_order_request import (
            LimitOrderRequest,
            OrderSide,
            OrderType,
        )

        order_request = LimitOrderRequest(
            token_id="token_yes",
            side=OrderSide.BUY,
            size=50.0,
            price=0.65,
            order_type=OrderType.GTC,
        )

        order_response = client.submit_limit_order(order_request)
        assert order_response.success is True
        assert order_response.order_id == "order_xyz"

    @patch("requests.Session.get")
    @patch("polymarket_client.clob_client._ClobClient.get_user_positions")
    def test_portfolio_analysis_workflow(
        self, mock_get_positions, mock_get, integration_config
    ):
        """Test portfolio analysis workflow with positions and market data."""
        # Mock current events for context
        events_response = Mock()
        events_response.json.return_value = [
            {
                "id": "event1",
                "ticker": "ELECTION",
                "title": "Presidential Election",
                "active": True,
                "markets": [{"condition_id": "0x123", "question": "Who will win?"}],
            }
        ]
        events_response.raise_for_status.return_value = None
        mock_get.return_value = events_response

        # Mock user positions
        mock_positions_data = {
            "positions": [
                {
                    "token_id": "token1",
                    "market_id": "0x123",
                    "outcome": "Yes",
                    "size": "100.0",
                    "value": "65.0",
                    "avg_price": "0.65",
                }
            ]
        }
        mock_get_positions.return_value = mock_positions_data

        client = PolymarketClient(integration_config)
        user_address = "0x" + "5" * 40

        # Get current events for context
        events = client.get_events()
        assert len(events) == 1

        # Get portfolio positions
        positions = client.get_user_positions(user_address)
        assert positions is not None

        # Analysis: User has positions in active election market
        election_market_id = events[0].markets[0]["condition_id"]
        # This would be where portfolio analysis logic would go
        assert election_market_id == "0x123"
