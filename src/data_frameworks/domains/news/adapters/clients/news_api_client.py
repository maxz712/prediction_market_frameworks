from typing import Dict, List, Any
import requests
from ...ports.news_port import NewsPort


class NewsApiClient(NewsPort):
    """Client for News API service."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self._connected = False
    
    def connect(self):
        """Connect to News API."""
        self._connected = True
    
    def disconnect(self):
        """Disconnect from News API."""
        self._connected = False
    
    def health_check(self) -> bool:
        """Check if News API is healthy."""
        if not self._connected:
            return False
        try:
            response = requests.get(
                f"{self.base_url}/top-headlines",
                params={"apiKey": self.api_key, "pageSize": 1}
            )
            return response.status_code == 200
        except:
            return False
    
    def get_articles(self, category: str = None, country: str = "us", limit: int = 20) -> List[Dict[str, Any]]:
        """Get top headlines."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        params = {
            "apiKey": self.api_key,
            "country": country,
            "pageSize": limit
        }
        
        if category:
            params["category"] = category
        
        response = requests.get(f"{self.base_url}/top-headlines", params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        for article in data.get('articles', []):
            articles.append({
                'id': article.get('url'),  # Using URL as ID
                'title': article.get('title'),
                'description': article.get('description'),
                'url': article.get('url'),
                'published_at': article.get('publishedAt'),
                'source': article.get('source', {}).get('name'),
                'author': article.get('author'),
                'content': article.get('content', '')
            })
        return articles
    
    def get_sentiment(self, text: str) -> Dict[str, Any]:
        """Get sentiment analysis for text (placeholder implementation)."""
        # This would typically use a sentiment analysis service
        return {
            'sentiment': 'neutral',
            'score': 0.0,
            'confidence': 0.5
        }
    
    def search_articles(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for articles containing a query."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        params = {
            "apiKey": self.api_key,
            "q": query,
            "pageSize": limit,
            "sortBy": "relevancy"
        }
        
        response = requests.get(f"{self.base_url}/everything", params=params)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        for article in data.get('articles', []):
            articles.append({
                'id': article.get('url'),
                'title': article.get('title'),
                'description': article.get('description'),
                'url': article.get('url'),
                'published_at': article.get('publishedAt'),
                'source': article.get('source', {}).get('name'),
                'author': article.get('author'),
                'content': article.get('content', '')
            })
        return articles