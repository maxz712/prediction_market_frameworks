from typing import Dict, Any, Optional
from ...ports.executor_port import ExecutorPort
from ..clients.polymarket_client import PolymarketClient
from ..configs.polymarket_configs import PolymarketConfig


class PolymarketExecutorAdapter(ExecutorPort):
    """
    Executor adapter for Polymarket that implements trading operations.
    
    This adapter provides the interface for submitting market orders, limit orders,
    managing positions, and canceling orders on the Polymarket platform.
    """
    
    def __init__(self, config: Optional[PolymarketConfig] = None):
        """
        Initialize the Polymarket executor adapter.
        
        Args:
            config: PolymarketConfig instance. If None, loads from environment variables.
        """
        self.config = config or PolymarketConfig.from_env()
        self.client: Optional[PolymarketClient] = None
        self._connected = False
    
    def connect(self):
        """Establish connection to Polymarket APIs."""
        if not self._connected:
            self.client = PolymarketClient(self.config)
            self._connected = True
    
    def disconnect(self):
        """Disconnect from Polymarket APIs."""
        if self._connected:
            self.client = None
            self._connected = False
    
    def place_order(self, market: str, side: str, price: float, size: float) -> Dict[str, Any]:
        """
        Place a limit order on Polymarket.
        
        Args:
            market: Market/token ID to trade
            side: 'BUY' or 'SELL'
            price: Price per unit
            size: Size of the order
            
        Returns:
            Order response from the API
        """
        if not self._connected or not self.client:
            raise RuntimeError("Executor not connected. Call connect() first.")
        
        return self.client.submit_limit_order_gtc(
            token_id=market,
            side=side,
            size=size,
            price=price
        )
    
    def submit_market_order(self, token_id: str, side: str, size: float) -> Dict[str, Any]:
        """
        Submit a market order for immediate execution.
        
        Args:
            token_id: The token ID to trade
            side: 'BUY' or 'SELL'
            size: Size of the order
            
        Returns:
            Order response from the API
        """
        if not self._connected or not self.client:
            raise RuntimeError("Executor not connected. Call connect() first.")
        
        return self.client.submit_market_order(token_id, side, size)
    
    def submit_limit_order_gtc(self, token_id: str, side: str, size: float, price: float) -> Dict[str, Any]:
        """
        Submit a limit order that is good till cancellation (GTC).
        
        Args:
            token_id: The token ID to trade
            side: 'BUY' or 'SELL'
            size: Size of the order
            price: Price per unit
            
        Returns:
            Order response from the API
        """
        if not self._connected or not self.client:
            raise RuntimeError("Executor not connected. Call connect() first.")
        
        return self.client.submit_limit_order_gtc(token_id, side, size, price)
    
    def get_open_orders(self, market: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current open orders for the authenticated user.
        
        Args:
            market: Optional market filter
            
        Returns:
            Dict containing open orders
        """
        if not self._connected or not self.client:
            raise RuntimeError("Executor not connected. Call connect() first.")
        
        return self.client.get_open_orders(market)
    
    def get_open_positions(self) -> Dict[str, Any]:
        """
        Get current open positions for the authenticated user.
        
        Returns:
            Dict containing user positions
        """
        if not self._connected or not self.client:
            raise RuntimeError("Executor not connected. Call connect() first.")
        
        return self.client.get_current_user_position()
    
    def get_current_user_position(self, market: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current user position with optional market filter.
        
        Args:
            market: Optional market filter
            
        Returns:
            Dict containing user positions
        """
        if not self._connected or not self.client:
            raise RuntimeError("Executor not connected. Call connect() first.")
        
        return self.client.get_current_user_position(market)
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel a specific order.
        
        Args:
            order_id: The ID of the order to cancel
            
        Returns:
            Cancellation response from the API
        """
        if not self._connected or not self.client:
            raise RuntimeError("Executor not connected. Call connect() first.")
        
        return self.client.cancel_order(order_id)
    
    def cancel_orders(self, order_ids: list) -> Dict[str, Any]:
        """
        Cancel multiple orders.
        
        Args:
            order_ids: List of order IDs to cancel
            
        Returns:
            Cancellation response from the API
        """
        if not self._connected or not self.client:
            raise RuntimeError("Executor not connected. Call connect() first.")
        
        return self.client.cancel_orders(order_ids)
    
    def cancel_all_orders(self) -> Dict[str, Any]:
        """
        Cancel all open orders.
        
        Returns:
            Cancellation response from the API
        """
        if not self._connected or not self.client:
            raise RuntimeError("Executor not connected. Call connect() first.")
        
        return self.client.cancel_all_orders()
    
    def execute_cycle(self):
        """Optional periodic processing (fills, status)."""
        pass