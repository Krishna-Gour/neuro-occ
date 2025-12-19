import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List, Dict, Any
from loguru import logger
from sqlalchemy.orm import Session
from database import get_db, Pilot

app = FastAPI(title="Neuro-OCC Crew MCP")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def get_pilots(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    try:
        pilots = db.query(Pilot).all()
        logger.info(f"Retrieved {len(pilots)} pilots")
        return [{"pilot_id": p.pilot_id, "name": p.name, "base": p.base, "total_hours": p.total_hours, "fatigue_score": p.fatigue_score, "last_rest_end": p.last_rest_end.isoformat(), "consecutive_night_duties": p.consecutive_night_duties} for p in pilots]
    except Exception as e:
        logger.error(f"Error retrieving pilots: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/pilots/{pilot_id}")
async def get_pilot(pilot_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        pilot = db.query(Pilot).filter(Pilot.pilot_id == pilot_id).first()
        if not pilot:
            logger.warning(f"Pilot {pilot_id} not found")
            raise HTTPException(status_code=404, detail="Pilot not found")
        logger.info(f"Retrieved pilot {pilot_id}")
        return {"pilot_id": pilot.pilot_id, "name": pilot.name, "base": pilot.base, "total_hours": pilot.total_hours, "fatigue_score": pilot.fatigue_score, "last_rest_end": pilot.last_rest_end.isoformat(), "consecutive_night_duties": pilot.consecutive_night_duties}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving pilot {pilot_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/pilots/status/fatigue")
async def get_high_fatigue_pilots(threshold: float = 0.3, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    try:
        pilots = db.query(Pilot).filter(Pilot.fatigue_score > threshold).all()
        logger.info(f"Found {len(pilots)} pilots with fatigue > {threshold}")
        return [{"pilot_id": p.pilot_id, "name": p.name, "base": p.base, "total_hours": p.total_hours, "fatigue_score": p.fatigue_score, "last_rest_end": p.last_rest_end.isoformat(), "consecutive_night_duties": p.consecutive_night_duties} for p in pilots]
    except Exception as e:
        logger.error(f"Error retrieving high fatigue pilots: {e}")
        raise HTTPException(status_code=500, detail="Database error")

if __name__ == "__main__":
    import uvicorn
    logger.add("crew_mcp.log", rotation="10 MB")
    uvicorn.run(app, host="0.0.0.0", port=8001)
