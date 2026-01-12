"""
Tests for Indicator Validator
"""
import pytest
from src.validators import IndicatorValidator
from src.models import IndicatorType


class TestIndicatorDetection:
    """Test indicator type detection"""
    
    def test_md5_hash_detection(self):
        """Test MD5 hash detection"""
        hash_md5 = "d131dd02c5e6eec4693d61a8d9ca3759"
        indicator = IndicatorValidator.validate(hash_md5)
        assert indicator.type == IndicatorType.HASH_MD5
        assert indicator.value == hash_md5
    
    def test_sha1_hash_detection(self):
        """Test SHA1 hash detection"""
        hash_sha1 = "356a192b7913b04c54574d18c28d46e6395428ab"
        indicator = IndicatorValidator.validate(hash_sha1)
        assert indicator.type == IndicatorType.HASH_SHA1
    
    def test_sha256_hash_detection(self):
        """Test SHA256 hash detection"""
        hash_sha256 = "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
        indicator = IndicatorValidator.validate(hash_sha256)
        assert indicator.type == IndicatorType.HASH_SHA256
    
    def test_ipv4_detection(self):
        """Test IPv4 detection"""
        ip = "8.8.8.8"
        indicator = IndicatorValidator.validate(ip)
        assert indicator.type == IndicatorType.IP_V4
        assert indicator.is_private == False
    
    def test_private_ip_detection(self):
        """Test private IP detection"""
        private_ips = ["192.168.1.1", "10.0.0.1", "127.0.0.1"]
        for ip in private_ips:
            indicator = IndicatorValidator.validate(ip)
            assert indicator.is_private == True
    
    def test_domain_detection(self):
        """Test domain detection"""
        domain = "example.com"
        indicator = IndicatorValidator.validate(domain)
        assert indicator.type == IndicatorType.DOMAIN
    
    def test_email_detection(self):
        """Test email detection"""
        email = "test@example.com"
        indicator = IndicatorValidator.validate(email)
        assert indicator.type == IndicatorType.EMAIL
    
    def test_url_detection(self):
        """Test URL detection"""
        url = "https://example.com/malware"
        indicator = IndicatorValidator.validate(url)
        assert indicator.type == IndicatorType.URL
    
    def test_invalid_indicator(self):
        """Test invalid indicator raises ValueError"""
        with pytest.raises(ValueError):
            IndicatorValidator.validate("not_valid_anything")
    
    def test_empty_indicator(self):
        """Test empty indicator raises ValueError"""
        with pytest.raises(ValueError):
            IndicatorValidator.validate("")
    
    def test_case_insensitive_hash(self):
        """Test hash detection is case insensitive"""
        hash_upper = "D131DD02C5E6EEC4693D61A8D9CA3759"
        indicator = IndicatorValidator.validate(hash_upper)
        assert indicator.type == IndicatorType.HASH_MD5


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_hash_with_whitespace(self):
        """Test hash with leading/trailing whitespace"""
        hash_with_space = "  d131dd02c5e6eec4693d61a8d9ca3759  "
        indicator = IndicatorValidator.validate(hash_with_space)
        assert indicator.type == IndicatorType.HASH_MD5
    
    def test_subdomain(self):
        """Test subdomain detection"""
        subdomain = "mail.example.com"
        indicator = IndicatorValidator.validate(subdomain)
        assert indicator.type == IndicatorType.DOMAIN
    
    def test_ipv6_detection(self):
        """Test IPv6 detection"""
        ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        indicator = IndicatorValidator.validate(ipv6)
        assert indicator.type == IndicatorType.IP_V6
