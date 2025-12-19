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

import requests
import asyncio
import json

# ... (keep existing imports up to 'random')

def _get_operational_context(timeout: int = 5) -> Dict[str, Any]:
    """
    Fetches the live operational "world model" from all MCP servers.
    """
    logger.info("Fetching operational context from MCP servers...")
    
    urls = {
        "flights": "http://localhost:8002/flights",
        "aircraft": "http://localhost:8002/aircraft",
        "pilots": "http://localhost:8001/pilots" # Assuming crew_mcp runs on 8001
    }
    
    try:
        with requests.Session() as session:
            responses = {
                key: session.get(url, timeout=timeout)
                for key, url in urls.items()
            }
        
        context = {}
        for key, response in responses.items():
            if response.status_code == 200:
                context[key] = response.json()
                logger.info(f"Successfully fetched {len(context[key])} {key}.")
            else:
                logger.warning(f"Failed to fetch {key}. Status: {response.status_code}")
                context[key] = [] # Return empty list on failure
        
        return context

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to MCP servers: {e}")
        return {"flights": [], "aircraft": [], "pilots": []}


def _build_llm_prompt(disruption: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Builds a goal-oriented, structured prompt for the LLM to generate a precise, optimal recovery plan.
    """
    
    # Provide full context, but warn about potential size issues.
    # TODO: Implement intelligent context pruning for very large datasets.
    flights = context.get('flights', [])
    aircraft = context.get('aircraft', [])
    pilots = context.get('pilots', [])

    prompt = f"""
You are an expert AI Operations Controller for a major airline. Your goal is to create the most optimal, precise, and compliant recovery plan for a given disruption.

**Current Disruption:**
- **Type:** {disruption.get('type')}
- **Severity:** {disruption.get('severity')}
- **Affected Airport:** {disruption.get('affected_airport')}
- **Description:** {disruption.get('description')}

**Optimization Goals (in order of importance):**
1.  **Maximize Regulatory Compliance:** The plan must be 100% compliant with DGCA FDTL rules.
2.  **Minimize Passenger Disruption:** Prioritize solutions that avoid cancellations. Delaying flights is better than cancelling.
3.  **Minimize Operational Cost:** Consider the financial impact of each action. Swapping crew is often cheaper than swapping aircraft.
4.  **Utilize Resources Intelligently:** Consider aircraft health scores (lower is worse) and pilot fatigue scores (higher is worse). Avoid using high-fatigue pilots or unhealthy aircraft unless necessary.

**Live Operational Context:**
```json
{{
  "flights": {json.dumps(flights, indent=2)},
  "aircraft": {json.dumps(aircraft, indent=2)},
  "pilots": {json.dumps(pilots, indent=2)}
}}
```

**Your Task:**
Generate a single JSON object that represents the most optimal and detailed recovery plan.

**Action Schema:**
Your response **MUST** be a single JSON object with the following structure. Do not add any text before or after the JSON object.
{{
  "plan_summary": "<A brief, human-readable summary of your plan>",
  "confidence_score": <A float from 0.0 to 1.0 indicating your confidence in this plan's optimality>,
  "estimated_cost_impact_usd": <A numerical estimate of the plan's cost impact in USD>,
  "actions": [
    {{
      "action_type": "CANCEL_FLIGHT",
      "flight_id": "<The flight_id of the flight to cancel, e.g., 'AI-203'>",
      "reason": "<Brief reason for cancellation based on optimization goals>"
    }},
    {{
      "action_type": "DELAY_FLIGHT",
      "flight_id": "<The flight_id of the flight to delay>",
      "delay_minutes": <The delay duration in minutes>,
      "reason": "<Brief reason for delay>"
    }},
    {{
      "action_type": "SWAP_AIRCRAFT",
      "flight_id": "<The flight_id that needs a new aircraft>",
      "new_aircraft_id": "<The tail_number of the new aircraft to assign>",
      "reason": "<Brief reason for the swap>"
    }},
    {{
      "action_type": "REASSIGN_CREW",
      "pilot_id": "<The pilot_id of the crew member to reassign>",
      "from_flight_id": "<The original flight_id, can be null if pilot was on standby>",
      "to_flight_id": "<The new flight_id>",
      "reason": "<Brief reason for the reassignment>"
    }},
    {{
      "action_type": "GROUND_AIRCRAFT",
      "aircraft_id": "<The tail_number of the aircraft to ground>",
      "reason": "<Brief reason for grounding>"
    }}
  ]
}}

**Instructions:**
1.  Strictly adhere to the optimization goals. Your plan's quality will be judged by them.
2.  Your entire response must be a single valid JSON object.
3.  Use exact `flight_id`, `pilot_id`, and `aircraft_id` values from the context. Do not invent new ones.
4.  For `REASSIGN_CREW`, if you are assigning a reserve pilot, the `from_flight_id` can be null.

Begin JSON response:
"""
    return prompt.strip()


def _calculate_plan_cost(plan_actions: List[Dict[str, Any]]) -> float:
    """
    Calculates a quantitative cost for a given recovery plan based on business rules.
    """
    logger.info("Calculating quantitative cost for the proposed plan...")

    # Define a simple cost model (these values should be in a config file)
    COST_MODEL = {
        "CANCEL_FLIGHT": 15000,  # Cost per cancellation in USD
        "DELAY_FLIGHT_PER_MINUTE": 100,  # Cost per minute of delay
        "SWAP_AIRCRAFT": 5000,   # Fixed cost for an aircraft swap
        "REASSIGN_CREW": 1000,     # Fixed cost for reassigning crew
        "GROUND_AIRCRAFT": 2000    # Fixed cost for grounding (e.g., maintenance checks)
    }

    total_cost = 0.0
    for action in plan_actions:
        action_type = action.get("action_type")
        if action_type == "CANCEL_FLIGHT":
            total_cost += COST_MODEL["CANCEL_FLIGHT"]
        elif action_type == "DELAY_FLIGHT":
            delay_minutes = action.get("delay_minutes", 0)
            total_cost += delay_minutes * COST_MODEL["DELAY_FLIGHT_PER_MINUTE"]
        elif action_type == "SWAP_AIRCRAFT":
            total_cost += COST_MODEL["SWAP_AIRCRAFT"]
        elif action_type == "REASSIGN_CREW":
            total_cost += COST_MODEL["REASSIGN_CREW"]
        elif action_type == "GROUND_AIRCRAFT":
            total_cost += COST_MODEL["GROUND_AIRCRAFT"]
            
    logger.info(f"Calculated plan cost: ${total_cost:,.2f} USD")
    return total_cost


@app.post("/generate-recovery-proposals")
async def generate_recovery_proposals(disruption: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generates a high-precision recovery plan using a world model and a structured LLM prompt.
    """
    try:
        logger.info(f"Generating high-precision recovery plan for disruption: {disruption}")
        
        # 1. Fetch the live operational "world model"
        operational_context = _get_operational_context()
        if not any(operational_context.values()):
            raise HTTPException(status_code=503, detail="MCP servers are unavailable. Cannot generate a precise plan.")

        # Create maps for quick lookups
        pilots_map = {{p['pilot_id']: p for p in operational_context.get('pilots', [])}}

        # 2. Build the detailed, goal-oriented prompt for the LLM
        prompt = _build_llm_prompt(disruption, operational_context)

        # 3. Invoke System 1 (LLM Proposer) to get a structured plan
        logger.info("Invoking LLM Proposer for a structured, actionable plan...")
        llm_agent = System2Agent()
        raw_llm_output = llm_agent.reason_and_act_structured(prompt)
        
        if not raw_llm_output:
            raise ValueError("LLM agent returned no output.")

        # 4. Parse and Validate the LLM's JSON output
        try:
            if raw_llm_output.startswith("```json"):
                raw_llm_output = raw_llm_output[7:-4].strip()
            plan = json.loads(raw_llm_output)
            logger.info(f"LLM proposed plan: {plan.get('plan_summary')}")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM. Output: {raw_llm_output}")
            raise ValueError("LLM did not return a valid JSON object.")

        # 5. Accurate Verification with System 2 (Symbolic Verifier)
        all_actions_compliant = True
        violations = []
        
        for action in plan.get("actions", []):
            pilot_data_for_action = None
            
            # Find the specific pilot data for validation if the action involves crew
            if action['action_type'] == 'REASSIGN_CREW':
                pilot_id = action.get('pilot_id')
                if pilot_id in pilots_map:
                    pilot_data_for_action = pilots_map[pilot_id]
                else:
                    logger.warning(f"Pilot '{pilot_id}' from plan not found in context.")
                    all_actions_compliant = False
                    violations.append({
                        "rule": "data_consistency_error",
                        "description": f"Proposed pilot_id '{pilot_id}' does not exist in the provided context.",
                        "severity": "high"
                    })
                    continue # Skip validation for this action

            # If action doesn't involve a pilot, we can't do FDTL validation
            if not pilot_data_for_action:
                continue

            # The verifier needs to be adapted to handle structured actions
            # For now, we adapt the call to fit the old validation function signature
            compliance_result = _validate_with_fdtl(
                {"action": f"{action['action_type']} {action.get('flight_id', '')}"}, 
                pilot_data_for_action # Use the CORRECT pilot data
            )
            if not compliance_result["compliant"]:
                all_actions_compliant = False
                violations.extend(compliance_result["violations"])
        
        # 6. Calculate quantitative cost of the plan
        plan_cost_usd = _calculate_plan_cost(plan.get("actions", []))

        # 7. Format the response for the frontend
        proposal = {
            "id": 1,
            "action": plan.get("plan_summary", "No summary provided."),
            "reason": f"AI-generated plan to address {disruption.get('type')} disruption.",
            "savings": f"₹{plan_cost_usd * 80:,.0f}", # Use calculated cost, convert to INR
            "compliant": all_actions_compliant,
            "violations": violations,
            "source": "LLM+Verifier (Scored)",
            "confidence": plan.get("confidence_score", 0.0),
            "disruption_type": disruption.get('type'),
            "severity": disruption.get('severity'),
            "affected_airport": disruption.get('affected_airport'),
            "details": plan.get("actions", [])
        }
        
        logger.info(f"Generated 1 high-precision, scored recovery proposal.")
        return [proposal]

    except Exception as e:
        logger.error(f"Error generating high-precision proposals: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate proposals: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    logger.add("brain_api.log", rotation="10 MB")
    uvicorn.run(app, host="0.0.0.0", port=8004)