from abc import ABC, abstractmethod

class Connector(ABC):
    """Shared lifecycle interface for all connectors."""
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass
