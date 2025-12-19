from fastapi import FastAPI
import os
from typing import Dict, Any

app = FastAPI(title="Neuro-OCC Reg MCP")

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

@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "reg_mcp"}

@app.get("/rules")
async def get_all_rules() -> Dict[str, Dict[str, Any]]:
    return RULES

@app.get("/rules/{rule_id}")
async def get_rule(rule_id: str) -> Dict[str, Any]:
    if rule_id not in RULES:
        return {"error": "Rule not found"}
    return RULES[rule_id]

@app.get("/verify/rest")
async def check_rest_compliance(consecutive_nights: int, rest_hours: float) -> Dict[str, Any]:
    if consecutive_nights >= 2 and rest_hours < 56:
        return {"compliant": False, "reason": "Rule Rule B: Consecutive night duties require 56h rest."}
    return {"compliant": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
