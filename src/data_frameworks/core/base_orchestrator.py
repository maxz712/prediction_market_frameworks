from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional


class BaseOrchestrator(ABC):
    """Base orchestrator class with shared functionality across domains."""
    
    def __init__(self):
        self._adapters: Dict[str, Any] = {}
        self._is_running = False
    
    def register_adapter(self, name: str, adapter: Any):
        """Register an adapter with the orchestrator."""
        self._adapters[name] = adapter
    
    def get_adapter(self, name: str) -> Optional[Any]:
        """Get a registered adapter by name."""
        return self._adapters.get(name)
    
    def list_adapters(self) -> List[str]:
        """List all registered adapter names."""
        return list(self._adapters.keys())
    
    @abstractmethod
    def start(self):
        """Start the orchestrator."""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the orchestrator."""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, bool]:
        """Check health of all registered adapters."""
        pass
    
    def is_running(self) -> bool:
        """Check if orchestrator is running."""
        return self._is_running