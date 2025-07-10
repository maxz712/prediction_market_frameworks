import datetime
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models.event import Event
from .configs.polymarket_configs import PolymarketConfig
from .exceptions import (
    PolymarketAPIError, 
    PolymarketNetworkError, 
    PolymarketValidationError
)


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
    def from_config(cls, config: PolymarketConfig) -> 'GammaClient':
        """Create GammaClient from configuration object."""
        return cls(config)
    
    @classmethod
    def from_env(cls) -> 'GammaClient':
        """Create GammaClient from environment variables."""
        config = PolymarketConfig.from_env()
        return cls(config)
    
    @classmethod
    def from_url(cls, url: str, **config_kwargs) -> 'GammaClient':
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
            'User-Agent': f'polymarket-sdk/{self.config.sdk_version}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        
        return session

    def get_events(
        self, 
        active: bool = True, 
        closed: bool = False,
        end_date_min: Optional[str] = None, 
        limit: Optional[int] = None,
        offset: int = 0,
        auto_paginate: Optional[bool] = None
    ) -> List[Event]:
        """Retrieves events from the Gamma API.
        
        Args:
            active: Filter for active events
            closed: Filter for closed events
            end_date_min: Minimum end date filter (ISO format)
            limit: Maximum number of events to return per request (uses config default if None)
            offset: Offset for pagination
            auto_paginate: Whether to automatically paginate through all results (uses config default if None)
            
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
        
        # Validate parameters
        if limit > self.config.max_page_size:
            raise PolymarketValidationError(
                f"Limit {limit} exceeds maximum allowed {self.config.max_page_size}",
                field="limit",
                value=limit
            )
        
        url = f"{self.base_url}/events"
        
        if end_date_min is None:
            end_date_min = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
        
        params = {
            "active": str(active).lower(),
            "closed": str(closed).lower(),
            "end_date_min": end_date_min,
            "limit": limit,
            "offset": offset
        }
        
        all_events = []
        current_offset = offset
        
        while True:
            params["offset"] = current_offset
            
            try:
                resp = self._session.get(url, params=params)
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
                    status_code=resp.status_code if 'resp' in locals() else None,
                    endpoint=url
                )
            
            if not isinstance(events, list):
                raise PolymarketAPIError(
                    f"Unexpected response format: expected list, got {type(events).__name__}",
                    response_data=events,
                    endpoint=url
                )
            
            all_events.extend(events)
            
            # Stop if we got fewer events than requested or if auto_paginate is disabled
            if len(events) < limit or not auto_paginate:
                break
                
            current_offset += limit

        try:
            return [Event.model_validate(event) for event in all_events]
        except Exception as e:
            raise PolymarketValidationError(
                f"Failed to validate event data: {e}",
                details={"raw_events": all_events}
            )

    def get_markets(self, market_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve market data from Gamma API.
        
        Args:
            market_id: Optional market identifier
            
        Returns:
            Market data dictionary
            
        Raises:
            NotImplementedError: This endpoint is not yet implemented
        """
        raise NotImplementedError("get_markets endpoint not yet implemented")

    def health_check(self) -> Dict[str, Any]:
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