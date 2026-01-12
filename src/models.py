"""
ThreatFusion Data Models
Defines core data structures for indicators and enrichment results
"""
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class IndicatorType(Enum):
    """Types of threat indicators"""
    HASH_MD5 = "hash_md5"
    HASH_SHA1 = "hash_sha1"
    HASH_SHA256 = "hash_sha256"
    IP_V4 = "ip_v4"
    IP_V6 = "ip_v6"
    DOMAIN = "domain"
    EMAIL = "email"
    URL = "url"


class Indicator(BaseModel):
    """Validated threat indicator"""
    value: str = Field(..., description="Indicator value")
    type: IndicatorType = Field(..., description="Indicator type")
    is_private: bool = Field(default=False, description="Private/RFC1918 IP")


class EnrichmentResult(BaseModel):
    """Result from a single enrichment agent"""
    indicator: str
    source: str
    status: str = Field(default="success", description="success|error")
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RiskScore(BaseModel):
    """Calculated risk score from multiple sources"""
    score: float = Field(..., ge=0.0, le=10.0)
    max: float = 10.0
    severity: str = Field(..., description="CRITICAL|HIGH|MEDIUM|LOW")
    severity_emoji: str = Field(default="🟢")
    components: list[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ThreatReport(BaseModel):
    """Complete threat intelligence report"""
    indicator: Indicator
    risk_score: RiskScore
    enrichment_results: Dict[str, EnrichmentResult]
    generation_time: float = Field(..., description="Time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
