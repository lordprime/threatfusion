"""
Example: Basic ThreatFusion Usage
"""
from src.validators import IndicatorValidator
from src.agents.virustotal import VirusTotalAgent
from src.agents.otx import OTXAgent
from src.fusion.orchestrator import EnrichmentOrchestrator
from src.fusion.scorer import RiskScorer
from src.config import config


def main():
    # Example indicator
    indicator = "d131dd02c5e6eec4693d61a8d9ca3759"
    
    # Validate indicator
    validated = IndicatorValidator.validate(indicator)
    print(f"Indicator Type: {validated.type.value}")
    
    # Initialize agents (replace with your API keys)
    agents = []
    
    if config.api_config.vt_api_key:
        agents.append(VirusTotalAgent(config.api_config.vt_api_key))
    
    if config.api_config.otx_api_key:
        agents.append(OTXAgent(config.api_config.otx_api_key))
    
    if not agents:
        print("No API keys configured. Please set up .env file.")
        return
    
    # Create orchestrator and enrich
    orchestrator = EnrichmentOrchestrator(agents)
    results = orchestrator.enrich_parallel(indicator, validated.type)
    
    # Calculate risk score
    risk_score = RiskScorer.calculate_risk(results)
    
    # Print results
    print(f"\nRisk Score: {risk_score.score}/10 ({risk_score.severity})")
    print(f"Confidence: {risk_score.confidence * 100:.0f}%")
    
    for component in risk_score.components:
        print(f"  - {component['source']}: {component['score']}/{component['max']}")


if __name__ == "__main__":
    main()
