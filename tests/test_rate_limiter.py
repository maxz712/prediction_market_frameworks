from unittest.mock import Mock, patch

import pytest
import requests

from polymarket_client.rate_limiter import (
    RateLimitedHTTPAdapter,
    RateLimitError,
    SlidingWindowRateLimiter,
    TokenBucketRateLimiter,
    create_rate_limited_session,
)


class TestTokenBucketRateLimiter:
    """Test token bucket rate limiter implementation."""

    def test_initialization(self):
        """Test rate limiter initialization with default values."""
        limiter = TokenBucketRateLimiter(requests_per_second=2.0)
        assert limiter.rate == 2.0
        assert limiter.burst_capacity == 4  # 2x rate by default
        assert limiter.per_host is True

    def test_initialization_with_custom_burst(self):
        """Test rate limiter initialization with custom burst capacity."""
        limiter = TokenBucketRateLimiter(requests_per_second=5.0, burst_capacity=20)
        assert limiter.rate == 5.0
        assert limiter.burst_capacity == 20

    def test_can_proceed_initial_burst(self):
        """Test that initial burst requests can proceed."""
        limiter = TokenBucketRateLimiter(requests_per_second=1.0, burst_capacity=3)

        # Should allow initial burst
        assert limiter.can_proceed("http://example.com") is True
        assert limiter.can_proceed("http://example.com") is True
        assert limiter.can_proceed("http://example.com") is True

        # Should deny after burst is exhausted
        assert limiter.can_proceed("http://example.com") is False

    def test_per_host_buckets(self):
        """Test that per-host rate limiting works correctly."""
        limiter = TokenBucketRateLimiter(
            requests_per_second=1.0, burst_capacity=2, per_host=True
        )

        # Different hosts should have separate buckets
        assert limiter.can_proceed("http://example1.com") is True
        assert limiter.can_proceed("http://example1.com") is True
        assert limiter.can_proceed("http://example2.com") is True
        assert limiter.can_proceed("http://example2.com") is True

        # Both hosts should be exhausted now
        assert limiter.can_proceed("http://example1.com") is False
        assert limiter.can_proceed("http://example2.com") is False

    def test_global_bucket(self):
        """Test that global rate limiting works correctly."""
        limiter = TokenBucketRateLimiter(
            requests_per_second=1.0, burst_capacity=2, per_host=False
        )

        # All requests should share the same bucket
        assert limiter.can_proceed("http://example1.com") is True
        assert limiter.can_proceed("http://example2.com") is True

        # Both hosts should be affected by global limit
        assert limiter.can_proceed("http://example1.com") is False
        assert limiter.can_proceed("http://example2.com") is False

    def test_wait_if_needed_timeout(self):
        """Test that timeout is respected when waiting."""
        limiter = TokenBucketRateLimiter(requests_per_second=1.0, burst_capacity=1)

        # Exhaust the bucket
        limiter.can_proceed("http://example.com")

        # Should timeout quickly
        with pytest.raises(RateLimitError) as exc_info:
            limiter.wait_if_needed("http://example.com", timeout=0.1)

        assert exc_info.value.retry_after is not None


class TestSlidingWindowRateLimiter:
    """Test sliding window rate limiter implementation."""

    def test_initialization(self):
        """Test rate limiter initialization."""
        limiter = SlidingWindowRateLimiter(
            requests_per_window=10, window_size_seconds=60
        )
        assert limiter.limit == 10
        assert limiter.window_size == 60
        assert limiter.per_host is True

    def test_can_proceed_within_limit(self):
        """Test that requests within limit can proceed."""
        limiter = SlidingWindowRateLimiter(
            requests_per_window=3, window_size_seconds=60
        )

        # Should allow requests within limit
        assert limiter.can_proceed("http://example.com") is True
        assert limiter.can_proceed("http://example.com") is True
        assert limiter.can_proceed("http://example.com") is True

        # Should deny after limit is reached
        assert limiter.can_proceed("http://example.com") is False

    def test_per_host_windows(self):
        """Test that per-host rate limiting works correctly."""
        limiter = SlidingWindowRateLimiter(
            requests_per_window=2, window_size_seconds=60, per_host=True
        )

        # Different hosts should have separate windows
        assert limiter.can_proceed("http://example1.com") is True
        assert limiter.can_proceed("http://example1.com") is True
        assert limiter.can_proceed("http://example2.com") is True
        assert limiter.can_proceed("http://example2.com") is True

        # Both hosts should be at limit now
        assert limiter.can_proceed("http://example1.com") is False
        assert limiter.can_proceed("http://example2.com") is False


