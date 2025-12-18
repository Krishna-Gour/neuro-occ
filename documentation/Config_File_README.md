# Documentation: Configuration File (config.yaml)

## 1. Purpose: Centralized Configuration Management

The `config.yaml` file serves as the single source of truth for all configurable parameters in the Neuro-OCC system. This separation of configuration from code allows for easy customization, experimentation, and deployment across different environments without modifying the source code.

## 2. Structure Overview

The configuration is organized into logical sections:

```yaml
# ==============================================================================
# CONFIGURATION FOR NEURO-OCC SYNTHETIC DATA GENERATION
# ==============================================================================

# --- Simulation Parameters ---
random_seed: 42
simulation_start_date: "2025-12-01T00:00:00Z"

# --- Data Generation Counts ---
num_airports: 30
num_aircraft: 100
num_pilots: 500

# --- Entity Properties ---
airport_codes: [...]
aircraft_models: [...]

# --- Flight & Rotation Generation Parameters ---
min_flights_per_rotation: 2
max_flights_per_rotation: 5
min_turnaround_time_minutes: 45
max_turnaround_time_minutes: 90
min_flight_duration_hours: 0.75
max_flight_duration_hours: 4.0

# DGCA 2025 FDTL Regulatory Constants
dgca_fdtl:
  max_daily_flight_time: 8.0
  max_daily_duty_period: 12.0
  min_rest_period: 12.0
  max_consecutive_night_duties: 2
  mandatory_night_rest_hours: 56.0
  weekly_flight_time_limit: 35.0

# --- Reinforcement Learning Cost Function Weights ---
cost_weights:
  w_delay: 1.0
  w_cancel: 500.0
  w_violation: 1000.0
```

## 3. Section Details

### Simulation Parameters
- **`random_seed`**: Ensures reproducible results across runs. Set to 42 for consistent data generation.
- **`simulation_start_date`**: The reference date for all generated timestamps. Uses ISO 8601 format.

### Data Generation Counts
- **`num_airports`**: Number of airports to generate (sampled from `airport_codes`).
- **`num_aircraft`**: Total aircraft in the fleet.
- **`num_pilots`**: Total pilots in the roster.

### Entity Properties
- **`airport_codes`**: List of IATA codes to sample from when generating airports.
- **`aircraft_models`**: Available aircraft types (e.g., "Airbus A320", "Boeing 737").

### Flight & Rotation Generation Parameters
- **`min_flights_per_rotation` / `max_flights_per_rotation`**: Range for flights per aircraft per day.
- **`min_turnaround_time_minutes` / `max_turnaround_time_minutes`**: Ground time between flights.
- **`min_flight_duration_hours` / `max_flight_duration_hours`**: Realistic flight duration range.

### DGCA FDTL Regulatory Constants
These define the aviation safety regulations enforced by the system:

- **`max_daily_flight_time`**: Maximum flight hours per pilot per day (8.0 hours).
- **`max_daily_duty_period`**: Maximum total duty time including non-flight activities (12.0 hours).
- **`min_rest_period`**: Minimum rest required between duty periods (12.0 hours).
- **`max_consecutive_night_duties`**: Maximum consecutive night shifts before mandatory rest (2).
- **`mandatory_night_rest_hours`**: Required rest after max consecutive nights (56.0 hours).
- **`weekly_flight_time_limit`**: Maximum flight hours per pilot per week (35.0 hours).

### Reinforcement Learning Cost Function Weights
These weights determine the RL agent's priorities:

- **`w_delay`**: Cost multiplier for each minute of flight delay (1.0).
- **`w_cancel`**: Cost penalty for flight cancellation (500.0).
- **`w_violation`**: High penalty for regulatory violations (1000.0).

## 4. How to Modify

### For Different Scenarios
- **Larger Fleet**: Increase `num_airports`, `num_aircraft`, `num_pilots`.
- **Stricter Regulations**: Decrease FDTL limits.
- **Cost-Sensitive Optimization**: Increase `w_cancel` and `w_violation` relative to `w_delay`.

### Validation
After modifying `config.yaml`, run the test suite to ensure compatibility:
```bash
python -m pytest tests/
```

### Environment-Specific Configs
For different environments (development, staging, production), create separate config files:
- `config.dev.yaml`
- `config.prod.yaml`

Load them by passing the path to components that use configuration.

## 5. Dependencies

The config is loaded using PyYAML:
```python
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

Ensure `pyyaml` is installed:
```bash
pip install pyyaml
```