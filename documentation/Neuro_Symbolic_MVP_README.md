# High-Precision Neuro-Symbolic Architecture

## 1. Purpose: The Intelligent Core of Neuro-OCC 2.0

The Neuro-OCC system implements a **true neuro-symbolic architecture** that is now capable of generating **high-precision, actionable, and verifiably optimal** recovery plans. It moves beyond simple proposal-verification to a more sophisticated reasoning process.

**Core Upgrade**: The architecture has been fundamentally enhanced to transform the LLM from a simple "idea generator" into a **goal-oriented reasoning engine**. It now produces complete, structured plans designed to be optimal against defined business objectives.

## 2. High-Precision Architecture (Current Implementation)

The new architecture introduces the concepts of a **World Model** and a **Quantitative Cost Function** to enable a higher level of intelligent decision-making.

```
                  ┌───────────────────┐
                  │    MCP Servers    │
                  │ (Fleet, Crew, Regs) │
                  └─────────┬─────────┘
                            │ (Live Data Feeds)
              ┌─────────────▼─────────────┐
              │     Build "World Model"   │
              │ (Flights, Pilots, A/C)    │
              └─────────────┬─────────────┘
                            │ (Full Context)
┌───────────────────────────▼───────────────────────────┐
│              NEURO-SYMBOLIC REASONING ENGINE          │
│                                                       │
│   1. PROPOSER (Goal-Oriented LLM)                     │
│      └─→ Generates structured JSON plan based on      │
│          optimization goals (cost, passenger impact)  │
│                                                       │
│   2. SCORER (Quantitative Cost Function)              │
│      └─→ Calculates a concrete cost for the plan      │
│          based on defined business rules              │
│                                                       │
│   3. VERIFIER (Symbolic Engine)                       │
│      └─→ Validates each specific action in the        │
│          plan against DGCA FDTL rules                 │
│                                                       │
└───────────────────────────┬───────────────────────────┘
                            │ (Scored & Validated Plan)
              ┌─────────────▼─────────────┐
              │  Human-in-the-Loop Review │
              │        (Dashboard)        │
              └───────────────────────────┘
```

## 3. "Thinking, Fast and Slow" - An Evolved Analogy

Our implementation of Daniel Kahneman's model has matured:

*   **Proposer (System 1 - "Goal-Oriented Reasoner")**: The LLM agent (`System2Agent`) now acts as an expert planner. Provided with a complete "World Model" and explicit optimization goals (e.g., "minimize cost," "avoid cancellations"), it generates a detailed, structured JSON plan of specific actions.

*   **Scorer & Verifier (System 2 - "Deliberate Evaluation")**: This is now a two-stage process.
    1.  The **Cost Function** (`_calculate_plan_cost`) provides a rapid, quantitative score for the plan's business impact.
    2.  The symbolic **`FDTLValidator`** then performs a rigorous, methodical check of each action in the plan against the codified DGCA FDTL rulebook.

*   **Explainer (System 1.5 - "Informed Narration")**: The LLM can now explain *why* a specific, detailed plan is optimal by referencing the goals it was given and the validation results it passed.

## 4. The High-Precision Core Loop

The production system now follows this more intelligent workflow:

### Phase 1: Build the World Model
- **Fetch Live Data**: The `brain_api` calls all `mcp_servers` (`/flights`, `/aircraft`, `/pilots`) to assemble a complete, real-time snapshot of the entire operation. This snapshot is the "World Model."

### Phase 2: Goal-Oriented Proposal (System 1)
- **Build Rich Prompt**: A detailed prompt is constructed, including the disruption details, the full World Model, and a list of **optimization goals** (e.g., minimize cost, passenger impact).
- **Generate Structured Plan**: The LLM Proposer processes this rich prompt and returns a single JSON object representing a complete, multi-step recovery plan with specific, atomic actions (`CANCEL_FLIGHT`, `SWAP_AIRCRAFT`, etc.).

### Phase 3: Quantitative Scoring (System 2, Part 1)
- **Calculate Real Cost**: The `_calculate_plan_cost` function processes the `actions` array from the LLM's plan.
- **Apply Business Rules**: It calculates a deterministic, quantitative cost for the plan based on a defined cost model (e.g., cost per cancellation, cost per minute of delay). This replaces the LLM's guess with a hard number.

### Phase 4: Symbolic Verification (System 2, Part 2)
- **Verify Each Action**: The system iterates through each action in the structured plan.
- **Accurate Compliance Check**: If an action involves a pilot (`REASSIGN_CREW`), the `FDTLValidator` is called with the specific data for *that pilot*, ensuring the compliance check is accurate and relevant. Data consistency is also checked to prevent hallucinations.

### Phase 5: Human-in-the-Loop Review
- **Dashboard Presentation**: The final, validated, and scored plan is presented to the human operator, including the detailed list of actions, the calculated cost, and any compliance warnings.

## 5. Why This Architecture is More Powerful

*   **Verifiable Optimality**: By using a quantitative cost function, the system can prove that a proposed plan is not just *compliant* but also *optimal* from a business perspective. It allows for direct, data-driven comparison of different solutions.
*   **Deeply Grounded Decisions**: Plans are no longer generalized ideas. They are grounded in a comprehensive "World Model" of the airline's real-time state, making them immediately relevant and actionable.
*   **Reduced Hallucination**: By requiring a structured JSON output based on real data from the context, the risk of the LLM "hallucinating" or inventing details is significantly minimized.
*   **Safety and Reliability**: The symbolic verifier remains the ultimate safety gate, ensuring that even the most complex, AI-generated plans are 100% compliant with codified rules.
*   **Scalability & Clarity**: The structured action format is machine-readable and can be directly fed into execution engines, while also being clear and unambiguous for the human operator.

This enhanced architecture represents a significant step towards a truly intelligent and trustworthy AI co-pilot for mission-critical operations.