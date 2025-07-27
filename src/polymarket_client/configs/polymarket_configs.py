import os

from py_clob_client.clob_types import ApiCreds
from pydantic import BaseModel, Field, field_validator


class PolymarketConfig(BaseModel):
    endpoints: dict[str, str] = Field(
        default={
            "gamma": "https://gamma-api.polymarket.com",
            "clob": "https://clob.polymarket.com",
            "info": "https://strapi-matic.polymarket.com",
            "neg_risk": "https://neg-risk-api.polymarket.com",
            "data_api": "https://data-api.polymarket.com"
        },
        description="API endpoint URLs for Polymarket services"
    )
    chain_id: int = Field(default=137, description="Blockchain chain ID")
    api_key: str = Field(..., description="CLOB API key")
    api_secret: str = Field(..., description="CLOB API secret")
    api_passphrase: str = Field(..., description="CLOB API passphrase")
    pk: str = Field(..., description="Private key for trading operations")
    wallet_proxy_address: str | None = Field(None, description="Wallet proxy address for funder operations (optional)")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")

    # Pagination settings
    default_page_size: int = Field(default=100, description="Default page size for paginated requests")
    max_page_size: int = Field(default=1000, description="Maximum allowed page size")
    max_total_results: int = Field(default=10000, description="Maximum total results to prevent memory issues")

    # Feature flags
    enable_auto_pagination: bool = Field(default=False, description="Automatically paginate through all results")
    enable_response_caching: bool = Field(default=False, description="Enable response caching")
    warn_large_requests: bool = Field(default=True, description="Warn when requesting large datasets")

    # Performance monitoring settings
    enable_performance_logging: bool = Field(default=True, description="Enable performance metrics logging")
    log_memory_usage: bool = Field(default=False, description="Log memory usage statistics")
    performance_log_threshold_ms: float = Field(default=1000.0, description="Log operations slower than this threshold")
    log_level: str = Field(default="INFO", description="Logging level for performance metrics")
    log_format: str = Field(default="structured", description="Log format: 'structured' or 'simple'")
    enable_console_logging: bool = Field(default=True, description="Enable console logging")
    log_file_path: str | None = Field(None, description="File path for log output")

    # Rate limiting settings
    enable_rate_limiting: bool = Field(default=True, description="Enable client-side rate limiting")
    rate_limiter_type: str = Field(default="token_bucket", description="Rate limiter type: 'token_bucket' or 'sliding_window'")
    requests_per_second: float = Field(default=5.0, description="Max requests per second for token bucket rate limiter")
    burst_capacity: int | None = Field(default=None, description="Burst capacity for token bucket (defaults to 2x rate)")
    requests_per_window: int = Field(default=100, description="Max requests per window for sliding window rate limiter")
    window_size_seconds: int = Field(default=60, description="Window size in seconds for sliding window rate limiter")
    rate_limit_per_host: bool = Field(default=True, description="Apply rate limiting per host (vs globally)")
    rate_limit_timeout: float | None = Field(default=30.0, description="Max time to wait for rate limit (None for no timeout)")

    # SDK metadata
    sdk_version: str = Field(default="0.1.0", description="SDK version for User-Agent header")

    @field_validator("api_key", "api_secret", "api_passphrase", "pk")
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            msg = "Required field cannot be empty"
            raise ValueError(msg)
        return v.strip()

    @field_validator("wallet_proxy_address")
    @classmethod
    def validate_proxy_address(cls, v):
        if v is not None and (not v or not v.strip()):
            msg = "Wallet proxy address cannot be empty string"
            raise ValueError(msg)
        return v.strip() if v else None

    @field_validator("endpoints")
    @classmethod
    def validate_endpoints(cls, v):
        required_endpoints = {"gamma", "clob"}
        if not all(endpoint in v for endpoint in required_endpoints):
            msg = f"endpoints must contain keys: {required_endpoints}"
            raise ValueError(msg)
        return v

    @classmethod
    def from_env(cls,
                 api_key_env: str = "POLYMARKET_API_KEY",
                 api_secret_env: str = "POLYMARKET_API_SECRET",
                 api_passphrase_env: str = "POLYMARKET_API_PASSPHRASE",
                 private_key_env: str = "POLYMARKET_PRIVATE_KEY",
                 wallet_proxy_address_env: str = "POLYMARKET_WALLET_PROXY_ADDRESS",
                 chain_id_env: str = "POLYMARKET_CHAIN_ID",
                 timeout_env: str = "POLYMARKET_TIMEOUT",
                 max_retries_env: str = "POLYMARKET_MAX_RETRIES",
                 default_page_size_env: str = "POLYMARKET_DEFAULT_PAGE_SIZE",
                 max_page_size_env: str = "POLYMARKET_MAX_PAGE_SIZE",
                 max_total_results_env: str = "POLYMARKET_MAX_TOTAL_RESULTS",
                 enable_auto_pagination_env: str = "POLYMARKET_ENABLE_AUTO_PAGINATION",
                 enable_response_caching_env: str = "POLYMARKET_ENABLE_RESPONSE_CACHING",
                 warn_large_requests_env: str = "POLYMARKET_WARN_LARGE_REQUESTS",
                 enable_performance_logging_env: str = "POLYMARKET_ENABLE_PERFORMANCE_LOGGING",
                 log_memory_usage_env: str = "POLYMARKET_LOG_MEMORY_USAGE",
                 performance_log_threshold_ms_env: str = "POLYMARKET_PERFORMANCE_LOG_THRESHOLD_MS",
                 log_level_env: str = "POLYMARKET_LOG_LEVEL",
                 log_format_env: str = "POLYMARKET_LOG_FORMAT",
                 enable_console_logging_env: str = "POLYMARKET_ENABLE_CONSOLE_LOGGING",
                 log_file_path_env: str = "POLYMARKET_LOG_FILE_PATH",
                 enable_rate_limiting_env: str = "POLYMARKET_ENABLE_RATE_LIMITING",
                 rate_limiter_type_env: str = "POLYMARKET_RATE_LIMITER_TYPE",
                 requests_per_second_env: str = "POLYMARKET_REQUESTS_PER_SECOND",
                 burst_capacity_env: str = "POLYMARKET_BURST_CAPACITY",
                 requests_per_window_env: str = "POLYMARKET_REQUESTS_PER_WINDOW",
                 window_size_seconds_env: str = "POLYMARKET_WINDOW_SIZE_SECONDS",
                 rate_limit_per_host_env: str = "POLYMARKET_RATE_LIMIT_PER_HOST",
                 rate_limit_timeout_env: str = "POLYMARKET_RATE_LIMIT_TIMEOUT") -> "PolymarketConfig":
        """Create config from environment variables."""
        config_data = {
            "api_key": os.getenv(api_key_env, ""),
            "api_secret": os.getenv(api_secret_env, ""),
            "api_passphrase": os.getenv(api_passphrase_env, ""),
            "pk": os.getenv(private_key_env, ""),
            "wallet_proxy_address": os.getenv(wallet_proxy_address_env)
        }

        # Custom endpoints from environment variables
        endpoints = {}
        if os.getenv("POLYMARKET_GAMMA_URL"):
            endpoints["gamma"] = os.getenv("POLYMARKET_GAMMA_URL")
        if os.getenv("POLYMARKET_CLOB_URL"):
            endpoints["clob"] = os.getenv("POLYMARKET_CLOB_URL")
        if os.getenv("POLYMARKET_INFO_URL"):
            endpoints["info"] = os.getenv("POLYMARKET_INFO_URL")
        if os.getenv("POLYMARKET_NEG_RISK_URL"):
            endpoints["neg_risk"] = os.getenv("POLYMARKET_NEG_RISK_URL")
        if os.getenv("POLYMARKET_DATA_API_URL"):
            endpoints["data_api"] = os.getenv("POLYMARKET_DATA_API_URL")
        if endpoints:
            config_data["endpoints"] = endpoints

        # Optional numeric fields
        chain_id_str = os.getenv(chain_id_env)
        if chain_id_str:
            config_data["chain_id"] = int(chain_id_str)

        timeout_str = os.getenv(timeout_env)
        if timeout_str:
            config_data["timeout"] = int(timeout_str)

        max_retries_str = os.getenv(max_retries_env)
        if max_retries_str:
            config_data["max_retries"] = int(max_retries_str)

        # Additional optional settings
        default_page_size_str = os.getenv(default_page_size_env)
        if default_page_size_str:
            config_data["default_page_size"] = int(default_page_size_str)

        max_page_size_str = os.getenv(max_page_size_env)
        if max_page_size_str:
            config_data["max_page_size"] = int(max_page_size_str)

        max_total_results_str = os.getenv(max_total_results_env)
        if max_total_results_str:
            config_data["max_total_results"] = int(max_total_results_str)

        enable_auto_pagination_str = os.getenv(enable_auto_pagination_env)
        if enable_auto_pagination_str:
            config_data["enable_auto_pagination"] = enable_auto_pagination_str.lower() in ("true", "1", "yes")

        enable_response_caching_str = os.getenv(enable_response_caching_env)
        if enable_response_caching_str:
            config_data["enable_response_caching"] = enable_response_caching_str.lower() in ("true", "1", "yes")

        warn_large_requests_str = os.getenv(warn_large_requests_env)
        if warn_large_requests_str:
            config_data["warn_large_requests"] = warn_large_requests_str.lower() in ("true", "1", "yes")

        # Performance monitoring settings
        enable_performance_logging_str = os.getenv(enable_performance_logging_env)
        if enable_performance_logging_str:
            config_data["enable_performance_logging"] = enable_performance_logging_str.lower() in ("true", "1", "yes")

        log_memory_usage_str = os.getenv(log_memory_usage_env)
        if log_memory_usage_str:
            config_data["log_memory_usage"] = log_memory_usage_str.lower() in ("true", "1", "yes")

        performance_log_threshold_ms_str = os.getenv(performance_log_threshold_ms_env)
        if performance_log_threshold_ms_str:
            config_data["performance_log_threshold_ms"] = float(performance_log_threshold_ms_str)

        log_level_str = os.getenv(log_level_env)
        if log_level_str:
            config_data["log_level"] = log_level_str

        log_format_str = os.getenv(log_format_env)
        if log_format_str:
            config_data["log_format"] = log_format_str

        enable_console_logging_str = os.getenv(enable_console_logging_env)
        if enable_console_logging_str:
            config_data["enable_console_logging"] = enable_console_logging_str.lower() in ("true", "1", "yes")

        log_file_path_str = os.getenv(log_file_path_env)
        if log_file_path_str:
            config_data["log_file_path"] = log_file_path_str

        # Rate limiting settings
        enable_rate_limiting_str = os.getenv(enable_rate_limiting_env)
        if enable_rate_limiting_str:
            config_data["enable_rate_limiting"] = enable_rate_limiting_str.lower() in ("true", "1", "yes")

        rate_limiter_type_str = os.getenv(rate_limiter_type_env)
        if rate_limiter_type_str:
            config_data["rate_limiter_type"] = rate_limiter_type_str

        requests_per_second_str = os.getenv(requests_per_second_env)
        if requests_per_second_str:
            config_data["requests_per_second"] = float(requests_per_second_str)

        burst_capacity_str = os.getenv(burst_capacity_env)
        if burst_capacity_str:
            config_data["burst_capacity"] = int(burst_capacity_str)

        requests_per_window_str = os.getenv(requests_per_window_env)
        if requests_per_window_str:
            config_data["requests_per_window"] = int(requests_per_window_str)

        window_size_seconds_str = os.getenv(window_size_seconds_env)
        if window_size_seconds_str:
            config_data["window_size_seconds"] = int(window_size_seconds_str)

        rate_limit_per_host_str = os.getenv(rate_limit_per_host_env)
        if rate_limit_per_host_str:
            config_data["rate_limit_per_host"] = rate_limit_per_host_str.lower() in ("true", "1", "yes")

        rate_limit_timeout_str = os.getenv(rate_limit_timeout_env)
        if rate_limit_timeout_str:
            if rate_limit_timeout_str.lower() in ("none", "null", ""):
                config_data["rate_limit_timeout"] = None
            else:
                config_data["rate_limit_timeout"] = float(rate_limit_timeout_str)

        return cls(**config_data)

    @property
    def api_creds(self) -> ApiCreds:
        """Create ApiCreds object for py_clob_client."""
        return ApiCreds(
            api_key=self.api_key,
            api_secret=self.api_secret,
            api_passphrase=self.api_passphrase
        )

    def get_endpoint(self, service: str) -> str:
        """Get endpoint URL for a specific service."""
        if service not in self.endpoints:
            msg = f"Service '{service}' not found in endpoints. Available: {list(self.endpoints.keys())}"
            raise ValueError(msg)
        return self.endpoints[service].rstrip("/")

    class Config:
        env_prefix = "POLYMARKET_"
