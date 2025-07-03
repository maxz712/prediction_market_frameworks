from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.data_frameworks.core.shared_models.base_data import BaseData


class Price(BaseData):
    """Model for financial price data."""
    
    symbol: str = Field(..., description="Trading symbol (e.g., BTC-USD)")
    price: Decimal = Field(..., description="Current price")
    currency: str = Field(..., description="Currency denomination")
    exchange: str = Field(..., description="Exchange name")
    volume_24h: Optional[Decimal] = Field(default=None, description="24-hour trading volume")
    change_24h: Optional[Decimal] = Field(default=None, description="24-hour price change")
    change_percent_24h: Optional[Decimal] = Field(default=None, description="24-hour percent change")
    
    def validate_data(self) -> bool:
        """Validate price data integrity."""
        if self.price <= 0:
            return False
        if self.volume_24h is not None and self.volume_24h < 0:
            return False
        return True
    
    @property
    def formatted_price(self) -> str:
        """Get formatted price string."""
        return f"{self.price:.8f} {self.currency}"
    
    @property
    def is_crypto(self) -> bool:
        """Check if this is a cryptocurrency price."""
        crypto_symbols = ['BTC', 'ETH', 'ADA', 'DOT', 'SOL', 'AVAX', 'MATIC']
        return any(crypto in self.symbol.upper() for crypto in crypto_symbols)