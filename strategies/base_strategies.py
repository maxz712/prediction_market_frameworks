from abc import ABC, abstractmethod
from typing import List, Dict

class BaseStrategy(ABC):
    def __init__(self,
                 data_conns: List = None,
                 exec_conns: List = None):
        self.data_conns = data_conns or []
        self.exec_conns = exec_conns or []

    @abstractmethod
    def on_tick(self, data: Dict[str, dict]):
        """
        Called each cycle. 'data' maps connector names to market data dicts.
        Place logic and order placement here.
        """
        pass
