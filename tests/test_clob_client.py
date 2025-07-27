"""Tests for the _ClobClient class."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from polymarket_client.clob_client import _ClobClient as ClobClient
from polymarket_client.models import (
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
from polymarket_client.models.order import OrderSide
from polymarket_client.models.order import OrderType as PMOrderType


class TestClobClient:
    """Test cases for ClobClient."""

    @patch("polymarket_client.clob_client.create_rate_limited_session")
    @patch("polymarket_client.clob_client.PyClobClient")
    def test_init_with_config(
        self, mock_py_clob_client, mock_rate_limited_session, test_config
    ):
        """Test client initialization with provided config."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)

        assert client.config == test_config
        assert client._py_client == mock_client_instance
        assert client._session is not None

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_init_with_proxy_config(self, mock_py_clob_client, test_config):
        """Test client initialization with proxy wallet configuration."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        # Set up proxy configuration
        test_config.wallet_proxy_address = "0xproxy123"

        ClobClient(test_config)

        # Verify proxy setup was called
        mock_py_clob_client.assert_called_with(
            host=test_config.get_endpoint("clob"),
            key=test_config.pk,
            chain_id=test_config.chain_id,
            signature_type=1,
            funder=test_config.wallet_proxy_address,
        )
        mock_client_instance.set_api_creds.assert_called_once()
        mock_client_instance.create_or_derive_api_creds.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_from_config_dict(self, mock_py_clob_client, test_config):
        """Test from_config_dict factory method."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        config_dict = {
            "api_key": test_config.api_key,
            "api_secret": test_config.api_secret,
            "api_passphrase": test_config.api_passphrase,
            "pk": test_config.pk,
            "endpoints": test_config.endpoints,
            "chain_id": test_config.chain_id,
        }

        client = ClobClient.from_config_dict(config_dict)

        assert isinstance(client, ClobClient)
        assert client.config.api_key == test_config.api_key

    @patch.dict(
        "os.environ",
        {
            "POLYMARKET_API_KEY": "test_key",
            "POLYMARKET_API_SECRET": "test_secret",
            "POLYMARKET_API_PASSPHRASE": "test_passphrase",
            "POLYMARKET_PRIVATE_KEY": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        },
    )
    @patch("polymarket_client.clob_client.PyClobClient")
    def test_from_env(self, mock_py_clob_client):
        """Test from_env factory method."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient.from_env()

        assert isinstance(client, ClobClient)
        assert client.config.api_key == "test_key"

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_init_session_configuration(self, mock_py_clob_client, test_config):
        """Test that session is properly configured."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        session = client._session

        assert session.timeout == test_config.timeout
        # Check that adapters are mounted
        assert "https://" in session.adapters
        assert "http://" in session.adapters

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_market(self, mock_py_clob_client, test_config, sample_market_data):
        """Test get_market method."""
        mock_client_instance = Mock()
        mock_client_instance.get_market.return_value = sample_market_data
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_market("test_token_id")

        assert isinstance(result, Market)
        mock_client_instance.get_market.assert_called_once_with("test_token_id")

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_order_book(self, mock_py_clob_client, test_config):
        """Test get_order_book method."""
        mock_client_instance = Mock()
        mock_summary = Mock()
        mock_summary.market = "test_market"
        mock_summary.asset_id = "test_asset"
        mock_summary.timestamp = 1640995200
        mock_summary.hash = "test_hash"
        mock_summary.bids = [["0.5", "100"]]
        mock_summary.asks = [["0.6", "200"]]
        mock_client_instance.get_order_book.return_value = mock_summary
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_order_book("test_token_id")

        assert isinstance(result, OrderBook)
        mock_client_instance.get_order_book.assert_called_once_with("test_token_id")

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_post_order(self, mock_py_clob_client, test_config):
        """Test post_order method."""
        mock_client_instance = Mock()
        mock_client_instance.create_and_post_order.return_value = {
            "order_id": "test_order"
        }
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        order_args = {
            "token_id": "test_token",
            "price": 0.5,
            "size": 100.0,
            "side": "BUY",
        }

        result = client.post_order(order_args)

        assert result == {"order_id": "test_order"}
        mock_client_instance.create_and_post_order.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_cancel_order(self, mock_py_clob_client, test_config):
        """Test cancel_order method."""
        mock_client_instance = Mock()
        mock_client_instance.cancel.return_value = {"success": True}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.cancel_order("test_order_id")

        assert isinstance(result, CancelResponse)
        mock_client_instance.cancel.assert_called_once_with("test_order_id")

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_cancel_orders(self, mock_py_clob_client, test_config):
        """Test cancel_orders method."""
        mock_client_instance = Mock()
        mock_client_instance.cancel_orders.return_value = {"success": True}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        order_ids = ["order1", "order2"]
        result = client.cancel_orders(order_ids)

        assert isinstance(result, CancelResponse)
        mock_client_instance.cancel_orders.assert_called_once_with(order_ids)

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_cancel_all(self, mock_py_clob_client, test_config):
        """Test cancel_all method."""
        mock_client_instance = Mock()
        mock_client_instance.cancel_all.return_value = {"success": True}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.cancel_all()

        assert isinstance(result, CancelResponse)
        mock_client_instance.cancel_all.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_user_market_trades_history(self, mock_py_clob_client, test_config):
        """Test get_user_market_trades_history method."""
        mock_client_instance = Mock()
        mock_trades = [
            {"id": "1", "market": "test_token", "side": "buy", "size": "100"},
            {"id": "2", "market": "other_token", "side": "sell", "size": "50"},
        ]
        mock_client_instance.get_trades.return_value = mock_trades
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_user_market_trades_history("test_token", limit=10)

        assert isinstance(result, TradeHistory)
        mock_client_instance.get_trades.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_user_market_trades_history_with_error(
        self, mock_py_clob_client, test_config
    ):
        """Test get_user_market_trades_history method handles errors gracefully."""
        mock_client_instance = Mock()
        mock_client_instance.get_trades.side_effect = Exception("API Error")
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_user_market_trades_history("test_token")

        assert isinstance(result, TradeHistory)

    @patch("polymarket_client.clob_client.PyClobClient")
    @patch("polymarket_client.clob_client.requests.Session.get")
    def test_get_user_positions(self, mock_get, mock_py_clob_client, test_config):
        """Test get_user_positions method."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        mock_response = Mock()
        mock_response.json.return_value = {"positions": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = ClobClient(test_config)
        result = client.get_user_positions("0xtest_address")

        assert result == {"positions": []}
        mock_get.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    @patch("polymarket_client.clob_client.requests.Session.get")
    def test_get_user_positions_http_error(
        self, mock_get, mock_py_clob_client, test_config
    ):
        """Test get_user_positions method with HTTP error."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "400 Bad Request"
        )
        mock_get.return_value = mock_response

        client = ClobClient(test_config)

        with pytest.raises(requests.HTTPError):
            client.get_user_positions("0xtest_address")

    @patch("polymarket_client.clob_client.PyClobClient")
    @patch("polymarket_client.clob_client.requests.Session.get")
    def test_get_user_activity(self, mock_get, mock_py_clob_client, test_config):
        """Test get_user_activity method."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        mock_response = Mock()
        mock_response.json.return_value = {"activities": [], "next_cursor": None}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = ClobClient(test_config)
        result = client.get_user_activity(
            "0xtest_address",
            limit=50,
            market="test_market",
            activity_type="TRADE",
            side="BUY",
        )

        assert isinstance(result, UserActivity)
        mock_get.assert_called_once()

        # Check that parameters were properly formatted
        args, kwargs = mock_get.call_args
        params = kwargs["params"]
        assert params["user"] == "0xtest_address"
        assert params["limit"] == 50
        assert params["market"] == "test_market"
        assert params["type"] == "TRADE"
        assert params["side"] == "BUY"

    @patch("polymarket_client.clob_client.PyClobClient")
    @patch("polymarket_client.clob_client.requests.Session.get")
    def test_get_user_activity_with_limit_capping(
        self, mock_get, mock_py_clob_client, test_config
    ):
        """Test get_user_activity method caps limit at 500."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        mock_response = Mock()
        mock_response.json.return_value = {"activities": [], "next_cursor": None}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = ClobClient(test_config)
        client.get_user_activity("0xtest_address", limit=1000)  # Over the limit

        # Check that limit was capped at 500
        args, kwargs = mock_get.call_args
        params = kwargs["params"]
        assert params["limit"] == 500

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_current_user_activity(self, mock_py_clob_client, test_config):
        """Test get_current_user_activity method."""
        mock_client_instance = Mock()
        mock_client_instance.get_address.return_value = "0xcurrent_user"
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)

        with patch.object(client, "get_user_activity") as mock_get_activity:
            mock_get_activity.return_value = Mock(spec=UserActivity)

            client.get_current_user_activity(limit=25)

            mock_get_activity.assert_called_once_with(
                proxy_wallet_address="0xcurrent_user",
                limit=25,
                offset=0,
                market=None,
                activity_type=None,
                start=None,
                end=None,
                side=None,
                sort_by="TIMESTAMP",
                sort_direction="DESC",
            )

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_submit_market_order(self, mock_py_clob_client, test_config):
        """Test submit_market_order method."""
        mock_client_instance = Mock()
        mock_order = Mock()
        mock_client_instance.create_market_order.return_value = mock_order
        mock_client_instance.post_order.return_value = {"order_id": "market_order_123"}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.submit_market_order("test_token", "BUY", 100.0)

        assert result == {"order_id": "market_order_123"}
        mock_client_instance.create_market_order.assert_called_once()
        mock_client_instance.post_order.assert_called_once_with(mock_order)

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_submit_limit_order_gtc(self, mock_py_clob_client, test_config):
        """Test submit_limit_order method with GTC order."""
        mock_client_instance = Mock()
        mock_order = Mock()
        mock_client_instance.create_order.return_value = mock_order
        mock_client_instance.post_order.return_value = {"order_id": "limit_order_123"}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        request = LimitOrderRequest(
            token_id="test_token",
            price=0.5,
            size=100.0,
            side=OrderSide.BUY,
            order_type=PMOrderType.GTC,
        )

        result = client.submit_limit_order(request)

        assert isinstance(result, OrderResponse)
        mock_client_instance.create_order.assert_called_once()
        mock_client_instance.post_order.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_submit_limit_order_gtd_with_expiration(
        self, mock_py_clob_client, test_config
    ):
        """Test submit_limit_order method with GTD order and expiration."""
        mock_client_instance = Mock()
        mock_order = Mock()
        mock_client_instance.create_order.return_value = mock_order
        mock_client_instance.post_order.return_value = {"order_id": "gtd_order_123"}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        expiration_time = int(datetime.now().timestamp()) + 3600  # 1 hour from now
        request = LimitOrderRequest(
            token_id="test_token",
            price=0.5,
            size=100.0,
            side=OrderSide.BUY,
            order_type=PMOrderType.GTD,
            expires_at=expiration_time,
        )

        result = client.submit_limit_order(request)

        assert isinstance(result, OrderResponse)

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_submit_limit_order_gtd_without_expiration_raises_error(
        self, mock_py_clob_client, test_config
    ):
        """Test submit_limit_order method with GTD order but no expiration raises error."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        request = LimitOrderRequest(
            token_id="test_token",
            price=0.5,
            size=100.0,
            side=OrderSide.BUY,
            order_type=PMOrderType.GTD,  # No expires_at set
        )

        with pytest.raises(ValueError, match="expires_at must be set for GTD orders"):
            client.submit_limit_order(request)

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_open_orders(self, mock_py_clob_client, test_config):
        """Test get_open_orders method."""
        mock_client_instance = Mock()
        mock_client_instance.get_orders.return_value = {"orders": []}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_open_orders()

        assert isinstance(result, OrderList)
        mock_client_instance.get_orders.assert_called_once_with()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_open_orders_with_market_filter(self, mock_py_clob_client, test_config):
        """Test get_open_orders method with market filter."""
        mock_client_instance = Mock()
        mock_client_instance.get_orders.return_value = {"orders": []}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_open_orders(market="test_market")

        assert isinstance(result, OrderList)
        mock_client_instance.get_orders.assert_called_once_with(market="test_market")

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_user_position(self, mock_py_clob_client, test_config):
        """Test get_user_position method."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)

        with patch.object(client, "get_user_positions") as mock_get_positions:
            mock_get_positions.return_value = {"positions": []}

            result = client.get_user_position("0xtest_address")

            assert isinstance(result, UserPositions)
            mock_get_positions.assert_called_once_with("0xtest_address")

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_current_user_position(self, mock_py_clob_client, test_config):
        """Test get_current_user_position method."""
        mock_client_instance = Mock()
        mock_client_instance.get_address.return_value = "0xcurrent_user"
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)

        with patch.object(client, "get_user_position") as mock_get_position:
            mock_get_position.return_value = Mock(spec=UserPositions)

            client.get_current_user_position(market="test_market")

            mock_get_position.assert_called_once_with(
                proxy_wallet_address="0xcurrent_user", market="test_market"
            )

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_balance_allowance_collateral(self, mock_py_clob_client, test_config):
        """Test get_balance_allowance method for collateral."""
        mock_client_instance = Mock()
        mock_client_instance.get_balance_allowance.return_value = {
            "balance": "1000",
            "allowance": "500",
        }
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_balance_allowance("COLLATERAL")

        assert result == {"balance": "1000", "allowance": "500"}
        mock_client_instance.get_balance_allowance.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_balance_allowance_conditional(self, mock_py_clob_client, test_config):
        """Test get_balance_allowance method for conditional tokens."""
        mock_client_instance = Mock()
        mock_client_instance.get_balance_allowance.return_value = {
            "balance": "100",
            "allowance": "50",
        }
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_balance_allowance("CONDITIONAL", "test_token_id")

        assert result == {"balance": "100", "allowance": "50"}
        mock_client_instance.get_balance_allowance.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_update_balance_allowance(self, mock_py_clob_client, test_config):
        """Test update_balance_allowance method."""
        mock_client_instance = Mock()
        mock_client_instance.update_balance_allowance.return_value = {
            "balance": "1200",
            "allowance": "600",
        }
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.update_balance_allowance("COLLATERAL")

        assert result == {"balance": "1200", "allowance": "600"}
        mock_client_instance.update_balance_allowance.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_usdc_balance_allowance(self, mock_py_clob_client, test_config):
        """Test get_usdc_balance_allowance convenience method."""
        mock_client_instance = Mock()
        mock_client_instance.get_balance_allowance.return_value = {
            "balance": "1000",
            "allowance": "500",
        }
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_usdc_balance_allowance()

        assert result == {"balance": "1000", "allowance": "500"}

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_update_usdc_balance_allowance(self, mock_py_clob_client, test_config):
        """Test update_usdc_balance_allowance convenience method."""
        mock_client_instance = Mock()
        mock_client_instance.update_balance_allowance.return_value = {
            "balance": "1200",
            "allowance": "600",
        }
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.update_usdc_balance_allowance()

        assert result == {"balance": "1200", "allowance": "600"}

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_check_usdc_allowance_sufficient_true(
        self, mock_py_clob_client, test_config
    ):
        """Test check_usdc_allowance_sufficient returns True when sufficient."""
        mock_client_instance = Mock()
        mock_client_instance.get_balance_allowance.return_value = {"allowance": "1000"}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.check_usdc_allowance_sufficient(500.0)

        assert result is True

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_check_usdc_allowance_sufficient_false(
        self, mock_py_clob_client, test_config
    ):
        """Test check_usdc_allowance_sufficient returns False when insufficient."""
        mock_client_instance = Mock()
        mock_client_instance.get_balance_allowance.return_value = {"allowance": "100"}
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.check_usdc_allowance_sufficient(500.0)

        assert result is False

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_check_usdc_allowance_sufficient_error_handling(
        self, mock_py_clob_client, test_config
    ):
        """Test check_usdc_allowance_sufficient handles errors gracefully."""
        mock_client_instance = Mock()
        mock_client_instance.get_balance_allowance.side_effect = Exception("API Error")
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.check_usdc_allowance_sufficient(500.0)

        assert result is False

    @patch("polymarket_client.clob_client.PyClobClient")
    @patch("polymarket_client.clob_client.requests.Session.get")
    def test_get_prices_history(self, mock_get, mock_py_clob_client, test_config):
        """Test get_prices_history method."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        mock_response = Mock()
        mock_response.json.return_value = {"prices": [], "timestamps": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = ClobClient(test_config)
        result = client.get_prices_history(
            market="test_market",
            start_ts=1640995200,
            end_ts=1641081600,
            interval="1h",
            fidelity=60,
        )

        assert isinstance(result, PricesHistory)
        mock_get.assert_called_once()

        # Check that parameters were properly passed
        args, kwargs = mock_get.call_args
        params = kwargs["params"]
        assert params["market"] == "test_market"
        assert params["startTs"] == 1640995200
        assert params["endTs"] == 1641081600
        assert params["interval"] == "1h"
        assert params["fidelity"] == 60

    @patch("polymarket_client.clob_client.PyClobClient")
    @patch("polymarket_client.clob_client.requests.Session.get")
    def test_get_prices_history_minimal_params(
        self, mock_get, mock_py_clob_client, test_config
    ):
        """Test get_prices_history method with minimal parameters."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        mock_response = Mock()
        mock_response.json.return_value = {"prices": [], "timestamps": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = ClobClient(test_config)
        result = client.get_prices_history(market="test_market")

        assert isinstance(result, PricesHistory)

        # Check that only required parameter was passed
        args, kwargs = mock_get.call_args
        params = kwargs["params"]
        assert params == {"market": "test_market"}

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_get_user_address(self, mock_py_clob_client, test_config):
        """Test get_user_address method."""
        mock_client_instance = Mock()
        mock_client_instance.get_address.return_value = "0xuser_address"
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)
        result = client.get_user_address()

        assert result == "0xuser_address"
        mock_client_instance.get_address.assert_called_once()

    @patch("polymarket_client.clob_client.PyClobClient")
    def test_py_client_property(self, mock_py_clob_client, test_config):
        """Test py_client property exposes underlying client."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        client = ClobClient(test_config)

        assert client.py_client == mock_client_instance

    @patch("polymarket_client.clob_client.PyClobClient")
    @patch("polymarket_client.clob_client.requests.Session.get")
    def test_get_prices_history_http_error(
        self, mock_get, mock_py_clob_client, test_config
    ):
        """Test get_prices_history method with HTTP error."""
        mock_client_instance = Mock()
        mock_py_clob_client.return_value = mock_client_instance

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "500 Server Error"
        )
        mock_get.return_value = mock_response

        client = ClobClient(test_config)

        with pytest.raises(requests.HTTPError):
            client.get_prices_history(market="test_market")
