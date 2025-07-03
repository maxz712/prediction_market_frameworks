from typing import Dict, List, Any
from src.data_frameworks.core.base_orchestrator import BaseOrchestrator


class NewsDataOrchestrator(BaseOrchestrator):
    """Orchestrator for news data operations."""
    
    def __init__(self):
        super().__init__()
        self.name = "news"
    
    def start(self):
        """Start the news data orchestrator."""
        if self._is_running:
            return
        
        # Connect all registered adapters
        for adapter in self._adapters.values():
            if hasattr(adapter, 'connect'):
                adapter.connect()
        
        self._is_running = True
    
    def stop(self):
        """Stop the news data orchestrator."""
        if not self._is_running:
            return
        
        # Disconnect all adapters
        for adapter in self._adapters.values():
            if hasattr(adapter, 'disconnect'):
                adapter.disconnect()
        
        self._is_running = False
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all news adapters."""
        health_status = {}
        for name, adapter in self._adapters.items():
            if hasattr(adapter, 'health_check'):
                health_status[name] = adapter.health_check()
            else:
                health_status[name] = True
        return health_status
    
    def get_articles(self, source: str = None, limit: int = 20, **kwargs) -> List[Dict[str, Any]]:
        """Get articles from news sources."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if source and source in self._adapters:
            adapter = self._adapters[source]
            return adapter.get_articles(limit=limit, **kwargs)
        
        # Aggregate from all adapters if no specific source
        all_articles = []
        for adapter in self._adapters.values():
            if hasattr(adapter, 'get_articles'):
                try:
                    articles = adapter.get_articles(limit=limit//len(self._adapters), **kwargs)
                    all_articles.extend(articles)
                except:
                    continue
        
        return all_articles[:limit]
    
    def search_articles(self, query: str, source: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for articles containing a query."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if source and source in self._adapters:
            adapter = self._adapters[source]
            return adapter.search_articles(query, limit=limit)
        
        # Search across all adapters
        all_articles = []
        for adapter in self._adapters.values():
            if hasattr(adapter, 'search_articles'):
                try:
                    articles = adapter.search_articles(query, limit=limit//len(self._adapters))
                    all_articles.extend(articles)
                except:
                    continue
        
        return all_articles[:limit]
    
    def get_sentiment(self, text: str, source: str = None) -> Dict[str, Any]:
        """Get sentiment analysis for text."""
        if not self._is_running:
            raise RuntimeError("Orchestrator not running")
        
        if source and source in self._adapters:
            adapter = self._adapters[source]
            return adapter.get_sentiment(text)
        
        # Use first available adapter
        for adapter in self._adapters.values():
            if hasattr(adapter, 'get_sentiment'):
                try:
                    return adapter.get_sentiment(text)
                except:
                    continue
        
        raise RuntimeError("No sentiment analysis adapter available")