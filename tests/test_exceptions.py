"""Tests for custom exceptions."""

import pytest
from src.polymarket_client.exceptions import (
    PolymarketError,
    PolymarketConfigurationError,
    PolymarketAPIError,
    PolymarketAuthenticationError,
    PolymarketRateLimitError,
    PolymarketNotFoundError,
    PolymarketValidationError,
    PolymarketNetworkError,
)


class TestPolymarketExceptions:
    """Test cases for custom exceptions."""
    
    def test_base_exception(self):
        """Test base PolymarketError."""
        error = PolymarketError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_api_error_basic(self):
        """Test basic PolymarketAPIError."""
        error = PolymarketAPIError("API error")
        assert str(error) == "API error"
        assert error.status_code is None
        assert error.response_data is None
        assert error.request_id is None
    
    def test_api_error_with_details(self):
        """Test PolymarketAPIError with all details."""
        response_data = {"error": "Invalid request", "code": "INVALID_REQUEST"}
        error = PolymarketAPIError(
            "API error",
            status_code=400,
            response_data=response_data,
            request_id="req_123"
        )
        
        assert "API error" in str(error)
        assert "(Status: 400)" in str(error)
        assert "(Request ID: req_123)" in str(error)
        assert error.response_data == response_data
    
    def test_validation_error(self):
        """Test PolymarketValidationError."""
        error = PolymarketValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, PolymarketError)
    
    def test_rate_limit_error(self):
        """Test PolymarketRateLimitError."""
        error = PolymarketRateLimitError(retry_after=60)
        assert "Rate limit exceeded" in str(error)
        assert error.retry_after == 60
        assert isinstance(error, PolymarketAPIError)
    
    def test_authentication_error(self):
        """Test PolymarketAuthenticationError."""
        error = PolymarketAuthenticationError()
        assert "Authentication failed" in str(error)
        assert isinstance(error, PolymarketAPIError)
    
    def test_not_found_error(self):
        """Test PolymarketNotFoundError."""
        error = PolymarketNotFoundError("Market not found")
        assert str(error) == "Market not found"
        assert isinstance(error, PolymarketAPIError)
    
    def test_exception_inheritance(self):
        """Test that all exceptions inherit from PolymarketError."""
        exceptions = [
            PolymarketAPIError("test"),
            PolymarketValidationError("test"),
            PolymarketRateLimitError("test"),
            PolymarketAuthenticationError("test"),
            PolymarketNotFoundError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, PolymarketError)