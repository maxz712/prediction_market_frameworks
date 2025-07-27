"""Polymarket SDK exceptions package.

This package contains all custom exceptions used throughout the Polymarket SDK,
organized by category for better maintainability and clarity.

Exception Hierarchy:
    PolymarketError (base)
    ├── PolymarketConfigurationError
    ├── PolymarketAPIError
    │   ├── PolymarketAuthenticationError
    │   ├── PolymarketAuthorizationError
    │   ├── PolymarketRateLimitError
    │   ├── PolymarketNotFoundError
    │   ├── PolymarketServerError
    │   ├── PolymarketClientError
    │   │   ├── PolymarketBadRequestError
    │   │   └── PolymarketConflictError
    ├── PolymarketValidationError
    │   ├── PolymarketFieldValidationError
    │   ├── PolymarketTypeValidationError
    │   ├── PolymarketRangeValidationError
    │   ├── PolymarketRequiredFieldError
    │   ├── PolymarketFormatValidationError
    │   └── PolymarketBusinessRuleError
    └── PolymarketNetworkError
        ├── PolymarketConnectionError
        ├── PolymarketTimeoutError
        ├── PolymarketSSLError
        ├── PolymarketProxyError
        └── PolymarketDNSError
"""

# Base exceptions
# API-related exceptions
from .api_errors import (
    PolymarketAPIError,
    PolymarketAuthenticationError,
    PolymarketAuthorizationError,
    PolymarketBadRequestError,
    PolymarketClientError,
    PolymarketConflictError,
    PolymarketNotFoundError,
    PolymarketRateLimitError,
    PolymarketServerError,
)
from .base import (
    PolymarketConfigurationError,
    PolymarketError,
)

# Network exceptions
from .network_errors import (
    PolymarketConnectionError,
    PolymarketDNSError,
    PolymarketNetworkError,
    PolymarketProxyError,
    PolymarketSSLError,
    PolymarketTimeoutError,
)

# Validation exceptions
from .validation_errors import (
    PolymarketBusinessRuleError,
    PolymarketFieldValidationError,
    PolymarketFormatValidationError,
    PolymarketRangeValidationError,
    PolymarketRequiredFieldError,
    PolymarketTypeValidationError,
    PolymarketValidationError,
)

# Export all exceptions
__all__ = [
    # API exceptions
    "PolymarketAPIError",
    "PolymarketAuthenticationError",
    "PolymarketAuthorizationError",
    "PolymarketBadRequestError",
    "PolymarketBusinessRuleError",
    "PolymarketClientError",
    "PolymarketConfigurationError",
    "PolymarketConflictError",
    "PolymarketConnectionError",
    "PolymarketDNSError",
    # Base exceptions
    "PolymarketError",
    "PolymarketFieldValidationError",
    "PolymarketFormatValidationError",
    # Network exceptions
    "PolymarketNetworkError",
    "PolymarketNotFoundError",
    "PolymarketProxyError",
    "PolymarketRangeValidationError",
    "PolymarketRateLimitError",
    "PolymarketRequiredFieldError",
    "PolymarketSSLError",
    "PolymarketServerError",
    "PolymarketTimeoutError",
    "PolymarketTypeValidationError",
    # Validation exceptions
    "PolymarketValidationError",
]
