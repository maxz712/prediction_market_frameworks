"""Mixin class to add unified pagination capabilities to clients."""

from collections.abc import Callable, Generator
from typing import Any, TypeVar

from pydantic import BaseModel

from ..models.pagination import PaginatedResponse
from ..pagination import Paginator, create_offset_paginator

T = TypeVar("T", bound=BaseModel)


class PaginationMixin:
    """Mixin class that provides unified pagination methods."""
    
    def _create_paginated_fetcher(
        self,
        fetch_func: Callable[..., list[dict[str, Any]]],
        model_class: type[T],
        initial_offset: int = 0
    ) -> Paginator[T]:
        """Create a paginator for a given fetch function and model class.
        
        Args:
            fetch_func: Function that fetches raw data from the API
            model_class: Pydantic model class to validate the data
            initial_offset: Starting offset for pagination
            
        Returns:
            Configured Paginator instance
        """
        # Ensure self has a config attribute
        if not hasattr(self, "config"):
            raise AttributeError(
                "PaginationMixin requires the class to have a 'config' attribute"
            )
        
        return create_offset_paginator(
            fetch_func=fetch_func,
            model_class=model_class,
            config=self.config,
            initial_offset=initial_offset
        )
    
    def _paginated_fetch(
        self,
        endpoint: str,
        model_class: type[T],
        params: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int = 0,
        auto_paginate: bool | None = None
    ) -> list[T]:
        """Fetch paginated data from an endpoint.
        
        Args:
            endpoint: API endpoint to fetch from
            model_class: Pydantic model class to validate data
            params: Query parameters
            limit: Maximum number of items to fetch
            offset: Starting offset
            auto_paginate: Whether to auto-paginate
            
        Returns:
            List of validated model instances
        """
        if params is None:
            params = {}
        
        # Create fetch function for this endpoint
        def fetch_func(**kwargs) -> list[dict[str, Any]]:
            # Merge params with kwargs
            request_params = {**params, **kwargs}
            
            # Make request (assuming self has _session)
            if not hasattr(self, "_session"):
                raise AttributeError(
                    "PaginationMixin requires the class to have a '_session' attribute"
                )
            
            resp = self._session.get(endpoint, params=request_params)
            resp.raise_for_status()
            return resp.json()
        
        # Create paginator
        paginator = self._create_paginated_fetcher(
            fetch_func=fetch_func,
            model_class=model_class,
            initial_offset=offset
        )
        
        # Override auto_paginate if specified
        if auto_paginate is not None:
            paginator.auto_paginate = auto_paginate
        
        # Fetch data
        return paginator.fetch_all(limit=limit, offset=offset)
    
    def _paginated_response(
        self,
        endpoint: str,
        model_class: type[T],
        params: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int = 0,
        auto_paginate: bool | None = None
    ) -> PaginatedResponse[T]:
        """Fetch paginated data with metadata from an endpoint.
        
        Args:
            endpoint: API endpoint to fetch from
            model_class: Pydantic model class to validate data
            params: Query parameters
            limit: Maximum number of items to fetch
            offset: Starting offset
            auto_paginate: Whether to auto-paginate
            
        Returns:
            PaginatedResponse with data and pagination info
        """
        if params is None:
            params = {}
        
        # Create fetch function for this endpoint
        def fetch_func(**kwargs) -> list[dict[str, Any]]:
            # Merge params with kwargs
            request_params = {**params, **kwargs}
            
            # Make request
            if not hasattr(self, "_session"):
                raise AttributeError(
                    "PaginationMixin requires the class to have a '_session' attribute"
                )
            
            resp = self._session.get(endpoint, params=request_params)
            resp.raise_for_status()
            return resp.json()
        
        # Create paginator
        paginator = self._create_paginated_fetcher(
            fetch_func=fetch_func,
            model_class=model_class,
            initial_offset=offset
        )
        
        # Override auto_paginate if specified
        if auto_paginate is not None:
            paginator.auto_paginate = auto_paginate
        
        # Fetch paginated response
        return paginator.fetch_paginated(limit=limit, offset=offset)
    
    def _paginated_iter(
        self,
        endpoint: str,
        model_class: type[T],
        params: dict[str, Any] | None = None,
        page_size: int | None = None,
        offset: int = 0
    ) -> Generator[T, None, None]:
        """Create an iterator for paginated data from an endpoint.
        
        Args:
            endpoint: API endpoint to fetch from
            model_class: Pydantic model class to validate data
            params: Query parameters
            page_size: Number of items per page
            offset: Starting offset
            
        Yields:
            Validated model instances one at a time
        """
        if params is None:
            params = {}
        
        # Create fetch function for this endpoint
        def fetch_func(**kwargs) -> list[dict[str, Any]]:
            # Merge params with kwargs
            request_params = {**params, **kwargs}
            
            # Make request
            if not hasattr(self, "_session"):
                raise AttributeError(
                    "PaginationMixin requires the class to have a '_session' attribute"
                )
            
            resp = self._session.get(endpoint, params=request_params)
            resp.raise_for_status()
            return resp.json()
        
        # Create paginator
        paginator = self._create_paginated_fetcher(
            fetch_func=fetch_func,
            model_class=model_class,
            initial_offset=offset
        )
        
        # Return iterator
        yield from paginator.iter_pages(page_size=page_size, offset=offset)