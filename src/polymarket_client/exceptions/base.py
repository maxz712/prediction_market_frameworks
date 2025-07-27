"""Base exceptions for the Polymarket SDK."""

from typing import Any


class PolymarketError(Exception):
    """Base exception for all Polymarket SDK errors.

    This is the root exception that all other Polymarket SDK exceptions inherit from.
    Use this to catch any error from the SDK.
    """

    def __init__(self, message: str, details: Any | None = None) -> None:
        """Initialize the base exception.

        Args:
            message: Human-readable error message
            details: Optional additional details about the error
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        return self.message


class PolymarketConfigurationError(PolymarketError):
    """Exception raised for configuration-related errors.

    This includes issues with:
    - Missing required configuration values
    - Invalid configuration formats
    - Environment variable issues
    """

    def __init__(self, message: str = "Configuration error", **kwargs) -> None:
        super().__init__(message, **kwargs)
