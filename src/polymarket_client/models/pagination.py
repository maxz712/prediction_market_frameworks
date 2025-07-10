from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationInfo(BaseModel):
    """Pagination metadata for API responses."""
    
    total_count: Optional[int] = Field(None, description="Total number of items available")
    page: int = Field(description="Current page number (1-based)")
    per_page: int = Field(description="Number of items per page")
    has_next: bool = Field(description="Whether there are more pages available")
    has_previous: bool = Field(description="Whether there are previous pages")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and per_page."""
        return (self.page - 1) * self.per_page
    
    @classmethod
    def from_offset(cls, offset: int, limit: int, total_returned: int, requested_limit: int) -> 'PaginationInfo':
        """Create pagination info from offset-based parameters."""
        page = (offset // limit) + 1
        has_next = total_returned == requested_limit  # If we got exactly what we asked for, there might be more
        has_previous = offset > 0
        
        return cls(
            page=page,
            per_page=limit,
            has_next=has_next,
            has_previous=has_previous
        )

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    
    data: List[T] = Field(description="List of items in current page")
    pagination: PaginationInfo = Field(description="Pagination metadata")
    
    @property
    def items(self) -> List[T]:
        """Alias for data for backward compatibility."""
        return self.data