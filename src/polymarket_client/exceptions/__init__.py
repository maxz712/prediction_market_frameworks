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
from .base import (
    PolymarketError,
    PolymarketConfigurationError,
)

# API-related exceptions
from .api_errors import (
    PolymarketAPIError,
    PolymarketAuthenticationError,
    PolymarketAuthorizationError,
    PolymarketRateLimitError,
    PolymarketNotFoundError,
    PolymarketServerError,
    PolymarketClientError,
    PolymarketBadRequestError,
    PolymarketConflictError,
)

# Validation exceptions
from .validation_errors import (
    PolymarketValidationError,
    PolymarketFieldValidationError,
    PolymarketTypeValidationError,
    PolymarketRangeValidationError,
    PolymarketRequiredFieldError,
    PolymarketFormatValidationError,
    PolymarketBusinessRuleError,
)

# Network exceptions
from .network_errors import (
    PolymarketNetworkError,
    PolymarketConnectionError,
    PolymarketTimeoutError,
    PolymarketSSLError,
    PolymarketProxyError,
    PolymarketDNSError,
)

# Export all exceptions
__all__ = [
    # Base exceptions
    "PolymarketError",
    "PolymarketConfigurationError",
    
    # API exceptions
    "PolymarketAPIError",
    "PolymarketAuthenticationError",
    "PolymarketAuthorizationError",
    "PolymarketRateLimitError",
    "PolymarketNotFoundError",
    "PolymarketServerError",
    "PolymarketClientError",
    "PolymarketBadRequestError",
    "PolymarketConflictError",
    
    # Validation exceptions
    "PolymarketValidationError",
    "PolymarketFieldValidationError",
    "PolymarketTypeValidationError",
    "PolymarketRangeValidationError",
    "PolymarketRequiredFieldError",
    "PolymarketFormatValidationError",
    "PolymarketBusinessRuleError",
    
    # Network exceptions
    "PolymarketNetworkError",
    "PolymarketConnectionError",
    "PolymarketTimeoutError",
    "PolymarketSSLError",
    "PolymarketProxyError",
    "PolymarketDNSError",
]