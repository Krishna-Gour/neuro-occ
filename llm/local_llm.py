import random
import json
from typing import List, Dict, Any
from dgca_rules.validator import FDTLValidator

class LocalLLM:
    """
    Local LLM implementation for generating recovery proposals when OpenAI API is unavailable.
    Uses rule-based generation with randomization for varied responses.
    """

    def __init__(self):
        self.verifier = FDTLValidator()

        # Disruption-specific action templates
        self.action_templates = {
            "weather": [
                "Implement ground stop for {duration} hours at {airport}",
                "Delay all departures by {delay_hours} hours due to visibility issues",
                "Divert flights to alternate airports: {alternates}",
                "Cancel non-essential flights and consolidate passenger loads",
                "Activate weather contingency protocols with {delay_hours} hour buffer"
            ],
            "technical": [
                "Ground affected aircraft for immediate inspection",
                "Swap to backup aircraft from maintenance fleet",
                "Delay maintenance-critical flights by {delay_hours} hours",
                "Implement reduced capacity operations on similar aircraft types",
                "Activate technical contingency protocols with engineering oversight"
            ],
            "crew": [
                "Reassign crew from cancelled flights to maintain schedules",
                "Call in reserve crew members for affected rotations",
                "Implement fatigue management protocols with rest requirements",
                "Delay flights requiring specific crew qualifications by {delay_hours} hours",
                "Activate crew contingency protocols with duty time adjustments"
            ],
            "security": [
                "Ground all flights at affected airport until clearance",
                "Divert international flights to secure alternate airports",
                "Implement enhanced security screening protocols",
                "Cancel flights to high-risk destinations with passenger rebooking",
                "Activate security contingency protocols with emergency coordination"
            ],
            "air_traffic": [
                "Delay departures by {delay_hours} hours due to ATC congestion",
                "Implement slot-based departure sequencing",
                "Route changes to less congested airspace corridors",
                "Ground stop implementation for traffic flow management",
                "Activate ATC contingency protocols with priority sequencing"
            ]
        }

        # Cost ranges for different action types
        self.cost_ranges = {
            "delay": (300, 800),
            "cancel": (2000, 5000),
            "divert": (800, 1500),
            "ground": (400, 900),
            "swap": (600, 1200),
            "reassign": (200, 600),
            "protocol": (100, 400)
        }

    def generate_proposals(self, disruption_event: str, pilot_data: Dict[str, Any], aircraft_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generate 2-3 varied recovery proposals based on disruption type.
        """
        # Parse disruption type from the event string
        disruption_type = self._extract_disruption_type(disruption_event)
        severity = self._extract_severity(disruption_event)
        airport = self._extract_airport(disruption_event)

        # Get appropriate action templates
        templates = self.action_templates.get(disruption_type, self.action_templates["weather"])

        proposals = []
        selected_templates = random.sample(templates, min(3, len(templates)))

        for i, template in enumerate(selected_templates):
            # Fill in template variables
            action = self._fill_template(template, {
                "duration": random.randint(2, 6),
                "delay_hours": random.randint(1, 4),
                "airport": airport or "affected airport",
                "alternates": "BOM, CCU, HYD"
            })

            # Generate cost based on action type
            cost = self._estimate_cost(action)

            # Create proposal
            proposal = {
                "action": action,
                "cost": cost,
                "reasoning": self._generate_reasoning(action, disruption_type, severity)
            }

            # Validate with FDTL rules
            compliant, reason = self._validate_proposal(proposal, pilot_data)
            proposal["compliant"] = compliant
            proposal["validation_reason"] = reason

            proposals.append(proposal)

        return proposals

    def _extract_disruption_type(self, event: str) -> str:
        """Extract disruption type from event description."""
        event_lower = event.lower()
        if "weather" in event_lower or "fog" in event_lower or "storm" in event_lower:
            return "weather"
        elif "technical" in event_lower or "maintenance" in event_lower or "engine" in event_lower:
            return "technical"
        elif "crew" in event_lower or "pilot" in event_lower or "fatigue" in event_lower:
            return "crew"
        elif "security" in event_lower or "threat" in event_lower or "emergency" in event_lower:
            return "security"
        elif "traffic" in event_lower or "atc" in event_lower or "congestion" in event_lower:
            return "air_traffic"
        else:
            return "weather"  # default

    def _extract_severity(self, event: str) -> str:
        """Extract severity level."""
        event_lower = event.lower()
        if "critical" in event_lower:
            return "critical"
        elif "high" in event_lower:
            return "high"
        elif "medium" in event_lower:
            return "medium"
        else:
            return "low"

    def _extract_airport(self, event: str) -> str:
        """Extract airport code if mentioned."""
        import re
        airport_match = re.search(r'\b([A-Z]{3})\b', event)
        return airport_match.group(1) if airport_match else "DEL"

    def _fill_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Fill template variables."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def _estimate_cost(self, action: str) -> int:
        """Estimate cost based on action keywords."""
        action_lower = action.lower()
        if "delay" in action_lower:
            return random.randint(*self.cost_ranges["delay"])
        elif "cancel" in action_lower:
            return random.randint(*self.cost_ranges["cancel"])
        elif "divert" in action_lower:
            return random.randint(*self.cost_ranges["divert"])
        elif "ground" in action_lower:
            return random.randint(*self.cost_ranges["ground"])
        elif "swap" in action_lower:
            return random.randint(*self.cost_ranges["swap"])
        elif "reassign" in action_lower:
            return random.randint(*self.cost_ranges["reassign"])
        else:
            return random.randint(*self.cost_ranges["protocol"])

    def _generate_reasoning(self, action: str, disruption_type: str, severity: str) -> str:
        """Generate reasoning for the action."""
        reasonings = {
            "weather": [
                "Minimizes passenger inconvenience while ensuring safety in poor visibility",
                "Balances operational continuity with weather-related safety requirements",
                "Provides buffer time for weather conditions to improve naturally"
            ],
            "technical": [
                "Ensures aircraft safety and compliance with maintenance regulations",
                "Maintains schedule integrity while addressing technical concerns",
                "Prevents potential cascading failures from unaddressed issues"
            ],
            "crew": [
                "Complies with DGCA fatigue management and duty time regulations",
                "Maintains safety standards while optimizing crew resource allocation",
                "Prevents crew scheduling conflicts and ensures proper rest periods"
            ],
            "security": [
                "Prioritizes passenger and operational security above schedule adherence",
                "Complies with security protocols and emergency response requirements",
                "Minimizes risk exposure while coordinating with security authorities"
            ],
            "air_traffic": [
                "Optimizes airspace utilization and reduces congestion-related delays",
                "Maintains ATC safety margins while improving traffic flow efficiency",
                "Balances schedule recovery with air traffic management constraints"
            ]
        }

        base_reasonings = reasonings.get(disruption_type, reasonings["weather"])
        return random.choice(base_reasonings)

    def _validate_proposal(self, proposal: Dict[str, Any], pilot_data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate proposal against FDTL rules."""
        try:
            # Extract duration from action
            action = proposal.get("action", "").lower()
            duration_hours = 2.0  # Default

            if "delay" in action:
                # Try to extract delay hours
                import re
                delay_match = re.search(r'delay.*?(\d+)', action)
                if delay_match:
                    duration_hours = float(delay_match.group(1))
            elif "cancel" in action:
                duration_hours = 0.0
            elif "ground" in action:
                duration_hours = 1.0

            flight_data = {"duration_hours": duration_hours, "action": action}
            return self.verifier.validate_assignment(pilot_data, flight_data)
        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Test the local LLM
if __name__ == "__main__":
    local_llm = LocalLLM()
    pilot_data = {
        "consecutive_night_duties": 2,
        "hours_since_last_rest": 24,
        "daily_flight_hours": 2
    }

    proposals = local_llm.generate_proposals(
        "Weather disruption at DEL: Heavy fog reducing visibility to 100m. Severity: high.",
        pilot_data
    )

    print("Local LLM Generated Proposals:")
    for i, prop in enumerate(proposals, 1):
        print(f"{i}. {prop['action']}")
        print(f"   Cost: ₹{prop['cost']}")
        print(f"   Reasoning: {prop['reasoning']}")
        print(f"   Compliant: {prop['compliant']}")
        print()