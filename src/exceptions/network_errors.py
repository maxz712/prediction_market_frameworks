"""Network-related exceptions for the Polymarket SDK."""


from .base import PolymarketError


class PolymarketNetworkError(PolymarketError):
    """Base exception for network-related errors.
    
    This is raised when there are issues with network connectivity,
    timeouts, or other transport-level problems.
    """

    def __init__(
        self,
        message: str = "Network error occurred",
        original_error: Exception | None = None,
        endpoint: str | None = None
    ) -> None:
        """Initialize the network error.
        
        Args:
            message: Human-readable error message
            original_error: The underlying network exception
            endpoint: The endpoint that was being accessed
        """
        super().__init__(message)
        self.original_error = original_error
        self.endpoint = endpoint

    def __str__(self) -> str:
        error_msg = super().__str__()
        if self.endpoint:
            error_msg += f" (Endpoint: {self.endpoint})"
        if self.original_error:
            error_msg += f" (Cause: {self.original_error})"
        return error_msg


class PolymarketConnectionError(PolymarketNetworkError):
    """Exception raised when connection to the API fails.
    
    This includes:
    - DNS resolution failures
    - Connection refused
    - SSL/TLS handshake failures
    """

    def __init__(self, message: str = "Failed to connect to API", **kwargs) -> None:
        super().__init__(message, **kwargs)


class PolymarketTimeoutError(PolymarketNetworkError):
    """Exception raised when a request times out.
    
    This includes:
    - Connection timeouts
    - Read timeouts
    - Request timeouts
    """

    def __init__(
        self,
        message: str = "Request timed out",
        timeout_duration: float | None = None,
        **kwargs
    ) -> None:
        """Initialize the timeout error.
        
        Args:
            message: Error message
            timeout_duration: The timeout duration in seconds
            **kwargs: Additional network error parameters
        """
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration

    def __str__(self) -> str:
        error_msg = super().__str__()
        if self.timeout_duration:
            error_msg += f" (Timeout: {self.timeout_duration}s)"
        return error_msg


class PolymarketSSLError(PolymarketNetworkError):
    """Exception raised for SSL/TLS-related errors.
    
    This includes:
    - Certificate verification failures
    - SSL handshake errors
    - Protocol mismatches
    """

    def __init__(self, message: str = "SSL/TLS error", **kwargs) -> None:
        super().__init__(message, **kwargs)


class PolymarketProxyError(PolymarketNetworkError):
    """Exception raised for proxy-related errors.
    
    This includes:
    - Proxy authentication failures
    - Proxy connection errors
    - Proxy configuration issues
    """

    def __init__(self, message: str = "Proxy error", **kwargs) -> None:
        super().__init__(message, **kwargs)


class PolymarketDNSError(PolymarketNetworkError):
    """Exception raised for DNS resolution errors.
    
    This includes:
    - Host not found
    - DNS server failures
    - DNS timeout errors
    """

    def __init__(self, message: str = "DNS resolution failed", **kwargs) -> None:
        super().__init__(message, **kwargs)
