from abc import ABC, abstractmethod

from src.prediction_market_frameworks.ports.port import Port


class ExecutorPort(Port, ABC):
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
