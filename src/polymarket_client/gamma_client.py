import datetime
import warnings
from collections.abc import Generator
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .configs.polymarket_configs import PolymarketConfig
from .exceptions import (
    PolymarketAPIError,
    PolymarketNetworkError,
    PolymarketValidationError,
)
from .models import Event, PaginatedResponse, PaginationInfo


class GammaClient:
    """Client for interacting with Polymarket Gamma API.
    
    Handles event and market data retrieval from the Gamma API service.
    Follows industry best practices for configuration management and error handling.
    """

    def __init__(self, config: PolymarketConfig) -> None:
        """Initialize the Gamma client.
        
        Args:
            config: Polymarket configuration with endpoints and settings
        """
        self.config = config
        self.base_url = config.get_endpoint("gamma")
        self._session = self._init_session()

    @classmethod
    def from_config(cls, config: PolymarketConfig) -> "GammaClient":
        """Create GammaClient from configuration object."""
        return cls(config)

    @classmethod
    def from_env(cls) -> "GammaClient":
        """Create GammaClient from environment variables."""
        config = PolymarketConfig.from_env()
        return cls(config)

    @classmethod
    def from_url(cls, url: str, **config_kwargs) -> "GammaClient":
        """Create GammaClient from URL (backward compatibility).
        
        Args:
            url: Gamma API base URL
            **config_kwargs: Additional configuration parameters
        """
        # Set minimal required config for other endpoints
        endpoints = {
            "gamma": url,
            "clob": config_kwargs.pop("clob_url", "https://clob.polymarket.com"),
            "info": config_kwargs.pop("info_url", "https://strapi-matic.polymarket.com"),
            "neg_risk": config_kwargs.pop("neg_risk_url", "https://neg-risk-api.polymarket.com")
        }

        config = PolymarketConfig(
            endpoints=endpoints,
            api_key=config_kwargs.pop("api_key", ""),
            api_secret=config_kwargs.pop("api_secret", ""),
            api_passphrase=config_kwargs.pop("api_passphrase", ""),
            pk=config_kwargs.pop("pk", ""),
            **config_kwargs
        )
        return cls(config)

    def _init_session(self) -> requests.Session:
        """Initialize session with configuration-based settings."""
        session = requests.Session()

        # Configure retry strategy from config
        retry = Retry(
            total=self.config.max_retries,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        # Set timeout from config
        session.timeout = self.config.timeout

        # Set standard headers
        session.headers.update({
            "User-Agent": f"polymarket-sdk/{self.config.sdk_version}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

        return session

    def get_events(
        self,
        # Pagination parameters
        limit: int | None = None,
        offset: int = 0,
        auto_paginate: bool | None = None,
        # Sorting parameters
        order: str | None = None,
        ascending: bool = True,
        # ID and slug filters
        event_id: int | list[int] | None = None,
        slug: str | list[str] | None = None,
        # Status filters
        archived: bool | None = None,
        active: bool | None = True,
        closed: bool | None = False,
        # Volume and liquidity filters
        liquidity_min: float | None = None,
        liquidity_max: float | None = None,
        volume_min: float | None = None,
        volume_max: float | None = None,
        # Date filters
        start_date_min: str | None = None,
        start_date_max: str | None = None,
        end_date_min: str | None = None,
        end_date_max: str | None = None,
        # Tag filters
        tag: str | list[str] | None = None,
        tag_id: int | list[int] | None = None,
        related_tags: bool | None = None,
        tag_slug: str | list[str] | None = None
    ) -> list[Event]:
        """Retrieves events from the Gamma API.
        
        Args:
            limit: Maximum number of events to return total (uses config default if None)
            offset: Offset for pagination
            auto_paginate: Whether to automatically paginate through all results (uses config default if None)
            order: Key to sort by
            ascending: Sort direction, defaults to True (requires order parameter)
            event_id: ID of a single event to query, can be int or list of ints
            slug: Slug of a single event to query, can be string or list of strings
            archived: Filter by archived status
            active: Filter for active events
            closed: Filter for closed events
            liquidity_min: Filter by minimum liquidity
            liquidity_max: Filter by maximum liquidity
            volume_min: Filter by minimum volume
            volume_max: Filter by maximum volume
            start_date_min: Filter by minimum start date (ISO format)
            start_date_max: Filter by maximum start date (ISO format)
            end_date_min: Minimum end date filter (ISO format)
            end_date_max: Filter by maximum end date (ISO format)
            tag: Filter by tag labels, can be string or list of strings
            tag_id: Filter by tag ID, can be int or list of ints
            related_tags: Include events with related tags (requires tag_id parameter)
            tag_slug: Filter by tag slug, can be string or list of strings
            
        Returns:
            List of Event objects
            
        Raises:
            PolymarketValidationError: If parameters are invalid
            PolymarketNetworkError: If network request fails
            PolymarketAPIError: If API returns an error
        """
        # Use config defaults
        if limit is None:
            limit = self.config.default_page_size
        if auto_paginate is None:
            auto_paginate = self.config.enable_auto_pagination

        # Validate and warn about large requests
        self._validate_and_warn_limit(limit, auto_paginate)

        # For backward compatibility, return just the events
        paginated_response = self.get_events_paginated(
            limit=limit,
            offset=offset,
            auto_paginate=auto_paginate,
            order=order,
            ascending=ascending,
            event_id=event_id,
            slug=slug,
            archived=archived,
            active=active,
            closed=closed,
            liquidity_min=liquidity_min,
            liquidity_max=liquidity_max,
            volume_min=volume_min,
            volume_max=volume_max,
            start_date_min=start_date_min,
            start_date_max=start_date_max,
            end_date_min=end_date_min,
            end_date_max=end_date_max,
            tag=tag,
            tag_id=tag_id,
            related_tags=related_tags,
            tag_slug=tag_slug
        )

        return paginated_response.data

    def get_events_paginated(
        self,
        # Pagination parameters
        limit: int | None = None,
        offset: int = 0,
        auto_paginate: bool | None = None,
        # Sorting parameters
        order: str | None = None,
        ascending: bool = True,
        # ID and slug filters
        event_id: int | list[int] | None = None,
        slug: str | list[str] | None = None,
        # Status filters
        archived: bool | None = None,
        active: bool | None = True,
        closed: bool | None = False,
        # Volume and liquidity filters
        liquidity_min: float | None = None,
        liquidity_max: float | None = None,
        volume_min: float | None = None,
        volume_max: float | None = None,
        # Date filters
        start_date_min: str | None = None,
        start_date_max: str | None = None,
        end_date_min: str | None = None,
        end_date_max: str | None = None,
        # Tag filters
        tag: str | list[str] | None = None,
        tag_id: int | list[int] | None = None,
        related_tags: bool | None = None,
        tag_slug: str | list[str] | None = None
    ) -> PaginatedResponse[Event]:
        """Retrieves events from the Gamma API with pagination metadata.
        
        Args:
            limit: Maximum number of events to return total (uses config default if None)
            offset: Offset for pagination
            auto_paginate: Whether to automatically paginate through all results (uses config default if None)
            order: Key to sort by
            ascending: Sort direction, defaults to True (requires order parameter)
            event_id: ID of a single event to query, can be int or list of ints
            slug: Slug of a single event to query, can be string or list of strings
            archived: Filter by archived status
            active: Filter for active events
            closed: Filter for closed events
            liquidity_min: Filter by minimum liquidity
            liquidity_max: Filter by maximum liquidity
            volume_min: Filter by minimum volume
            volume_max: Filter by maximum volume
            start_date_min: Filter by minimum start date (ISO format)
            start_date_max: Filter by maximum start date (ISO format)
            end_date_min: Minimum end date filter (ISO format)
            end_date_max: Filter by maximum end date (ISO format)
            tag: Filter by tag labels, can be string or list of strings
            tag_id: Filter by tag ID, can be int or list of ints
            related_tags: Include events with related tags (requires tag_id parameter)
            tag_slug: Filter by tag slug, can be string or list of strings
            
        Returns:
            PaginatedResponse containing Event objects and pagination info
            
        Raises:
            PolymarketValidationError: If parameters are invalid
            PolymarketNetworkError: If network request fails
            PolymarketAPIError: If API returns an error
        """
        # Use config defaults
        if limit is None:
            limit = self.config.default_page_size
        if auto_paginate is None:
            auto_paginate = self.config.enable_auto_pagination

        # Validate and warn about large requests
        self._validate_and_warn_limit(limit, auto_paginate)

        # Validate parameter combinations
        self._validate_parameters(order, ascending, tag_id, related_tags)

        url = f"{self.base_url}/events"

        # Determine page size for API requests
        page_size = min(limit, self.config.max_page_size) if not auto_paginate else self.config.default_page_size

        # Build parameters dict with all possible filters
        params = {
            "limit": page_size,
            "offset": offset
        }

        # Add optional parameters only if they are provided
        if order is not None:
            params["order"] = order
            params["ascending"] = str(ascending).lower()

        # Handle ID parameters (can be single value or list)
        if event_id is not None:
            if isinstance(event_id, list):
                params["id"] = [str(eid) for eid in event_id]
            else:
                params["id"] = str(event_id)

        # Handle slug parameters (can be single value or list)
        if slug is not None:
            if isinstance(slug, list):
                params["slug"] = slug
            else:
                params["slug"] = slug

        # Status filters
        if archived is not None:
            params["archived"] = str(archived).lower()
        if active is not None:
            params["active"] = str(active).lower()
        if closed is not None:
            params["closed"] = str(closed).lower()

        # Volume and liquidity filters
        if liquidity_min is not None:
            params["liquidity_min"] = str(liquidity_min)
        if liquidity_max is not None:
            params["liquidity_max"] = str(liquidity_max)
        if volume_min is not None:
            params["volume_min"] = str(volume_min)
        if volume_max is not None:
            params["volume_max"] = str(volume_max)

        # Date filters
        if start_date_min is not None:
            params["start_date_min"] = start_date_min
        if start_date_max is not None:
            params["start_date_max"] = start_date_max
        if end_date_min is not None:
            params["end_date_min"] = end_date_min
        elif active is True:  # Only set default end_date_min if we're filtering for active events
            params["end_date_min"] = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
        if end_date_max is not None:
            params["end_date_max"] = end_date_max

        # Tag filters
        if tag is not None:
            if isinstance(tag, list):
                params["tag"] = tag
            else:
                params["tag"] = tag

        # Handle tag_id parameters (can be single value or list)
        if tag_id is not None:
            if isinstance(tag_id, list):
                params["tag_id"] = [str(tid) for tid in tag_id]
            else:
                params["tag_id"] = str(tag_id)

        if related_tags is not None:
            params["related_tags"] = str(related_tags).lower()

        # Handle tag_slug parameters (can be single value or list)
        if tag_slug is not None:
            if isinstance(tag_slug, list):
                params["tag_slug"] = tag_slug
            else:
                params["tag_slug"] = tag_slug

        all_events = []
        current_offset = offset

        while True:
            # Create a copy of params for this request
            request_params = params.copy()
            request_params["offset"] = current_offset

            # If we have a specific limit and we're close to it, adjust page size
            if not auto_paginate or (limit and len(all_events) + page_size > limit):
                remaining = limit - len(all_events) if limit else page_size
                if remaining <= 0:
                    break
                request_params["limit"] = min(page_size, remaining)

            try:
                resp = self._session.get(url, params=request_params)
                resp.raise_for_status()
                events = resp.json()
            except requests.RequestException as e:
                raise PolymarketNetworkError(
                    f"Failed to fetch events: {e}",
                    original_error=e,
                    endpoint=url
                )
            except requests.HTTPError as e:
                raise PolymarketAPIError(
                    f"API request failed: {e}",
                    status_code=resp.status_code if "resp" in locals() else None,
                    endpoint=url
                )

            if not isinstance(events, list):
                raise PolymarketAPIError(
                    f"Unexpected response format: expected list, got {type(events).__name__}",
                    response_data=events,
                    endpoint=url
                )

            all_events.extend(events)

            # Stop if we got fewer events than requested, auto_paginate is disabled, or reached limit
            if len(events) < request_params["limit"] or not auto_paginate:
                break

            if limit and len(all_events) >= limit:
                break

            current_offset += request_params["limit"]

        # Truncate to exact limit if specified
        if limit and len(all_events) > limit:
            all_events = all_events[:limit]

        try:
            validated_events = [Event.model_validate(event) for event in all_events]

            # Create pagination info
            pagination_info = PaginationInfo.from_offset(
                offset=offset,
                limit=page_size,
                total_returned=len(validated_events),
                requested_limit=request_params.get("limit", page_size)
            )

            return PaginatedResponse(
                data=validated_events,
                pagination=pagination_info
            )
        except Exception as e:
            raise PolymarketValidationError(
                f"Failed to validate event data: {e}",
                details={"raw_events": all_events}
            )

    def iter_events(
        self,
        # Pagination parameters
        page_size: int | None = None,
        offset: int = 0,
        # Sorting parameters
        order: str | None = None,
        ascending: bool = True,
        # ID and slug filters
        event_id: int | list[int] | None = None,
        slug: str | list[str] | None = None,
        # Status filters
        archived: bool | None = None,
        active: bool | None = True,
        closed: bool | None = False,
        # Volume and liquidity filters
        liquidity_min: float | None = None,
        liquidity_max: float | None = None,
        volume_min: float | None = None,
        volume_max: float | None = None,
        # Date filters
        start_date_min: str | None = None,
        start_date_max: str | None = None,
        end_date_min: str | None = None,
        end_date_max: str | None = None,
        # Tag filters
        tag: str | list[str] | None = None,
        tag_id: int | list[int] | None = None,
        related_tags: bool | None = None,
        tag_slug: str | list[str] | None = None
    ) -> Generator[Event, None, None]:
        """Generator that yields events one page at a time.
        
        This is memory-efficient for processing large datasets.
        
        Args:
            page_size: Number of events per page (uses config default if None)
            offset: Offset for pagination
            order: Key to sort by
            ascending: Sort direction, defaults to True (requires order parameter)
            event_id: ID of a single event to query, can be int or list of ints
            slug: Slug of a single event to query, can be string or list of strings
            archived: Filter by archived status
            active: Filter for active events
            closed: Filter for closed events
            liquidity_min: Filter by minimum liquidity
            liquidity_max: Filter by maximum liquidity
            volume_min: Filter by minimum volume
            volume_max: Filter by maximum volume
            start_date_min: Filter by minimum start date (ISO format)
            start_date_max: Filter by maximum start date (ISO format)
            end_date_min: Minimum end date filter (ISO format)
            end_date_max: Filter by maximum end date (ISO format)
            tag: Filter by tag labels, can be string or list of strings
            tag_id: Filter by tag ID, can be int or list of ints
            related_tags: Include events with related tags (requires tag_id parameter)
            tag_slug: Filter by tag slug, can be string or list of strings
            
        Yields:
            Event objects one at a time
            
        Raises:
            PolymarketValidationError: If parameters are invalid
            PolymarketNetworkError: If network request fails
            PolymarketAPIError: If API returns an error
        """
        if page_size is None:
            page_size = self.config.default_page_size

        # Validate page size
        if page_size > self.config.max_page_size:
            raise PolymarketValidationError(
                f"Page size {page_size} exceeds maximum allowed {self.config.max_page_size}",
                field="page_size",
                value=page_size
            )

        current_offset = offset

        while True:
            # Get one page of events
            page_response = self.get_events_paginated(
                limit=page_size,
                offset=current_offset,
                auto_paginate=False,
                order=order,
                ascending=ascending,
                event_id=event_id,
                slug=slug,
                archived=archived,
                active=active,
                closed=closed,
                liquidity_min=liquidity_min,
                liquidity_max=liquidity_max,
                volume_min=volume_min,
                volume_max=volume_max,
                start_date_min=start_date_min,
                start_date_max=start_date_max,
                end_date_min=end_date_min,
                end_date_max=end_date_max,
                tag=tag,
                tag_id=tag_id,
                related_tags=related_tags,
                tag_slug=tag_slug
            )

            # Yield each event
            for event in page_response.data:
                yield event

            # Stop if we got fewer events than requested (no more pages)
            if not page_response.pagination.has_next:
                break

            current_offset += page_size

    def _validate_and_warn_limit(self, limit: int, auto_paginate: bool) -> None:
        """Validate limit parameters and warn about large requests."""
        if limit > self.config.max_page_size:
            raise PolymarketValidationError(
                f"Limit {limit} exceeds maximum allowed {self.config.max_page_size}",
                field="limit",
                value=limit
            )

        # Warn about potentially large requests
        if self.config.warn_large_requests:
            if auto_paginate and limit > self.config.default_page_size * 10:
                warnings.warn(
                    f"Requesting {limit} events with auto_paginate=True may consume significant memory. "
                    f"Consider using iter_events() for large datasets or set auto_paginate=False.",
                    UserWarning,
                    stacklevel=3
                )
            elif auto_paginate and limit > self.config.max_total_results:
                warnings.warn(
                    f"Requesting {limit} events exceeds recommended maximum of {self.config.max_total_results}. "
                    f"This may cause memory issues. Consider using iter_events() for streaming.",
                    UserWarning,
                    stacklevel=3
                )

    def _validate_parameters(
        self,
        order: str | None,
        ascending: bool,
        tag_id: int | list[int] | None,
        related_tags: bool | None
    ) -> None:
        """Validate parameter combinations and requirements."""
        # ascending parameter requires order parameter
        if order is None and ascending is not True:
            raise PolymarketValidationError(
                "The 'ascending' parameter requires the 'order' parameter to be specified",
                field="ascending",
                value=ascending
            )

        # related_tags parameter requires tag_id parameter
        if related_tags is not None and tag_id is None:
            raise PolymarketValidationError(
                "The 'related_tags' parameter requires the 'tag_id' parameter to be specified",
                field="related_tags",
                value=related_tags
            )

    def health_check(self) -> dict[str, Any]:
        """Check if the Gamma API is accessible.
        
        Returns:
            Dictionary with health status information
        """
        try:
            url = f"{self.base_url}/health"
            resp = self._session.get(url, timeout=5)
            resp.raise_for_status()
            return {
                "status": "healthy",
                "endpoint": self.base_url,
                "response_time_ms": resp.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "endpoint": self.base_url,
                "error": str(e)
            }
