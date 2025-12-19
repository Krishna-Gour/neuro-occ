"""
RL Model Integration Helper for brain_api.py

This module provides utility functions to load and use a trained RL model
in the brain_api.py service.

Usage in brain_api.py:
    from scripts.rl_integration import RLProposalGenerator
    
    rl_generator = RLProposalGenerator("models/rl_recovery_ppo.zip")
    proposal = rl_generator.generate_proposal(disruption, pilot_data)
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, Optional
from loguru import logger

class RLProposalGenerator:
    """
    Wrapper for trained RL model to generate recovery proposals
    """
    
    def __init__(self, model_path: str):
        """
        Initialize the RL proposal generator
        
        Args:
            model_path: Path to the trained RL model (.zip file)
        """
        self.model = None
        self.model_path = model_path
        self.env = None
        
        try:
            # Try to load stable-baselines3
            from stable_baselines3 import PPO, DQN
            from brain.recovery_env import AirlineRecoveryEnv
            
            # Load the model based on filename
            if "ppo" in model_path.lower():
                self.model = PPO.load(model_path)
            elif "dqn" in model_path.lower():
                self.model = DQN.load(model_path)
            else:
                raise ValueError("Model path must contain 'ppo' or 'dqn'")
            
            self.env = AirlineRecoveryEnv()
            logger.info(f"RL model loaded successfully from {model_path}")
            
        except ImportError:
            logger.warning("stable-baselines3 not installed. RL proposals disabled.")
        except FileNotFoundError:
            logger.warning(f"Model file not found at {model_path}. RL proposals disabled.")
        except Exception as e:
            logger.error(f"Failed to load RL model: {e}")
    
    def is_available(self) -> bool:
        """Check if RL model is loaded and available"""
        return self.model is not None and self.env is not None
    
    def generate_proposal(
        self, 
        disruption: Dict[str, Any], 
        pilot_data: Dict[str, Any],
        validate_with_fdtl=True
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a recovery proposal using the trained RL agent
        
        Args:
            disruption: Disruption details (type, severity, etc.)
            pilot_data: Current pilot state
            validate_with_fdtl: Whether to validate with FDTL rules
            
        Returns:
            Proposal dict or None if RL not available
        """
        if not self.is_available():
            return None
        
        try:
            # Reset environment with disruption context
            obs, info = self.env.reset()
            
            # Get action from trained model (deterministic for production)
            action, _states = self.model.predict(obs, deterministic=True)
            
            # Execute action to get reward
            _, reward, _, _, info = self.env.step(action)
            
            # Map action to description
            action_names = {
                0: "No Action",
                1: "Delay flight by 60 minutes",
                2: "Cancel flight",
                3: "Swap aircraft",
                4: "Swap crew"
            }
            
            action_name = action_names.get(int(action), f"Action {action}")
            
            # Create proposal
            proposal = {
                "action": action_name,
                "reason": f"RL-optimized recovery strategy (Reward: {reward:.2f})",
                "savings": f"₹{abs(reward) * 1000:.0f}",
                "source": "RL-Trained",
                "disruption_type": disruption.get("type", "unknown"),
                "severity": disruption.get("severity", "medium"),
                "affected_airport": disruption.get("affected_airport", "N/A")
            }
            
            # Validate with FDTL if requested
            if validate_with_fdtl:
                from dgca_rules.validator import FDTLValidator
                validator = FDTLValidator()
                
                # Extract duration from action
                duration_hours = 2.0  # Default
                if "60 minutes" in action_name:
                    duration_hours = 1.0
                elif "cancel" in action_name.lower():
                    duration_hours = 0.0
                
                proposed_flight = {"duration_hours": duration_hours}
                is_compliant, reason = validator.validate_assignment(pilot_data, proposed_flight)
                
                violations = []
                if not is_compliant:
                    violations.append({
                        "rule": "fdtl_violation",
                        "description": reason,
                        "severity": "high",
                        "impact": "DGCA 2025 FDTL rule violation"
                    })
                
                proposal["compliant"] = is_compliant
                proposal["violations"] = violations
            
            return proposal
            
        except Exception as e:
            logger.error(f"Error generating RL proposal: {e}")
            return None
    
    def generate_multiple_proposals(
        self,
        disruption: Dict[str, Any],
        pilot_data: Dict[str, Any],
        num_proposals: int = 3
    ) -> list:
        """
        Generate multiple proposals by running the model multiple times
        with different randomness settings
        
        Args:
            disruption: Disruption details
            pilot_data: Current pilot state
            num_proposals: Number of proposals to generate
            
        Returns:
            List of proposal dicts
        """
        if not self.is_available():
            return []
        
        proposals = []
        
        for i in range(num_proposals):
            # Use non-deterministic prediction for variety
            try:
                obs, info = self.env.reset()
                action, _states = self.model.predict(obs, deterministic=False)
                
                proposal = self.generate_proposal(disruption, pilot_data)
                if proposal:
                    proposal["id"] = i + 1
                    proposals.append(proposal)
                    
            except Exception as e:
                logger.error(f"Error generating proposal {i+1}: {e}")
                continue
        
        return proposals


# Example usage for testing
if __name__ == "__main__":
    # Test the RL integration
    generator = RLProposalGenerator("models/rl_recovery_ppo.zip")
    
    if generator.is_available():
        test_disruption = {
            "type": "weather",
            "severity": "high",
            "description": "Severe fog at Delhi",
            "affected_airport": "DEL"
        }
        
        test_pilot = {
            "consecutive_night_duties": 1,
            "hours_since_last_rest": 12,
            "daily_flight_hours": 4,
            "weekly_flight_hours": 20
        }
        
        proposal = generator.generate_proposal(test_disruption, test_pilot)
        
        if proposal:
            print("RL Proposal Generated:")
            print(f"  Action: {proposal['action']}")
            print(f"  Reason: {proposal['reason']}")
            print(f"  Compliant: {proposal.get('compliant', 'Unknown')}")
        else:
            print("Failed to generate proposal")
    else:
        print("RL model not available")
