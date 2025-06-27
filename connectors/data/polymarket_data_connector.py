import os
from typing import List, Dict

from .abstract_data_connector import DataConnector
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OpenOrderParams

class PolymarketDataConnector(DataConnector):
    def __init__(self, host: str, chain_id: int):
        self.host = host
        self.chain_id = chain_id
        self.client: ClobClient = None
        self.pk = os.getenv("PK")
        self.api_creds = ApiCreds(
            api_key=os.getenv("CLOB_API_KEY"),
            api_secret=os.getenv("CLOB_SECRET"),
            api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
        )

    def connect(self):
        if self.client is None:
            self.client = ClobClient(
                self.host,
                key=self.pk,
                chain_id=self.chain_id,
                creds=self.api_creds
            )

    def disconnect(self):
        self.client = None

    def _ensure_connected(self):
        if self.client is None:
            self.connect()

    def get_active_events(self) -> List[Dict]:
        """
        Returns list of active events, each with associated markets and token_ids/condition_ids.
        """
        self._ensure_connected()
        events = self.client.get_events(active=True)
        result = []
        for ev in events:
            markets = self.client.get_markets(condition_ids=[ev["id"]])
            enriched = {
                "event": ev,
                "markets": [
                    {
                        "market": m,
                        "condition_id": m["condition_id"],
                        "token_ids": [t["token_id"] for t in m["tokens"]]
                    } for m in markets
                ]
            }
            result.append(enriched)
        return result

    def search_event(self, slug: str) -> Dict:
        """
        Returns event by slug, including its markets.
        """
        self._ensure_connected()
        evs = self.client.get_events(slug=[slug])
        if not evs:
            raise KeyError(f"No event found with slug '{slug}'")
        ev = evs[0]
        markets = self.client.get_markets(condition_ids=[ev["id"]])
        ev["markets"] = markets
        return ev

    def get_token_ids_by_condition(self, condition_id: str) -> List[str]:
        """
        Returns token IDs for all tokens under markets matching condition_id.
        """
        self._ensure_connected()
        markets = self.client.get_markets(condition_ids=[condition_id])
        token_ids = []
        for m in markets:
            token_ids.extend([t["token_id"] for t in m["tokens"]])
        return token_ids

    def get_order_book(self, token_ids: List[str]) -> Dict[str, List[Dict]]:
        """
        Returns order book per token_id.
        """
        self._ensure_connected()
        order_books = {}
        for tid in token_ids:
            resp = self.client.get_orders(OpenOrderParams(asset_id=tid))
            order_books[tid] = resp
        return order_books

    def get_market_resolution(self, token_id: str) -> str:
        """
        Returns the resolution condition/criteria for a given market token.

        :param token_id: The unique token ID for the market.
        :return: The resolution condition string.
        """
        self._ensure_connected()
        market = self.client.get_market(token_id)
        # According to API, 'condition_id' corresponds to CTF condition;
        # resolution criteria is part of market metadata.
        for key in ["resolution_criteria", "resolution_source", "resolutionCondition", "resolution_condition"]:
            if key in market:
                return market[key]
        raise ValueError(
            f"Resolution condition not found for market {token_id}. Keys available: {list(market.keys())}"
        )
