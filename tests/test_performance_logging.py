import json
import logging
import time
from io import StringIO
from unittest.mock import patch

import pytest

from polymarket_client.logger import (
    PerformanceMetrics,
    create_performance_logger,
    log_memory_usage,
    measure_performance,
    setup_logging,
)


class TestPerformanceMetrics:
    """Test the PerformanceMetrics class."""

    def test_record_operation(self, caplog):
        """Test recording individual operations."""
        logger = logging.getLogger("test")
        metrics = PerformanceMetrics(logger)

        with caplog.at_level(logging.INFO):
            metrics.record_operation("test_op", 100.5, True, {"endpoint": "/test"})

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Operation completed: test_op (100.50ms)" in record.getMessage()
        assert record.event_type == "performance_metric"
        assert record.operation == "test_op"
        assert record.duration_ms == 100.5
        assert record.success is True
        assert record.total_count == 1
        assert record.metadata == {"endpoint": "/test"}

    def test_get_operation_stats(self):
        """Test getting operation statistics."""
        logger = logging.getLogger("test")
        metrics = PerformanceMetrics(logger)

        # Record multiple operations
        metrics.record_operation("test_op", 100.0)
        metrics.record_operation("test_op", 200.0)
        metrics.record_operation("test_op", 150.0)

        stats = metrics.get_operation_stats("test_op")
        assert stats is not None
        assert stats["count"] == 3
        assert stats["min_ms"] == 100.0
        assert stats["max_ms"] == 200.0
        assert stats["avg_ms"] == 150.0
        assert stats["total_ms"] == 450.0

    def test_get_operation_stats_nonexistent(self):
        """Test getting stats for nonexistent operation."""
        logger = logging.getLogger("test")
        metrics = PerformanceMetrics(logger)

        stats = metrics.get_operation_stats("nonexistent")
        assert stats is None

    def test_log_operation_summary(self, caplog):
        """Test logging operation summary."""
        logger = logging.getLogger("test")
        metrics = PerformanceMetrics(logger)

        # Record some operations
        metrics.record_operation("test_op", 100.0)
        metrics.record_operation("test_op", 200.0)

        with caplog.at_level(logging.INFO):
            caplog.clear()
            metrics.log_operation_summary("test_op")

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Operation summary: test_op" in record.getMessage()
        assert record.event_type == "operation_summary"
        assert record.operation == "test_op"
        assert record.statistics["count"] == 2

    def test_reset_metrics(self):
        """Test resetting metrics."""
        logger = logging.getLogger("test")
        metrics = PerformanceMetrics(logger)

        # Record some operations
        metrics.record_operation("test_op", 100.0)
        assert metrics.get_operation_stats("test_op") is not None

        # Reset and verify
        metrics.reset_metrics()
        assert metrics.get_operation_stats("test_op") is None


class TestMeasurePerformance:
    """Test the measure_performance context manager."""

    def test_successful_operation(self, caplog):
        """Test measuring a successful operation."""
        logger = logging.getLogger("test")

        with caplog.at_level(logging.INFO):
            with measure_performance(logger, "test_operation", {"test": "data"}):
                time.sleep(0.01)  # Small delay to ensure measurable time

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Operation test_operation:" in record.getMessage()
        assert "(success)" in record.getMessage()
        assert record.event_type == "performance_metric"
        assert record.operation == "test_operation"
        assert record.success is True
        assert record.duration_ms > 0
        assert record.metadata == {"test": "data"}

    def test_failed_operation(self, caplog):
        """Test measuring a failed operation."""
        logger = logging.getLogger("test")

        with caplog.at_level(logging.INFO):
            with pytest.raises(ValueError):
                with measure_performance(logger, "test_operation"):
                    raise ValueError("Test error")

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Operation test_operation:" in record.getMessage()
        assert "(failed)" in record.getMessage()
        assert record.event_type == "performance_metric"
        assert record.operation == "test_operation"
        assert record.success is False
        assert record.duration_ms > 0


class TestMemoryLogging:
    """Test memory usage logging."""

    @patch("polymarket_client.logger.psutil")
    def test_log_memory_usage_success(self, mock_psutil, caplog):
        """Test successful memory logging."""
        # Mock psutil objects
        mock_process = mock_psutil.Process.return_value
        mock_memory_info = mock_process.memory_info.return_value
        mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB
        mock_memory_info.vms = 200 * 1024 * 1024  # 200 MB
        mock_process.cpu_percent.return_value = 25.5

        logger = logging.getLogger("test")

        with caplog.at_level(logging.INFO):
            log_memory_usage(logger, "test_operation", {"context": "test"})

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Memory usage: 100.0 MB RSS, 200.0 MB VMS" in record.getMessage()
        assert record.event_type == "memory_usage"
        assert record.rss_mb == 100.0
        assert record.vms_mb == 200.0
        assert record.cpu_percent == 25.5
        assert record.operation == "test_operation"
        assert record.metadata == {"context": "test"}

    def test_log_memory_usage_no_psutil(self, caplog):
        """Test memory logging when psutil is not available."""
        logger = logging.getLogger("test")

        with patch("polymarket_client.logger.psutil", side_effect=ImportError):
            with caplog.at_level(logging.WARNING):
                log_memory_usage(logger)

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "psutil not available for memory monitoring" in record.getMessage()
        assert record.event_type == "memory_usage_unavailable"


class TestCreatePerformanceLogger:
    """Test the create_performance_logger function."""

    def test_create_performance_logger(self):
        """Test creating a performance logger and metrics."""
        logger, metrics = create_performance_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert isinstance(metrics, PerformanceMetrics)
        assert logger.name == "polymarket_client.test_module"
        assert metrics.logger is logger


class TestSetupLogging:
    """Test the setup_logging function."""

    def test_setup_structured_logging(self):
        """Test setting up structured logging."""
        log_output = StringIO()

        # Setup logging with string output
        setup_logging(level="DEBUG", format_type="structured", enable_console=False)
        logger = logging.getLogger("polymarket_client")

        # Add our test handler
        handler = logging.StreamHandler(log_output)
        from polymarket_client.logger import StructuredFormatter
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

        # Log a test message
        logger.info("Test message", extra={"test_field": "test_value"})

        # Verify structured output
        log_content = log_output.getvalue()
        assert log_content

        # Parse JSON to verify structure
        log_data = json.loads(log_content.strip())
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test message"
        assert log_data["extra"]["test_field"] == "test_value"
        assert "timestamp" in log_data

    def test_setup_simple_logging(self):
        """Test setting up simple logging."""
        log_output = StringIO()

        # Setup simple logging
        setup_logging(level="INFO", format_type="simple", enable_console=False)
        logger = logging.getLogger("polymarket_client")

        # Add our test handler
        handler = logging.StreamHandler(log_output)
        handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logger.addHandler(handler)

        # Log a test message
        logger.info("Test message")

        # Verify simple output format
        log_content = log_output.getvalue().strip()
        assert "INFO - Test message" in log_content
