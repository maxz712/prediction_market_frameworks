from typing import Dict, List, Any
from src.data_frameworks.core.base_orchestrator import BaseOrchestrator


class ExecutorOrchestrator(BaseOrchestrator):
    """Orchestrator for prediction market execution operations."""
    
    def __init__(self):
        super().__init__()
        self.name = "prediction_markets_executor"
    
    def start(self):
        """Start the prediction market executor orchestrator."""
        if self._is_running:
            return
        
        # Connect all registered adapters
        for adapter in self._adapters.values():
            if hasattr(adapter, 'connect'):
                adapter.connect()
        
        self._is_running = True
    
    def stop(self):
        """Stop the prediction market executor orchestrator."""
        if not self._is_running:
            return
        
        # Disconnect all adapters
        for adapter in self._adapters.values():
            if hasattr(adapter, 'disconnect'):
                adapter.disconnect()
        
        self._is_running = False
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all executor adapters."""
        health_status = {}
        for name, adapter in self._adapters.items():
            if hasattr(adapter, 'health_check'):
                health_status[name] = adapter.health_check()
            else:
                health_status[name] = True
        return health_status
    
    def place_order(self, adapter_name: str, market: str, side: str, price: float, size: float) -> Dict[str, Any]:
        """Place an order using a specific adapter."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if adapter_name not in self._adapters:
            raise ValueError(f"Adapter {adapter_name} not found")
        
        adapter = self._adapters[adapter_name]
        return adapter.place_order(market, side, price, size)
    
    def submit_market_order(self, adapter_name: str, token_id: str, side: str, size: float) -> Dict[str, Any]:
        """Submit a market order using a specific adapter."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if adapter_name not in self._adapters:
            raise ValueError(f"Adapter {adapter_name} not found")
        
        adapter = self._adapters[adapter_name]
        if hasattr(adapter, 'submit_market_order'):
            return adapter.submit_market_order(token_id, side, size)
        else:
            raise ValueError(f"Adapter {adapter_name} does not support market orders")
    
    def submit_limit_order_gtc(self, adapter_name: str, token_id: str, side: str, size: float, price: float) -> Dict[str, Any]:
        """Submit a limit order GTC using a specific adapter."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if adapter_name not in self._adapters:
            raise ValueError(f"Adapter {adapter_name} not found")
        
        adapter = self._adapters[adapter_name]
        if hasattr(adapter, 'submit_limit_order_gtc'):
            return adapter.submit_limit_order_gtc(token_id, side, size, price)
        else:
            raise ValueError(f"Adapter {adapter_name} does not support limit orders")
    
    def cancel_order(self, adapter_name: str, order_id: str) -> Dict[str, Any]:
        """Cancel an order using a specific adapter."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if adapter_name not in self._adapters:
            raise ValueError(f"Adapter {adapter_name} not found")
        
        adapter = self._adapters[adapter_name]
        return adapter.cancel_order(order_id)
    
    def get_open_orders(self, adapter_name: str, market: str = None) -> Dict[str, Any]:
        """Get open orders using a specific adapter."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if adapter_name not in self._adapters:
            raise ValueError(f"Adapter {adapter_name} not found")
        
        adapter = self._adapters[adapter_name]
        if hasattr(adapter, 'get_open_orders'):
            return adapter.get_open_orders(market)
        else:
            raise ValueError(f"Adapter {adapter_name} does not support getting open orders")
    
    def get_open_positions(self, adapter_name: str) -> Dict[str, Any]:
        """Get open positions using a specific adapter."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if adapter_name not in self._adapters:
            raise ValueError(f"Adapter {adapter_name} not found")
        
        adapter = self._adapters[adapter_name]
        return adapter.get_open_positions()