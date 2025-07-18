"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock
from src.polymarket_client.configs.polymarket_configs import PolymarketConfig


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return PolymarketConfig(
        api_key="test_api_key",
        api_secret="test_api_secret", 
        api_passphrase="test_passphrase",
        pk="test_private_key",
        endpoints={
            "gamma": "https://test-gamma.example.com",
            "clob": "https://test-clob.example.com",
            "info": "https://test-info.example.com",
            "neg_risk": "https://test-neg-risk.example.com"
        },
        chain_id=137,
        timeout=30,
        max_retries=3
    )


@pytest.fixture
def mock_session():
    """Create a mock requests session."""
    return Mock()


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "id": "test_event_id",
        "title": "Test Event",
        "description": "A test event",
        "slug": "test-event",
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-12-31T23:59:59Z",
        "active": True,
        "closed": False,
        "tags": [],
        "markets": [],
        "clob_rewards": []
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "condition_id": "test_condition_id",
        "question": "Test question?",
        "description": "Test market description",
        "market_slug": "test-market",
        "end_date_iso": "2024-12-31T23:59:59Z",
        "game_start_time": "2024-01-01T00:00:00Z",
        "seconds_delay": 0,
        "fpmm": "0x1234567890abcdef",
        "maker_base_fee": 0.01,
        "taker_base_fee": 0.01,
        "tags": [],
        "outcomes": ["Yes", "No"],
        "outcome_prices": ["0.5", "0.5"],
        "volume": "1000.0",
        "volume_24hr": "100.0",
        "liquidity": "500.0"
    }