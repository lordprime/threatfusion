"""
Indicator Validator
Detects and validates threat indicators
"""
import re
import ipaddress
from typing import Union
from src.models import Indicator, IndicatorType


class IndicatorValidator:
    """Validates and categorizes threat indicators"""
    
    # Regex patterns for detection
    PATTERNS = {
        IndicatorType.HASH_SHA256: r'^[a-f0-9]{64}$',
        IndicatorType.HASH_SHA1: r'^[a-f0-9]{40}$',
        IndicatorType.HASH_MD5: r'^[a-f0-9]{32}$',
        IndicatorType.URL: r'^https?://',
        IndicatorType.EMAIL: r'^[^@]+@[^@]+\.[a-z]{2,}$',
        IndicatorType.DOMAIN: r'^[a-z0-9.-]+\.[a-z]{2,}$'
    }
    
    @classmethod
    def detect_type(cls, indicator: str) -> IndicatorType:
        """Detect indicator type from value"""
        indicator = indicator.strip()
        
        # Check hashes first (most specific)
        for itype in [IndicatorType.HASH_SHA256, IndicatorType.HASH_SHA1, IndicatorType.HASH_MD5]:
            if re.match(cls.PATTERNS[itype], indicator, re.IGNORECASE):
                return itype
        
        # Check IP addresses
        try:
            ip = ipaddress.ip_address(indicator)
            return IndicatorType.IP_V6 if ip.version == 6 else IndicatorType.IP_V4
        except ValueError:
            pass
        
        # Check URL
        if re.match(cls.PATTERNS[IndicatorType.URL], indicator, re.IGNORECASE):
            return IndicatorType.URL
        
        # Check email
        if re.match(cls.PATTERNS[IndicatorType.EMAIL], indicator, re.IGNORECASE):
            return IndicatorType.EMAIL
        
        # Check domain
        if re.match(cls.PATTERNS[IndicatorType.DOMAIN], indicator, re.IGNORECASE):
            return IndicatorType.DOMAIN
        
        raise ValueError(f"Unknown indicator type: {indicator}")
    
    @classmethod
    def is_private_ip(cls, indicator: str) -> bool:
        """Check if IP is private/RFC1918"""
        try:
            ip = ipaddress.ip_address(indicator)
            return ip.is_private or ip.is_loopback or ip.is_reserved
        except ValueError:
            return False
    
    @classmethod
    def validate(cls, indicator: str) -> Indicator:
        """Validate and return Indicator object"""
        indicator = indicator.strip()
        
        if not indicator:
            raise ValueError("Indicator cannot be empty")
        
        itype = cls.detect_type(indicator)
        is_private = False
        
        # Check if private IP
        if itype in [IndicatorType.IP_V4, IndicatorType.IP_V6]:
            is_private = cls.is_private_ip(indicator)
        
        return Indicator(
            value=indicator,
            type=itype,
            is_private=is_private
        )
