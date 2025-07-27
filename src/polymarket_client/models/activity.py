"""Activity models for on-chain user activity data."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, validator


class ActivityMarket(BaseModel):
    """Market information in activity data."""
    condition_id: str = Field(description="The condition ID of the market")
    question: str = Field(description="The market question")
    slug: str = Field(description="The market slug")
    group_item_title: str | None = Field(None, description="Group item title")
    group_item_threshold: str | None = Field(None, description="Group item threshold")
    end_date_iso: str | None = Field(None, description="Market end date in ISO format")


class UserProfile(BaseModel):
    """User profile information in activity data."""
    name: str | None = Field(None, description="User display name")
    username: str | None = Field(None, description="Username")
    profile_picture: str | None = Field(None, description="Profile picture URL")


class Activity(BaseModel):
    """Single activity record."""
    id: str = Field(description="Unique activity ID")
    proxy_wallet: str = Field(description="Proxy wallet address")
    timestamp: int = Field(description="Activity timestamp (Unix seconds)")
    condition_id: str = Field(description="Market condition ID")
    type: str = Field(description="Activity type (TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION)")
    size: str = Field(description="Size of the activity (as string to preserve precision)")
    price: str | None = Field(None, description="Price of the trade (if applicable)")
    side: str | None = Field(None, description="Trade side (BUY/SELL) if applicable")
    outcome: str | None = Field(None, description="Outcome name if applicable")
    market: ActivityMarket | None = Field(None, description="Market information")
    user_profile: UserProfile | None = Field(None, description="User profile information")

    @validator("timestamp")
    def validate_timestamp(cls, v):
        """Ensure timestamp is a valid Unix timestamp."""
        if v < 0:
            raise ValueError("Timestamp cannot be negative")
        return v

    @property
    def datetime(self) -> datetime:
        """Convert timestamp to datetime object."""
        return datetime.fromtimestamp(self.timestamp)

    @property
    def size_decimal(self) -> Decimal:
        """Get size as Decimal for precise calculations."""
        return Decimal(self.size)

    @property
    def price_decimal(self) -> Decimal | None:
        """Get price as Decimal for precise calculations."""
        return Decimal(self.price) if self.price else None

    @property
    def is_trade(self) -> bool:
        """Check if this activity is a trade."""
        return self.type == "TRADE"

    @property
    def is_buy(self) -> bool:
        """Check if this is a buy trade."""
        return self.is_trade and self.side == "BUY"

    @property
    def is_sell(self) -> bool:
        """Check if this is a sell trade."""
        return self.is_trade and self.side == "SELL"


class UserActivity(BaseModel):
    """User activity history response."""
    activities: list[Activity] = Field(default_factory=list, description="List of user activities")
    total_count: int | None = Field(None, description="Total count if available")

    @classmethod
    def from_raw_data(cls, raw_data: list[dict[str, Any]]) -> "UserActivity":
        """Create UserActivity from raw API response data."""
        activities = []
        for item in raw_data:
            # Handle nested market data
            market_data = None
            if item.get("market"):
                market_data = ActivityMarket(
                    condition_id=item["market"].get("conditionId", ""),
                    question=item["market"].get("question", ""),
                    slug=item["market"].get("slug", ""),
                    group_item_title=item["market"].get("groupItemTitle"),
                    group_item_threshold=item["market"].get("groupItemThreshold"),
                    end_date_iso=item["market"].get("endDateIso")
                )

            # Handle nested user profile data
            user_profile_data = None
            if item.get("userProfile"):
                user_profile_data = UserProfile(
                    name=item["userProfile"].get("name"),
                    username=item["userProfile"].get("username"),
                    profile_picture=item["userProfile"].get("profilePicture")
                )

            activity = Activity(
                id=item.get("id", ""),
                proxy_wallet=item.get("proxyWallet", ""),
                timestamp=int(item.get("timestamp", 0)),
                condition_id=item.get("conditionId", ""),
                type=item.get("type", ""),
                size=str(item.get("size", "0")),
                price=str(item.get("price")) if item.get("price") is not None else None,
                side=item.get("side"),
                outcome=item.get("outcome"),
                market=market_data,
                user_profile=user_profile_data
            )
            activities.append(activity)

        return cls(activities=activities, total_count=len(activities))

    def filter_by_type(self, activity_type: str) -> "UserActivity":
        """Filter activities by type."""
        filtered_activities = [a for a in self.activities if a.type == activity_type]
        return UserActivity(activities=filtered_activities, total_count=len(filtered_activities))

    def filter_by_market(self, condition_id: str) -> "UserActivity":
        """Filter activities by market condition ID."""
        filtered_activities = [a for a in self.activities if a.condition_id == condition_id]
        return UserActivity(activities=filtered_activities, total_count=len(filtered_activities))

    def get_trades_only(self) -> "UserActivity":
        """Get only trade activities."""
        return self.filter_by_type("TRADE")

    def get_buy_trades(self) -> "UserActivity":
        """Get only buy trade activities."""
        buy_trades = [a for a in self.activities if a.is_buy]
        return UserActivity(activities=buy_trades, total_count=len(buy_trades))

    def get_sell_trades(self) -> "UserActivity":
        """Get only sell trade activities."""
        sell_trades = [a for a in self.activities if a.is_sell]
        return UserActivity(activities=sell_trades, total_count=len(sell_trades))

    def __len__(self) -> int:
        """Return the number of activities."""
        return len(self.activities)

    def __iter__(self):
        """Make the object iterable."""
        return iter(self.activities)

    def __getitem__(self, index):
        """Allow indexing."""
        return self.activities[index]
