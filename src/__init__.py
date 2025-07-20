"""Prediction Market Frameworks - Unified Python SDK.

This package provides unified access to multiple prediction market platforms
including Polymarket and Kalshi through a consistent, easy-to-use interface.

Basic Usage:
    >>> # After installation: pip install prediction-market-frameworks
    >>> from prediction_market_frameworks import PolymarketClient  # doctest: +SKIP
    >>> client = PolymarketClient()  # doctest: +SKIP
    >>> events = client.get_active_events()  # doctest: +SKIP

For more advanced usage:
    >>> from prediction_market_frameworks import PolymarketConfig  # doctest: +SKIP
    >>> config = PolymarketConfig.from_env()  # doctest: +SKIP
    >>> client = PolymarketClient(config)  # doctest: +SKIP
"""

# Import main client classes
# Import commonly used exceptions
from .polymarket_client import (
    ClobClient,
    GammaClient,
    PolymarketAPIError,
    PolymarketAuthenticationError,
    PolymarketClient,
    PolymarketConfig,
    PolymarketConfigurationError,
    PolymarketError,
    PolymarketNetworkError,
    PolymarketRateLimitError,
    PolymarketValidationError,
)

# Import data models that users might need
from .polymarket_client.models import (
    Event,
    Market,
    OrderBook,
)

# Package metadata
__version__ = "0.1.0"
__author__ = "Prediction Market Frameworks Team"
__description__ = "Unified Python SDK for prediction market platforms"

# Define what gets imported with "from prediction_market_frameworks import *"
__all__ = [
    # Main client classes
    "PolymarketClient",
    "PolymarketConfig",
    "ClobClient",
    "GammaClient",

    # Core exceptions users need to handle
    "PolymarketError",
    "PolymarketAPIError",
    "PolymarketValidationError",
    "PolymarketConfigurationError",
    "PolymarketRateLimitError",
    "PolymarketAuthenticationError",
    "PolymarketNetworkError",

    # Data models
    "Event",
    "Market",
    "OrderBook",

    # Metadata
    "__version__",
]

# Future: Add Kalshi client when implemented
# from .kalshi_client import KalshiClient
# __all__.append("KalshiClient")
