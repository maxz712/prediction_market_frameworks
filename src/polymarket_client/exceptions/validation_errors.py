"""Validation-related exceptions for the Polymarket SDK."""

from typing import Any

from .base import PolymarketError


class PolymarketValidationError(PolymarketError):
    """Base exception for validation errors.

    This is raised when input data doesn't meet the required format,
    constraints, or business rules.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
        errors: dict[str, list[str]] | None = None
    ) -> None:
        """Initialize the validation error.

        Args:
            message: Human-readable error message
            field: The field that failed validation
            value: The invalid value that was provided
            errors: Dictionary of field names to list of error messages
        """
        super().__init__(message)
        self.field = field
        self.value = value
        self.errors = errors or {}

    def __str__(self) -> str:
        error_msg = super().__str__()
        if self.field:
            error_msg += f" (Field: {self.field})"
        if self.value is not None:
            error_msg += f" (Value: {self.value})"
        return error_msg


class PolymarketFieldValidationError(PolymarketValidationError):
    """Exception raised when a specific field fails validation.

    This includes:
    - Required fields that are missing
    - Fields with invalid formats
    - Fields outside allowed ranges
    """

    def __init__(
        self,
        field: str,
        message: str,
        value: Any | None = None,
        **kwargs
    ) -> None:
        super().__init__(message, field=field, value=value, **kwargs)


class PolymarketTypeValidationError(PolymarketValidationError):
    """Exception raised when a value has the wrong type.

    This includes:
    - Strings provided where numbers are expected
    - Invalid enum values
    - Incorrect data structures
    """

    def __init__(
        self,
        field: str,
        expected_type: str,
        actual_type: str,
        value: Any | None = None
    ) -> None:
        message = f"Expected {expected_type}, got {actual_type}"
        super().__init__(message, field=field, value=value)
        self.expected_type = expected_type
        self.actual_type = actual_type


class PolymarketRangeValidationError(PolymarketValidationError):
    """Exception raised when a value is outside the allowed range.

    This includes:
    - Numbers too large or too small
    - Strings too long or too short
    - Arrays with invalid lengths
    """

    def __init__(
        self,
        field: str,
        value: Any,
        min_value: Any | None = None,
        max_value: Any | None = None
    ) -> None:
        if min_value is not None and max_value is not None:
            message = f"Value must be between {min_value} and {max_value}"
        elif min_value is not None:
            message = f"Value must be at least {min_value}"
        elif max_value is not None:
            message = f"Value must be at most {max_value}"
        else:
            message = "Value is outside allowed range"

        super().__init__(message, field=field, value=value)
        self.min_value = min_value
        self.max_value = max_value


class PolymarketRequiredFieldError(PolymarketValidationError):
    """Exception raised when a required field is missing.

    This is a specific type of validation error for missing required fields.
    """

    def __init__(self, field: str) -> None:
        message = f"Required field '{field}' is missing"
        super().__init__(message, field=field)


class PolymarketFormatValidationError(PolymarketValidationError):
    """Exception raised when a value doesn't match the expected format.

    This includes:
    - Invalid email addresses
    - Malformed URLs
    - Incorrect date formats
    - Invalid market IDs or condition IDs
    """

    def __init__(
        self,
        field: str,
        value: Any,
        expected_format: str,
        pattern: str | None = None
    ) -> None:
        message = f"Invalid format. Expected: {expected_format}"
        if pattern:
            message += f" (Pattern: {pattern})"

        super().__init__(message, field=field, value=value)
        self.expected_format = expected_format
        self.pattern = pattern


class PolymarketBusinessRuleError(PolymarketValidationError):
    """Exception raised when data violates business rules.

    This includes:
    - Invalid trading pairs
    - Insufficient balance for orders
    - Orders placed on closed markets
    - Invalid price/size combinations
    """

    def __init__(self, message: str, rule: str | None = None, **kwargs) -> None:
        super().__init__(message, **kwargs)
        self.rule = rule

    def __str__(self) -> str:
        error_msg = super().__str__()
        if self.rule:
            error_msg += f" (Rule: {self.rule})"
        return error_msg
