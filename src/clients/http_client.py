"""
HTTP Client with retry logic and rate limiting
"""
import time
import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HTTPClient:
    """Robust HTTP client with retry and timeout handling"""
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5
    ):
        self.timeout = timeout
        self.session = self._create_session(max_retries, backoff_factor)
    
    def _create_session(self, max_retries: int, backoff_factor: float) -> requests.Session:
        """Create session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        auth: Optional[tuple] = None
    ) -> requests.Response:
        """Execute GET request with retry logic"""
        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                auth=auth,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {str(e)}")
    
    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """Execute POST request with retry logic"""
        try:
            response = self.session.post(
                url,
                headers=headers,
                data=data,
                json=json,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {str(e)}")
    
    def close(self):
        """Close session"""
        self.session.close()
