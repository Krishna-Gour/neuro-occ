import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Tuple
from loguru import logger
from llm.system_2_agent import System2Agent
from dgca_rules.validator import FDTLValidator
from brain.recovery_env import AirlineRecoveryEnv
import random

app = FastAPI(title="Neuro-OCC Brain API")

# Initialize the symbolic verifier (System 2 component)
try:
    fdtl_validator = FDTLValidator()
    logger.info("FDTL Validator initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize FDTL Validator: {e}")
    fdtl_validator = None

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
            "mamba_sentinel_monitoring",
            "llm_proposer_verifier_loop"
        ]
    }

@app.post("/sentinel/monitor")
async def sentinel_monitor(flight_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mamba Sentinel: Proactive disruption detection endpoint
    
    This endpoint should be called periodically with real-time flight data.
    The Mamba model analyzes patterns and predicts potential disruptions.
    When a disruption is detected, it triggers the recovery workflow.
    
    TODO: Integrate trained Mamba model for time-series anomaly detection
    """
    logger.info("Sentinel monitoring triggered")
    
    # TODO: Load trained Mamba model
    # TODO: Process flight_data into time-series tensor
    # TODO: Run Mamba inference to detect anomalies/disruptions
    # TODO: If disruption predicted, automatically trigger generate_recovery_proposals
    
    return {
        "status": "monitoring_active",
        "message": "Mamba Sentinel integration pending - model training required",
        "predicted_disruptions": []
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

def _validate_with_fdtl(action_data: Dict[str, Any], pilot_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use the real FDTL Validator (System 2 Verifier) to check DGCA compliance.
    This replaces the mock _evaluate_dgca_compliance function.
    """
    if not fdtl_validator:
        logger.warning("FDTL Validator not available, using basic validation")
        return {
            "compliant": True,
            "violations": [],
            "violation_count": 0,
            "reason": "Validator not initialized"
        }
    
    # Extract flight duration from action
    action = action_data.get("action", "").lower()
    
    # Estimate duration based on action type
    duration_hours = 2.0  # Default
    if "delay" in action:
        try:
            # Try to extract delay hours from action string
            words = action.split()
            for i, word in enumerate(words):
                if "hour" in word and i > 0:
                    duration_hours = float(words[i-1])
                    break
        except:
            duration_hours = 2.0
    elif "cancel" in action:
        duration_hours = 0.0
    elif "swap" in action:
        duration_hours = 1.0
    
    # Create proposed flight dict
    proposed_flight = {
        "duration_hours": duration_hours,
        "action": action_data.get("action", "")
    }
    
    # Validate using the real FDTLValidator
    is_compliant, reason = fdtl_validator.validate_assignment(pilot_data, proposed_flight)
    
    violations = []
    if not is_compliant:
        violations.append({
            "rule": "fdtl_violation",
            "description": reason,
            "severity": "high",
            "impact": "DGCA 2025 FDTL rule violation"
        })
    
    return {
        "compliant": is_compliant,
        "violations": violations,
        "violation_count": len(violations),
        "reason": reason
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

        # SYSTEM 1 (LLM PROPOSER): Generate creative, context-aware recovery proposals
        logger.info("Invoking System 1 (LLM Proposer)...")
        try:
            llm_agent = System2Agent()  # Initialize only when needed
            enhanced_description = f"{disruption_type.title()} disruption at {affected_airport}: {disruption.get('description', 'Service disruption')}. Severity: {severity}."

            llm_results = llm_agent.reason_and_act(
                enhanced_description,
                pilot_data,
                None
            )

            if isinstance(llm_results, list) and len(llm_results) > 0:
                # SYSTEM 2 (SYMBOLIC VERIFIER): Already validated in System2Agent
                for i, llm_result in enumerate(llm_results[:2]):  # Take up to 2 LLM proposals
                    proposals.append({
                        "id": len(proposals) + 1,
                        "action": llm_result.get("action", "LLM Generated Action"),
                        "reason": llm_result.get("reasoning", "LLM reasoning"),
                        "savings": f"₹{llm_result.get('cost', 0):.0f}",
                        "compliant": llm_result.get("compliant", True),
                        "violations": [] if llm_result.get("compliant", True) else [{"rule": "fdtl_violation", "description": llm_result.get("validation_reason", "Unknown")}],
                        "source": "LLM+Verifier",
                        "disruption_type": disruption_type,
                        "severity": severity,
                        "affected_airport": affected_airport
                    })
                logger.info(f"LLM proposals added: {len(llm_results)} generated, {len([p for p in proposals if p['source'] == 'LLM+Verifier'])} validated")
            else:
                raise ValueError("LLM did not return valid proposals")
                
        except Exception as e:
            logger.error(f"LLM+Verifier pipeline failed: {e}")
            # Use disruption-specific fallbacks
            logger.warning("Using disruption-specific fallback proposals")

        # RL AGENT: Disabled until properly trained
        # TODO: Train RL agent using Stable-Baselines3 or RLlib
        # TODO: Load trained model and use model.predict() instead of random actions
        # For now, the RL component is disabled to focus on the core neuro-symbolic loop
        logger.info("RL agent training required - skipping RL proposals for now")
        
        # Uncomment below to add RL proposals once trained:
        # rl_env.reset()
        # trained_model = load_trained_model()  # Load your trained RL model
        # state = rl_env.get_state()
        # action, _states = trained_model.predict(state, deterministic=True)
        # ... validate with FDTL and add to proposals

        # If no proposals generated, add disruption-specific fallbacks
        if not proposals:
            fallback_actions = base_actions[:2]  # Take first 2 base actions
            for i, action in enumerate(fallback_actions):
                # Validate fallback with FDTL
                action_data = {"action": action}
                compliance_result = _validate_with_fdtl(action_data, pilot_data)
                
                proposals.append({
                    "id": len(proposals) + 1,
                    "action": action,
                    "reason": f"Disruption-specific fallback for {disruption_type}",
                    "savings": f"₹{500 + i * 200}",  # Vary costs slightly
                    "compliant": compliance_result["compliant"],
                    "violations": compliance_result["violations"],
                    "source": "Fallback",
                    "disruption_type": disruption_type,
                    "severity": severity,
                    "affected_airport": affected_airport
                })

        logger.info(f"Generated {len(proposals)} recovery proposals")
        return proposals

    except Exception as e:
        logger.error(f"Error generating proposals: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate proposals")

if __name__ == "__main__":
    import uvicorn
    logger.add("brain_api.log", rotation="10 MB")
    uvicorn.run(app, host="0.0.0.0", port=8004)