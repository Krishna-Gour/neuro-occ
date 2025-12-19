import yaml
import os
from typing import Dict, Any, Tuple

class FDTLValidator:
    """
    Standalone library for DGCA 2025 Flight Duty Time Limitation (FDTL) compliance.
    """
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Try to find config.yaml in the project root
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.rules = config['dgca_fdtl']
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {config_path}")
        except KeyError:
            raise KeyError("Invalid config: missing 'dgca_fdtl' section")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing config YAML: {e}")

    def validate_assignment(self, pilot_data: Dict[str, Any], proposed_flight: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates if a proposed flight assignment for a pilot is legal under DGCA rules.
        
        Args:
            pilot_data (dict): Current state of the pilot (hours, rest, etc.)
            proposed_flight (dict): Details of the flight to be assigned.
            
        Returns:
            tuple: (is_compliant, reason)
        """
        proposed_hours = proposed_flight.get('duration_hours', 0)
        
        # 1. Check Daily Flight Time
        current_daily_hours = pilot_data.get('daily_flight_hours', 0)
        if (current_daily_hours + proposed_hours) > self.rules['max_daily_flight_time']:
            return False, f"Exceeds max daily flight time of {self.rules['max_daily_flight_time']} hours."

        # 2. Check Night Duty Rest
        consecutive_nights = pilot_data.get('consecutive_night_duties', 0)
        last_rest_hours = pilot_data.get('hours_since_last_rest', 0)
        
        if consecutive_nights >= self.rules['max_consecutive_night_duties']:
            if last_rest_hours < self.rules['mandatory_night_rest_hours']:
                return False, f"Rule violation: {consecutive_nights} consecutive night duties require {self.rules['mandatory_night_rest_hours']}h rest."

        # 3. Check Weekly Limits
        weekly_hours = pilot_data.get('weekly_flight_hours', 0)
        if (weekly_hours + proposed_hours) > self.rules['weekly_flight_time_limit']:
            return False, f"Exceeds {self.rules['weekly_flight_time_limit']}-hour weekly flight limit."

        return True, "Compliant"
