from datetime import datetime

from pydantic import BaseModel


class RewardRate(BaseModel):
    asset_address: str
    rewards_daily_rate: int


class Rewards(BaseModel):
    rates: list[RewardRate] | None
    min_size: int
    max_spread: float


class Token(BaseModel):
    token_id: str
    outcome: str
    price: float
    winner: bool


class Market(BaseModel):
    enable_order_book: bool
    active: bool
    closed: bool
    archived: bool
    accepting_orders: bool
    accepting_order_timestamp: datetime
    minimum_order_size: int
    minimum_tick_size: float
    condition_id: str
    question_id: str
    question: str
    description: str
    market_slug: str
    end_date_iso: datetime
    game_start_time: datetime | None
    seconds_delay: int
    fpmm: str
    maker_base_fee: int
    taker_base_fee: int
    notifications_enabled: bool
    neg_risk: bool
    neg_risk_market_id: str
    neg_risk_request_id: str
    icon: str
    image: str
    rewards: Rewards
    is_50_50_outcome: bool
    tokens: list[Token]
    tags: list[str]
