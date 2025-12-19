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
from database import get_db, Aircraft, Flight

app = FastAPI(title="Neuro-OCC Fleet MCP")

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
    logger.info("Fleet MCP service starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Fleet MCP service shutting down")

@app.get("/health")
async def health_check() -> Dict[str, str]:
    logger.info("Health check requested")
    return {"status": "healthy", "service": "fleet_mcp"}

@app.get("/aircraft")
async def get_all_aircraft(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    try:
        aircraft = db.query(Aircraft).all()
        logger.info(f"Retrieved {len(aircraft)} aircraft")
        return [{"tail_number": a.tail_number, "model": a.type, "base": a.base, "health_score": a.health_score} for a in aircraft]
    except Exception as e:
        logger.error(f"Error retrieving aircraft: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/aircraft/{tail_number}")
async def get_aircraft(tail_number: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        aircraft = db.query(Aircraft).filter(Aircraft.tail_number == tail_number).first()
        if not aircraft:
            logger.warning(f"Aircraft {tail_number} not found")
            raise HTTPException(status_code=404, detail="Aircraft not found")
        logger.info(f"Retrieved aircraft {tail_number}")
        return {"tail_number": aircraft.tail_number, "model": aircraft.type, "base": aircraft.base, "health_score": aircraft.health_score}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving aircraft {tail_number}: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/flights")
async def get_all_flights(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    try:
        flights = db.query(Flight).all()
        logger.info(f"Retrieved {len(flights)} flights")
        return [{"flight_id": f.flight_number, "tail_number": f.aircraft_tail, "origin": f.origin, "destination": f.destination, "departure_time": f.scheduled_departure.isoformat(), "arrival_time": f.scheduled_arrival.isoformat(), "status": f.status, "crew": f.pilot_id} for f in flights]
    except Exception as e:
        logger.error(f"Error retrieving flights: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/aircraft/{tail_number}/mamba-score")
async def get_mamba_health_score(tail_number: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        aircraft = db.query(Aircraft).filter(Aircraft.tail_number == tail_number).first()
        if not aircraft:
            logger.warning(f"Aircraft {tail_number} not found")
            raise HTTPException(status_code=404, detail="Aircraft not found")
        logger.info(f"Retrieved Mamba score for {tail_number}")
        return {"tail_number": tail_number, "health_score": aircraft.health_score}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Mamba score for {tail_number}: {e}")
        raise HTTPException(status_code=500, detail="Database error")

if __name__ == "__main__":
    import uvicorn
    logger.add("fleet_mcp.log", rotation="10 MB")
    uvicorn.run(app, host="0.0.0.0", port=8002)
