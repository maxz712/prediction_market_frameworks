import threading
import time
from collections import defaultdict, deque
from typing import Any
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter


class RateLimitError(Exception):
    """Raised when rate limit is exceeded and request cannot be made."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter implementation.

    This implementation allows burst capacity while maintaining a sustained rate limit.
    Each endpoint/host can have its own bucket.
    """

    def __init__(
        self,
        requests_per_second: float = 5.0,
        burst_capacity: int | None = None,
        per_host: bool = True,
    ) -> None:
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum sustained requests per second
            burst_capacity: Maximum burst requests (defaults to 2x rate if None)
            per_host: Whether to apply rate limiting per host or globally
        """
        self.rate = requests_per_second
        self.burst_capacity = burst_capacity or int(requests_per_second * 2)
        self.per_host = per_host
        self._buckets: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "tokens": self.burst_capacity,
                "last_update": time.time(),
                "lock": threading.Lock(),
            }
        )
        self._global_bucket = {
            "tokens": self.burst_capacity,
            "last_update": time.time(),
            "lock": threading.Lock(),
        }

    def _get_bucket_key(self, url: str) -> str:
        """Extract bucket key from URL."""
        if self.per_host:
            try:
                return urlparse(url).netloc
            except Exception:
                return "global"
        return "global"

    def _get_bucket(self, bucket_key: str) -> dict[str, Any]:
        """Get the appropriate bucket for the request."""
        if bucket_key == "global" and not self.per_host:
            return self._global_bucket
        return self._buckets[bucket_key]

    def _refill_tokens(self, bucket: dict[str, Any]) -> None:
        """Refill tokens in bucket based on elapsed time."""
        now = time.time()
        elapsed = now - bucket["last_update"]
        tokens_to_add = elapsed * self.rate
        bucket["tokens"] = min(self.burst_capacity, bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now

    def can_proceed(self, url: str) -> bool:
        """Check if request can proceed without blocking."""
        bucket_key = self._get_bucket_key(url)
        bucket = self._get_bucket(bucket_key)

        with bucket["lock"]:
            self._refill_tokens(bucket)
            return bucket["tokens"] >= 1.0

    def wait_if_needed(self, url: str, timeout: float | None = None) -> None:
        """
        Wait until request can proceed or timeout is reached.

        Args:
            url: URL for the request
            timeout: Maximum time to wait (None for no timeout)

        Raises:
            RateLimitError: If timeout is reached while waiting
        """
        bucket_key = self._get_bucket_key(url)
        bucket = self._get_bucket(bucket_key)

        start_time = time.time()

        while True:
            with bucket["lock"]:
                self._refill_tokens(bucket)

                if bucket["tokens"] >= 1.0:
                    bucket["tokens"] -= 1.0
                    return

                # Calculate wait time for next token
                wait_time = (1.0 - bucket["tokens"]) / self.rate

            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed + wait_time > timeout:
                    msg = f"Rate limit timeout exceeded for {bucket_key}"
                    raise RateLimitError(msg, retry_after=wait_time)

            # Sleep for a small fraction of the wait time for more frequent checks
            time.sleep(min(wait_time, 0.1))


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter implementation.

    Tracks requests in a sliding time window and enforces limits.
    More accurate than token bucket for precise rate limiting.
    """

    def __init__(
        self,
        requests_per_window: int = 100,
        window_size_seconds: int = 60,
        per_host: bool = True,
    ) -> None:
        """
        Initialize sliding window rate limiter.

        Args:
            requests_per_window: Maximum requests per time window
            window_size_seconds: Size of the sliding window in seconds
            per_host: Whether to apply rate limiting per host or globally
        """
        self.limit = requests_per_window
        self.window_size = window_size_seconds
        self.per_host = per_host
        self._windows: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"requests": deque(), "lock": threading.Lock()}
        )
        self._global_window = {"requests": deque(), "lock": threading.Lock()}

    def _get_bucket_key(self, url: str) -> str:
        """Extract bucket key from URL."""
        if self.per_host:
            try:
                return urlparse(url).netloc
            except Exception:
                return "global"
        return "global"

    def _get_window(self, bucket_key: str) -> dict[str, Any]:
        """Get the appropriate window for the request."""
        if bucket_key == "global" and not self.per_host:
            return self._global_window
        return self._windows[bucket_key]

    def _cleanup_old_requests(self, window: dict[str, Any]) -> None:
        """Remove requests outside the current window."""
        now = time.time()
        cutoff = now - self.window_size

        while window["requests"] and window["requests"][0] < cutoff:
            window["requests"].popleft()

    def can_proceed(self, url: str) -> bool:
        """Check if request can proceed without blocking."""
        bucket_key = self._get_bucket_key(url)
        window = self._get_window(bucket_key)

        with window["lock"]:
            self._cleanup_old_requests(window)
            return len(window["requests"]) < self.limit

    def wait_if_needed(self, url: str, timeout: float | None = None) -> None:
        """
        Wait until request can proceed or timeout is reached.

        Args:
            url: URL for the request
            timeout: Maximum time to wait (None for no timeout)

        Raises:
            RateLimitError: If timeout is reached while waiting
        """
        bucket_key = self._get_bucket_key(url)
        window = self._get_window(bucket_key)

        start_time = time.time()

        while True:
            with window["lock"]:
                self._cleanup_old_requests(window)

                if len(window["requests"]) < self.limit:
                    window["requests"].append(time.time())
                    return

                # Calculate wait time until oldest request expires
                oldest_request = window["requests"][0]
                wait_time = oldest_request + self.window_size - time.time()

            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed + wait_time > timeout:
                    msg = f"Rate limit timeout exceeded for {bucket_key}"
                    raise RateLimitError(msg, retry_after=wait_time)

            # Sleep for a reasonable interval
            time.sleep(min(wait_time, 1.0))


