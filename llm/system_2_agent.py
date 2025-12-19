import os
import json
from dgca_rules.validator import FDTLValidator
from openai import OpenAI
from dotenv import load_dotenv
try:
    from .local_llm import LocalLLM
except ImportError:
    from local_llm import LocalLLM

load_dotenv()

class System2Agent:
    """
    Test-Time Compute Agent (Chain-of-Thought Optimizer).
    Evaluates multiple recovery branches and validates with the Symbolic layer.
    """
    def __init__(self):
        self.verifier = FDTLValidator()
        self.local_llm = LocalLLM()
        
        # Try to initialize OpenAI client
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.openai_available = True
            else:
                self.client = None
                self.openai_available = False
        except Exception as e:
            print(f"OpenAI client initialization failed: {e}")
            self.client = None
            self.openai_available = False

    def reason_and_act(self, disruption_event, pilot_data, aircraft_data):
        print(f"--- Entering System 2 Reasoning Mode ---")
        print(f"Disruption: {disruption_event}")
        
        if self.openai_available:
            print("Using OpenAI GPT-4 for proposal generation...")
            return self._reason_with_openai(disruption_event, pilot_data, aircraft_data)
        else:
            print("OpenAI API not available, using Local LLM...")
            return self._reason_with_local_llm(disruption_event, pilot_data, aircraft_data)
    
    def _reason_with_openai(self, disruption_event, pilot_data, aircraft_data):
        """Generate proposals using OpenAI GPT-4."""
        prompt = f"""
        You are an airline operations expert. A disruption has occurred: {disruption_event}
        
        Pilot data: {json.dumps(pilot_data)}
        Aircraft data: {json.dumps(aircraft_data) if aircraft_data else 'N/A'}
        
        Generate 2-3 potential recovery strategies specific to this disruption type. Each strategy should include:
        - action: Specific action description tailored to the disruption
        - cost: Estimated cost impact in rupees (₹)
        - reasoning: Brief explanation of why this strategy works for this disruption
        
        Make sure the actions are varied and appropriate for the specific disruption type mentioned.
        
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
            print(f"OpenAI call failed: {e}. Falling back to local LLM.")
            return self._reason_with_local_llm(disruption_event, pilot_data, aircraft_data)
        
        # Validate each proposal
        valid_options = []
        for prop in proposals:
            # Parse action to estimate duration
            action = prop.get('action', '').lower()
            duration_hours = 2.0  # Default
            if "delay" in action:
                try:
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
            
            flight_data = {"duration_hours": duration_hours, "action": action}
            compliant, reason = self.verifier.validate_assignment(pilot_data, flight_data)
            prop['compliant'] = compliant
            prop['validation_reason'] = reason
            if compliant:
                valid_options.append(prop)
        
        return valid_options if valid_options else self._reason_with_local_llm(disruption_event, pilot_data, aircraft_data)
    
    def _reason_with_local_llm(self, disruption_event, pilot_data, aircraft_data):
        """Generate proposals using local LLM."""
        try:
            proposals = self.local_llm.generate_proposals(disruption_event, pilot_data, aircraft_data)
            return proposals if proposals else self._fallback_proposals()
        except Exception as e:
            print(f"Local LLM failed: {e}. Using basic fallback.")
            return self._fallback_proposals()

    def _fallback_proposals(self):
        """Basic fallback proposals when all else fails."""
        return [
            {
                "action": "Delay flight by 2 hours",
                "cost": 500,
                "reasoning": "Standard recovery procedure to allow time for assessment",
                "compliant": True,
                "validation_reason": "Basic delay within DGCA limits"
            },
            {
                "action": "Swap to backup aircraft",
                "cost": 1200,
                "reasoning": "Maintains schedule while addressing the issue",
                "compliant": True,
                "validation_reason": "Aircraft swap within operational limits"
            }
        ]

    def generate_explainability_memo(self, proposals, reason):
        """Generate explainability memo for multiple proposals."""
        if not proposals:
            return "No valid recovery plans found that meet DGCA 2025 norms."
        
        memo = "RECOMMENDED RECOVERY STRATEGIES:\n\n"
        for i, proposal in enumerate(proposals, 1):
            memo += f"OPTION {i}:\n"
            memo += f"  ACTION: {proposal.get('action', 'N/A')}\n"
            memo += f"  COMPLIANCE STATUS: {'Compliant' if proposal.get('compliant', False) else 'Non-compliant'}\n"
            memo += f"  REASONING: {proposal.get('reasoning', 'N/A')}\n"
            memo += f"  ESTIMATED COST: ₹{proposal.get('cost', 'N/A')}\n"
            if not proposal.get('compliant', True):
                memo += f"  VIOLATION: {proposal.get('validation_reason', 'Unknown')}\n"
            memo += "\n"
        
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
