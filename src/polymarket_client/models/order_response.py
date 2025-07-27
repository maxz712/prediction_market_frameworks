from pydantic import BaseModel, Field

from .order import Order


class OrderResponse(BaseModel):
    """Response model for order submission."""

    success: bool = Field(
        ..., description="Whether the order was submitted successfully"
    )
    order_id: str | None = Field(None, description="Unique order identifier")
    order: Order | None = Field(None, description="Full order details if available")
    message: str | None = Field(None, description="Response message")
    error: str | None = Field(None, description="Error message if submission failed")

    # Transaction details
    transaction_hash: str | None = Field(
        None, description="Blockchain transaction hash"
    )
    gas_used: int | None = Field(None, description="Gas used for the transaction")

    # Market details
    market_id: str | None = Field(None, description="Market identifier")
    token_id: str | None = Field(None, description="Token identifier")

    @classmethod
    def from_raw_response(cls, raw_response: dict) -> "OrderResponse":
        """Create an OrderResponse from raw API response."""
        # Handle different response formats from the API
        if isinstance(raw_response, dict):
            success = raw_response.get("success", True)
            order_id = raw_response.get(
                "orderID", raw_response.get("order_id", raw_response.get("id"))
            )

            # Try to extract order details if present
            order = None
            if "order" in raw_response:
                try:
                    order = Order.from_raw_data(raw_response["order"])
                except Exception:
                    # If order parsing fails, continue without it
                    pass

            return cls(
                success=success,
                order_id=order_id,
                order=order,
                message=raw_response.get("message"),
                error=raw_response.get("error"),
                transaction_hash=raw_response.get(
                    "txhash", raw_response.get("transaction_hash")
                ),
                gas_used=raw_response.get("gas_used"),
                market_id=raw_response.get("market_id", raw_response.get("market")),
                token_id=raw_response.get("token_id", raw_response.get("asset_id")),
            )

        # Handle unexpected response format
        return cls(
            success=False,
            order_id=None,
            order=None,
            message=None,
            error=f"Unexpected response format: {type(raw_response)}",
            transaction_hash=None,
            gas_used=None,
            market_id=None,
            token_id=None,
        )

    @property
    def is_successful(self) -> bool:
        """Check if the order submission was successful."""
        return self.success and self.error is None

    @property
    def has_order_id(self) -> bool:
        """Check if we have an order ID."""
        return self.order_id is not None and self.order_id != ""
