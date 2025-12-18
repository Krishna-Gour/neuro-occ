# Documentation: Human-in-the-Loop - The Co-Pilot Dashboard

## 1. Purpose: AI as a Co-Pilot, Not an Auto-Pilot

The Neuro-OCC system is designed to be a powerful assistant, not a replacement for human expertise. In mission-critical environments like an Airline Operations Control Center (OCC), the final authority and accountability must reside with the human operator. The **Co-Pilot Dashboard** is the interface that facilitates this crucial human-AI collaboration.

The dashboard provides the human operator with a clear, real-time view of the operational network, presents the AI's suggestions in an understandable format, and empowers the operator to make the final, informed decision.

## 2. Why Human-in-the-Loop (HITL) is Critical

*   **Accountability and Safety**: A human operator is ultimately responsible for the safety and legality of all flight operations. The AI suggests, the human decides.
*   **Context and Nuance**: An experienced operator can incorporate real-world information that may not be present in the AI's data model, such as developing weather patterns, airport-specific NOTAMs (Notice to Air Missions), or crew members who are "fit for duty" on paper but may be experiencing stress.
*   **Building Trust**: By making the AI's reasoning transparent and giving the operator the final say, the system builds trust and encourages adoption. It's a tool to augment intelligence, not replace it.

## 3. Key Technical Components

*   **`dashboard/`**: The root directory for the React-based frontend application.
*   **`dashboard/package.json`**: Defines the project's dependencies and scripts. The key libraries are:
    *   `react`: The core UI library.
    *   `reactflow`: A powerful library for creating the node-based flight network visualization.
    *   `d3`: A general-purpose data visualization library for potential future use.
    *   `lucide-react`: For clean, modern icons.
*   **`dashboard/src/App.js`**: The main React component. In the current proof-of-concept, it contains the entire UI and state management for demonstrating the HITL workflow.

## 4. The User Experience: A Step-by-Step Workflow

The `App.js` file simulates a complete interaction cycle between the operator and the AI:

**Step 1: The Normal Operating Picture**
The dashboard displays a map-like view created with ReactFlow, showing airports as nodes and active flights as green, animated edges. This provides a clear, at-a-glance view of the healthy network.

**Step 2: A Disruption Occurs**
The operator can click the **"Inject Disruption"** button to simulate a real-world event (e.g., fog at a major airport).

**Step 3: Visual Alerts and AI Activation**
The dashboard immediately reflects the problem:
*   The affected flight paths on the map turn from green to **red**.
*   A "System Status" panel appears, showing the Neuro-OCC AI is actively working. It displays a log of its thought process: `Evaluating simulations...`, `Querying Crew MCP...`, `Checking DGCA Compliance...`. This provides valuable transparency.

**Step 4: AI Presents Recovery Proposals**
After a few moments, the AI populates the status panel with a list of ranked recovery proposals. The UI makes a critical distinction:

*   **Compliant Proposals**: These are valid, legal solutions that have been **PASSED** by the Symbolic Verifier. Each proposal is presented on a card showing:
    *   **The Action**: e.g., "Swap VT-ICD with VT-IIJ".
    *   **The Reason**: A human-readable explanation from the LLM, e.g., "Prevents FDTL violation for Pilot Sharma".
    *   **The Impact**: The estimated financial or operational impact, e.g., "Savings: ₹4.5L".
    *   **An "Approve Plan" button**.

*   **Non-Compliant Proposals**: The dashboard also shows ideas that were rejected by the Verifier. These are clearly marked with a red **FAILED** status.
    *   They show the reason for the failure, e.g., "Exceeds max daily flight time of 8.0 hours."
    *   Crucially, they **do not have an "Approve" button**, demonstrating a powerful safety guardrail.

**Step 5: The Human Makes the Call**
The operator, using their experience and the information provided, evaluates the *compliant* options. They might choose the one with the highest savings, the lowest passenger impact, or another factor. They then click **"Approve Plan"** on their chosen solution.

**Step 6: Execution and Confirmation**
Upon approval, the UI provides immediate feedback:
*   A confirmation message appears: "Recovery Plan Approved & Executed!".
*   The flight paths on the map turn back to green.
*   In a real system, this would trigger a call to the backend to enact the chosen plan.

## 5. How to Run the Dashboard

1.  **Navigate to the dashboard directory**:
    ```bash
    cd dashboard
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Run the development server**:
    ```bash
    npm start
    ```

This will open the dashboard in your default web browser, typically at `http://localhost:3000`.