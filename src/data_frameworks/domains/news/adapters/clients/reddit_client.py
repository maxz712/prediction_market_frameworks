from typing import Dict, List, Any
import requests
from ...ports.news_port import NewsPort


class RedditClient(NewsPort):
    """Client for Reddit news data."""
    
    def __init__(self, client_id: str = None, client_secret: str = None, user_agent: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.base_url = "https://www.reddit.com"
        self._connected = False
    
    def connect(self):
        """Connect to Reddit API."""
        self._connected = True
    
    def disconnect(self):
        """Disconnect from Reddit API."""
        self._connected = False
    
    def health_check(self) -> bool:
        """Check if Reddit API is healthy."""
        if not self._connected:
            return False
        try:
            response = requests.get(f"{self.base_url}/r/popular.json", headers={'User-Agent': self.user_agent})
            return response.status_code == 200
        except:
            return False
    
    def get_articles(self, subreddit: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get articles from a subreddit."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        response = requests.get(
            f"{self.base_url}/r/{subreddit}/hot.json",
            params={"limit": limit},
            headers={'User-Agent': self.user_agent}
        )
        response.raise_for_status()
        
        data = response.json()
        articles = []
        for item in data.get('data', {}).get('children', []):
            post = item.get('data', {})
            articles.append({
                'id': post.get('id'),
                'title': post.get('title'),
                'url': post.get('url'),
                'score': post.get('score'),
                'created_utc': post.get('created_utc'),
                'author': post.get('author'),
                'subreddit': post.get('subreddit'),
                'selftext': post.get('selftext', '')
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
    
    def search_articles(self, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Search for articles containing a query."""
        if not self._connected:
            raise RuntimeError("Client not connected")
        
        response = requests.get(
            f"{self.base_url}/search.json",
            params={
                "q": query,
                "limit": limit,
                "sort": "relevance"
            },
            headers={'User-Agent': self.user_agent}
        )
        response.raise_for_status()
        
        data = response.json()
        articles = []
        for item in data.get('data', {}).get('children', []):
            post = item.get('data', {})
            articles.append({
                'id': post.get('id'),
                'title': post.get('title'),
                'url': post.get('url'),
                'score': post.get('score'),
                'created_utc': post.get('created_utc'),
                'author': post.get('author'),
                'subreddit': post.get('subreddit'),
                'selftext': post.get('selftext', '')
            })
        return articles