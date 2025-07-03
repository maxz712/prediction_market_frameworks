from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.data_frameworks.core.shared_models.base_data import BaseData


class Ticker(BaseData):
    """Model for financial ticker data."""
    
    symbol: str = Field(..., description="Trading symbol")
    open_price: Decimal = Field(..., description="Opening price")
    high_price: Decimal = Field(..., description="Highest price")
    low_price: Decimal = Field(..., description="Lowest price")
    close_price: Decimal = Field(..., description="Closing price")
    volume: Decimal = Field(..., description="Trading volume")
    quote_volume: Optional[Decimal] = Field(default=None, description="Quote asset volume")
    trades_count: Optional[int] = Field(default=None, description="Number of trades")
    
    def validate_data(self) -> bool:
        """Validate ticker data integrity."""
        if any(price <= 0 for price in [self.open_price, self.high_price, self.low_price, self.close_price]):
            return False
        if self.high_price < self.low_price:
            return False
        if self.volume < 0:
            return False
        return True
    
    @property
    def price_change(self) -> Decimal:
        """Calculate price change from open to close."""
        return self.close_price - self.open_price
    
    @property
    def price_change_percent(self) -> Decimal:
        """Calculate percentage price change."""
        if self.open_price == 0:
            return Decimal('0')
        return (self.price_change / self.open_price) * 100
    
    @property
    def is_bullish(self) -> bool:
        """Check if the ticker shows bullish trend."""
        return self.close_price > self.open_price