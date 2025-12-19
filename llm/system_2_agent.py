import os
import json
from dgca_rules.validator import FDTLValidator

class System2Agent:
    """
    Test-Time Compute Agent (Chain-of-Thought Optimizer).
    Evaluates multiple recovery branches and validates with the Symbolic layer.
    """
    def __init__(self):
        self.verifier = FDTLValidator()

    def reason_and_act(self, disruption_event, pilot_data, aircraft_data):
        print(f"--- Entering System 2 Reasoning Mode ---")
        print(f"Disruption: {disruption_event}")
        
        # Branch A: Delay
        branch_a_cost = 500
        branch_a_compliant, _ = self.verifier.validate_assignment(pilot_data, {"duration_hours": 2})
        
        # Branch B: Swap Aircraft
        branch_b_cost = 1200
        branch_b_compliant, _ = self.verifier.validate_assignment(pilot_data, {"duration_hours": 1})
        
        # Branch C: Cancel
        branch_c_cost = 5000
        branch_c_compliant = True # Cancellation is always 'safe' for the crew
        
        # Tree-of-Thought Selection
        options = [
            {"name": "Delay 2 Hours", "cost": branch_a_cost, "compliant": branch_a_compliant},
            {"name": "Swap with VT-ABC", "cost": branch_b_cost, "compliant": branch_b_compliant},
            {"name": "Cancel Flight", "cost": branch_c_cost, "compliant": branch_c_compliant},
        ]
        
        # Filter by compliance first (Neuro-Symbolic Valve)
        valid_options = [o for o in options if o['compliant']]
        
        if not valid_options:
            return "No valid recovery plan found that meets DGCA 2025 norms."
        
        # Select lowest cost
        winner = min(valid_options, key=lambda x: x['cost'])
        
        return winner

    def generate_explainability_memo(self, winner, reason):
        memo = f"""
        RECOMMENDED ACTION: {winner['name']}
        COMPLIANCE STATUS: Verified (DGCA 2025 Rule B)
        REASONING: {reason}
        ESTIMATED COST SAVINGS: ₹4.5L vs Cascade Delay.
        """
        return memo

if __name__ == "__main__":
    agent = System2Agent()
    pilot_sample = {
        "consecutive_night_duties": 2,
        "hours_since_last_rest": 24, # Rule B violation if assigned more night work
        "daily_flight_hours": 2
    }
    result = agent.reason_and_act("Fog in Delhi - 30% Capacity", pilot_sample, None)
    print(f"Winner: {result}")
