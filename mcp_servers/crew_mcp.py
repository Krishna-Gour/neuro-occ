import pandas as pd
from fastapi import FastAPI, HTTPException
import os
from typing import List, Dict, Any
from loguru import logger

app = FastAPI(title="Neuro-OCC Crew MCP")

DATA_PATH = "data/pilots.csv"

def load_pilots() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")
    return pd.read_csv(DATA_PATH)

@app.on_event("startup")
async def startup_event():
    logger.info("Crew MCP service starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Crew MCP service shutting down")

@app.get("/health")
async def health_check() -> Dict[str, str]:
    logger.info("Health check requested")
    return {"status": "healthy", "service": "crew_mcp"}

@app.get("/pilots")
async def get_pilots() -> List[Dict[str, Any]]:
    try:
        df = load_pilots()
        logger.info(f"Retrieved {len(df)} pilots")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        logger.error("Pilots data not available")
        raise HTTPException(status_code=404, detail="Pilots data not available")

@app.get("/pilots/{pilot_id}")
async def get_pilot(pilot_id: str) -> Dict[str, Any]:
    try:
        df = load_pilots()
        pilot = df[df['pilot_id'] == pilot_id]
        if pilot.empty:
            logger.warning(f"Pilot {pilot_id} not found")
            raise HTTPException(status_code=404, detail="Pilot not found")
        logger.info(f"Retrieved pilot {pilot_id}")
        return pilot.iloc[0].to_dict()
    except FileNotFoundError:
        logger.error("Pilots data not available")
        raise HTTPException(status_code=404, detail="Pilots data not available")

@app.get("/pilots/status/fatigue")
async def get_high_fatigue_pilots(threshold: float = 0.3) -> List[Dict[str, Any]]:
    try:
        df = load_pilots()
        high_fatigue = df[df['fatigue_score'] > threshold]
        logger.info(f"Found {len(high_fatigue)} pilots with fatigue > {threshold}")
        return high_fatigue.to_dict(orient="records")
    except FileNotFoundError:
        logger.error("Pilots data not available")
        raise HTTPException(status_code=404, detail="Pilots data not available")

if __name__ == "__main__":
    import uvicorn
    logger.add("crew_mcp.log", rotation="10 MB")
    uvicorn.run(app, host="0.0.0.0", port=8001)
