"""Position model for Polymarket positions."""

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class Position(BaseModel):
    """Represents a user's position in a Polymarket market."""

    market: str = Field(..., description="Market identifier")
    token_id: str = Field(..., description="Token/outcome identifier")
    size: Decimal = Field(..., description="Position size/quantity")
    avg_price: Decimal = Field(..., description="Average entry price")
    realized_pnl: Decimal = Field(default=Decimal("0"), description="Realized profit/loss")
    unrealized_pnl: Decimal = Field(default=Decimal("0"), description="Unrealized profit/loss")
    user: str = Field(..., description="User address")

    @classmethod
    def from_raw_data(cls, data: dict[str, Any]) -> "Position":
        """Create Position from raw API data."""
        return cls(
            market=data.get("market", data.get("conditionId", "")),
            token_id=data.get("tokenId", data.get("token_id", data.get("asset", ""))),
            size=Decimal(str(data.get("size", "0"))),
            avg_price=Decimal(str(data.get("avgPrice", data.get("avg_price", "0")))),
            realized_pnl=Decimal(str(data.get("realizedPnl", data.get("realized_pnl", "0")))),
            unrealized_pnl=Decimal(str(data.get("unrealizedPnl", data.get("unrealized_pnl", data.get("cashPnl", "0"))))),
            user=data.get("user", data.get("proxyWallet", "")),
        )

    @property
    def total_pnl(self) -> Decimal:
        """Calculate total profit/loss (realized + unrealized)."""
        return self.realized_pnl + self.unrealized_pnl

    @property
    def is_long(self) -> bool:
        """Check if this is a long position."""
        return self.size > 0

    @property
    def is_short(self) -> bool:
        """Check if this is a short position."""
        return self.size < 0

    @property
    def has_position(self) -> bool:
        """Check if there's an active position."""
        return self.size != 0


class UserPositions(BaseModel):
    """Container for user positions across markets."""

    positions: list[Position] = Field(default_factory=list, description="List of user positions")

    @classmethod
    def from_raw_data(cls, data: dict[str, Any] | list[dict[str, Any]]) -> "UserPositions":
        """Create UserPositions from raw API data."""
        positions = []

        # Handle case where data is a list directly (data API format)
        if isinstance(data, list):
            positions_list = data
        # Handle case where data is a dict with "positions" key (other API format)
        else:
            positions_list = data.get("positions", [])

        for pos_data in positions_list:
            try:
                positions.append(Position.from_raw_data(pos_data))
            except Exception:
                # Skip invalid position data
                continue
        return cls(positions=positions)

    def filter_by_market(self, market: str) -> "UserPositions":
        """Filter positions by market."""
        filtered = [pos for pos in self.positions if pos.market == market]
        return UserPositions(positions=filtered)

    @property
    def total_realized_pnl(self) -> Decimal:
        """Calculate total realized P&L across all positions."""
        return sum(pos.realized_pnl for pos in self.positions)

    @property
    def total_unrealized_pnl(self) -> Decimal:
        """Calculate total unrealized P&L across all positions."""
        return sum(pos.unrealized_pnl for pos in self.positions)

    @property
    def total_pnl(self) -> Decimal:
        """Calculate total P&L across all positions."""
        return self.total_realized_pnl + self.total_unrealized_pnl

    @property
    def markets_with_positions(self) -> list[str]:
        """Get list of markets where user has positions."""
        return list({pos.market for pos in self.positions if pos.has_position})
