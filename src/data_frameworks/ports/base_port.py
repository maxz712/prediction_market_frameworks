from abc import ABC, abstractmethod


class BasePort(ABC):
    """Common port interface for all data framework connectors."""
    
    @abstractmethod
    def connect(self):
        """Establish connection to the external service."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection to the external service."""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the connection is healthy."""
        pass