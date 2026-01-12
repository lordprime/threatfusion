"""
Enrichment Orchestrator
Coordinates parallel execution of multiple agents
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import List, Dict, Any
from src.agents.base import EnrichmentAgent
from src.models import IndicatorType


class EnrichmentOrchestrator:
    """Orchestrates parallel enrichment across multiple agents"""
    
    def __init__(self, agents: List[EnrichmentAgent], max_workers: int = 8):
        self.agents = agents
        self.max_workers = max_workers
    
    def enrich_parallel(
        self,
        indicator: str,
        itype: IndicatorType,
        timeout: int = 30
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute all applicable agents in parallel
        
        Args:
            indicator: The indicator to enrich
            itype: The indicator type
            timeout: Maximum total time for all agents
        
        Returns:
            Dictionary mapping agent names to their results
        """
        results = {}
        start_time = time.time()
        
        # Filter agents that support this indicator type
        applicable_agents = [
            agent for agent in self.agents
            if agent.is_supported(itype)
        ]
        
        if not applicable_agents:
            return {
                "error": f"No agents support indicator type: {itype.value}"
            }
        
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(applicable_agents))) as executor:
            # Submit all agent queries
            future_to_agent = {
                executor.submit(self._safe_enrich, agent, indicator, itype): agent
                for agent in applicable_agents
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent, timeout=timeout):
                agent = future_to_agent[future]
                
                try:
                    result = future.result(timeout=5)  # Per-agent timeout
                    results[agent.name] = result
                
                except TimeoutError:
                    results[agent.name] = {
                        "status": "error",
                        "error": f"Agent timeout (>5s)",
                        "indicator": indicator,
                        "source": agent.name
                    }
                
                except Exception as e:
                    results[agent.name] = {
                        "status": "error",
                        "error": str(e),
                        "indicator": indicator,
                        "source": agent.name
                    }
        
        # Calculate total execution time
        execution_time = time.time() - start_time
        results['_metadata'] = {
            "execution_time": round(execution_time, 2),
            "agents_queried": len(applicable_agents),
            "results_received": len([r for r in results.values() if isinstance(r, dict) and r.get('status') != 'error'])
        }
        
        return results
    
    def _safe_enrich(self, agent: EnrichmentAgent, indicator: str, itype: IndicatorType) -> Dict[str, Any]:
        """
        Safely execute agent enrichment with exception handling
        """
        try:
            return agent.enrich(indicator, itype)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "indicator": indicator,
                "source": agent.name
            }
    
    def get_agent_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all agents"""
        stats = {}
        for agent in self.agents:
            stats[agent.name] = agent.get_stats()
        return stats
