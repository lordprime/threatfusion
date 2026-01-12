"""
Shodan Agent
Enriches IP addresses using Shodan API
"""
from typing import Dict, Any
from src.agents.base import EnrichmentAgent
from src.models import IndicatorType
from src.clients.http_client import HTTPClient
from src.clients.rate_limiter import rate_limit


class ShodanAgent(EnrichmentAgent):
    """Shodan infrastructure intelligence agent"""
    
    BASE_URL = "https://api.shodan.io"
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "Shodan")
        self.client = HTTPClient(timeout=30)
        self.supported_types = [IndicatorType.IP_V4]  # Shodan only supports IPv4
    
    @rate_limit('shodan')
    def enrich(self, indicator: str, itype: IndicatorType) -> Dict[str, Any]:
        """Enrich IP address using Shodan"""
        try:
            if itype != IndicatorType.IP_V4:
                return self.create_result(
                    indicator,
                    {},
                    status="error",
                    error=f"Shodan only supports IPv4 addresses"
                ).dict()
            
            data = self._check_host(indicator)
            return self.create_result(indicator, data).dict()
        
        except Exception as e:
            return self.handle_error(indicator, e).dict()
    
    def _check_host(self, ip: str) -> Dict[str, Any]:
        """Check host information in Shodan"""
        url = f"{self.BASE_URL}/shodan/host/{ip}"
        params = {"key": self.api_key}
        
        try:
            response = self.client.get(url, params=params)
            data = response.json()
            
            # Extract services
            services = []
            for item in data.get('data', [])[:10]:  # Top 10 services
                services.append({
                    "port": item.get('port'),
                    "transport": item.get('transport'),
                    "product": item.get('product'),
                    "version": item.get('version'),
                    "banner": item.get('data', '')[:200]  # First 200 chars
                })
            
            return {
                "hostnames": data.get('hostnames', []),
                "country": data.get('country_name'),
                "country_code": data.get('country_code'),
                "city": data.get('city'),
                "org": data.get('org'),
                "isp": data.get('isp'),
                "asn": data.get('asn'),
                "ports": data.get('ports', []),
                "vulns": list(data.get('vulns', {}).keys())[:10],  # Top 10 vulnerabilities
                "tags": data.get('tags', []),
                "services": services,
                "last_update": data.get('last_update')
            }
        
        except Exception as e:
            if "404" in str(e) or "No information" in str(e):
                return {
                    "status": "not_found",
                    "message": "IP not found in Shodan database"
                }
            raise
