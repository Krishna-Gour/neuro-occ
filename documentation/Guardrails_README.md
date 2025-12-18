# Documentation: Guardrails Module - Additional Safety Verifiers

## 1. Purpose: Redundant Safety Checks

The `guardrails` module provides additional layers of safety verification beyond the core `dgca_rules` validator. While the primary validator focuses on DGCA FDTL compliance, guardrails implement broader safety checks and can serve as a fail-safe mechanism.

## 2. Key Components

*   **`guardrails/verifier.py`**: Contains the `DGCAVerifier` class, which provides an alternative implementation of FDTL validation with potentially different logic or additional checks.

## 3. Relationship to Core Validator

The `guardrails/verifier.py` appears to be a parallel implementation to `dgca_rules/validator.py`. Both classes:

- Load configuration from `config.yaml`
- Implement `verify_plan` or `validate_assignment` methods
- Check against DGCA FDTL rules

### Potential Differences
- **Additional Checks**: May include extra validation logic not present in the core validator.
- **Alternative Implementation**: Could use different algorithms or edge case handling.
- **Backup System**: Serves as a redundant verifier for critical operations.

## 4. Usage

```python
from guardrails.verifier import DGCAVerifier

verifier = DGCAVerifier()
is_compliant, reason = verifier.verify_plan(pilot_data, proposed_flight)
```

## 5. Integration with System

The guardrails verifier is used by the System 2 Agent (`llm/system_2_agent.py`) for compliance checking. It provides an additional layer of assurance that proposed recovery plans meet regulatory requirements.

## 6. Testing

The guardrails should be tested alongside the core validator to ensure consistency:

```python
# Compare outputs
core_result = core_validator.validate_assignment(pilot_data, flight)
guardrail_result = guardrail_verifier.verify_plan(pilot_data, flight)
assert core_result[0] == guardrail_result[0], "Validators disagree on compliance"
```

## 7. Future Enhancements

*   **Expanded Rules**: Add checks for additional aviation regulations beyond FDTL.
*   **Machine Learning Integration**: Use ML models to predict potential violations.
*   **Real-time Monitoring**: Continuous validation during flight operations.