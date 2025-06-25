from .abstract_execution_connector import ExecutionConnector
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
from typing import List, Dict

class PolymarketExecutionConnector(ExecutionConnector):
    def __init__(self, host: str, key: str, chain_id: int,
                 signature_type: int = 0, funder: str = None):
        self.host = host
        self.key = key
        self.chain_id = chain_id
        self.signature_type = signature_type
        self.funder = funder
        self.client: ClobClient = None

    def connect(self):
        self.client = ClobClient(
            self.host,
            key=self.key,
            chain_id=self.chain_id,
            signature_type=self.signature_type,
            funder=self.funder
        )
        api_creds = self.client.create_or_derive_api_creds()
        self.client.set_api_creds(api_creds)

    def place_order(self, market: str, side: str, price: float, size: float) -> Dict:
        order_args = OrderArgs(
            price=price,
            size=size,
            side=BUY if side.upper() == "BUY" else SELL,
            token_id=market,
        )
        signed = self.client.create_order(order_args)
        resp = self.client.post_order(signed, OrderType.GTC)
        return resp

    def cancel_order(self, order_id: str) -> Dict:
        return self.client.post_cancel(order_id)

    def get_open_positions(self) -> List[Dict]:
        return self.client.get_user_positions()

    def execute_cycle(self):
        # Optionally fetch order updates, refresh allowances, etc.
        pass

    def disconnect(self):
        self.client = None
