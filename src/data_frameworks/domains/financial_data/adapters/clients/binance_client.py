from typing import Dict, List, Any
import requests
from ...ports.financial_data_port import FinancialDataPort


class BinanceClient(FinancialDataPort):
    """Client for Binance financial data API."""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com/api/v3"
        self._connected = False
    
    def connect(self):
        """Connect to Binance API."""
        self._connected = True
    
    def disconnect(self):
        """Disconnect from Binance API."""
        self._connected = False
    
    def health_check(self) -> bool:
        """Check if Binance API is healthy."""
        if not self._connected:
            return False
        try:
            response = requests.get(f"{self.base_url}/ping")
            return response.status_code == 200
        except:
            return False
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data for a symbol."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        response = requests.get(
            f"{self.base_url}/ticker/24hr",
            params={"symbol": symbol}
        )
        response.raise_for_status()
        return response.json()
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        response = requests.get(
            f"{self.base_url}/ticker/price",
            params={"symbol": symbol}
        )
        response.raise_for_status()
        return response.json()
    
    def get_historical_prices(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical price data."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        response = requests.get(
            f"{self.base_url}/klines",
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
        )
        response.raise_for_status()
        return response.json()