class RateLimitedHTTPAdapter(HTTPAdapter):
    """
    HTTP adapter that applies rate limiting to all requests.

    Integrates with requests library session to provide transparent rate limiting.
    """

    def __init__(
        self,
        rate_limiter: Any | None = None,
        timeout_on_rate_limit: float | None = 30.0,
        **kwargs,
    ) -> None:
        """
        Initialize rate limited HTTP adapter.

        Args:
            rate_limiter: Rate limiter instance (TokenBucket or SlidingWindow)
            timeout_on_rate_limit: Max time to wait for rate limit (None for no timeout)
            **kwargs: Additional arguments passed to HTTPAdapter
        """
        super().__init__(**kwargs)
        self.rate_limiter = rate_limiter or TokenBucketRateLimiter()
        self.timeout_on_rate_limit = timeout_on_rate_limit

    def send(self, request, **kwargs) -> requests.Response:
        """Send request with rate limiting applied."""
        if self.rate_limiter:
            try:
                self.rate_limiter.wait_if_needed(
                    request.url, timeout=self.timeout_on_rate_limit
                )
            except RateLimitError as e:
                # Convert to requests timeout error for consistency
                msg = f"Rate limit exceeded: {e}"
                raise requests.exceptions.Timeout(msg) from e

        return super().send(request, **kwargs)


def create_rate_limited_session(
    rate_limiter_type: str = "token_bucket",
    requests_per_second: float = 5.0,
    burst_capacity: int | None = None,
    requests_per_window: int = 100,
    window_size_seconds: int = 60,
    per_host: bool = True,
    timeout_on_rate_limit: float | None = 30.0,
    **session_kwargs,
) -> requests.Session:
    """
    Create a requests session with rate limiting enabled.

    Args:
        rate_limiter_type: "token_bucket" or "sliding_window"
        requests_per_second: Rate limit for token bucket (ignored for sliding window)
        burst_capacity: Burst capacity for token bucket (ignored for sliding window)
        requests_per_window: Max requests per window for sliding window
            (ignored for token bucket)
        window_size_seconds: Window size for sliding window (ignored for token bucket)
        per_host: Whether to apply rate limiting per host
        timeout_on_rate_limit: Max time to wait for rate limit
        **session_kwargs: Additional session configuration

    Returns:
        requests.Session with rate limiting enabled
    """
    session = requests.Session()

    # Create appropriate rate limiter
    if rate_limiter_type == "sliding_window":
        rate_limiter = SlidingWindowRateLimiter(
            requests_per_window=requests_per_window,
            window_size_seconds=window_size_seconds,
            per_host=per_host,
        )
    else:  # default to token_bucket
        rate_limiter = TokenBucketRateLimiter(
            requests_per_second=requests_per_second,
            burst_capacity=burst_capacity,
            per_host=per_host,
        )

    # Create rate limited adapter
    adapter = RateLimitedHTTPAdapter(
        rate_limiter=rate_limiter,
        timeout_on_rate_limit=timeout_on_rate_limit,
        **session_kwargs,
    )

    # Mount adapter for both HTTP and HTTPS
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session
