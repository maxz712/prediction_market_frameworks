"""Price history data models for Polymarket."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PricePoint(BaseModel):
    """Model for a single price point in the history."""

    model_config = ConfigDict(extra="allow")

    timestamp: int = Field(alias="t", description="UTC timestamp")
    price: float = Field(alias="p", description="Price")


class PricesHistory(BaseModel):
    """Model for price history response."""

    model_config = ConfigDict(extra="allow")

    history: list[PricePoint]
    market: str | None = None
    start_ts: int | None = None
    end_ts: int | None = None
    interval: str | None = None
    fidelity: int | None = None

    @classmethod
    def from_raw_data(
        cls,
        raw_data: dict[str, Any],
        market: str | None = None,
        start_ts: int | None = None,
        end_ts: int | None = None,
        interval: str | None = None,
        fidelity: int | None = None,
    ) -> "PricesHistory":
        """Create PricesHistory from raw API response data.

        Args:
            raw_data: Raw response from the API
            market: Market ID that was queried
            start_ts: Start timestamp that was queried
            end_ts: End timestamp that was queried
            interval: Interval that was queried
            fidelity: Fidelity that was queried

        Returns:
            PricesHistory instance
        """
        history_data = raw_data.get("history", [])
        price_points = [
            PricePoint(t=point["t"], p=point["p"]) for point in history_data
        ]

        return cls(
            history=price_points,
            market=market,
            start_ts=start_ts,
            end_ts=end_ts,
            interval=interval,
            fidelity=fidelity,
        )
