from pydantic import BaseModel, Field


class CancelResponse(BaseModel):
    """Response model for order cancellation operations."""

    canceled: list[str] = Field(
        ..., description="List of order IDs that were successfully canceled"
    )
    not_canceled: dict[str, str] = Field(
        ..., description="Map of order IDs to failure reasons for failed cancellations"
    )

    @classmethod
    def from_raw_response(cls, raw_response: dict) -> "CancelResponse":
        """Create a CancelResponse from raw API response.

        Args:
            raw_response: Raw response from the cancel API endpoint

        Returns:
            CancelResponse: Parsed response with canceled and not_canceled orders
        """
        if isinstance(raw_response, dict):
            return cls(
                canceled=raw_response.get("canceled", []),
                not_canceled=raw_response.get("not_canceled", {}),
            )

        # Handle unexpected response format
        return cls(
            canceled=[],
            not_canceled={"error": f"Unexpected response format: {type(raw_response)}"},
        )

    @property
    def is_successful(self) -> bool:
        """Check if all cancellation requests were successful."""
        return len(self.not_canceled) == 0

    @property
    def has_failures(self) -> bool:
        """Check if any cancellation requests failed."""
        return len(self.not_canceled) > 0

    @property
    def canceled_count(self) -> int:
        """Number of orders successfully canceled."""
        return len(self.canceled)

    @property
    def failed_count(self) -> int:
        """Number of orders that failed to cancel."""
        return len(self.not_canceled)

    @property
    def total_requested(self) -> int:
        """Total number of orders in the cancellation request."""
        return self.canceled_count + self.failed_count

    def get_failure_reason(self, order_id: str) -> str | None:
        """Get the failure reason for a specific order ID.

        Args:
            order_id: The order ID to check

        Returns:
            The failure reason if the order failed to cancel,
            None if it was canceled successfully
        """
        return self.not_canceled.get(order_id)

    def was_canceled(self, order_id: str) -> bool:
        """Check if a specific order was successfully canceled.

        Args:
            order_id: The order ID to check

        Returns:
            True if the order was canceled, False otherwise
        """
        return order_id in self.canceled

    def summary(self) -> str:
        """Get a human-readable summary of the cancellation results."""
        if self.is_successful:
            return f"Successfully canceled {self.canceled_count} order(s)"
        return (
            f"Canceled {self.canceled_count} order(s), "
            f"failed to cancel {self.failed_count} order(s)"
        )