class TestRateLimitedHTTPAdapter:
    """Test rate limited HTTP adapter."""

    def test_initialization(self):
        """Test adapter initialization."""
        limiter = TokenBucketRateLimiter(requests_per_second=5.0)
        adapter = RateLimitedHTTPAdapter(rate_limiter=limiter)
        assert adapter.rate_limiter is limiter

    def test_initialization_with_defaults(self):
        """Test adapter initialization with default rate limiter."""
        adapter = RateLimitedHTTPAdapter()
        assert adapter.rate_limiter is not None
        assert isinstance(adapter.rate_limiter, TokenBucketRateLimiter)

    @patch("requests.adapters.HTTPAdapter.send")
    def test_send_with_rate_limiting(self, mock_super_send):
        """Test that send method applies rate limiting."""
        limiter = Mock()
        limiter.wait_if_needed = Mock()
        adapter = RateLimitedHTTPAdapter(rate_limiter=limiter)

        # Mock request and response
        request = Mock()
        request.url = "http://example.com"
        mock_response = Mock()
        mock_super_send.return_value = mock_response

        # Send request
        response = adapter.send(request)

        # Verify rate limiting was applied
        limiter.wait_if_needed.assert_called_once_with(
            "http://example.com", timeout=30.0
        )
        mock_super_send.assert_called_once()
        assert response is mock_response

    @patch("requests.adapters.HTTPAdapter.send")
    def test_send_rate_limit_error_conversion(self, mock_super_send):
        """Test that RateLimitError is converted to Timeout."""
        limiter = Mock()
        limiter.wait_if_needed = Mock(side_effect=RateLimitError("Rate limited"))
        adapter = RateLimitedHTTPAdapter(rate_limiter=limiter)

        request = Mock()
        request.url = "http://example.com"

        # Should convert RateLimitError to Timeout
        with pytest.raises(requests.exceptions.Timeout):
            adapter.send(request)


class TestCreateRateLimitedSession:
    """Test session creation function."""

    def test_create_token_bucket_session(self):
        """Test creating session with token bucket rate limiter."""
        session = create_rate_limited_session(
            rate_limiter_type="token_bucket",
            requests_per_second=10.0,
            burst_capacity=20,
        )

        assert isinstance(session, requests.Session)
        # Check that rate limited adapters are mounted
        http_adapter = session.get_adapter("http://example.com")
        https_adapter = session.get_adapter("https://example.com")
        assert isinstance(http_adapter, RateLimitedHTTPAdapter)
        assert isinstance(https_adapter, RateLimitedHTTPAdapter)

    def test_create_sliding_window_session(self):
        """Test creating session with sliding window rate limiter."""
        session = create_rate_limited_session(
            rate_limiter_type="sliding_window",
            requests_per_window=100,
            window_size_seconds=60,
        )

        assert isinstance(session, requests.Session)
        # Check that rate limited adapters are mounted
        http_adapter = session.get_adapter("http://example.com")
        https_adapter = session.get_adapter("https://example.com")
        assert isinstance(http_adapter, RateLimitedHTTPAdapter)
        assert isinstance(https_adapter, RateLimitedHTTPAdapter)

    def test_create_session_with_custom_timeout(self):
        """Test creating session with custom rate limit timeout."""
        session = create_rate_limited_session(timeout_on_rate_limit=60.0)

        adapter = session.get_adapter("https://example.com")
        assert adapter.timeout_on_rate_limit == 60.0


class TestRateLimitError:
    """Test rate limit error exception."""

    def test_initialization(self):
        """Test error initialization."""
        error = RateLimitError("Rate limited", retry_after=30.0)
        assert str(error) == "Rate limited"
        assert error.retry_after == 30.0

    def test_initialization_without_retry_after(self):
        """Test error initialization without retry_after."""
        error = RateLimitError("Rate limited")
        assert str(error) == "Rate limited"
        assert error.retry_after is None
