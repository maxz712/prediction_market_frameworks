from abc import ABC, abstractmethod
from typing import Dict, List, Any
from src.data_frameworks.ports.base_port import BasePort


class OrchestratorPort(BasePort, ABC):
    """Interface for prediction market orchestrators."""
    
    @abstractmethod
    def start(self):
        """Start the orchestrator."""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the orchestrator."""
        pass
    
    @abstractmethod
    def register_adapter(self, name: str, adapter: Any):
        """Register an adapter with the orchestrator."""
        pass
    
    @abstractmethod
    def get_adapter(self, name: str) -> Any:
        """Get a registered adapter by name."""
        pass
    
    @abstractmethod
    def list_adapters(self) -> List[str]:
        """List all registered adapter names."""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        pass
    
    @abstractmethod
    def get_events(self, adapter_name: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Get events from prediction market sources."""
        pass
    
    @abstractmethod
    def get_markets(self, adapter_name: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Get markets from prediction market sources."""
        pass
    
    @abstractmethod
    def get_order_books(self, adapter_name: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Get order books from prediction market sources."""
        pass