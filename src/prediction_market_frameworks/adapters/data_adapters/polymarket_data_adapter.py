import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List, Dict


from src.prediction_market_frameworks.adapters.polymarket_configs import PolymarketConfig
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderBookSummary

from src.prediction_market_frameworks.core.models.order_book import BookLevel, OrderBook
from src.prediction_market_frameworks.ports.data_port import DataPort


class PolymarketDataAdapter(DataPort):
    EVENTS_PATH = "/events"

    def __init__(self, config: PolymarketConfig):
        self.config = config
        self.client: ClobClient = None
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

    def connect(self):
        if self.client is None:
            self.client = ClobClient(
                self.config.hosts["clob"],
                key=self.config.pk,
                chain_id=self.config.chain_id,
                creds=ApiCreds(
                    api_key=self.config.api_key,
                    api_secret=self.config.api_secret,
                    api_passphrase=self.config.api_passphrase,
                ),
            )

    def disconnect(self):
        self.client = None

    def _ensure_connected(self):
        if self.client is None:
            self.connect()

    def get_market(self, condition_id: str) -> str:
        self._ensure_connected()
        return self.client.get_market(condition_id)

    def get_order_book(self, token_id: str) -> OrderBook:
        self._ensure_connected()
        summary = self.client.get_order_book(token_id)
        bids = self._convert_levels(summary.bids)
        asks = self._convert_levels(summary.asks)
        return OrderBook(
            market_id=summary.market,
            asset_id=summary.asset_id,
            timestamp=int(summary.timestamp),
            hash=summary.hash,
            bids=bids,
            asks=asks
        )

    def _convert_levels(self, raw_levels) -> list[BookLevel]:
        """
        Convert a list of summary-level objects to sorted BookLevel list.
        raw_levels: sequence of objects with 'price' and 'size' (strings or numbers).
        """
        # Parse price and volume
        parsed = [(float(r.price), float(r.size)) for r in raw_levels]

        # Sort: bids descending, asks ascending
        # Determine side by checking first price (but typically adapter knows side)
        is_bid = bool(parsed and parsed[0][0] >= parsed[-1][0])
        sorted_levels = sorted(parsed, key=lambda p: -p[0]) if is_bid else sorted(parsed, key=lambda p: p[0])

        levels = []
        total = 0.0
        for price, vol in sorted_levels:
            total += vol
            levels.append(BookLevel(price=price, volume=vol, total=total))
        return levels

    def get_active_events(self, limit: int = 100) -> List[Dict]:
        """
        Retrieves all currently *ongoing* events: active=true & closed=false, optionally filtering by future end dates.
        """
        base = self.config.hosts["gamma"].rstrip("/")
        url = f"{base}{self.EVENTS_PATH}"
        now_iso = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
        params = {
            "active": "true",
            "closed": "false",
            "end_date_min": now_iso,
            "limit": limit,
            "offset": 0
        }
        all_events = []
        while True:
            resp = self._session.get(url, params=params)
            resp.raise_for_status()
            events = resp.json()
            if not isinstance(events, list):
                raise RuntimeError(f"Unexpected payload: {events}")
            all_events.extend(events)
            if len(events) < limit:
                break
            params["offset"] += limit

        return all_events
