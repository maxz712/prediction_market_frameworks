from .abstract_data_connector import DataConnector
from py_clob_client.client import ClobClient
from typing import List, Dict

class PolymarketDataConnector(DataConnector):
    """
    Fetches real-time market data from Polymarket's CLOB via py-clob-client.
    """

    def __init__(self, host: str, key: str, chain_id: int, markets: List[str]):
        self.host = host
        self.key = key
        self.chain_id = chain_id
        self.markets = markets
        self.client: ClobClient = None

    def connect(self):
        # Initialize and authenticate the client
        self.client = ClobClient(self.host, key=self.key, chain_id=self.chain_id)
        self.client.set_api_creds(self.client.create_or_derive_api_creds())
        # No persistent connections yet; REST/WebSocket if needed

    def get_market_data(self) -> Dict[str]:
        data = {}
        for token_id in self.markets:
            resp = self.client.get_price(token_id=token_id)
            data[token_id] = resp  # resp contains price, book, etc.
        return data

    def disconnect(self):
        # No teardown required for REST; include cleanup logic if necessary
        self.client = None
