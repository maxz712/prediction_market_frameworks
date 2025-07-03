from typing import Dict, List, Any, Optional
from .shared_models.query import Query, QueryType
from ..domains.prediction_markets.core.data_orchestrator import DataOrchestrator as PredictionMarketOrchestrator
from ..domains.prediction_markets.core.executor_orchestrator import ExecutorOrchestrator as PredictionMarketExecutor
from ..domains.financial_data.core.data_orchestrator import FinancialDataOrchestrator
from ..domains.news.core.data_orchestrator import NewsDataOrchestrator


class UnifiedInterface:
    """Facade for cross-domain queries and operations."""
    
    def __init__(self):
        self._orchestrators = {
            "prediction_markets": {
                "data": PredictionMarketOrchestrator(),
                "executor": PredictionMarketExecutor()
            },
            "financial_data": {
                "data": FinancialDataOrchestrator()
            },
            "news": {
                "data": NewsDataOrchestrator()
            }
        }
        self._running = False
    
    def start(self):
        """Start all orchestrators."""
        for domain, orchestrators in self._orchestrators.items():
            for name, orchestrator in orchestrators.items():
                orchestrator.start()
        self._running = True
    
    def stop(self):
        """Stop all orchestrators."""
        for domain, orchestrators in self._orchestrators.items():
            for name, orchestrator in orchestrators.items():
                orchestrator.stop()
        self._running = False
    
    def register_adapter(self, domain: str, orchestrator_type: str, name: str, adapter: Any):
        """Register an adapter with a specific orchestrator."""
        if domain in self._orchestrators and orchestrator_type in self._orchestrators[domain]:
            self._orchestrators[domain][orchestrator_type].register_adapter(name, adapter)
        else:
            raise ValueError(f"Unknown domain/orchestrator: {domain}/{orchestrator_type}")
    
    def execute_query(self, query: Query) -> Dict[str, Any]:
        """Execute a query across one or more domains."""
        if not self._running:
            raise RuntimeError("Unified interface not started")
        
        results = {}
        
        if query.is_cross_domain():
            # Execute across multiple domains
            for domain in query.domains:
                if domain in self._orchestrators:
                    domain_params = query.get_domain_parameters(domain)
                    results[domain] = self._execute_domain_query(domain, domain_params)
        else:
            # Execute on single domain
            if query.query_type == QueryType.PREDICTION_MARKET:
                results["prediction_markets"] = self._execute_prediction_market_query(query.parameters)
            elif query.query_type == QueryType.FINANCIAL_DATA:
                results["financial_data"] = self._execute_financial_data_query(query.parameters)
            elif query.query_type == QueryType.NEWS:
                results["news"] = self._execute_news_query(query.parameters)
        
        return results
    
    def _execute_domain_query(self, domain: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a query on a specific domain."""
        if domain == "prediction_markets":
            return self._execute_prediction_market_query(parameters)
        elif domain == "financial_data":
            return self._execute_financial_data_query(parameters)
        elif domain == "news":
            return self._execute_news_query(parameters)
        else:
            raise ValueError(f"Unknown domain: {domain}")
    
    def _execute_prediction_market_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute prediction market query."""
        orchestrator = self._orchestrators["prediction_markets"]["data"]
        
        operation = parameters.get("operation")
        if operation == "get_events":
            return orchestrator.get_events(**parameters.get("params", {}))
        elif operation == "get_markets":
            return orchestrator.get_markets(**parameters.get("params", {}))
        elif operation == "get_order_books":
            return orchestrator.get_order_books(**parameters.get("params", {}))
        else:
            raise ValueError(f"Unknown prediction market operation: {operation}")
    
    def _execute_financial_data_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute financial data query."""
        orchestrator = self._orchestrators["financial_data"]["data"]
        
        operation = parameters.get("operation")
        if operation == "get_price":
            return orchestrator.get_price(**parameters.get("params", {}))
        elif operation == "get_ticker":
            return orchestrator.get_ticker(**parameters.get("params", {}))
        else:
            raise ValueError(f"Unknown financial data operation: {operation}")
    
    def _execute_news_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute news query."""
        orchestrator = self._orchestrators["news"]["data"]
        
        operation = parameters.get("operation")
        if operation == "get_articles":
            return orchestrator.get_articles(**parameters.get("params", {}))
        elif operation == "search_articles":
            return orchestrator.search_articles(**parameters.get("params", {}))
        elif operation == "get_sentiment":
            return orchestrator.get_sentiment(**parameters.get("params", {}))
        else:
            raise ValueError(f"Unknown news operation: {operation}")
    
    def health_check(self) -> Dict[str, Dict[str, Dict[str, bool]]]:
        """Check health of all orchestrators."""
        health_status = {}
        for domain, orchestrators in self._orchestrators.items():
            health_status[domain] = {}
            for name, orchestrator in orchestrators.items():
                health_status[domain][name] = orchestrator.health_check()
        return health_status
    
    def get_orchestrator(self, domain: str, orchestrator_type: str = "data") -> Any:
        """Get a specific orchestrator."""
        if domain in self._orchestrators and orchestrator_type in self._orchestrators[domain]:
            return self._orchestrators[domain][orchestrator_type]
        else:
            raise ValueError(f"Unknown domain/orchestrator: {domain}/{orchestrator_type}")
    
    def list_domains(self) -> List[str]:
        """List all available domains."""
        return list(self._orchestrators.keys())
    
    def is_running(self) -> bool:
        """Check if unified interface is running."""
        return self._running