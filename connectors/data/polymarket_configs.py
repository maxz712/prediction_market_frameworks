from dataclasses import dataclass

@dataclass
class PolymarketConfig:
    hosts: dict
    chain_id: int
    api_key: str
    api_secret: str
    api_passphrase: str
    pk: str