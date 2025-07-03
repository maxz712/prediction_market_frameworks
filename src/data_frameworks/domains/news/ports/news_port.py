from abc import ABC, abstractmethod
from typing import Dict, List, Any
from src.data_frameworks.ports.base_port import BasePort


class NewsPort(BasePort, ABC):
    """Interface for news data providers."""
    
    @abstractmethod
    def get_articles(self, **kwargs) -> List[Dict[str, Any]]:
        """Get articles from the news source."""
        pass
    
    @abstractmethod
    def search_articles(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for articles containing a query."""
        pass
    
    @abstractmethod
    def get_sentiment(self, text: str) -> Dict[str, Any]:
        """Get sentiment analysis for text."""
        pass