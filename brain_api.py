import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from loguru import logger
from llm.system_2_agent import System2Agent
from brain.recovery_env import AirlineRecoveryEnv
import random

app = FastAPI(title="Neuro-OCC Brain API")

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
    logger.info("Brain API service starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Brain API service shutting down")


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Simple health probe used by orchestration scripts and the dashboard."""
    return {
        "status": "healthy",
        "service": "brain_api",
        "message": "Neuro-Symbolic reasoning engine online"
    }


@app.get("/status")
async def status_snapshot() -> Dict[str, Any]:
    """Operational snapshot for dashboard system status widgets."""
    return {
        "service": "brain_api",
        "status": "healthy",
        "capabilities": [
            "neuro_symbolic_reasoning",
            "dgca_compliance_guardrails",
            "rl_recovery_simulation"
        ]
    }

@app.get("/disruption-types")
async def get_disruption_types() -> List[Dict[str, Any]]:
    """
    Get available disruption types with descriptions and severity levels
    """
    return [
        {
            "type": "weather",
            "name": "Weather Disruption",
            "description": "Fog, rain, storms, or other weather-related issues",
            "severities": ["low", "medium", "high", "critical"],
            "common_actions": ["Delay flights", "Cancel flights", "Divert routes", "Ground stop"]
        },
        {
            "type": "technical",
            "name": "Technical Issues",
            "description": "Aircraft maintenance, equipment failure, or technical problems",
            "severities": ["low", "medium", "high"],
            "common_actions": ["Ground aircraft", "Swap aircraft", "Delay maintenance", "Reduce capacity"]
        },
        {
            "type": "crew",
            "name": "Crew Availability",
            "description": "Pilot illness, fatigue, scheduling conflicts, or crew shortages",
            "severities": ["low", "medium", "high"],
            "common_actions": ["Reassign crew", "Call reserves", "Delay flights", "Cancel flights"]
        },
        {
            "type": "security",
            "name": "Security Incident",
            "description": "Security threats, airport lockdowns, or emergency situations",
            "severities": ["medium", "high", "critical"],
            "common_actions": ["Ground flights", "Divert routes", "Enhanced screening", "Cancel flights"]
        },
        {
            "type": "air_traffic",
            "name": "Air Traffic Control",
            "description": "ATC delays, airspace restrictions, or congestion issues",
            "severities": ["low", "medium", "high"],
            "common_actions": ["Delay departures", "Hold at gate", "Route changes", "Slot adjustments"]
        }
    ]

def _evaluate_dgca_compliance(action_data: Dict[str, Any], pilot_data: Dict[str, Any], disruption_type: str, severity: str = "medium") -> Dict[str, Any]:
    """
    Enhanced DGCA compliance checking with specific rule violations
    """
    violations = []
    compliant = True

    action = action_data.get("action", "").lower()

    # Check rest requirements
    if "delay" in action and "hour" in action:
        # Extract delay hours
        try:
            delay_hours = int(action.split("hour")[0].split()[-1])
            if delay_hours > 4:  # Long delays might violate rest rules
                if pilot_data.get("consecutive_night_duties", 0) >= 2:
                    violations.append({
                        "rule": "rule_48_hour_rest",
                        "description": "Consecutive night duties require 56h rest period",
                        "severity": "high",
                        "impact": "Crew fatigue and safety risk"
                    })
                    compliant = False
        except:
            pass

    # Check flight time limits
    if pilot_data.get("daily_flight_hours", 0) + 2 > 8:  # Assuming 2 hours additional
        violations.append({
            "rule": "max_daily_flight_time",
            "description": "Daily flight time cannot exceed 8 hours",
            "severity": "high",
            "impact": "Crew duty time violation"
        })
        compliant = False

    # Check weekly limits
    if pilot_data.get("weekly_flight_hours", 0) + 2 > 35:
        violations.append({
            "rule": "weekly_flight_limit",
            "description": "Weekly flight time cannot exceed 35 hours",
            "severity": "medium",
            "impact": "Long-term fatigue accumulation"
        })
        compliant = False

    # Disruption-specific violations
    if disruption_type == "security" and "cancel" not in action:
        violations.append({
            "rule": "emergency_procedures",
            "description": "Security incidents require flight cancellations",
            "severity": "critical",
            "impact": "Passenger safety and regulatory compliance"
        })
        compliant = False

    if disruption_type == "weather" and "ground stop" not in action and severity == "high":
        violations.append({
            "rule": "weather_contingency",
            "description": "Severe weather requires ground stop procedures",
            "severity": "high",
            "impact": "Safety and operational risk"
        })
        compliant = False

    return {
        "compliant": compliant,
        "violations": violations,
        "violation_count": len(violations)
    }

@app.post("/generate-recovery-proposals")
async def generate_recovery_proposals(disruption: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate recovery proposals using LLM + RL integration with varied disruptions and DGCA compliance
    """
    try:
        logger.info(f"Generating recovery proposals for disruption: {disruption}")

        # Initialize agents
        rl_env = AirlineRecoveryEnv()

        proposals = []
        violations = []

        # Enhanced disruption types with specific impacts
        disruption_type = disruption.get("type", "weather")
        severity = disruption.get("severity", "medium")
        affected_airport = disruption.get("affected_airport", "DEL")

        # Get sample pilot and aircraft data from environment
        if rl_env.pilots:
            sample_pilot = rl_env.pilots[0]  # Get first pilot
            pilot_data = {
                "consecutive_night_duties": sample_pilot.consecutive_night_duties,
                "hours_since_last_rest": 12,  # Mock
                "daily_flight_hours": 6,  # Mock
                "weekly_flight_hours": 20  # Mock
            }
        else:
            pilot_data = {
                "consecutive_night_duties": 2,
                "hours_since_last_rest": 24,
                "daily_flight_hours": 2
            }

        # Generate context-aware proposals based on disruption type
        if disruption_type == "weather":
            base_actions = [
                "Delay all departures by 2-4 hours",
                "Cancel non-critical flights",
                "Divert flights to alternate airports",
                "Implement ground stop procedures"
            ]
        elif disruption_type == "technical":
            base_actions = [
                "Ground affected aircraft for inspection",
                "Swap to backup aircraft",
                "Delay maintenance-critical flights",
                "Implement reduced capacity operations"
            ]
        elif disruption_type == "crew":
            base_actions = [
                "Reassign crew from cancelled flights",
                "Call in reserve crew members",
                "Implement fatigue management protocols",
                "Delay flights requiring specific crew qualifications"
            ]
        elif disruption_type == "security":
            base_actions = [
                "Ground all flights at affected airport",
                "Divert international flights",
                "Implement enhanced security screening",
                "Cancel flights to high-risk destinations"
            ]
        else:
            base_actions = [
                "Assess situation and determine impact",
                "Implement contingency procedures",
                "Communicate with stakeholders",
                "Monitor situation for changes"
            ]

        # Try LLM first with enhanced context
        try:
            llm_agent = System2Agent()  # Initialize only when needed
            enhanced_description = f"{disruption_type.title()} disruption at {affected_airport}: {disruption.get('description', 'Service disruption')}. Severity: {severity}."

            llm_result = llm_agent.reason_and_act(
                enhanced_description,
                pilot_data,
                None
            )

            if isinstance(llm_result, dict):
                # Enhanced compliance checking
                compliance_result = _evaluate_dgca_compliance(llm_result, pilot_data, disruption_type, severity)
                proposals.append({
                    "id": 1,
                    "action": llm_result.get("action", "LLM Generated Action"),
                    "reason": llm_result.get("reasoning", "LLM reasoning"),
                    "savings": f"₹{llm_result.get('cost', 0):.0f}",
                    "compliant": compliance_result["compliant"],
                    "violations": compliance_result["violations"],
                    "source": "LLM",
                    "disruption_type": disruption_type,
                    "severity": severity,
                    "affected_airport": affected_airport
                })
        except Exception as e:
            logger.warning(f"LLM call failed (expected without API key): {e}")
            # Add enhanced mock LLM proposals based on disruption type
            mock_action = random.choice(base_actions)
            compliance_result = _evaluate_dgca_compliance({"action": mock_action}, pilot_data, disruption_type, severity)
            proposals.append({
                "id": len(proposals) + 1,
                "action": f"{mock_action} (LLM Simulation)",
                "reason": f"AI analysis for {disruption_type} disruption suggests {mock_action.lower()}",
                "savings": f"₹{random.randint(500, 5000):.0f}K",
                "compliant": compliance_result["compliant"],
                "violations": compliance_result["violations"],
                "source": "LLM-Simulated",
                "disruption_type": disruption_type,
                "severity": severity,
                "affected_airport": affected_airport
            })

        # Add RL-based proposals
        rl_env.reset()
        for i in range(3):
            action = random.choice([0, 1, 2, 3, 4])  # Random action
            _, reward, done, _, info = rl_env.step(action)

            action_names = {
                0: "No Action",
                1: "Delay flight by 60 minutes",
                2: "Cancel flight",
                3: "Swap aircraft",
                4: "Swap crew"
            }

            action_name = action_names.get(action, f"Action {action}")
            compliance_result = _evaluate_dgca_compliance({"action": action_name}, pilot_data, disruption_type, severity)

            proposals.append({
                "id": len(proposals) + 1,
                "action": action_name,
                "reason": f"RL optimization - Reward: {reward:.2f}. Disruption-aware: {disruption_type} at {affected_airport}",
                "savings": f"₹{abs(reward) * 1000:.0f}",
                "compliant": compliance_result["compliant"],
                "violations": compliance_result["violations"],
                "source": "RL",
                "disruption_type": disruption_type,
                "severity": severity,
                "affected_airport": affected_airport
            })

            if done:
                break

        # If no proposals generated, add fallbacks
        if not proposals:
            proposals = [
                {
                    "id": 1,
                    "action": "Delay flight by 2 hours",
                    "reason": "Standard recovery procedure",
                    "savings": "₹500",
                    "compliant": True,
                    "source": "Fallback"
                },
                {
                    "id": 2,
                    "action": "Swap to backup aircraft",
                    "reason": "Maintains schedule",
                    "savings": "₹1200",
                    "compliant": True,
                    "source": "Fallback"
                }
            ]

        logger.info(f"Generated {len(proposals)} recovery proposals")
        return proposals

    except Exception as e:
        logger.error(f"Error generating proposals: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate proposals")

if __name__ == "__main__":
    import uvicorn
    logger.add("brain_api.log", rotation="10 MB")
    uvicorn.run(app, host="0.0.0.0", port=8004)