"""
ThreatFusion Configuration Management
Loads environment variables and validates API keys
"""
import os
from typing import Optional
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables
load_dotenv()


@dataclass
class APIConfig:
    """API Configuration Container"""
    vt_api_key: Optional[str] = None
    shodan_api_key: Optional[str] = None
    censys_api_id: Optional[str] = None
    censys_api_secret: Optional[str] = None
    otx_api_key: Optional[str] = None
    abuseipdb_api_key: Optional[str] = None
    urlhaus_api_key: Optional[str] = None
    talos_api_key: Optional[str] = None


@dataclass
class AppConfig:
    """Application Configuration"""
    cache_ttl_hours: int = 24
    max_workers: int = 8
    default_timeout: int = 30
    log_level: str = "INFO"


class ConfigManager:
    """Manages application and API configurations"""
    
    def __init__(self):
        self.api_config = self._load_api_config()
        self.app_config = self._load_app_config()
    
    def _load_api_config(self) -> APIConfig:
        """Load API keys from environment"""
        return APIConfig(
            vt_api_key=os.getenv('VT_API_KEY'),
            shodan_api_key=os.getenv('SHODAN_API_KEY'),
            censys_api_id=os.getenv('CENSYS_API_ID'),
            censys_api_secret=os.getenv('CENSYS_API_SECRET'),
            otx_api_key=os.getenv('OTX_API_KEY'),
            abuseipdb_api_key=os.getenv('ABUSEIPDB_API_KEY'),
            urlhaus_api_key=os.getenv('URLHAUS_API_KEY'),
            talos_api_key=os.getenv('TALOS_API_KEY')
        )
    
    def _load_app_config(self) -> AppConfig:
        """Load application settings"""
        return AppConfig(
            cache_ttl_hours=int(os.getenv('CACHE_TTL_HOURS', '24')),
            max_workers=int(os.getenv('MAX_WORKERS', '8')),
            default_timeout=int(os.getenv('DEFAULT_TIMEOUT', '30')),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
    
    def validate_api_keys(self) -> dict[str, bool]:
        """Validate which API keys are configured"""
        return {
            'virustotal': bool(self.api_config.vt_api_key),
            'shodan': bool(self.api_config.shodan_api_key),
            'censys': bool(self.api_config.censys_api_id and self.api_config.censys_api_secret),
            'otx': bool(self.api_config.otx_api_key),
            'abuseipdb': bool(self.api_config.abuseipdb_api_key),
            'urlhaus': bool(self.api_config.urlhaus_api_key),
            'talos': bool(self.api_config.talos_api_key)
        }
    
    def get_configured_apis(self) -> list[str]:
        """Get list of configured API services"""
        validation = self.validate_api_keys()
        return [api for api, configured in validation.items() if configured]


# Global config instance
config = ConfigManager()
