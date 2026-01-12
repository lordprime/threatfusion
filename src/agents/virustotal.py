"""
VirusTotal Agent
Enriches indicators using VirusTotal API v3
"""
from typing import Dict, Any
from src.agents.base import EnrichmentAgent
from src.models import IndicatorType
from src.clients.http_client import HTTPClient
from src.clients.rate_limiter import rate_limit


class VirusTotalAgent(EnrichmentAgent):
    """VirusTotal threat intelligence agent"""
    
    BASE_URL = "https://www.virustotal.com/api/v3"
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "VirusTotal")
        self.client = HTTPClient(timeout=30)
        self.supported_types = [
            IndicatorType.HASH_MD5,
            IndicatorType.HASH_SHA1,
            IndicatorType.HASH_SHA256,
            IndicatorType.IP_V4,
            IndicatorType.DOMAIN,
            IndicatorType.URL
        ]
    
    @rate_limit('virustotal')
    def enrich(self, indicator: str, itype: IndicatorType) -> Dict[str, Any]:
        """Enrich indicator using VirusTotal API"""
        try:
            if itype in [IndicatorType.HASH_MD5, IndicatorType.HASH_SHA1, IndicatorType.HASH_SHA256]:
                data = self._check_file(indicator)
            elif itype == IndicatorType.IP_V4:
                data = self._check_ip(indicator)
            elif itype == IndicatorType.DOMAIN:
                data = self._check_domain(indicator)
            elif itype == IndicatorType.URL:
                data = self._check_url(indicator)
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
    
    def _check_file(self, file_hash: str) -> Dict[str, Any]:
        """Check file hash in VirusTotal"""
        url = f"{self.BASE_URL}/files/{file_hash}"
        headers = {"x-apikey": self.api_key}
        
        try:
            response = self.client.get(url, headers=headers)
            data = response.json()
            
            attrs = data['data']['attributes']
            stats = attrs.get('last_analysis_stats', {})
            
            return {
                "detections": stats.get('malicious', 0),
                "suspicious": stats.get('suspicious', 0),
                "undetected": stats.get('undetected', 0),
                "total": sum(stats.values()),
                "names": attrs.get('names', [])[:5],  # Top 5 names
                "first_seen": attrs.get('first_submission_date'),
                "last_analyzed": attrs.get('last_analysis_date'),
                "file_type": attrs.get('type_description'),
                "size": attrs.get('size'),
                "md5": attrs.get('md5'),
                "sha1": attrs.get('sha1'),
                "sha256": attrs.get('sha256'),
                "detection_ratio": f"{stats.get('malicious', 0)}/{sum(stats.values())}"
            }
        
        except Exception as e:
            if "404" in str(e):
                return {
                    "detections": 0,
                    "total": 0,
                    "status": "not_found",
                    "message": "Hash not found in VirusTotal database"
                }
            raise
    
    def _check_ip(self, ip: str) -> Dict[str, Any]:
        """Check IP address in VirusTotal"""
        url = f"{self.BASE_URL}/ip_addresses/{ip}"
        headers = {"x-apikey": self.api_key}
        
        response = self.client.get(url, headers=headers)
        data = response.json()
        
        attrs = data['data']['attributes']
        stats = attrs.get('last_analysis_stats', {})
        
        return {
            "detections": stats.get('malicious', 0),
            "suspicious": stats.get('suspicious', 0),
            "total": sum(stats.values()),
            "country": attrs.get('country'),
            "asn": attrs.get('asn'),
            "as_owner": attrs.get('as_owner'),
            "network": attrs.get('network'),
            "detection_ratio": f"{stats.get('malicious', 0)}/{sum(stats.values())}"
        }
    
    def _check_domain(self, domain: str) -> Dict[str, Any]:
        """Check domain in VirusTotal"""
        url = f"{self.BASE_URL}/domains/{domain}"
        headers = {"x-apikey": self.api_key}
        
        response = self.client.get(url, headers=headers)
        data = response.json()
        
        attrs = data['data']['attributes']
        stats = attrs.get('last_analysis_stats', {})
        
        return {
            "detections": stats.get('malicious', 0),
            "suspicious": stats.get('suspicious', 0),
            "total": sum(stats.values()),
            "categories": attrs.get('categories', {}),
            "creation_date": attrs.get('creation_date'),
            "registrar": attrs.get('registrar'),
            "detection_ratio": f"{stats.get('malicious', 0)}/{sum(stats.values())}"
        }
    
    def _check_url(self, url: str) -> Dict[str, Any]:
        """Check URL in VirusTotal"""
        import base64
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        
        check_url = f"{self.BASE_URL}/urls/{url_id}"
        headers = {"x-apikey": self.api_key}
        
        response = self.client.get(check_url, headers=headers)
        data = response.json()
        
        attrs = data['data']['attributes']
        stats = attrs.get('last_analysis_stats', {})
        
        return {
            "detections": stats.get('malicious', 0),
            "suspicious": stats.get('suspicious', 0),
            "total": sum(stats.values()),
            "detection_ratio": f"{stats.get('malicious', 0)}/{sum(stats.values())}"
        }
