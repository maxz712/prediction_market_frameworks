from pydantic import BaseModel, Field

from .order import OrderSide, OrderType


class LimitOrderRequest(BaseModel):
    """Request model for submitting limit orders."""

    token_id: str = Field(..., description="Token identifier")
    side: OrderSide = Field(..., description="Order side (BUY or SELL)")
    size: float = Field(..., gt=0, description="Order size (must be positive)")
    price: float = Field(..., gt=0, description="Price per unit (must be positive)")
    order_type: OrderType = Field(OrderType.GTC, description="Order type (GTC, FOK, FAK, GTD)")
    expires_at: int | None = Field(None, description="Expiration timestamp for GTD orders")

    def to_dict(self) -> dict:
        """Convert to dictionary for API calls."""
        result = {
            "token_id": self.token_id,
            "side": self.side.value,
            "size": self.size,
            "price": self.price
        }
        if self.expires_at is not None:
            result["expires_at"] = self.expires_at
        return result
