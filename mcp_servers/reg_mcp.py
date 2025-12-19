import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Dict, Any, List
from loguru import logger
from sqlalchemy.orm import Session
from database import get_db, Airport

app = FastAPI(title="Neuro-OCC Reg MCP")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DGCA 2025 FDTL Rules (Summarized for Agent Consumption)
RULES: Dict[str, Dict[str, Any]] = {
    "rule_48_hour_rest": {
        "description": "If consecutive night duties = 2, then rest period >= 56 hours.",
        "applicability": "2025 DGCA CAR",
        "hard_constraint": True
    },
    "max_night_landings": {
        "limit": 2,
        "action": "duty_end = True",
        "hard_constraint": True
    },
    "max_daily_flight_time": {
        "limit_hours": 8,
        "hard_constraint": True
    },
    "weekly_flight_limit": {
        "limit_hours": 35,
        "hard_constraint": True
    }
}

@app.on_event("startup")
async def startup_event():
    logger.info("Reg MCP service starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Reg MCP service shutting down")

@app.get("/health")
async def health_check() -> Dict[str, str]:
    logger.info("Health check requested")
    return {"status": "healthy", "service": "reg_mcp"}

@app.get("/rules")
async def get_all_rules() -> Dict[str, Dict[str, Any]]:
    logger.info("Retrieved all rules")
    return RULES

@app.get("/rules/{rule_id}")
async def get_rule(rule_id: str) -> Dict[str, Any]:
    if rule_id not in RULES:
        logger.warning(f"Rule {rule_id} not found")
        raise HTTPException(status_code=404, detail="Rule not found")
    logger.info(f"Retrieved rule {rule_id}")
    return RULES[rule_id]

@app.get("/verify/rest")
async def check_rest_compliance(consecutive_nights: int, rest_hours: float) -> Dict[str, Any]:
    logger.info(f"Checking rest compliance: nights={consecutive_nights}, rest={rest_hours}")
    if consecutive_nights >= 2 and rest_hours < 56:
        return {"compliant": False, "reason": "Rule Rule B: Consecutive night duties require 56h rest."}
    return {"compliant": True}

@app.get("/airports")
async def get_airports(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    try:
        airports = db.query(Airport).all()
        logger.info(f"Retrieved {len(airports)} airports")
        return [{"code": a.id, "name": a.name, "lat": a.lat, "lon": a.lon} for a in airports]
    except Exception as e:
        logger.error(f"Error retrieving airports: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/airports/{code}")
async def get_airport(code: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        airport = db.query(Airport).filter(Airport.id == code).first()
        if not airport:
            logger.warning(f"Airport {code} not found")
            raise HTTPException(status_code=404, detail="Airport not found")
        logger.info(f"Retrieved airport {code}")
        return {"code": airport.id, "name": airport.name, "lat": airport.lat, "lon": airport.lon}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving airport {code}: {e}")
        raise HTTPException(status_code=500, detail="Database error")

if __name__ == "__main__":
    import uvicorn
    logger.add("reg_mcp.log", rotation="10 MB")
    uvicorn.run(app, host="0.0.0.0", port=8003)
