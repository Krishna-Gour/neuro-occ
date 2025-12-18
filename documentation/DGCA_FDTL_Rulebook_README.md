# Documentation: DGCA FDTL Rulebook - The Symbolic Verifier

## 1. Purpose: Ensuring Safety and Compliance

In the high-stakes environment of airline operations, safety and regulatory compliance are non-negotiable. The Neuro-OCC system is designed to propose creative solutions to disruptions, but these solutions *must* adhere to the strict rules set by aviation authorities.

The **Symbolic Verifier** component acts as the system's "System 2" logical reasoning engine. Its sole purpose is to take a proposed crew assignment (e.g., assigning a pilot to a new flight) and rigorously check it against a codified version of the DGCA (Directorate General of Civil Aviation) regulations for Flight and Duty Time Limitations (FDTL).

This ensures that no matter what solution the creative LLM "Proposer" suggests, the system will never execute a plan that is illegal or unsafe.

## 2. Why a Symbolic Approach?

While LLMs are powerful, they can be prone to errors or "hallucinations." For regulatory compliance, we cannot tolerate any ambiguity. A symbolic, rule-based approach offers critical advantages:

*   **Transparency**: The rules are explicitly coded and easy to audit. We can see exactly why a proposed assignment was accepted or rejected.
*   **Verifiability**: Each rule can be independently tested and verified for correctness, ensuring the logic is sound.
*   **Reliability**: The verifier's logic is deterministic. Given the same input, it will always produce the same output, which is essential for a safety-critical system.
*   **Updatability**: When regulations change, the specific rules can be updated in a targeted manner without retraining an entire model.

## 3. Key Components

*   **`dgca_rules/validator.py`**: This file contains the `FDTLValidator` class. It is a self-contained library that implements the core logic for checking assignments against the DGCA rules defined in the project's `config.yaml`.

*   **`tests/test_dgca_rules.py`**: To ensure the verifier is absolutely reliable, it is accompanied by a suite of unit tests. These tests create various scenarios to confirm that each rule is implemented correctly and that the validator behaves as expected under different conditions.

*   **`config.yaml`**: This file stores the specific numerical limits for the FDTL rules. This separation of logic and data makes it easy to tweak the rules (e.g., if regulations are updated) without changing the Python code.

## 4. Implemented DGCA FDTL Rules

The current version of the `FDTLValidator` implements the following key rules based on the values in `config.yaml`:

| Rule                        | `config.yaml` Value                | Description                                                                                             |
| --------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Max Daily Flight Time**   | `max_daily_flight_time: 8.0`       | A pilot cannot fly more than 8 hours in a 24-hour period.                                               |
| **Max Consecutive Nights**  | `max_consecutive_night_duties: 2`  | A pilot cannot be assigned more than 2 consecutive night duties.                                        |
| **Mandatory Night Rest**    | `mandatory_night_rest_hours: 56.0` | After 2 consecutive night duties, a pilot must receive a mandatory rest period of 56 hours.             |
| **Weekly Flight Time Limit**| `weekly_flight_time_limit: 35.0`   | A pilot's total flight time cannot exceed 35 hours in any 7-day period.                                  |
| **Max Daily Duty Period**   | `max_daily_duty_period: 12.0`      | (Defined in config, for future use) The total duty period for a pilot in a day.                          |
| **Minimum Rest Period**     | `min_rest_period: 12.0`            | (Defined in config, for future use) The minimum rest a pilot must have between duty periods.           |

## 5. How It Works

The `FDTLValidator` class has a simple interface.

1.  **Initialization**: It is initialized with a path to the `config.yaml` file.
2.  **Validation**: The `validate_assignment` method takes two arguments:
    *   `pilot_data`: A dictionary representing the pilot's current status (e.g., hours flown today, hours flown this week, consecutive night duties).
    *   `proposed_flight`: A dictionary representing the flight being considered for assignment.
3.  **Output**: The method returns a tuple:
    *   `(True, "Compliant")` if the assignment is valid.
    *   `(False, "Reason for violation")` if the assignment breaks one of the rules.

## 6. How to Use the Validator

Here is a basic example of how the validator would be used within the Neuro-OCC system:

```python
from dgca_rules.validator import FDTLValidator

# 1. Initialize the validator
validator = FDTLValidator(config_path='config.yaml')

# 2. Define the pilot's current state
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