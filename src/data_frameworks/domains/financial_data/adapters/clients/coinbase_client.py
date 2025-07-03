from typing import Dict, List, Any
import requests
from ...ports.financial_data_port import FinancialDataPort


class CoinbaseClient(FinancialDataPort):
    """Client for Coinbase Pro financial data API."""
    
    def __init__(self, api_key: str = None, api_secret: str = None, passphrase: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.base_url = "https://api.pro.coinbase.com"
        self._connected = False
    
    def connect(self):
        """Connect to Coinbase API."""
        self._connected = True
    
    def disconnect(self):
        """Disconnect from Coinbase API."""
        self._connected = False
    
    def health_check(self) -> bool:
        """Check if Coinbase API is healthy."""
        if not self._connected:
            return False
        try:
            response = requests.get(f"{self.base_url}/time")
            return response.status_code == 200
        except:
            return False
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker data for a symbol."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        response = requests.get(f"{self.base_url}/products/{symbol}/ticker")
        response.raise_for_status()
        return response.json()
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        ticker = self.get_ticker(symbol)
        return {
            "symbol": symbol,
            "price": ticker.get("price", "0")
        }
    
    def get_historical_prices(self, symbol: str, granularity: int = 3600, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical price data."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        response = requests.get(
            f"{self.base_url}/products/{symbol}/candles",
            params={
                "granularity": granularity,
                "limit": limit
            }
        )
        response.raise_for_status()
        return response.json()