import os
import yaml
from dgca_rules.validator import FDTLValidator

# Mock LLM Explainer (System 2)
class System2Explainer:
    def explain(self, plan, compliance_result):
        is_compliant, reason = compliance_result
        if is_compliant:
            return f"The proposed plan '{plan}' is optimal and fully compliant with DGCA FDTL rules."
        else:
            return f"The proposed plan '{plan}' was REJECTED because: {reason}. Searching for alternatives..."

def run_mvp_demo():
    print("=== Neuro-Symbolic 'Proposer-Verifier-Explainer' MVP ===\n")
    
    validator = FDTLValidator()
    explainer = System2Explainer()
    
    # 1. Disruption Occurs
    print("[EVENT]: Pilot Sharma (PLT001) has reported fatigue for flight 6E-101.")
    
    # 2. Proposer (Heuristic/Agent) suggests a recovery plan
    proposals = [
        {"action": "Swap in Pilot Verma", "pilot_data": {"daily_flight_hours": 7, "consecutive_night_duties": 2, "hours_since_last_rest": 12, "weekly_flight_hours": 20}, "flight": {"duration_hours": 2}},
        {"action": "Swap in Pilot Kumar", "pilot_data": {"daily_flight_hours": 4, "consecutive_night_duties": 1, "hours_since_last_rest": 24, "weekly_flight_hours": 10}, "flight": {"duration_hours": 2}}
    ]
    
    for i, prop in enumerate(proposals):
        print(f"\n[PROPOSAL {i+1}]: {prop['action']}")
        
        # 3. Verifier (Symbolic Rulebook) checks the plan
        compliance_result = validator.validate_assignment(prop['pilot_data'], prop['flight'])
        
        # 4. LLM Explainer provides the "Glass Box" reasoning
        explanation = explainer.explain(prop['action'], compliance_result)
        print(f"[EXPLANATION]: {explanation}")
        
        if compliance_result[0]:
            print("\n[DECISION]: Proposal Approved. Executing recovery.")
            break
        else:
            print("[DECISION]: Proposal Rejected. Retrying...")

if __name__ == "__main__":
    run_mvp_demo()
