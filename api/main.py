"""
ThreatFusion API Server
FastAPI backend for the web dashboard
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json

from src.config import config
from src.validators import IndicatorValidator
from src.models import IndicatorType
from src.agents.virustotal import VirusTotalAgent
from src.agents.shodan import ShodanAgent
from src.agents.censys import CensysAgent
from src.agents.otx import OTXAgent
from src.agents.abuseipdb import AbuseIPDBAgent
from src.fusion.orchestrator import EnrichmentOrchestrator
from src.fusion.scorer import RiskScorer

app = FastAPI(
    title="ThreatFusion API",
    description="Threat Intelligence Aggregator API",
    version="0.1.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EnrichRequest(BaseModel):
    indicator: str
    timeout: int = 30


class EnrichResponse(BaseModel):
    indicator: str
    indicator_type: str
    is_private: bool
    risk_score: Dict[str, Any]
    results: Dict[str, Any]
    execution_time: float


def initialize_agents():
    """Initialize all configured threat intelligence agents"""
    agents = []
    api_config = config.api_config
    
    if api_config.vt_api_key:
        agents.append(VirusTotalAgent(api_config.vt_api_key))
    
    if api_config.shodan_api_key:
        agents.append(ShodanAgent(api_config.shodan_api_key))
    
    if api_config.censys_api_id and api_config.censys_api_secret:
        agents.append(CensysAgent(api_config.censys_api_id, api_config.censys_api_secret))
    
    if api_config.otx_api_key:
        agents.append(OTXAgent(api_config.otx_api_key))
    
    if api_config.abuseipdb_api_key:
        agents.append(AbuseIPDBAgent(api_config.abuseipdb_api_key))
    
    return agents


@app.get("/")
async def root():
    """API health check"""
    return {"status": "ok", "message": "ThreatFusion API is running"}


@app.get("/api/config")
async def get_config():
    """Get API configuration status"""
    validation = config.validate_api_keys()
    configured_count = sum(1 for v in validation.values() if v)
    
    return {
        "services": validation,
        "configured_count": configured_count,
        "total_services": len(validation)
    }


@app.post("/api/enrich", response_model=EnrichResponse)
async def enrich_indicator(request: EnrichRequest):
    """Enrich a threat indicator with intelligence from multiple sources"""
    import time
    
    # Validate indicator
    try:
        validated = IndicatorValidator.validate(request.indicator)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Initialize agents
    agents = initialize_agents()
    if not agents:
        raise HTTPException(
            status_code=503,
            detail="No API keys configured. Please set up .env file."
        )
    
    # Create orchestrator and run enrichment
    orchestrator = EnrichmentOrchestrator(agents, max_workers=config.app_config.max_workers)
    
    start_time = time.time()
    results = orchestrator.enrich_parallel(request.indicator, validated.type, timeout=request.timeout)
    execution_time = time.time() - start_time
    
    # Calculate risk score
    risk_score = RiskScorer.calculate_risk(results)
    
    return EnrichResponse(
        indicator=request.indicator,
        indicator_type=validated.type.value,
        is_private=validated.is_private,
        risk_score=risk_score.model_dump(),
        results=results,
        execution_time=round(execution_time, 2)
    )


# WebSocket for real-time progress updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    """WebSocket endpoint for real-time progress updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - will be used for progress updates
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
