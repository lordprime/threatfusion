"""
AlienVault OTX Agent
Enriches indicators using threat intelligence pulses
"""
from typing import Dict, Any
from src.agents.base import EnrichmentAgent
from src.models import IndicatorType
from src.clients.http_client import HTTPClient
from src.clients.rate_limiter import rate_limit


class OTXAgent(EnrichmentAgent):
    """AlienVault OTX community threat intelligence agent"""
    
    BASE_URL = "https://otx.alienvault.com/api/v1"
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "OTX")
        self.client = HTTPClient(timeout=30)
        # OTX supports all indicator types
        self.supported_types = []  # Empty = supports all
    
    @rate_limit('otx')
    def enrich(self, indicator: str, itype: IndicatorType) -> Dict[str, Any]:
        """Enrich indicator using AlienVault OTX"""
        try:
            # Map IndicatorType to OTX section type
            type_mapping = {
                IndicatorType.HASH_MD5: "file",
                IndicatorType.HASH_SHA1: "file",
                IndicatorType.HASH_SHA256: "file",
                IndicatorType.IP_V4: "IPv4",
                IndicatorType.IP_V6: "IPv6",
                IndicatorType.DOMAIN: "domain",
                IndicatorType.URL: "url",
                IndicatorType.EMAIL: "email"
            }
            
            section_type = type_mapping.get(itype, "file")
            data = self._get_general_info(indicator, section_type)
            
            return self.create_result(indicator, data).dict()
        
        except Exception as e:
            return self.handle_error(indicator, e).dict()
    
    def _get_general_info(self, indicator: str, section_type: str) -> Dict[str, Any]:
        """Get general information about indicator"""
        url = f"{self.BASE_URL}/indicators/{section_type}/{indicator}/general"
        headers = {"X-OTX-API-KEY": self.api_key}
        
        try:
            response = self.client.get(url, headers=headers)
            data = response.json()
            
            pulse_info = data.get('pulse_info', {})
            pulses = pulse_info.get('pulses', [])
            
            # Extract pulse details
            pulse_details = []
            for pulse in pulses[:10]:  # Top 10 pulses
                pulse_details.append({
                    "name": pulse.get('name'),
                    "created": pulse.get('created'),
                    "modified": pulse.get('modified'),
                    "author": pulse.get('author_name'),
                    "tags": pulse.get('tags', [])[:5],
                    "adversary": pulse.get('adversary'),
                    "targeted_countries": pulse.get('targeted_countries', [])[:5],
                    "malware_families": pulse.get('malware_families', [])[:5],
                    "attack_ids": pulse.get('attack_ids', [])[:5]
                })
            
            validation = data.get('validation', [])
            
            return {
                "pulse_count": pulse_info.get('count', 0),
                "pulses": pulse_details,
                "validation": validation[:5],
                "indicator_type": section_type,
                "has_threat_intel": pulse_info.get('count', 0) > 0
            }
        
        except Exception as e:
            if "404" in str(e):
                return {
                    "pulse_count": 0,
                    "pulses": [],
                    "has_threat_intel": False,
                    "message": "No threat intelligence found for indicator"
                }
            raise
