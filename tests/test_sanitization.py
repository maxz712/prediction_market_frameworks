"""Tests for input sanitization utilities."""

import pytest

from polymarket_client.sanitization import InputSanitizer


class TestInputSanitizer:
    """Test the InputSanitizer class."""

    def test_sanitize_hex_address_valid(self):
        """Test sanitizing valid hex addresses."""
        valid_addresses = [
            "0x1234567890abcdef1234567890abcdef12345678",
            "0xABCDEF1234567890ABCDEF1234567890ABCDEF12",
            "0xabcdef1234567890abcdef1234567890abcdef12",
        ]

        for address in valid_addresses:
            result = InputSanitizer.sanitize_hex_address(address)
            assert result == address.lower()

    def test_sanitize_hex_address_with_whitespace(self):
        """Test sanitizing addresses with whitespace."""
        address = "  0x1234567890abcdef1234567890abcdef12345678  "
        result = InputSanitizer.sanitize_hex_address(address)
        assert result == "0x1234567890abcdef1234567890abcdef12345678"

    def test_sanitize_hex_address_none(self):
        """Test sanitizing None address."""
        result = InputSanitizer.sanitize_hex_address(None)
        assert result is None

    def test_sanitize_hex_address_empty_string(self):
        """Test sanitizing empty string address."""
        result = InputSanitizer.sanitize_hex_address("")
        assert result is None

        result = InputSanitizer.sanitize_hex_address("   ")
        assert result is None

    def test_sanitize_hex_address_invalid_type(self):
        """Test sanitizing non-string address."""
        with pytest.raises(TypeError, match="Address must be a string"):
            InputSanitizer.sanitize_hex_address(123)

    def test_sanitize_hex_address_invalid_format(self):
        """Test sanitizing invalid address formats."""
        invalid_addresses = [
            "0x123",  # Too short
            "1234567890abcdef1234567890abcdef12345678",  # Missing 0x
            "0x1234567890abcdef1234567890abcdef1234567g",  # Invalid char
            "0x1234567890abcdef1234567890abcdef123456789",  # Too long
        ]

        for address in invalid_addresses:
            with pytest.raises(ValueError, match="Invalid Ethereum address format"):
                InputSanitizer.sanitize_hex_address(address)

    def test_sanitize_token_id_hex_format(self):
        """Test sanitizing token IDs in hex format."""
        token_ids = [
            "0x123abc",
            "0xABCDEF",
            "0x1234567890abcdef",
        ]

        for token_id in token_ids:
            result = InputSanitizer.sanitize_token_id(token_id)
            assert result == token_id.lower()

    def test_sanitize_token_id_decimal_format(self):
        """Test sanitizing token IDs in decimal format."""
        result = InputSanitizer.sanitize_token_id("123")
        assert result == "0x7b"

        result = InputSanitizer.sanitize_token_id("255")
        assert result == "0xff"

    def test_sanitize_token_id_none(self):
        """Test sanitizing None token ID."""
        result = InputSanitizer.sanitize_token_id(None)
        assert result is None

    def test_sanitize_token_id_empty_string(self):
        """Test sanitizing empty string token ID."""
        result = InputSanitizer.sanitize_token_id("")
        assert result is None

        result = InputSanitizer.sanitize_token_id("   ")
        assert result is None

    def test_sanitize_token_id_invalid_type(self):
        """Test sanitizing non-string token ID."""
        with pytest.raises(TypeError, match="Token ID must be a string"):
            InputSanitizer.sanitize_token_id(123)

    def test_sanitize_token_id_invalid_format(self):
        """Test sanitizing invalid token ID formats."""
        invalid_token_ids = [
            "abc",  # Not hex, not decimal
            "0x",  # Empty hex
            "123abc",  # Mixed format
        ]

        for token_id in invalid_token_ids:
            with pytest.raises(ValueError, match="Invalid token ID format"):
                InputSanitizer.sanitize_token_id(token_id)

    def test_sanitize_order_id_valid(self):
        """Test sanitizing valid order IDs."""
        valid_order_ids = [
            "order-123",
            "ORDER_456",
            "order789",
            "123-456-789",
        ]

        for order_id in valid_order_ids:
            result = InputSanitizer.sanitize_order_id(order_id)
            assert result == order_id

    def test_sanitize_order_id_none(self):
        """Test sanitizing None order ID."""
        result = InputSanitizer.sanitize_order_id(None)
        assert result is None

    def test_sanitize_order_id_empty_string(self):
        """Test sanitizing empty string order ID."""
        result = InputSanitizer.sanitize_order_id("")
        assert result is None

    def test_sanitize_order_id_invalid_type(self):
        """Test sanitizing non-string order ID."""
        with pytest.raises(TypeError, match="Order ID must be a string"):
            InputSanitizer.sanitize_order_id(123)

    def test_sanitize_order_id_invalid_format(self):
        """Test sanitizing invalid order ID formats."""
        invalid_order_ids = [
            "order@123",  # Invalid character
            "order 123",  # Space
            "order#123",  # Hash
        ]

        for order_id in invalid_order_ids:
            with pytest.raises(ValueError, match="Invalid order ID format"):
                InputSanitizer.sanitize_order_id(order_id)

    def test_sanitize_slug_valid(self):
        """Test sanitizing valid slugs."""
        valid_slugs = [
            "my-event",
            "EVENT_123",
            "event123",
            "test-event-name",
        ]

        for slug in valid_slugs:
            result = InputSanitizer.sanitize_slug(slug)
            assert result == slug.lower()

    def test_sanitize_slug_none(self):
        """Test sanitizing None slug."""
        result = InputSanitizer.sanitize_slug(None)
        assert result is None

    def test_sanitize_slug_empty_string(self):
        """Test sanitizing empty string slug."""
        result = InputSanitizer.sanitize_slug("")
        assert result is None

    def test_sanitize_slug_invalid_type(self):
        """Test sanitizing non-string slug."""
        with pytest.raises(TypeError, match="Slug must be a string"):
            InputSanitizer.sanitize_slug(123)

    def test_sanitize_slug_invalid_format(self):
        """Test sanitizing invalid slug formats."""
        invalid_slugs = [
            "slug with spaces",
            "slug@123",
            "slug.test",
        ]

        for slug in invalid_slugs:
            with pytest.raises(ValueError, match="Invalid slug format"):
                InputSanitizer.sanitize_slug(slug)

    def test_sanitize_slug_list_string_input(self):
        """Test sanitizing slug list with string input."""
        result = InputSanitizer.sanitize_slug_list("test-slug")
        assert result == ["test-slug"]

    def test_sanitize_slug_list_list_input(self):
        """Test sanitizing slug list with list input."""
        slugs = ["test-slug1", "TEST_SLUG2", "slug3"]
        result = InputSanitizer.sanitize_slug_list(slugs)
        assert result == ["test-slug1", "test_slug2", "slug3"]

    def test_sanitize_slug_list_none(self):
        """Test sanitizing None slug list."""
        result = InputSanitizer.sanitize_slug_list(None)
        assert result is None

    def test_sanitize_slug_list_empty_string(self):
        """Test sanitizing empty string slug list."""
        result = InputSanitizer.sanitize_slug_list("")
        assert result is None

    def test_sanitize_slug_list_invalid_type(self):
        """Test sanitizing invalid type slug list."""
        with pytest.raises(
            TypeError, match="Slugs must be a string or list of strings"
        ):
            InputSanitizer.sanitize_slug_list(123)

    def test_sanitize_slug_list_with_invalid_slug(self):
        """Test sanitizing slug list with invalid slug."""
        with pytest.raises(ValueError, match="Invalid slug format"):
            InputSanitizer.sanitize_slug_list(["valid-slug", "invalid slug"])

    def test_sanitize_iso_date_valid(self):
        """Test sanitizing valid ISO dates."""
        valid_dates = [
            "2024-01-01T00:00:00Z",
            "2024-12-31T23:59:59.999Z",
            "2024-06-15T12:30:45",
        ]

        for date_str in valid_dates:
            result = InputSanitizer.sanitize_iso_date(date_str)
            assert result == date_str

    def test_sanitize_iso_date_none(self):
        """Test sanitizing None ISO date."""
        result = InputSanitizer.sanitize_iso_date(None)
        assert result is None

    def test_sanitize_iso_date_empty_string(self):
        """Test sanitizing empty string ISO date."""
        result = InputSanitizer.sanitize_iso_date("")
        assert result is None

    def test_sanitize_iso_date_invalid_type(self):
        """Test sanitizing non-string ISO date."""
        with pytest.raises(TypeError, match="Date must be a string"):
            InputSanitizer.sanitize_iso_date(123)

    def test_sanitize_iso_date_invalid_format(self):
        """Test sanitizing invalid ISO date formats."""
        invalid_dates = [
            "2024-01-01",  # Missing time
            "01/01/2024",  # Wrong format
            "not-a-date",
        ]

        for date_str in invalid_dates:
            with pytest.raises(ValueError, match="Invalid ISO date format"):
                InputSanitizer.sanitize_iso_date(date_str)

    def test_sanitize_iso_date_edge_cases(self):
        """Test sanitizing ISO date edge cases that pass regex but may be invalid."""
        # Note: The current regex allows some technically invalid dates
        # like month 13, but this is by design for the simple pattern matching
        edge_case = "2024-13-01T00:00:00Z"
        result = InputSanitizer.sanitize_iso_date(edge_case)
        assert result == edge_case  # The regex allows this format

    def test_sanitize_numeric_range_valid(self):
        """Test sanitizing valid numeric values."""
        assert InputSanitizer.sanitize_numeric_range(5) == 5
        assert InputSanitizer.sanitize_numeric_range(5.5) == 5.5
        assert InputSanitizer.sanitize_numeric_range(0) == 0

    def test_sanitize_numeric_range_with_limits(self):
        """Test sanitizing numeric values with range limits."""
        result = InputSanitizer.sanitize_numeric_range(5, min_val=1, max_val=10)
        assert result == 5

    def test_sanitize_numeric_range_none(self):
        """Test sanitizing None numeric value."""
        result = InputSanitizer.sanitize_numeric_range(None)
        assert result is None

    def test_sanitize_numeric_range_invalid_type(self):
        """Test sanitizing non-numeric value."""
        with pytest.raises(TypeError, match="Value must be numeric"):
            InputSanitizer.sanitize_numeric_range("123")

    def test_sanitize_numeric_range_below_minimum(self):
        """Test sanitizing value below minimum."""
        with pytest.raises(ValueError, match="Value 0 is below minimum 1"):
            InputSanitizer.sanitize_numeric_range(0, min_val=1)

    def test_sanitize_numeric_range_above_maximum(self):
        """Test sanitizing value above maximum."""
        with pytest.raises(ValueError, match="Value 11 is above maximum 10"):
            InputSanitizer.sanitize_numeric_range(11, max_val=10)

    def test_sanitize_limit_valid(self):
        """Test sanitizing valid limit values."""
        assert InputSanitizer.sanitize_limit(100) == 100
        assert InputSanitizer.sanitize_limit(1) == 1
        assert InputSanitizer.sanitize_limit(10000) == 10000

    def test_sanitize_limit_none(self):
        """Test sanitizing None limit."""
        result = InputSanitizer.sanitize_limit(None)
        assert result is None

    def test_sanitize_limit_invalid_range(self):
        """Test sanitizing invalid limit ranges."""
        with pytest.raises(ValueError, match="below minimum"):
            InputSanitizer.sanitize_limit(0)

        with pytest.raises(ValueError, match="above maximum"):
            InputSanitizer.sanitize_limit(10001)

    def test_sanitize_offset_valid(self):
        """Test sanitizing valid offset values."""
        assert InputSanitizer.sanitize_offset(0) == 0
        assert InputSanitizer.sanitize_offset(100) == 100

    def test_sanitize_offset_none(self):
        """Test sanitizing None offset."""
        result = InputSanitizer.sanitize_offset(None)
        assert result is None

    def test_sanitize_offset_invalid_range(self):
        """Test sanitizing invalid offset ranges."""
        with pytest.raises(ValueError, match="below minimum"):
            InputSanitizer.sanitize_offset(-1)

    def test_sanitize_string_enum_valid(self):
        """Test sanitizing valid string enum values."""
        allowed = ["BUY", "SELL"]
        assert InputSanitizer.sanitize_string_enum("buy", allowed) == "BUY"
        assert InputSanitizer.sanitize_string_enum("SELL", allowed) == "SELL"

    def test_sanitize_string_enum_none(self):
        """Test sanitizing None string enum."""
        result = InputSanitizer.sanitize_string_enum(None, ["BUY", "SELL"])
        assert result is None

    def test_sanitize_string_enum_empty_string(self):
        """Test sanitizing empty string enum."""
        result = InputSanitizer.sanitize_string_enum("", ["BUY", "SELL"])
        assert result is None

    def test_sanitize_string_enum_invalid_type(self):
        """Test sanitizing non-string enum."""
        with pytest.raises(TypeError, match="Value must be a string"):
            InputSanitizer.sanitize_string_enum(123, ["BUY", "SELL"])

    def test_sanitize_string_enum_invalid_value(self):
        """Test sanitizing invalid enum value."""
        with pytest.raises(
            ValueError, match="Invalid value 'INVALID'. Allowed: \\['BUY', 'SELL'\\]"
        ):
            InputSanitizer.sanitize_string_enum("INVALID", ["BUY", "SELL"])

    def test_sanitize_response_data_none(self):
        """Test sanitizing None response data."""
        result = InputSanitizer.sanitize_response_data(None)
        assert result is None

    def test_sanitize_response_data_dict(self):
        """Test sanitizing dictionary response data."""
        data = {"key1": "  value1  ", "key2": {"nested": "  value2  "}}
        result = InputSanitizer.sanitize_response_data(data)
        expected = {"key1": "value1", "key2": {"nested": "value2"}}
        assert result == expected

    def test_sanitize_response_data_list(self):
        """Test sanitizing list response data."""
        data = ["  item1  ", "  item2  ", {"key": "  value  "}]
        result = InputSanitizer.sanitize_response_data(data)
        expected = ["item1", "item2", {"key": "value"}]
        assert result == expected

    def test_sanitize_response_data_string(self):
        """Test sanitizing string response data."""
        result = InputSanitizer.sanitize_response_data("  test string  ")
        assert result == "test string"

    def test_sanitize_response_data_other_types(self):
        """Test sanitizing other data types."""
        assert InputSanitizer.sanitize_response_data(123) == 123
        assert InputSanitizer.sanitize_response_data(12.5) == 12.5
        assert InputSanitizer.sanitize_response_data(True) is True
