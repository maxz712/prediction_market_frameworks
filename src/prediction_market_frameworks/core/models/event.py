from datetime import datetime
from typing import List, Optional
from decimal import Decimal
import json
from pydantic import BaseModel, Field, field_validator


class Tag(BaseModel):
    id: str
    label: str
    slug: str
    force_show: bool = Field(default=False, alias="forceShow")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    published_at: Optional[datetime] = Field(default=None, alias="publishedAt")
    updated_by: Optional[int] = Field(default=None, alias="updatedBy")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    force_hide: Optional[bool] = Field(default=None, alias="forceHide")
    
    @field_validator('published_at', mode='before')
    @classmethod
    def parse_published_at(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            # Handle format like '2023-11-02 21:23:16.384+00'
            if v.endswith('+00'):
                v = v + ':00'  # Convert to proper timezone format
            return datetime.fromisoformat(v)
        return v

    class Config:
        populate_by_name = True


class ClobReward(BaseModel):
    id: str
    condition_id: str = Field(alias="conditionId")
    asset_address: str = Field(alias="assetAddress")
    rewards_amount: Decimal = Field(alias="rewardsAmount")
    rewards_daily_rate: Decimal = Field(alias="rewardsDailyRate")
    start_date: str = Field(alias="startDate")
    end_date: str = Field(alias="endDate")

    class Config:
        populate_by_name = True


class Market(BaseModel):
    id: str
    question: str
    condition_id: str = Field(alias="conditionId")
    slug: str
    resolution_source: str = Field(default="", alias="resolutionSource")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    liquidity: Decimal = Field(default=0)
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    image: str
    icon: str
    description: str
    outcomes: List[str]
    outcome_prices: List[Decimal] = Field(default=[], alias="outcomePrices")
    volume: Decimal = Field(default=0)
    active: bool
    closed: bool
    market_maker_address: str = Field(alias="marketMakerAddress")
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    new: bool
    featured: bool = Field(default=False)
    submitted_by: str = Field(default="", alias="submittedBy")
    archived: bool
    resolved_by: str = Field(default="", alias="resolvedBy")
    restricted: bool
    group_item_title: str = Field(default="", alias="groupItemTitle")
    group_item_threshold: Decimal = Field(default=0, alias="groupItemThreshold")
    question_id: str = Field(default="", alias="questionID")
    enable_order_book: bool = Field(alias="enableOrderBook")
    order_price_min_tick_size: Decimal = Field(alias="orderPriceMinTickSize")
    order_min_size: Decimal = Field(alias="orderMinSize")
    volume_num: Decimal = Field(default=0, alias="volumeNum")
    liquidity_num: Decimal = Field(default=0, alias="liquidityNum")
    end_date_iso: str = Field(default="", alias="endDateIso")
    start_date_iso: str = Field(default="", alias="startDateIso")
    has_reviewed_dates: bool = Field(default=False, alias="hasReviewedDates")
    volume_24hr: Decimal = Field(default=0, alias="volume24hr")
    volume_1wk: Decimal = Field(default=0, alias="volume1wk")
    volume_1mo: Decimal = Field(default=0, alias="volume1mo")
    volume_1yr: Decimal = Field(default=0, alias="volume1yr")
    clob_token_ids: List[str] = Field(default=[], alias="clobTokenIds")
    uma_bond: Decimal = Field(default=0, alias="umaBond")
    uma_reward: Decimal = Field(default=0, alias="umaReward")
    volume_24hr_clob: Decimal = Field(default=0, alias="volume24hrClob")
    volume_1wk_clob: Decimal = Field(default=0, alias="volume1wkClob")
    volume_1mo_clob: Decimal = Field(default=0, alias="volume1moClob")
    volume_1yr_clob: Decimal = Field(default=0, alias="volume1yrClob")
    volume_clob: Decimal = Field(default=0, alias="volumeClob")
    liquidity_clob: Decimal = Field(default=0, alias="liquidityClob")
    accepting_orders: bool = Field(default=False, alias="acceptingOrders")
    neg_risk: bool = Field(default=False, alias="negRisk")
    ready: bool
    funded: bool
    accepting_orders_timestamp: Optional[datetime] = Field(default=None, alias="acceptingOrdersTimestamp")
    cyom: bool
    competitive: Decimal = Field(default=0)
    pager_duty_notification_enabled: bool = Field(alias="pagerDutyNotificationEnabled")
    approved: bool
    clob_rewards: List[ClobReward] = Field(default=[], alias="clobRewards")
    rewards_min_size: Decimal = Field(alias="rewardsMinSize")
    rewards_max_spread: Decimal = Field(alias="rewardsMaxSpread")
    spread: Decimal
    one_day_price_change: Decimal = Field(default=0, alias="oneDayPriceChange")
    one_week_price_change: Decimal = Field(default=0, alias="oneWeekPriceChange")
    one_month_price_change: Decimal = Field(default=0, alias="oneMonthPriceChange")
    last_trade_price: Decimal = Field(default=0, alias="lastTradePrice")
    best_bid: Decimal = Field(default=0, alias="bestBid")
    best_ask: Decimal = Field(default=0, alias="bestAsk")
    automatically_active: bool = Field(default=False, alias="automaticallyActive")
    clear_book_on_start: bool = Field(alias="clearBookOnStart")
    manual_activation: bool = Field(alias="manualActivation")
    neg_risk_other: bool = Field(alias="negRiskOther")
    uma_resolution_statuses: List[str] = Field(alias="umaResolutionStatuses")
    pending_deployment: bool = Field(alias="pendingDeployment")
    deploying: bool
    rfq_enabled: bool = Field(alias="rfqEnabled")
    
    @field_validator('outcomes', mode='before')
    @classmethod
    def parse_outcomes(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    @field_validator('outcome_prices', mode='before')
    @classmethod
    def parse_outcome_prices(cls, v):
        if isinstance(v, str):
            return [Decimal(price) for price in json.loads(v)]
        return [Decimal(str(price)) for price in v]
    
    @field_validator('clob_token_ids', mode='before')
    @classmethod
    def parse_clob_token_ids(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v
    
    @field_validator('uma_resolution_statuses', mode='before')
    @classmethod
    def parse_uma_resolution_statuses(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    class Config:
        populate_by_name = True


class Event(BaseModel):
    id: str
    ticker: str
    slug: str
    title: str
    description: str
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    creation_date: Optional[datetime] = Field(default=None, alias="creationDate")
    end_date: datetime = Field(alias="endDate")
    image: str
    icon: str
    active: bool
    closed: bool
    archived: bool
    new: bool
    featured: bool
    restricted: bool
    liquidity: Decimal = Field(default=0)
    volume: Decimal = Field(default=0)
    open_interest: Decimal = Field(alias="openInterest")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    competitive: Decimal = Field(default=0)
    volume_24hr: Decimal = Field(default=0, alias="volume24hr")
    volume_1wk: Decimal = Field(default=0, alias="volume1wk")
    volume_1mo: Decimal = Field(default=0, alias="volume1mo")
    volume_1yr: Decimal = Field(default=0, alias="volume1yr")
    enable_order_book: bool = Field(alias="enableOrderBook")
    liquidity_clob: Decimal = Field(default=0, alias="liquidityClob")
    comment_count: int = Field(default=0, alias="commentCount")
    markets: List[Market]
    tags: List[Tag]
    cyom: bool
    show_all_outcomes: bool = Field(alias="showAllOutcomes")
    show_market_images: bool = Field(alias="showMarketImages")
    enable_neg_risk: bool = Field(alias="enableNegRisk")
    automatically_active: bool = Field(default=False, alias="automaticallyActive")
    neg_risk_augmented: bool = Field(alias="negRiskAugmented")
    pending_deployment: bool = Field(alias="pendingDeployment")
    deploying: bool

    class Config:
        populate_by_name = True