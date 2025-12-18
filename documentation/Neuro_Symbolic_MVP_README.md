# Documentation: The Neuro-Symbolic MVP - A "Proposer-Verifier-Explainer" Core

## 1. Purpose: The Heart of Neuro-OCC

The Minimum Viable Product (MVP) of the Neuro-OCC system is designed to demonstrate the power of its core architectural pattern: the **Proposer-Verifier-Explainer loop**.

This architecture is a direct implementation of a neuro-symbolic approach, combining a neural network's (LLM) ability to generate creative solutions with a symbolic engine's ability to perform rigorous, logical validation. This fusion aims to create an AI system that is both intelligent and trustworthy.

The `scripts/mvp_demo.py` script provides a clear, step-by-step demonstration of this loop in action.

## 2. Inspired by "Thinking, Fast and Slow"

This architecture is analogous to the dual-process model of human cognition described by Daniel Kahneman:

*   **The Proposer (System 1 - "Thinking Fast")**: This is the LLM agent. When faced with a disruption, it quickly and intuitively generates a potential solution. This is like a human expert's "gut feeling" or first idea. It's fast and creative but can sometimes be flawed.

*   **The Verifier (System 2 - "Thinking Slow")**: This is the symbolic `FDTLValidator`. It doesn't have ideas, but it knows the rules inside and out. It takes the proposed solution and deliberately, methodically, and unemotionally checks it against the codified DGCA FDTL rulebook. This process is slower but guarantees logical and regulatory soundness.

*   **The Explainer (System 1.5 - "Informed Narration")**: This is the LLM again, but now it's armed with the Verifier's logical output. It translates the cold, hard facts from the Verifier into a clear, human-readable explanation. This builds a "glass box," allowing the human operator to understand the *why* behind the AI's reasoning.

## 3. Key Components in the Demonstration

*   **`scripts/mvp_demo.py`**: The main script that simulates a disruption and runs the core loop.
*   **`dgca_rules/validator.py`**: The **Verifier**. It provides the indisputable ground truth about rule compliance.
*   **`System2Explainer` class (in `mvp_demo.py`)**: A mock stand-in for the LLM agent, playing the dual roles of **Proposer** (by providing a pre-defined list of proposals) and **Explainer**.

## 4. The Core Loop in Action: A Walkthrough of the MVP Demo

The `mvp_demo.py` script simulates the following sequence of events:

**Step 1: The Disruption**
A critical event occurs: `Pilot Sharma (PLT001) has reported fatigue for flight 6E-101.` A recovery action is required immediately.

**Step 2: The First Proposal (System 1)**
The Proposer suggests its first idea: `"Swap in Pilot Verma"`. This proposal includes Pilot Verma's current flight duty data. He has already flown 7 hours today. The proposed flight is 2 hours long.

**Step 3: Verification (System 2)**
The `FDTLValidator` is called to check the legality of assigning this 2-hour flight to Pilot Verma.
*   `current_hours (7.0) + proposed_hours (2.0) = 9.0`
*   The validator checks this against the `max_daily_flight_time` rule, which is `8.0` hours.
*   The result: `(False, "Exceeds max daily flight time of 8.0 hours.")`

**Step 4: Explanation & Rejection (System 1.5)**
The Explainer receives the verifier's feedback and reports: `"The proposed plan 'Swap in Pilot Verma' was REJECTED because: Exceeds max daily flight time of 8.0 hours. Searching for alternatives..."`. The proposal is rejected.

**Step 5: The Second Proposal (System 1)**
The loop repeats. Having learned from the previous failure, the Proposer now suggests a different option: `"Swap in Pilot Kumar"`. Pilot Kumar has only flown 4 hours today.

**Step 6: Verification (System 2)**
The validator checks the legality of assigning the 2-hour flight to Pilot Kumar.
*   `current_hours (4.0) + proposed_hours (2.0) = 6.0`
*   This is well within the 8-hour daily limit, and all other checks (weekly hours, night duties) also pass.
*   The result: `(True, "Compliant")`

**Step 7: Explanation & Approval (System 1.5)**
The Explainer receives the positive result and reports: `"The proposed plan 'Swap in Pilot Kumar' is optimal and fully compliant with DGCA FDTL rules."`

**Step 8: Decision**
The system has found a creative, safe, and fully compliant solution. The decision is made: `"Proposal Approved. Executing recovery."`

## 5. Why This Architecture is Powerful

*   **Safety and Reliability**: It grounds the creative "brainstorming" of an LLM in a bedrock of verifiable, symbolic logic. The system cannot break the rules, period.
*   **Trust Through Explainability**: By explaining *why* a decision was made (often referencing the specific rule that was checked), the system builds trust with the human operator.
*   **Intelligent Error Correction**: The loop is inherently self-correcting. A "bad" idea from the Proposer is caught and explained, leading to a better idea on the next attempt.