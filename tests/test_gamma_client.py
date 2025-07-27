"""Tests for the GammaClient class."""

from unittest.mock import Mock, patch

import pytest
import requests

from polymarket_client.exceptions import (
    PolymarketAPIError,
    PolymarketNetworkError,
    PolymarketValidationError,
)
from polymarket_client.gamma_client import _GammaClient as GammaClient


class TestGammaClient:
    """Test cases for GammaClient."""

    def test_init_with_config(self, test_config):
        """Test client initialization with provided config."""
        client = GammaClient(test_config)

        assert client.config == test_config
        assert client.base_url == test_config.get_endpoint("gamma")
        assert client._session is not None

    def test_from_config_factory_method(self, test_config):
        """Test from_config factory method."""
        client = GammaClient.from_config(test_config)

        assert isinstance(client, GammaClient)
        assert client.config == test_config

    @patch.dict(
        "os.environ",
        {
            "POLYMARKET_API_KEY": "test_key",
            "POLYMARKET_API_SECRET": "test_secret",
            "POLYMARKET_API_PASSPHRASE": "test_passphrase",
            "POLYMARKET_PRIVATE_KEY": "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        },
    )
    def test_from_env_factory_method(self):
        """Test from_env factory method."""
        client = GammaClient.from_env()

        assert isinstance(client, GammaClient)
        assert client.config.api_key == "test_key"

    def test_from_url_factory_method(self):
        """Test from_url factory method for backward compatibility."""
        url = "https://test-gamma.example.com"
        client = GammaClient.from_url(
            url,
            api_key="test",
            api_secret="test",
            api_passphrase="test",
            pk="0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        )

        assert isinstance(client, GammaClient)
        assert client.base_url == url

    def test_session_uses_config_settings(self, test_config):
        """Test that session is configured with settings from config."""
        client = GammaClient(test_config)
        session = client._session

        assert session.timeout == test_config.timeout
        assert "polymarket-sdk" in session.headers["User-Agent"]
        assert session.headers["Accept"] == "application/json"

    @patch("polymarket_client.gamma_client.requests.Session.get")
    def test_get_events_uses_config_defaults(
        self, mock_get, test_config, sample_event_data
    ):
        """Test that get_events uses config defaults when parameters not provided."""
        mock_response = Mock()
        mock_response.json.return_value = [sample_event_data]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = GammaClient(test_config)

        # Call without limit - should use config default
        client.get_events()

        # Check that the request was made with config default page size
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["limit"] == test_config.default_page_size

    def test_get_events_validates_limit_against_config(self, test_config):
        """Test that get_events validates limit against config max_page_size."""
        client = GammaClient(test_config)

        # Try to request more than max_page_size
        with pytest.raises(PolymarketValidationError) as exc_info:
            client.get_events(limit=test_config.max_page_size + 1)

        assert "exceeds maximum allowed" in str(exc_info.value)
        assert exc_info.value.field == "limit"

    @patch("polymarket_client.gamma_client.requests.Session.get")
    def test_get_events_handles_network_error(self, mock_get, test_config):
        """Test that get_events properly handles network errors."""
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        client = GammaClient(test_config)

        with pytest.raises(PolymarketNetworkError) as exc_info:
            client.get_events()

        assert "Failed to fetch events" in str(exc_info.value)
        assert exc_info.value.original_error is not None

    @patch("polymarket_client.gamma_client.requests.Session.get")
    def test_get_events_handles_http_error(self, mock_get, test_config):
        """Test that get_events properly handles HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "400 Bad Request"
        )
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        client = GammaClient(test_config)

        with pytest.raises(PolymarketAPIError) as exc_info:
            client.get_events()

        assert "API request failed" in str(exc_info.value)
        assert exc_info.value.status_code == 400

    @patch("polymarket_client.gamma_client.requests.Session.get")
    def test_get_events_handles_invalid_response_format(self, mock_get, test_config):
        """Test that get_events handles invalid response format."""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "not a list"}  # Should be a list
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = GammaClient(test_config)

        with pytest.raises(PolymarketAPIError) as exc_info:
            client.get_events()

        assert "Unexpected response format" in str(exc_info.value)

    @patch("polymarket_client.gamma_client.requests.Session.get")
    def test_get_events_auto_pagination_disabled(
        self, mock_get, test_config, sample_event_data
    ):
        """Test that auto_paginate=False stops after first page."""
        mock_response = Mock()
        mock_response.json.return_value = [sample_event_data] * 100  # Full page
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = GammaClient(test_config)

        # Disable auto-pagination
        result = client.get_events(auto_paginate=False, limit=100)

        # Should only make one request even though we got a full page
        assert mock_get.call_count == 1
        assert len(result) == 100

    @patch("polymarket_client.gamma_client.requests.Session.get")
    def test_health_check_healthy(self, mock_get, test_config):
        """Test health_check when API is healthy."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_get.return_value = mock_response

        client = GammaClient(test_config)
        result = client.health_check()

        assert result["status"] == "healthy"
        assert result["endpoint"] == client.base_url
        assert "response_time_ms" in result

    @patch("polymarket_client.gamma_client.requests.Session.get")
    def test_health_check_unhealthy(self, mock_get, test_config):
        """Test health_check when API is unhealthy."""
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        client = GammaClient(test_config)
        result = client.health_check()

        assert result["status"] == "unhealthy"
        assert result["endpoint"] == client.base_url
        assert "error" in result
