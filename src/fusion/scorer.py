"""
Risk Scorer
Calculates unified risk scores from multiple intelligence sources
"""
from datetime import datetime
from typing import Dict, Any
from src.models import RiskScore


class RiskScorer:
    """Calculates risk scores from enrichment results"""
    
    @staticmethod
    def calculate_risk(results: Dict[str, Dict[str, Any]]) -> RiskScore:
        """
        Calculate overall risk score from multiple sources
        
        Scoring breakdown:
        - VirusTotal: 0-5 points (detection ratio)
        - OTX: 0-2 points (community pulses)
        - Shodan: 0-2 points (vulnerabilities)
        - AbuseIPDB: 0-1 point (abuse score)
        
        Total: 0-10 points
        """
        score = 0.0
        max_score = 10.0
        components = []
        
        # Remove metadata from results
        enrichment_results = {
            k: v for k, v in results.items()
            if k != '_metadata' and isinstance(v, dict)
        }
        
        # VirusTotal scoring (max 5 points)
        if 'VirusTotal' in enrichment_results:
            vt_data = enrichment_results['VirusTotal']
            if vt_data.get('status') == 'success' and 'data' in vt_data:
                data = vt_data['data']
                detections = data.get('detections', 0)
                total = data.get('total', 1)
                
                if total > 0:
                    ratio = detections / max(total, 1)
                    vt_score = ratio * 5.0
                    score += vt_score
                    
                    components.append({
                        "source": "VirusTotal",
                        "score": round(vt_score, 2),
                        "max": 5.0,
                        "details": f"{detections}/{total} engines flagged as malicious"
                    })
        
        # OTX scoring (max 2 points)
        if 'OTX' in enrichment_results:
            otx_data = enrichment_results['OTX']
            if otx_data.get('status') == 'success' and 'data' in otx_data:
                data = otx_data['data']
                pulse_count = data.get('pulse_count', 0)
                
                # More pulses = higher risk (10+ pulses = max score)
                otx_score = min(pulse_count / 10.0 * 2.0, 2.0)
                score += otx_score
                
                components.append({
                    "source": "OTX",
                    "score": round(otx_score, 2),
                    "max": 2.0,
                    "details": f"{pulse_count} threat intelligence pulses"
                })
        
        # Shodan scoring (max 2 points)
        if 'Shodan' in enrichment_results:
            shodan_data = enrichment_results['Shodan']
            if shodan_data.get('status') == 'success' and 'data' in shodan_data:
                data = shodan_data['data']
                vulns = data.get('vulns', [])
                vuln_count = len(vulns)
                
                # More vulnerabilities = higher risk (3+ vulns = max score)
                if vuln_count > 0:
                    shodan_score = min(vuln_count / 3.0 * 2.0, 2.0)
                    score += shodan_score
                    
                    components.append({
                        "source": "Shodan",
                        "score": round(shodan_score, 2),
                        "max": 2.0,
                        "details": f"{vuln_count} known vulnerabilities detected"
                    })
        
        # AbuseIPDB scoring (max 1 point)
        if 'AbuseIPDB' in enrichment_results:
            abuse_data = enrichment_results['AbuseIPDB']
            if abuse_data.get('status') == 'success' and 'data' in abuse_data:
                data = abuse_data['data']
                abuse_score = data.get('abuse_confidence_score', 0)
                
                # Convert 0-100 scale to 0-1 points
                if abuse_score > 0:
                    abuse_points = abuse_score / 100.0
                    score += abuse_points
                    
                    components.append({
                        "source": "AbuseIPDB",
                        "score": round(abuse_points, 2),
                        "max": 1.0,
                        "details": f"{abuse_score}% abuse confidence"
                    })
        
        # Censys scoring (bonus 0.5 points for suspicious infrastructure)
        if 'Censys' in enrichment_results:
            censys_data = enrichment_results['Censys']
            if censys_data.get('status') == 'success' and 'data' in censys_data:
                data = censys_data['data']
                services = data.get('services', [])
                
                # Check for suspicious services
                suspicious_ports = [22, 23, 3389, 445]  # SSH, Telnet, RDP, SMB
                exposed_suspicious = any(
                    s.get('port') in suspicious_ports for s in services
                )
                
                if exposed_suspicious:
                    score += 0.5
                    components.append({
                        "source": "Censys",
                        "score": 0.5,
                        "max": 0.5,
                        "details": "Suspicious services exposed"
                    })
        
        # Cap at max score
        final_score = min(score, max_score)
        
        # Determine severity
        if final_score >= 8.0:
            severity = "CRITICAL"
            severity_emoji = "🔴"
        elif final_score >= 6.0:
            severity = "HIGH"
            severity_emoji = "🟠"
        elif final_score >= 4.0:
            severity = "MEDIUM"
            severity_emoji = "🟡"
        else:
            severity = "LOW"
            severity_emoji = "🟢"
        
        # Calculate confidence based on source coverage
        confidence = RiskScorer.calculate_confidence(enrichment_results)
        
        return RiskScore(
            score=round(final_score, 1),
            max=max_score,
            severity=severity,
            severity_emoji=severity_emoji,
            components=components,
            confidence=confidence,
            timestamp=datetime.utcnow()
        )
    
    @staticmethod
    def calculate_confidence(results: Dict[str, Dict[str, Any]]) -> float:
        """
        Calculate confidence in risk score based on source agreement
        Returns: 0.0-1.0
        """
        successful_sources = sum(
            1 for result in results.values()
            if isinstance(result, dict) and result.get('status') == 'success'
        )
        
        total_sources = len(results)
        
        if total_sources == 0:
            return 0.0
        
        response_rate = successful_sources / total_sources
        
        # Confidence levels based on response rate
        if response_rate >= 0.75:
            return 0.9  # High confidence
        elif response_rate >= 0.5:
            return 0.7  # Medium confidence
        elif response_rate >= 0.25:
            return 0.5  # Low confidence
        else:
            return 0.3  # Very low confidence
