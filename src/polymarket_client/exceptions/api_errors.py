"""API-related exceptions for the Polymarket SDK."""

from typing import Any

from .base import PolymarketError


class PolymarketAPIError(PolymarketError):
    """Base exception for API-related errors.

    This is raised when there are issues with API communication,
    including HTTP errors, authentication issues, and server errors.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        request_id: str | None = None,
        endpoint: str | None = None,
    ) -> None:
        """Initialize the API error.

        Args:
            message: Human-readable error message
            status_code: HTTP status code if available
            response_data: Raw response data from the API
            request_id: Unique request identifier for debugging
            endpoint: API endpoint that caused the error
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
        self.request_id = request_id
        self.endpoint = endpoint

    def __str__(self) -> str:
        error_msg = super().__str__()
        if self.status_code:
            error_msg += f" (Status: {self.status_code})"
        if self.endpoint:
            error_msg += f" (Endpoint: {self.endpoint})"
        if self.request_id:
            error_msg += f" (Request ID: {self.request_id})"
        return error_msg


class PolymarketAuthenticationError(PolymarketAPIError):
    """Exception raised for authentication failures.

    This includes:
    - Invalid API credentials
    - Expired tokens
    - Insufficient permissions
    """

    def __init__(self, message: str = "Authentication failed", **kwargs) -> None:
        super().__init__(message, **kwargs)


class PolymarketAuthorizationError(PolymarketAPIError):
    """Exception raised for authorization failures.

    This is raised when the user is authenticated but doesn't have
    permission to access a specific resource or perform an action.
    """

    def __init__(self, message: str = "Access denied", **kwargs) -> None:
        super().__init__(message, **kwargs)


class PolymarketRateLimitError(PolymarketAPIError):
    """Exception raised when rate limit is exceeded.

    This includes information about when the client can retry.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        **kwargs,
    ) -> None:
        """Initialize the rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            **kwargs: Additional API error parameters
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

    def __str__(self) -> str:
        error_msg = super().__str__()
        if self.retry_after:
            error_msg += f" (Retry after: {self.retry_after}s)"
        return error_msg


class PolymarketNotFoundError(PolymarketAPIError):
    """Exception raised when a resource is not found.

    This includes:
    - Market not found
    - Order not found
    - Event not found
    """

    def __init__(self, message: str = "Resource not found", **kwargs) -> None:
        super().__init__(message, **kwargs)


class PolymarketServerError(PolymarketAPIError):
    """Exception raised for server errors (5xx status codes).

    This indicates an issue on Polymarket's side that should be retried.
    """

    def __init__(self, message: str = "Internal server error", **kwargs) -> None:
        super().__init__(message, **kwargs)


class PolymarketClientError(PolymarketAPIError):
    """Exception raised for client errors (4xx status codes).

    This indicates an issue with the request that shouldn't be retried
    without modification.
    """

    def __init__(self, message: str = "Client error", **kwargs) -> None:
        super().__init__(message, **kwargs)


class PolymarketBadRequestError(PolymarketClientError):
    """Exception raised for malformed requests (400 status code)."""

    def __init__(self, message: str = "Bad request", **kwargs) -> None:
        super().__init__(message, **kwargs)


class PolymarketConflictError(PolymarketClientError):
    """Exception raised for conflict errors (409 status code).

    This typically indicates a business logic violation, such as
    trying to create a duplicate resource.
    """

    def __init__(self, message: str = "Conflict", **kwargs) -> None:
        super().__init__(message, **kwargs)
