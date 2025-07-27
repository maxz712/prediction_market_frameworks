"""Pytest configuration and fixtures."""

from unittest.mock import Mock

import pytest

from polymarket_client.configs.polymarket_configs import PolymarketConfig


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return PolymarketConfig(
        api_key="test_api_key",
        api_secret="test_api_secret",
        api_passphrase="test_passphrase",
        pk="0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
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
        "ticker": "TEST",
        "title": "Test Event",
        "description": "A test event",
        "slug": "test-event",
        "startDate": "2024-01-01T00:00:00Z",
        "endDate": "2024-12-31T23:59:59Z",
        "image": "https://example.com/image.png",
        "icon": "https://example.com/icon.png",
        "active": True,
        "closed": False,
        "archived": False,
        "new": False,
        "featured": False,
        "restricted": False,
        "openInterest": "0",
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "enableOrderBook": True,
        "cyom": False,
        "showAllOutcomes": True,
        "showMarketImages": True,
        "enableNegRisk": False,
        "negRiskAugmented": False,
        "pendingDeployment": False,
        "deploying": False,
        "tags": [],
        "markets": []
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing."""
    return {
        "enable_order_book": True,
        "active": True,
        "closed": False,
        "archived": False,
        "accepting_orders": True,
        "accepting_order_timestamp": "2024-01-01T00:00:00Z",
        "minimum_order_size": 1,
        "minimum_tick_size": 0.01,
        "condition_id": "test_condition_id",
        "question_id": "test_question_id",
        "question": "Test question?",
        "description": "Test market description",
        "market_slug": "test-market",
        "end_date_iso": "2024-12-31T23:59:59Z",
        "game_start_time": "2024-01-01T00:00:00Z",
        "seconds_delay": 0,
        "fpmm": "0x1234567890abcdef",
        "maker_base_fee": 1,
        "taker_base_fee": 1,
        "notifications_enabled": True,
        "neg_risk": False,
        "neg_risk_market_id": "",
        "neg_risk_request_id": "",
        "icon": "https://example.com/icon.png",
        "image": "https://example.com/image.png",
        "rewards": {
            "rates": None,
            "min_size": 1,
            "max_spread": 0.1
        },
        "is_50_50_outcome": True,
        "tokens": [
            {
                "token_id": "token1",
                "outcome": "Yes",
                "price": 0.5,
                "winner": False
            },
            {
                "token_id": "token2",
                "outcome": "No",
                "price": 0.5,
                "winner": False
            }
        ],
        "tags": []
    }
