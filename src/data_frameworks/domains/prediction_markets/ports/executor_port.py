from abc import ABC, abstractmethod

from src.data_frameworks.domains.prediction_markets.ports.orchestrator_port import OrchestratorPort
from src.data_frameworks.ports.base_port import BasePort


class ExecutorPort(OrchestratorPort, ABC):
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
