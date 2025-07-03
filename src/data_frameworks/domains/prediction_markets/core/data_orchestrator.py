from typing import Dict, List, Any
from src.data_frameworks.core.base_orchestrator import BaseOrchestrator


class DataOrchestrator(BaseOrchestrator):
    """Orchestrator for prediction market data operations."""
    
    def __init__(self):
        super().__init__()
        self.name = "prediction_markets"
    
    def start(self):
        """Start the prediction market data orchestrator."""
        if self._is_running:
            return
        
        # Connect all registered adapters
        for adapter in self._adapters.values():
            if hasattr(adapter, 'connect'):
                adapter.connect()
        
        self._is_running = True
    
    def stop(self):
        """Stop the prediction market data orchestrator."""
        if not self._is_running:
            return
        
        # Disconnect all adapters
        for adapter in self._adapters.values():
            if hasattr(adapter, 'disconnect'):
                adapter.disconnect()
        
        self._is_running = False
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all prediction market adapters."""
        health_status = {}
        for name, adapter in self._adapters.items():
            if hasattr(adapter, 'health_check'):
                health_status[name] = adapter.health_check()
            else:
                health_status[name] = True
        return health_status
    
    def get_events(self, adapter_name: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Get events from prediction market sources."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if adapter_name and adapter_name in self._adapters:
            adapter = self._adapters[adapter_name]
            if hasattr(adapter, 'get_active_events'):
                return adapter.get_active_events(**kwargs)
        
        # Try all adapters if no specific one specified
        for adapter in self._adapters.values():
            if hasattr(adapter, 'get_active_events'):
                try:
                    return adapter.get_active_events(**kwargs)
                except:
                    continue
        
        return []
    
    def get_markets(self, adapter_name: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Get markets from prediction market sources."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        markets = []
        if adapter_name and adapter_name in self._adapters:
            adapter = self._adapters[adapter_name]
            if hasattr(adapter, 'get_market'):
                try:
                    market = adapter.get_market(**kwargs)
                    markets.append(market.model_dump() if hasattr(market, 'model_dump') else market)
                except:
                    pass
        else:
            # Try all adapters
            for adapter in self._adapters.values():
                if hasattr(adapter, 'get_market'):
                    try:
                        market = adapter.get_market(**kwargs)
                        markets.append(market.model_dump() if hasattr(market, 'model_dump') else market)
                    except:
                        continue
        
        return markets
    
    def get_order_books(self, adapter_name: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Get order books from prediction market sources."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        order_books = []
        if adapter_name and adapter_name in self._adapters:
            adapter = self._adapters[adapter_name]
            if hasattr(adapter, 'get_order_book'):
                try:
                    order_book = adapter.get_order_book(**kwargs)
                    order_books.append(order_book.model_dump() if hasattr(order_book, 'model_dump') else order_book)
                except:
                    pass
        else:
            # Try all adapters
            for adapter in self._adapters.values():
                if hasattr(adapter, 'get_order_book'):
                    try:
                        order_book = adapter.get_order_book(**kwargs)
                        order_books.append(order_book.model_dump() if hasattr(order_book, 'model_dump') else order_book)
                    except:
                        continue
        
        return order_books