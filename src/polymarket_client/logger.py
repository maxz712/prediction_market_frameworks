import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=UTC
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from the log record
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "getMessage",
                "message"
            }
        }

        if extra_fields:
            log_entry["extra"] = extra_fields

        return json.dumps(log_entry, default=str)


def setup_logging(
    level: str = "INFO",
    format_type: str = "structured",
    enable_console: bool = True,
    log_file: str | None = None
) -> None:
    """
    Set up structured logging for the polymarket client.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type ('structured' for JSON, 'simple' for human-readable)
        enable_console: Whether to log to console
        log_file: Optional file path to write logs to
    """
    # Get the root logger for the polymarket_client package
    logger = logging.getLogger("polymarket_client")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Choose formatter based on format type
    if format_type == "structured":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Usually __name__ from the calling module

    Returns:
        Logger instance configured for structured logging
    """
    return logging.getLogger(f"polymarket_client.{name}")


def log_api_request(
    logger: logging.Logger,
    method: str,
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    request_id: str | None = None
) -> None:
    """
    Log an API request with structured data.

    Args:
        logger: Logger instance
        method: HTTP method
        url: Request URL
        params: Request parameters
        headers: Request headers (sensitive data will be filtered)
        request_id: Optional request ID for tracing
    """
    # Filter sensitive headers
    safe_headers = {}
    if headers:
        for key, value in headers.items():
            if key.lower() in {"authorization", "x-api-key", "cookie"}:
                safe_headers[key] = "[REDACTED]"
            else:
                safe_headers[key] = value

    logger.info(
        "API request initiated",
        extra={
            "event_type": "api_request",
            "http_method": method,
            "url": url,
            "params": params,
            "headers": safe_headers,
            "request_id": request_id,
        }
    )


def log_api_response(
    logger: logging.Logger,
    method: str,
    url: str,
    status_code: int,
    response_time_ms: float,
    request_id: str | None = None,
    error: str | None = None
) -> None:
    """
    Log an API response with structured data.

    Args:
        logger: Logger instance
        method: HTTP method
        url: Request URL
        status_code: HTTP status code
        response_time_ms: Response time in milliseconds
        request_id: Optional request ID for tracing
        error: Error message if any
    """
    http_error_threshold = 400
    level = logging.ERROR if status_code >= http_error_threshold else logging.INFO
    message = f"API response received - {status_code}"

    logger.log(
        level,
        message,
        extra={
            "event_type": "api_response",
            "http_method": method,
            "url": url,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "request_id": request_id,
            "error": error,
        }
    )


def log_user_action(
    logger: logging.Logger,
    action: str,
    user_id: str | None = None,
    market_id: str | None = None,
    order_id: str | None = None,
    additional_data: dict[str, Any] | None = None
) -> None:
    """
    Log a user action with structured data.

    Args:
        logger: Logger instance
        action: Action performed (e.g., "place_order", "cancel_order", "get_events")
        user_id: User identifier
        market_id: Market/token identifier
        order_id: Order identifier
        additional_data: Additional context data
    """
    extra_data = {
        "event_type": "user_action",
        "action": action,
        "user_id": user_id,
        "market_id": market_id,
        "order_id": order_id,
    }

    if additional_data:
        extra_data.update(additional_data)

    logger.info("User action: %s", action, extra=extra_data)
