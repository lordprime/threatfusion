"""
AbuseIPDB Agent
Enriches IP addresses with abuse reports and reputation scores
"""
from typing import Dict, Any
from src.agents.base import EnrichmentAgent
from src.models import IndicatorType
from src.clients.http_client import HTTPClient
from src.clients.rate_limiter import rate_limit


class AbuseIPDBAgent(EnrichmentAgent):
    """AbuseIPDB IP reputation agent"""
    
    BASE_URL = "https://api.abuseipdb.com/api/v2"
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "AbuseIPDB")
        self.client = HTTPClient(timeout=30)
        self.supported_types = [IndicatorType.IP_V4, IndicatorType.IP_V6]
    
    @rate_limit('abuseipdb')
    def enrich(self, indicator: str, itype: IndicatorType) -> Dict[str, Any]:
        """Enrich IP address using AbuseIPDB"""
        try:
            if itype not in [IndicatorType.IP_V4, IndicatorType.IP_V6]:
                return self.create_result(
                    indicator,
                    {},
                    status="error",
                    error=f"AbuseIPDB only supports IP addresses"
                ).dict()
            
            data = self._check_ip(indicator)
            return self.create_result(indicator, data).dict()
        
        except Exception as e:
            return self.handle_error(indicator, e).dict()
    
    def _check_ip(self, ip: str) -> Dict[str, Any]:
        """Check IP address in AbuseIPDB"""
        url = f"{self.BASE_URL}/check"
        headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }
        params = {
            "ipAddress": ip,
            "maxAgeInDays": 90,  # Last 90 days
            "verbose": True
        }
        
        try:
            response = self.client.get(url, headers=headers, params=params)
            data = response.json()
            
            result = data.get('data', {})
            
            return {
                "abuse_confidence_score": result.get('abuseConfidenceScore', 0),
                "country_code": result.get('countryCode'),
                "country_name": result.get('countryName'),
                "usage_type": result.get('usageType'),
                "isp": result.get('isp'),
                "domain": result.get('domain'),
                "total_reports": result.get('totalReports', 0),
                "num_distinct_users": result.get('numDistinctUsers', 0),
                "last_reported_at": result.get('lastReportedAt'),
                "is_public": result.get('isPublic', True),
                "is_whitelisted": result.get('isWhitelisted', False),
                "is_tor": result.get('isTor', False)
            }
        
        except Exception as e:
            if "429" in str(e):
                return {
                    "status": "rate_limited",
                    "message": "AbuseIPDB rate limit exceeded"
                }
            raise
