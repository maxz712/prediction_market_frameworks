from connectors.abstract_connector import Connector
from abc import ABC, abstractmethod

class ExecutionConnector(Connector, ABC):
    """Interface for submitting and managing trades."""

    @abstractmethod
    def place_order(self, market:str, side:str, price:float, size:float):
        pass

    @abstractmethod
    def cancel_order(self, order_id:str):
        pass

    @abstractmethod
    def get_open_positions(self):
        pass

    def execute_cycle(self):
        """Optional periodic processing (fills, status)."""
        pass
