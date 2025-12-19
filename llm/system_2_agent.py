import os
import json
from dgca_rules.validator import FDTLValidator
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class System2Agent:
    """
    Test-Time Compute Agent (Chain-of-Thought Optimizer).
    Evaluates multiple recovery branches and validates with the Symbolic layer.
    """
    def __init__(self):
        self.verifier = FDTLValidator()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def reason_and_act(self, disruption_event, pilot_data, aircraft_data):
        print(f"--- Entering System 2 Reasoning Mode ---")
        print(f"Disruption: {disruption_event}")
        
        # Use LLM to generate recovery options
        prompt = f"""
        You are an airline operations expert. A disruption has occurred: {disruption_event}
        
        Pilot data: {json.dumps(pilot_data)}
        Aircraft data: {json.dumps(aircraft_data) if aircraft_data else 'N/A'}
        
        Generate 3-4 potential recovery strategies. Each strategy should include:
        - action: Action description
        - cost: Estimated cost impact (₹)
        - reasoning: Brief explanation
        
        Format as JSON array of objects.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            llm_response = response.choices[0].message.content.strip()
            # Extract JSON from response
            start = llm_response.find('[')
            end = llm_response.rfind(']') + 1
            json_str = llm_response[start:end]
            proposals = json.loads(json_str)
        except Exception as e:
            print(f"LLM call failed: {e}. Using fallback.")
            proposals = self._fallback_proposals()
        
        # Validate each proposal
        valid_options = []
        for prop in proposals:
            # Mock validation - in real implementation, parse action and validate
            compliant, reason = self.verifier.validate_assignment(pilot_data, {"duration_hours": 2})
            prop['compliant'] = compliant
            prop['validation_reason'] = reason
            if compliant:
                valid_options.append(prop)
        
        if not valid_options:
            return "No valid recovery plan found that meets DGCA 2025 norms."
        
        # Select lowest cost
        winner = min(valid_options, key=lambda x: x.get('cost', 0))
        
        return winner

    def _fallback_proposals(self):
        return [
            {"action": "Delay flight by 2 hours", "cost": 500, "reasoning": "Minimal impact"},
            {"action": "Swap to backup aircraft", "cost": 1200, "reasoning": "Maintains schedule"},
            {"action": "Cancel flight", "cost": 5000, "reasoning": "Last resort"}
        ]

    def generate_explainability_memo(self, winner, reason):
        memo = f"""
        RECOMMENDED ACTION: {winner.get('action', 'N/A')}
        COMPLIANCE STATUS: {winner.get('compliant', 'Unknown')}
        REASONING: {winner.get('reasoning', 'N/A')}
        ESTIMATED COST: ₹{winner.get('cost', 'N/A')}
        """
        return memo

if __name__ == "__main__":
    agent = System2Agent()
    pilot_sample = {
        "consecutive_night_duties": 2,
        "hours_since_last_rest": 24,
        "daily_flight_hours": 2
    }
    result = agent.reason_and_act("Fog in Delhi - 30% Capacity", pilot_sample, None)
    print(f"Winner: {result}")
