from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BaseData(BaseModel, ABC):
    """Base class for all data models across domains."""
    
    id: str = Field(..., description="Unique identifier for the data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp when data was created")
    source: str = Field(..., description="Source of the data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True
    
    @abstractmethod
    def validate_data(self) -> bool:
        """Validate the data integrity."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model to a dictionary."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseData':
        """Create an instance from a dictionary."""
        return cls(**data)