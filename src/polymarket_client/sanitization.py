"""Input sanitization utilities for Polymarket client."""

import re
from typing import Any


class InputSanitizer:
    """Input sanitization utilities for Polymarket client."""

    # Valid patterns for different input types
    HEX_ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")
    HEX_TOKEN_ID_PATTERN = re.compile(r"^0x[a-fA-F0-9]+$")
    SLUG_PATTERN = re.compile(r"^[a-zA-Z0-9\-_]+$")
    ORDER_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-_]+$")
    ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$")

    @classmethod
    def sanitize_hex_address(cls, address: str | None) -> str | None:
        """Sanitize Ethereum address input.

        Args:
            address: Ethereum address string

        Returns:
            Sanitized address or None if invalid

        Raises:
            ValueError: If address format is invalid
        """
        if address is None:
            return None

        if not isinstance(address, str):
            msg = "Address must be a string"
            raise TypeError(msg)

        address = address.strip()
        if not address:
            return None

        if not cls.HEX_ADDRESS_PATTERN.match(address):
            msg = f"Invalid Ethereum address format: {address}"
            raise ValueError(msg)

        return address.lower()

    @classmethod
    def sanitize_token_id(cls, token_id: str | None) -> str | None:
        """Sanitize token ID input.

        Args:
            token_id: Token ID string (hex or decimal format)

        Returns:
            Sanitized token ID in hex format or None if invalid

        Raises:
            ValueError: If token ID format is invalid
        """
        if token_id is None:
            return None

        if not isinstance(token_id, str):
            msg = "Token ID must be a string"
            raise TypeError(msg)

        token_id = token_id.strip()
        if not token_id:
            return None

        # Check if it's already in hex format
        if cls.HEX_TOKEN_ID_PATTERN.match(token_id):
            return token_id.lower()

        # Try to convert from decimal format
        try:
            # Check if it's a valid decimal number
            if token_id.isdigit():
                hex_token = hex(int(token_id))
                return hex_token.lower()
            msg = f"Invalid token ID format: {token_id}"
            raise ValueError(msg)
        except ValueError as e:
            msg = f"Invalid token ID format: {token_id}"
            raise ValueError(msg) from e

    @classmethod
    def sanitize_order_id(cls, order_id: str | None) -> str | None:
        """Sanitize order ID input.

        Args:
            order_id: Order ID string

        Returns:
            Sanitized order ID or None if invalid

        Raises:
            ValueError: If order ID format is invalid
        """
        if order_id is None:
            return None

        if not isinstance(order_id, str):
            msg = "Order ID must be a string"
            raise TypeError(msg)

        order_id = order_id.strip()
        if not order_id:
            return None

        if not cls.ORDER_ID_PATTERN.match(order_id):
            msg = f"Invalid order ID format: {order_id}"
            raise ValueError(msg)

        return order_id

    @classmethod
    def sanitize_slug(cls, slug: str | None) -> str | None:
        """Sanitize slug input.

        Args:
            slug: Slug string

        Returns:
            Sanitized slug or None if invalid

        Raises:
            ValueError: If slug format is invalid
        """
        if slug is None:
            return None

        if not isinstance(slug, str):
            msg = "Slug must be a string"
            raise TypeError(msg)

        slug = slug.strip()
        if not slug:
            return None

        if not cls.SLUG_PATTERN.match(slug):
            msg = f"Invalid slug format: {slug}"
            raise ValueError(msg)

        return slug.lower()

    @classmethod
    def sanitize_slug_list(cls, slugs: str | list[str] | None) -> list[str] | None:
        """Sanitize list of slugs.

        Args:
            slugs: Single slug string or list of slug strings

        Returns:
            List of sanitized slugs or None if invalid

        Raises:
            ValueError: If any slug format is invalid
        """
        if slugs is None:
            return None

        if isinstance(slugs, str):
            slug = cls.sanitize_slug(slugs)
            return [slug] if slug else None

        if not isinstance(slugs, list):
            msg = "Slugs must be a string or list of strings"
            raise TypeError(msg)

        sanitized_slugs = []
        for slug in slugs:
            sanitized_slug = cls.sanitize_slug(slug)
            if sanitized_slug:
                sanitized_slugs.append(sanitized_slug)

        return sanitized_slugs if sanitized_slugs else None

    @classmethod
    def sanitize_iso_date(cls, date_str: str | None) -> str | None:
        """Sanitize ISO date string.

        Args:
            date_str: ISO date string

        Returns:
            Sanitized date string or None if invalid

        Raises:
            ValueError: If date format is invalid
        """
        if date_str is None:
            return None

        if not isinstance(date_str, str):
            msg = "Date must be a string"
            raise TypeError(msg)

        date_str = date_str.strip()
        if not date_str:
            return None

        if not cls.ISO_DATE_PATTERN.match(date_str):
            msg = f"Invalid ISO date format: {date_str}"
            raise ValueError(msg)

        return date_str

    @classmethod
    def sanitize_numeric_range(
        cls,
        value: int | float | None,
        min_val: int | float | None = None,
        max_val: int | float | None = None,
    ) -> int | float | None:
        """Sanitize numeric input with optional range validation.

        Args:
            value: Numeric value to sanitize
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            Sanitized numeric value or None if invalid

        Raises:
            ValueError: If value is out of range
        """
        if value is None:
            return None

        if not isinstance(value, int | float):
            msg = "Value must be numeric"
            raise TypeError(msg)

        if min_val is not None and value < min_val:
            msg = f"Value {value} is below minimum {min_val}"
            raise ValueError(msg)

        if max_val is not None and value > max_val:
            msg = f"Value {value} is above maximum {max_val}"
            raise ValueError(msg)

        return value

    @classmethod
    def sanitize_limit(cls, limit: int | None) -> int | None:
        """Sanitize limit parameter for pagination.

        Args:
            limit: Limit value

        Returns:
            Sanitized limit or None if invalid

        Raises:
            ValueError: If limit is invalid
        """
        return cls.sanitize_numeric_range(limit, min_val=1, max_val=10000)

    @classmethod
    def sanitize_offset(cls, offset: int | None) -> int | None:
        """Sanitize offset parameter for pagination.

        Args:
            offset: Offset value

        Returns:
            Sanitized offset or None if invalid

        Raises:
            ValueError: If offset is invalid
        """
        return cls.sanitize_numeric_range(offset, min_val=0)

    @classmethod
    def sanitize_string_enum(
        cls, value: str | None, allowed_values: list[str]
    ) -> str | None:
        """Sanitize string enum input.

        Args:
            value: String value to validate
            allowed_values: List of allowed values

        Returns:
            Sanitized value or None if invalid

        Raises:
            ValueError: If value is not in allowed values
        """
        if value is None:
            return None

        if not isinstance(value, str):
            msg = "Value must be a string"
            raise TypeError(msg)

        value = value.strip().upper()
        if not value:
            return None

        if value not in [v.upper() for v in allowed_values]:
            msg = f"Invalid value '{value}'. Allowed: {allowed_values}"
            raise ValueError(msg)

        return value

    @classmethod
    def sanitize_response_data(cls, data: Any) -> Any:
        """Sanitize response data from API.

        Args:
            data: Raw response data

        Returns:
            Sanitized data
        """
        if data is None:
            return None

        if isinstance(data, dict):
            return {
                key: cls.sanitize_response_data(value) for key, value in data.items()
            }

        if isinstance(data, list):
            return [cls.sanitize_response_data(item) for item in data]

        if isinstance(data, str):
            return data.strip()

        return data
