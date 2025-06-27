from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from connectors.data.abstract_data_connector import DataConnector
from connectors.execution.abstract_execution_connector import ExecutionConnector


class BaseStrategy(ABC):
    def __init__(self,
                 data_conns: Optional[List[DataConnector]] = None,
                 exec_conns: Optional[List[ExecutionConnector]] = None):
        self.data_conns = data_conns or []
        self.exec_conns = exec_conns or []

    @abstractmethod
    def on_tick(self, data: Dict[str, dict]):
        """
        Called each cycle. 'data' maps connector names to market data dicts.
        Place logic and order placement here.
        """
        pass
