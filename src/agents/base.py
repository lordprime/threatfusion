"""
Base Enrichment Agent
Abstract base class for all threat intelligence agents
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any
from src.models import IndicatorType, EnrichmentResult


class EnrichmentAgent(ABC):
    """Abstract base class for threat intelligence enrichment agents"""
    
    def __init__(self, api_key: str, name: str):
        self.api_key = api_key
        self.name = name
        self.request_count = 0
        self.error_count = 0
        self.supported_types: List[IndicatorType] = []
    
    @abstractmethod
    def enrich(self, indicator: str, itype: IndicatorType) -> Dict[str, Any]:
        """
        Enrich an indicator with threat intelligence
        
        Args:
            indicator: The indicator value (hash, IP, domain, etc.)
            itype: The indicator type
        
        Returns:
            Dictionary containing enrichment data
        """
        pass
    
    def is_supported(self, itype: IndicatorType) -> bool:
        """Check if agent supports this indicator type"""
        if not self.supported_types:
            return True  # Supports all types
        return itype in self.supported_types
    
    def create_result(
        self,
        indicator: str,
        data: Dict[str, Any],
        status: str = "success",
        error: str = None
    ) -> EnrichmentResult:
        """Create standardized enrichment result"""
        self.request_count += 1
        if error:
            self.error_count += 1
        
        return EnrichmentResult(
            indicator=indicator,
            source=self.name,
            status=status,
            data=data,
            error=error,
            timestamp=datetime.utcnow()
        )
    
    def handle_error(self, indicator: str, error: Exception) -> EnrichmentResult:
        """Standardized error handling"""
        return self.create_result(
            indicator=indicator,
            data={},
            status="error",
            error=str(error)
        )
    
    def get_stats(self) -> Dict[str, int]:
        """Get agent statistics"""
        return {
            "total_requests": self.request_count,
            "errors": self.error_count,
            "success_rate": 1 - (self.error_count / max(self.request_count, 1))
        }
