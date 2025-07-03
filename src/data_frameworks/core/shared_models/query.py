from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class QueryType(str, Enum):
    """Types of queries supported by the framework."""
    PREDICTION_MARKET = "prediction_market"
    FINANCIAL_DATA = "financial_data"
    NEWS = "news"
    CROSS_DOMAIN = "cross_domain"


class Query(BaseModel):
    """Universal query model for cross-domain data requests."""
    
    id: str = Field(..., description="Unique query identifier")
    query_type: QueryType = Field(..., description="Type of query")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Data filters")
    limit: Optional[int] = Field(default=100, description="Maximum number of results")
    offset: Optional[int] = Field(default=0, description="Offset for pagination")
    start_time: Optional[datetime] = Field(default=None, description="Start time filter")
    end_time: Optional[datetime] = Field(default=None, description="End time filter")
    domains: List[str] = Field(default_factory=list, description="Target domains for the query")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True
    
    def is_cross_domain(self) -> bool:
        """Check if this is a cross-domain query."""
        return len(self.domains) > 1 or self.query_type == QueryType.CROSS_DOMAIN
    
    def get_domain_parameters(self, domain: str) -> Dict[str, Any]:
        """Get parameters specific to a domain."""
        return self.parameters.get(domain, {})
    
    def add_domain_parameter(self, domain: str, key: str, value: Any):
        """Add a parameter for a specific domain."""
        if domain not in self.parameters:
            self.parameters[domain] = {}
        self.parameters[domain][key] = value