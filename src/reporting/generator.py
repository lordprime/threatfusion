"""
Report Generator
Generates threat intelligence reports in multiple formats
"""
import json
from datetime import datetime
from typing import Dict, Any
from jinja2 import Template
from src.models import ThreatReport, RiskScore


class ReportGenerator:
    """Generates threat intelligence reports in various formats"""
    
    @staticmethod
    def generate_text(
        indicator: str,
        results: Dict[str, Any],
        risk_score: RiskScore,
        execution_time: float
    ) -> str:
        """Generate formatted text report for terminal"""
        lines = []
        
        lines.append("=" * 80)
        lines.append("THREATFUSION ENRICHMENT REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Indicator: {indicator}")
        lines.append(f"Analysis Time: {execution_time:.2f}s")
        lines.append(f"Timestamp: {datetime.utcnow().isoformat()}")
        lines.append("")
        
        # Risk Score section
        lines.append(f"RISK SCORE: {risk_score.severity_emoji} {risk_score.score}/{risk_score.max} ({risk_score.severity})")
        lines.append(f"Confidence: {risk_score.confidence * 100:.0f}%")
        lines.append("")
        
        # Score components
        if risk_score.components:
            lines.append("RISK COMPONENTS:")
            for component in risk_score.components:
                lines.append(f"  • {component['source']}: {component['score']:.1f}/{component['max']} - {component['details']}")
            lines.append("")
        
        # Source results
        lines.append("SOURCE RESULTS:")
        lines.append("-" * 80)
        
        for source, data in results.items():
            if source == '_metadata':
                continue
            
            lines.append(f"\n{source}:")
            
            if isinstance(data, dict):
                if data.get('status') == 'error':
                    lines.append(f"  ❌ Error: {data.get('error', 'Unknown error')}")
                elif data.get('status') == 'success' and 'data' in data:
                    result_data = data['data']
                    
                    # Format based on source
                    if source == "VirusTotal":
                        lines.append(f"  Detection Ratio: {result_data.get('detection_ratio', 'N/A')}")
                        if result_data.get('names'):
                            lines.append(f"  Malware Names: {', '.join(result_data['names'][:3])}")
                    
                    elif source == "Shodan":
                        lines.append(f"  Country: {result_data.get('country', 'N/A')}")
                        lines.append(f"  Organization: {result_data.get('org', 'N/A')}")
                        if result_data.get('vulns'):
                            lines.append(f"  Vulnerabilities: {len(result_data['vulns'])} found")
                    
                    elif source == "OTX":
                        pulse_count = result_data.get('pulse_count', 0)
                        lines.append(f"  Threat Pulses: {pulse_count}")
                        if pulse_count > 0:
                            lines.append(f"  Has Threat Intel: Yes")
                    
                    elif source == "AbuseIPDB":
                        abuse_score = result_data.get('abuse_confidence_score', 0)
                        lines.append(f"  Abuse Score: {abuse_score}%")
                        lines.append(f"  Country: {result_data.get('country_name', 'N/A')}")
                        lines.append(f"  ISP: {result_data.get('isp', 'N/A')}")
                    
                    elif source == "Censys":
                        services = result_data.get('services', [])
                        lines.append(f"  Services Found: {len(services)}")
                        location = result_data.get('location', {})
                        lines.append(f"  Location: {location.get('city', 'N/A')}, {location.get('country', 'N/A')}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_json(
        indicator: str,
        results: Dict[str, Any],
        risk_score: RiskScore,
        execution_time: float
    ) -> str:
        """Generate JSON report"""
        report = {
            "indicator": indicator,
            "timestamp": datetime.utcnow().isoformat(),
            "execution_time": execution_time,
            "risk_score": {
                "score": risk_score.score,
                "max": risk_score.max,
                "severity": risk_score.severity,
                "confidence": risk_score.confidence,
                "components": risk_score.components
            },
            "sources": results
        }
        
        return json.dumps(report, indent=2)
    
    @staticmethod
    def generate_html(
        indicator: str,
        results: Dict[str, Any],
        risk_score: RiskScore,
        execution_time: float
    ) -> str:
        """Generate HTML report"""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ThreatFusion Report - {{ indicator }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        
        .risk-section {
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 3px solid #dee2e6;
        }
        .risk-score {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        .risk-badge {
            font-size: 4em;
        }
        .risk-details h2 { font-size: 1.5em; margin-bottom: 5px; }
        .risk-critical { color: #dc3545; }
        .risk-high { color: #fd7e14; }
        .risk-medium { color: #ffc107; }
        .risk-low { color: #28a745; }
        
        .components {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .component-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        .component-card h4 { color: #007bff; margin-bottom: 8px; }
        .component-card p { color: #6c757d; font-size: 0.9em; }
        
        .sources {
            padding: 30px;
        }
        .source-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #28a745;
        }
        .source-card.error { border-left-color: #dc3545; }
        .source-card h3 { margin-bottom: 15px; color: #2c3e50; }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        .data-table td {
            padding: 8px;
            border-bottom: 1px solid #dee2e6;
        }
        .data-table td:first-child {
            font-weight: 600;
            color: #495057;
            width: 200px;
        }
        
        .footer {
            padding: 20px 30px;
            background: #2c3e50;
            color: white;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 ThreatFusion Threat Intelligence Report</h1>
            <p>Indicator: <strong>{{ indicator }}</strong></p>
            <p>Generated: {{ timestamp }} | Analysis Time: {{ execution_time }}s</p>
        </div>
        
        <div class="risk-section">
            <div class="risk-score">
                <div class="risk-badge">{{ risk_score.severity_emoji }}</div>
                <div class="risk-details">
                    <h2 class="risk-{{ risk_score.severity.lower() }}">
                        Risk Score: {{ risk_score.score }}/{{ risk_score.max }}
                    </h2>
                    <p style="font-size: 1.2em;"><strong>{{ risk_score.severity }}</strong> | Confidence: {{ (risk_score.confidence * 100)|int }}%</p>
                </div>
            </div>
            
            {% if risk_score.components %}
            <div class="components">
                {% for component in risk_score.components %}
                <div class="component-card">
                    <h4>{{ component.source }}</h4>
                    <p><strong>{{ component.score }}/{{ component.max }}</strong> - {{ component.details }}</p>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        
        <div class="sources">
            <h2 style="margin-bottom: 20px; color: #2c3e50;">Intelligence Sources</h2>
            
            {% for source, data in sources.items() %}
            {% if source != '_metadata' %}
            <div class="source-card {% if data.status == 'error' %}error{% endif %}">
                <h3>{{ source }}</h3>
                
                {% if data.status == 'error' %}
                    <p style="color: #dc3545;">❌ Error: {{ data.error }}</p>
                {% elif data.status == 'success' and data.data %}
                    <table class="data-table">
                        {% for key, value in data.data.items() %}
                        <tr>
                            <td>{{ key|title }}</td>
                            <td>{{ value }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                {% endif %}
            </div>
            {% endif %}
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>ThreatFusion v0.1.0 | Automated Threat Intelligence Aggregator</p>
            <p style="opacity: 0.7; margin-top: 5px;">⚠️ This is an automated analysis. Manual verification recommended for critical decisions.</p>
        </div>
    </div>
</body>
</html>
"""
        
        template = Template(template_str)
        return template.render(
            indicator=indicator,
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            execution_time=round(execution_time, 2),
            risk_score=risk_score,
            sources=results
        )
