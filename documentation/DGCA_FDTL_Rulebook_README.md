# DGCA FDTL Rulebook - Production-Ready Symbolic Verifier

## 1. Purpose: Ensuring Safety and Compliance in Production

In the high-stakes environment of airline operations, safety and regulatory compliance are non-negotiable. **Neuro-OCC 2.0** is a production-ready system that proposes creative solutions to disruptions, but these solutions *must* adhere to the strict rules set by aviation authorities.

The **Symbolic Verifier** component acts as the system's "System 2" logical reasoning engine. Its sole purpose is to take a proposed crew assignment (e.g., assigning a pilot to a new flight) and rigorously check it against a codified version of the DGCA (Directorate General of Civil Aviation) regulations for Flight and Duty Time Limitations (FDTL).

This ensures that no matter what solution the creative LLM "Proposer" suggests, the system will never execute a plan that is illegal or unsafe.

## 2. Production System Integration

The DGCA validator is fully integrated into the Neuro-OCC 2.0 production pipeline:

- **Automated Validation**: Every AI-generated recovery proposal is automatically validated
- **Real-time Compliance**: Integrated with MCP servers for live pilot data access
- **Audit Trail**: All validation decisions are logged for regulatory compliance
- **Health Monitoring**: Validator performance is monitored in production dashboards

## 3. Why a Symbolic Approach?

While LLMs are powerful, they can be prone to errors or "hallucinations." For regulatory compliance, we cannot tolerate any ambiguity. A symbolic, rule-based approach offers critical advantages:

*   **Transparency**: The rules are explicitly coded and easy to audit. We can see exactly why a proposed assignment was accepted or rejected.
*   **Verifiability**: Each rule can be independently tested and verified for correctness, ensuring the logic is sound.
*   **Reliability**: The verifier's logic is deterministic. Given the same input, it will always produce the same output, which is essential for a safety-critical system.
*   **Updatability**: When regulations change, the specific rules can be updated in a targeted manner without retraining an entire model.

## 4. Key Components

*   **`dgca_rules/validator.py`**: This file contains the `FDTLValidator` class. It is a self-contained library that implements the core logic for checking assignments against the DGCA rules defined in the project's `config.yaml`.

*   **`tests/test_dgca_rules.py`**: To ensure the verifier is absolutely reliable, it is accompanied by a suite of unit tests. These tests create various scenarios to confirm that each rule is implemented correctly and that the validator behaves as expected under different conditions.

*   **`config.yaml`**: This file stores the specific numerical limits for the FDTL rules. This separation of logic and data makes it easy to tweak the rules (e.g., if regulations are updated) without changing the Python code.

*   **MCP Integration**: The validator connects to the Regulatory MCP server (Port 8003) for real-time rule updates and compliance reporting.

## 5. Implemented DGCA FDTL Rules

The current version of the `FDTLValidator` implements the following key rules based on the values in `config.yaml`:

| Rule                        | `config.yaml` Value                | Description                                                                                             |
| --------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Max Daily Flight Time**   | `max_daily_flight_time: 8.0`       | A pilot cannot fly more than 8 hours in a 24-hour period.                                               |
| **Max Consecutive Nights**  | `max_consecutive_night_duties: 2`  | A pilot cannot be assigned more than 2 consecutive night duties.                                        |
| **Mandatory Night Rest**    | `mandatory_night_rest_hours: 56.0` | After 2 consecutive night duties, a pilot must receive a mandatory rest period of 56 hours.             |
| **Weekly Flight Time Limit**| `weekly_flight_time_limit: 35.0`   | A pilot's total flight time cannot exceed 35 hours in any 7-day period.                                  |
| **Max Daily Duty Period**   | `max_daily_duty_period: 12.0`      | (Defined in config, for future use) The total duty period for a pilot in a day.                          |
| **Minimum Rest Period**     | `min_rest_period: 12.0`            | (Defined in config, for future use) The minimum rest a pilot must have between duty periods.           |

## 6. Production Architecture

### Service Integration
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Brain API     │───▶│  DGCA Validator  │───▶│ Regulatory MCP  │
│   (Port 8004)   │    │                  │    │   (Port 8003)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Compliance    │
                       │   Dashboard     │
                       │   (Port 3000)   │
                       └─────────────────┘
```

### Validation Pipeline
1. **AI Proposal Generation**: LLM creates recovery plan
2. **Real-time Data Fetch**: Query MCP servers for current pilot status
3. **Rule Validation**: Apply DGCA FDTL rules deterministically
4. **Compliance Report**: Generate detailed violation explanations
5. **Human Review**: Present validated proposals in dashboard
6. **Audit Logging**: Record all validation decisions

## 7. How It Works

The `FDTLValidator` class has a simple interface.

1.  **Initialization**: It is initialized with a path to the `config.yaml` file.
2.  **Validation**: The `validate_assignment` method takes two arguments:
    *   `pilot_data`: A dictionary representing the pilot's current status (e.g., hours flown today, hours flown this week, consecutive night duties).
    *   `proposed_flight`: A dictionary representing the flight being considered for assignment.
3.  **Output**: The method returns a tuple:
    *   `(True, "Compliant")` if the assignment is valid.
    *   `(False, "Reason for violation")` if the assignment breaks one of the rules.

## 8. Production Usage Example

Here is how the validator is used within the Neuro-OCC 2.0 production system:

```python
from dgca_rules.validator import FDTLValidator

# 1. Initialize the validator (done automatically by startup script)
validator = FDTLValidator(config_path='config.yaml')

# 2. Define the pilot's current state (fetched from MCP server)
pilot_state = {
    'daily_flight_hours': 7.0,
    'weekly_flight_hours': 30.0,
    'consecutive_night_duties': 0,
    'hours_since_last_rest': 24
}

# 3. Define the flight to be assigned
proposed_flight = {
    'duration_hours': 1.5
}

# 4. Validate the assignment
is_compliant, reason = validator.validate_assignment(pilot_state, proposed_flight)

if is_compliant:
    print("Assignment is legal.")
else:
    # This will fail because 7.0 + 1.5 > 8.0
    print(f"Assignment is ILLEGAL: {reason}")
    # Output: Assignment is ILLEGAL: Exceeds max daily flight time of 8.0 hours.
```

## 9. Production Monitoring

The DGCA validator includes comprehensive monitoring:

- **Performance Metrics**: Validation response times and throughput
- **Error Tracking**: Failed validations and system errors
- **Compliance Reports**: Daily/weekly regulatory compliance summaries
- **Audit Logs**: Complete trail of all validation decisions

## 10. Regulatory Updates

When DGCA regulations change:

1. Update `config.yaml` with new limits
2. Run test suite to validate changes
3. Deploy updated configuration via `./start.sh`
4. Monitor system behavior in production
5. Generate compliance reports for regulatory bodies