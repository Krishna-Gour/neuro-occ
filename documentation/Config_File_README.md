# Configuration File (config.yaml) - Neuro-OCC 2.0

## 1. Purpose: Centralized Configuration for Production-Ready System

The `config.yaml` file serves as the single source of truth for all configurable parameters in the Neuro-OCC 2.0 production system. This separation of configuration from code enables automated deployment, easy scaling, and environment-specific customization without modifying source code.

## 2. Current System Status

**Neuro-OCC 2.0** is a fully operational neuro-symbolic AI system for airline operations control, featuring:
- Automated deployment via `./start.sh`
- Real-time disruption management
- DGCA FDTL compliance validation
- Human-in-the-loop dashboard
- Production monitoring and health checks

## 3. Structure Overview

The configuration is organized into logical sections for the complete system:

```yaml
# ==============================================================================
# NEURO-OCC 2.0 PRODUCTION CONFIGURATION
# ==============================================================================

# --- System Environment ---
environment: production  # development | staging | production
log_level: INFO

# --- Service Configuration ---
services:
  brain_api:
    host: localhost
    port: 8004
  dashboard:
    host: localhost
    port: 3000
  mcp_servers:
    crew: 8001
    fleet: 8002
    regulatory: 8003

# --- LLM Configuration ---
llm:
  provider: openai  # openai | anthropic | local
  model: gpt-4-turbo-preview
  api_key: ${OPENAI_API_KEY}
  temperature: 0.7
  max_tokens: 2000
  timeout: 30

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
```

## 4. Section Details

### System Environment
- **`environment`**: Defines the deployment context (development/staging/production)
- **`log_level`**: Logging verbosity (DEBUG/INFO/WARNING/ERROR)

### Service Configuration
Defines all microservices in the Neuro-OCC system:
- **`brain_api`**: Central AI orchestration service (Port 8004)
- **`dashboard`**: React-based human-in-the-loop interface (Port 3000)
- **`mcp_servers`**: Model Context Protocol servers for real-time data access

### LLM Configuration
AI model settings for the neuro-symbolic system:
- **`provider`**: AI service provider (OpenAI, Anthropic, or local models)
- **`model`**: Specific model version for optimal performance
- **`api_key`**: Secure API key management via environment variables
- **`temperature`**: Creativity vs consistency balance (0.0-1.0)
- **`max_tokens`**: Response length limits
- **`timeout`**: Request timeout in seconds

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

## 5. Automated Deployment Integration

The configuration file is automatically loaded during system startup:

```bash
./start.sh  # Loads config.yaml and starts all services
```

### Environment Variables
Sensitive information like API keys should be set as environment variables:
```bash
export OPENAI_API_KEY="your-api-key-here"
./start.sh
```

### Configuration Validation
The startup script validates configuration before deployment:
- Checks for required API keys
- Validates port availability
- Ensures data generation parameters are reasonable
- Verifies DGCA compliance rules are properly defined

## 6. How to Modify

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

## 7. Dependencies

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

## 8. Production Monitoring

Configuration changes are logged and monitored:
- Configuration validation results
- Service startup parameters
- Performance tuning adjustments
- Compliance rule modifications

All changes are tracked for audit and rollback capabilities.