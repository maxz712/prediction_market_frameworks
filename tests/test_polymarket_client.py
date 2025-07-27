"""Tests for the main PolymarketClient class."""

from unittest.mock import patch

import pytest

from polymarket_client import PolymarketClient, PolymarketConfigurationError


class TestPolymarketClient:
    """Test cases for PolymarketClient."""

    def test_init_with_config(self, test_config):
        """Test client initialization with provided config."""
        client = PolymarketClient(test_config)

        assert client.config == test_config
        assert client.gamma_client is not None
        assert client.clob_client is not None

    @patch.dict("os.environ", {
        "POLYMARKET_API_KEY": "test_key",
        "POLYMARKET_API_SECRET": "test_secret",
        "POLYMARKET_API_PASSPHRASE": "test_passphrase",
        "POLYMARKET_PRIVATE_KEY": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    })
    def test_init_from_env(self):
        """Test client initialization from environment variables."""
        client = PolymarketClient()

        assert client.config.api_key == "test_key"
        assert client.config.api_secret == "test_secret"
        assert client.config.api_passphrase == "test_passphrase"
        assert client.config.pk == "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

    def test_init_without_config_or_env_raises_error(self):
        """Test that initialization fails without config or env vars."""
        with pytest.raises((ValueError, PolymarketConfigurationError)):
            PolymarketClient()

    def test_gamma_property(self, test_config):
        """Test access to gamma client property."""
        client = PolymarketClient(test_config)

        assert client.gamma is client.gamma_client

    def test_clob_property(self, test_config):
        """Test access to clob client property."""
        client = PolymarketClient(test_config)

        assert client.clob is client.clob_client

    @patch("polymarket_client.gamma_client._GammaClient.get_events")
    def test_get_events_delegation(self, mock_get_events, test_config, sample_event_data):
        """Test that get_events delegates to gamma client."""
        mock_get_events.return_value = [sample_event_data]
        client = PolymarketClient(test_config)

        result = client.get_events(limit=5)

        mock_get_events.assert_called_once_with(
            limit=5, offset=0, auto_paginate=None, order=None, ascending=True,
            event_id=None, slug=None, archived=None, active=True, closed=False,
            liquidity_min=None, liquidity_max=None, volume_min=None, volume_max=None,
            start_date_min=None, start_date_max=None, end_date_min=None, end_date_max=None,
            tag=None, tag_id=None, related_tags=None, tag_slug=None
        )
        assert result == [sample_event_data]

    @patch("polymarket_client.gamma_client._GammaClient.get_events")
    def test_get_active_events(self, mock_get_events, test_config, sample_event_data):
        """Test get_active_events method."""
        mock_get_events.return_value = [sample_event_data]
        client = PolymarketClient(test_config)

        result = client.get_active_events(limit=10)

        mock_get_events.assert_called_once_with(
            limit=10, offset=0, auto_paginate=None, order=None, ascending=True,
            event_id=None, slug=None, archived=None, active=True, closed=False,
            liquidity_min=None, liquidity_max=None, volume_min=None, volume_max=None,
            start_date_min=None, start_date_max=None, end_date_min=None, end_date_max=None,
            tag=None, tag_id=None, related_tags=None, tag_slug=None
        )
        assert result == [sample_event_data]

    @patch("polymarket_client.clob_client._ClobClient.get_market")
    def test_get_market_delegation(self, mock_get_market, test_config, sample_market_data):
        """Test that get_market delegates to clob client."""
        mock_get_market.return_value = sample_market_data
        client = PolymarketClient(test_config)

        client.get_market("0x1234567890abcdef1234567890abcdef12345678")

        mock_get_market.assert_called_once_with("0x1234567890abcdef1234567890abcdef12345678")
        # Note: The actual result would be a Market model, but we're testing delegation

    def test_client_has_expected_methods(self, test_config):
        """Test that client has all expected public methods."""
        client = PolymarketClient(test_config)

        expected_methods = [
            "get_events", "get_events_paginated", "get_active_events", "get_events_by_slug",
            "get_market", "get_order_book", "get_user_market_trades_history", "get_prices_history",
            "cancel_order", "cancel_orders", "cancel_all_orders", "submit_limit_order",
            "get_open_orders", "get_current_user_position", "get_user_position",
            "get_user_activity", "get_current_user_activity", "get_user_address"
        ]

        for method_name in expected_methods:
            assert hasattr(client, method_name), f"Missing method: {method_name}"
            assert callable(getattr(client, method_name)), f"Method not callable: {method_name}"
