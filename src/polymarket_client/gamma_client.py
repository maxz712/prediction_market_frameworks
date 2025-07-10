import datetime
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models.event import Event
from .exceptions import PolymarketAPIError, PolymarketNetworkError


class GammaClient:
    """Client for interacting with Polymarket Gamma API.
    
    Handles event and market data retrieval from the Gamma API service.
    """
    
    def __init__(self, base_url: str) -> None:
        """Initialize the Gamma client.
        
        Args:
            base_url: Base URL for the Gamma API
        """
        self.base_url = base_url.rstrip("/")
        self._session = self._init_session()

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3, backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def get_events(
        self, 
        active: bool = True, 
        closed: bool = False,
        end_date_min: Optional[str] = None, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Event]:
        """
        Retrieves events from the Gamma API.
        
        Args:
            active: Filter for active events
            closed: Filter for closed events
            end_date_min: Minimum end date filter (ISO format)
            limit: Maximum number of events to return per request
            offset: Offset for pagination
            
        Returns:
            List of Event objects
        """
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
                raise PolymarketNetworkError(f"Failed to fetch events: {e}", original_error=e)
            except requests.HTTPError as e:
                raise PolymarketAPIError(
                    f"API request failed: {e}",
                    status_code=resp.status_code if 'resp' in locals() else None
                )
            
            if not isinstance(events, list):
                raise RuntimeError(f"Unexpected payload: {events}")
            
            all_events.extend(events)
            
            if len(events) < limit:
                break
                
            current_offset += limit

        return [Event.model_validate(event) for event in all_events]

    def get_markets(self, market_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Skeleton method for retrieving market data from Gamma API.
        To be implemented later.
        
        Args:
            market_id: Optional market identifier
            
        Returns:
            Market data dictionary
        """
        raise NotImplementedError("get_markets endpoint not yet implemented")
