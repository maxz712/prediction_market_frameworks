from typing import Dict, List, Any
from src.data_frameworks.core.base_orchestrator import BaseOrchestrator


class FinancialDataOrchestrator(BaseOrchestrator):
    """Orchestrator for financial data operations."""
    
    def __init__(self):
        super().__init__()
        self.name = "financial_data"
    
    def start(self):
        """Start the financial data orchestrator."""
        if self._is_running:
            return
        
        # Connect all registered adapters
        for adapter in self._adapters.values():
            if hasattr(adapter, 'connect'):
                adapter.connect()
        
        self._is_running = True
    
    def stop(self):
        """Stop the financial data orchestrator."""
        if not self._is_running:
            return
        
        # Disconnect all adapters
        for adapter in self._adapters.values():
            if hasattr(adapter, 'disconnect'):
                adapter.disconnect()
        
        self._is_running = False
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all financial data adapters."""
        health_status = {}
        for name, adapter in self._adapters.items():
            if hasattr(adapter, 'health_check'):
                health_status[name] = adapter.health_check()
            else:
                health_status[name] = True
        return health_status
    
    def get_price(self, symbol: str, exchange: str = None) -> Dict[str, Any]:
        """Get price data for a symbol."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if exchange and exchange in self._adapters:
            adapter = self._adapters[exchange]
            return adapter.get_price(symbol)
        
        # Try all adapters if no specific exchange
        for adapter in self._adapters.values():
            if hasattr(adapter, 'get_price'):
                try:
                    return adapter.get_price(symbol)
                except:
                    continue
        
        raise RuntimeError(f"No adapter available for symbol {symbol}")
    
    def get_ticker(self, symbol: str, exchange: str = None) -> Dict[str, Any]:
        """Get ticker data for a symbol."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if exchange and exchange in self._adapters:
            adapter = self._adapters[exchange]
            return adapter.get_ticker(symbol)
        
        # Try all adapters if no specific exchange
        for adapter in self._adapters.values():
            if hasattr(adapter, 'get_ticker'):
                try:
                    return adapter.get_ticker(symbol)
                except:
                    continue
        
        raise RuntimeError(f"No adapter available for symbol {symbol}")