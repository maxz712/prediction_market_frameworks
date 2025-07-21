"""Unified pagination utilities for the Polymarket client."""

from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any, Callable, Generic, TypeVar

from pydantic import BaseModel, Field

from .models.pagination import PaginatedResponse, PaginationInfo

T = TypeVar("T", bound=BaseModel)


class PaginationStrategy(ABC, Generic[T]):
    """Abstract base class for pagination strategies."""
    
    @abstractmethod
    def fetch_page(self, **kwargs) -> tuple[list[T], bool]:
        """Fetch a single page of data.
        
        Returns:
            A tuple of (data, has_more) where has_more indicates if there are more pages
        """
        pass
    
    @abstractmethod
    def get_next_page_params(self, current_params: dict[str, Any]) -> dict[str, Any]:
        """Get parameters for the next page based on current parameters."""
        pass


class OffsetPaginationStrategy(PaginationStrategy[T]):
    """Offset-based pagination strategy (limit + offset)."""
    
    def __init__(
        self,
        fetch_func: Callable[..., list[dict[str, Any]]],
        model_class: type[T],
        page_size: int,
        max_page_size: int,
        initial_offset: int = 0
    ):
        self.fetch_func = fetch_func
        self.model_class = model_class
        self.page_size = min(page_size, max_page_size)
        self.max_page_size = max_page_size
        self.current_offset = initial_offset
    
    def fetch_page(self, **kwargs) -> tuple[list[T], bool]:
        """Fetch a page using offset pagination."""
        # Ensure limit and offset are in kwargs
        kwargs["limit"] = kwargs.get("limit", self.page_size)
        kwargs["offset"] = kwargs.get("offset", self.current_offset)
        
        # Fetch raw data
        raw_data = self.fetch_func(**kwargs)
        
        # Convert to model instances
        data = [self.model_class.model_validate(item) for item in raw_data]
        
        # Determine if there are more pages
        has_more = len(data) == kwargs["limit"]
        
        return data, has_more
    
    def get_next_page_params(self, current_params: dict[str, Any]) -> dict[str, Any]:
        """Get parameters for the next offset-based page."""
        next_params = current_params.copy()
        next_params["offset"] = current_params.get("offset", 0) + current_params.get("limit", self.page_size)
        return next_params


class Paginator(Generic[T]):
    """Unified paginator that handles different pagination strategies."""
    
    def __init__(
        self,
        strategy: PaginationStrategy[T],
        default_page_size: int = 100,
        max_total_results: int | None = None,
        auto_paginate: bool = True
    ):
        self.strategy = strategy
        self.default_page_size = default_page_size
        self.max_total_results = max_total_results
        self.auto_paginate = auto_paginate
    
    def fetch_all(
        self,
        limit: int | None = None,
        **kwargs
    ) -> list[T]:
        """Fetch all results up to the specified limit.
        
        Args:
            limit: Maximum number of results to fetch
            **kwargs: Additional parameters to pass to the fetch function
            
        Returns:
            List of all fetched items
        """
        if not self.auto_paginate and limit is None:
            limit = self.default_page_size
        
        all_results: list[T] = []
        params = kwargs.copy()
        
        while True:
            # Adjust page size if we're close to the limit
            if limit:
                remaining = limit - len(all_results)
                if remaining <= 0:
                    break
                params["limit"] = min(self.default_page_size, remaining)
            
            # Fetch page
            page_data, has_more = self.strategy.fetch_page(**params)
            all_results.extend(page_data)
            
            # Check if we should continue
            if not has_more or not self.auto_paginate:
                break
            
            if limit and len(all_results) >= limit:
                break
            
            if self.max_total_results and len(all_results) >= self.max_total_results:
                break
            
            # Update parameters for next page
            params = self.strategy.get_next_page_params(params)
        
        # Truncate to exact limit if specified
        if limit and len(all_results) > limit:
            all_results = all_results[:limit]
        
        return all_results
    
    def fetch_paginated(
        self,
        limit: int | None = None,
        **kwargs
    ) -> PaginatedResponse[T]:
        """Fetch results with pagination metadata.
        
        Args:
            limit: Maximum number of results to fetch
            **kwargs: Additional parameters to pass to the fetch function
            
        Returns:
            PaginatedResponse with data and pagination info
        """
        data = self.fetch_all(limit=limit, **kwargs)
        
        # Create pagination info
        offset = kwargs.get("offset", 0)
        page_size = kwargs.get("limit", self.default_page_size)
        pagination_info = PaginationInfo.from_offset(
            offset=offset,
            limit=page_size,
            total_returned=len(data),
            requested_limit=limit or page_size
        )
        
        return PaginatedResponse(
            data=data,
            pagination=pagination_info
        )
    
    def iter_pages(
        self,
        page_size: int | None = None,
        **kwargs
    ) -> Generator[T, None, None]:
        """Iterator that yields items one page at a time.
        
        Args:
            page_size: Number of items per page
            **kwargs: Additional parameters to pass to the fetch function
            
        Yields:
            Items one at a time
        """
        if page_size is None:
            page_size = self.default_page_size
        
        params = kwargs.copy()
        params["limit"] = page_size
        
        while True:
            # Fetch page
            page_data, has_more = self.strategy.fetch_page(**params)
            
            # Yield each item
            for item in page_data:
                yield item
            
            # Check if we should continue
            if not has_more:
                break
            
            # Update parameters for next page
            params = self.strategy.get_next_page_params(params)


def create_offset_paginator(
    fetch_func: Callable[..., list[dict[str, Any]]],
    model_class: type[T],
    config: Any,
    initial_offset: int = 0
) -> Paginator[T]:
    """Create a paginator with offset-based pagination strategy.
    
    Args:
        fetch_func: Function to fetch raw data
        model_class: Pydantic model class to validate data
        config: Configuration object with pagination settings
        initial_offset: Starting offset
        
    Returns:
        Configured Paginator instance
    """
    strategy = OffsetPaginationStrategy(
        fetch_func=fetch_func,
        model_class=model_class,
        page_size=config.default_page_size,
        max_page_size=config.max_page_size,
        initial_offset=initial_offset
    )
    
    return Paginator(
        strategy=strategy,
        default_page_size=config.default_page_size,
        max_total_results=config.max_total_results,
        auto_paginate=config.enable_auto_pagination
    )