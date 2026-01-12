"""
Censys Agent
Enriches indicators using Censys Search API v2
"""
from typing import Dict, Any
from src.agents.base import EnrichmentAgent
from src.models import IndicatorType
from src.clients.http_client import HTTPClient
from src.clients.rate_limiter import rate_limit


class CensysAgent(EnrichmentAgent):
    """Censys certificate and infrastructure intelligence agent"""
    
    BASE_URL = "https://search.censys.io/api/v2"
    
    def __init__(self, api_id: str, api_secret: str):
        super().__init__(api_id, "Censys")
        self.api_secret = api_secret
        self.client = HTTPClient(timeout=30)
        self.supported_types = [IndicatorType.IP_V4, IndicatorType.DOMAIN]
    
    @rate_limit('censys')
    def enrich(self, indicator: str, itype: IndicatorType) -> Dict[str, Any]:
        """Enrich indicator using Censys"""
        try:
            if itype == IndicatorType.IP_V4:
                data = self._check_host(indicator)
            elif itype == IndicatorType.DOMAIN:
                data = self._check_certificate(indicator)
            else:
                return self.create_result(
                    indicator,
                    {},
                    status="error",
                    error=f"Unsupported indicator type: {itype.value}"
                ).dict()
            
            return self.create_result(indicator, data).dict()
        
        except Exception as e:
            return self.handle_error(indicator, e).dict()
    
    def _check_host(self, ip: str) -> Dict[str, Any]:
        """Check host information in Censys"""
        url = f"{self.BASE_URL}/hosts/{ip}"
        auth = (self.api_key, self.api_secret)
        
        try:
            response = self.client.get(url, auth=auth)
            data = response.json()
            
            result = data.get('result', {})
            services = []
            
            for service in result.get('services', [])[:10]:
                services.append({
                    "port": service.get('port'),
                    "service_name": service.get('service_name'),
                    "transport_protocol": service.get('transport_protocol')
                })
            
            location = result.get('location', {})
            
            return {
                "ip": result.get('ip'),
                "services": services,
                "location": {
                    "country": location.get('country'),
                    "city": location.get('city'),
                    "coordinates": location.get('coordinates', {})
                },
                "autonomous_system": result.get('autonomous_system', {}),
                "last_updated": result.get('last_updated_at')
            }
        
        except Exception as e:
            if "404" in str(e):
                return {
                    "status": "not_found",
                    "message": "Host not found in Censys database"
                }
            raise
    
    def _check_certificate(self, domain: str) -> Dict[str, Any]:
        """Check certificate information for domain"""
        url = f"{self.BASE_URL}/certificates/search"
        auth = (self.api_key, self.api_secret)
        params = {
            "q": f"names: {domain}",
            "per_page": 5
        }
        
        try:
            response = self.client.get(url, params=params, auth=auth)
            data = response.json()
            
            hits = data.get('result', {}).get('hits', [])
            certificates = []
            
            for hit in hits[:5]:
                parsed = hit.get('parsed', {})
                certificates.append({
                    "fingerprint": hit.get('fingerprint_sha256'),
                    "issuer": parsed.get('issuer', {}).get('common_name', []),
                    "subject": parsed.get('subject', {}).get('common_name', []),
                    "validity": parsed.get('validity', {}),
                    "names": parsed.get('names', [])[:10]
                })
            
            return {
                "total_certificates": data.get('result', {}).get('total', 0),
                "certificates": certificates
            }
        
        except Exception as e:
            if "404" in str(e):
                return {
                    "status": "not_found",
                    "message": "No certificates found for domain"
                }
            raise
