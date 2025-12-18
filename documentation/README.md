# Neuro-OCC: A Neuro-Symbolic AI for Airline Operations Control

## 1. Introduction: The Challenge of Airline Disruption Management

Airline Operations Control Centers (OCCs) are the nerve centers of daily flight operations. They are responsible for managing complex schedules, crew assignments, and aircraft routing. However, disruptions like weather, technical issues, or crew unavailability are inevitable, causing a cascade of problems that are incredibly challenging to solve manually.

The key challenges in disruption management include:

*   **Complexity**: A single disruption can have ripple effects across the entire network, affecting hundreds of flights and thousands of passengers.
*   **Regulatory Constraints**: Airlines must adhere to strict regulations from authorities like the DGCA (Directorate General of Civil Aviation), especially concerning Flight and Duty Time Limitations (FDTL) for pilots.
*   **Speed**: Recovery solutions must be found and implemented quickly to minimize costs and passenger impact.
*   **Safety**: All solutions must prioritize the safety of passengers and crew above all else.

Current methods often rely on experienced human operators, but the sheer scale and complexity of the problem can overwhelm even the most skilled teams.

## 2. Our Solution: A Neuro-Symbolic Approach

**Neuro-OCC** is a proof-of-concept system that demonstrates how a neuro-symbolic AI can assist airline OCCs in managing disruptions more effectively. It combines the strengths of two powerful AI paradigms:

*   **Neural Networks (System 1 Thinking)**: We use Large Language Models (LLMs) for their creative problem-solving abilities. The LLM acts as a **Proposer**, generating potential recovery solutions in a flexible, intuitive manner, much like a human expert.
*   **Symbolic AI (System 2 Thinking)**: We use a symbolic rule engine as a **Verifier**. This component contains a codified representation of the DGCA FDTL rulebook, allowing it to rigorously and transparently check if the LLM's proposed solutions are compliant and feasible.

This hybrid approach, inspired by Daniel Kahneman's "Thinking, Fast and Slow," creates a powerful **Proposer-Verifier-Explainer** loop that delivers robust, safe, and explainable solutions.

## 3. System Architecture

The Neuro-OCC system is built around a few core components that work in concert:

1.  **Proposer (LLM Agent)**: An LLM-based agent that analyzes a disruption scenario and proposes a recovery plan.
    *   *See: `llm/system_2_agent.py`*

2.  **Verifier (Symbolic Engine)**: A Python-based rules engine that validates the proposed plan against the DGCA FDTL rulebook.
    *   *See: `dgca_rules/validator.py`*

3.  **Explainer (LLM Agent)**: The same LLM agent also provides natural language explanations for why a solution was chosen or why a proposed solution was invalid.

4.  **Orchestrator (RL Agent)**: A Reinforcement Learning agent that learns and optimizes the process of finding valid solutions, guiding the Proposer-Verifier interaction.
    *   *See: `brain/recovery_env.py`*

5.  **Human-in-the-Loop (Co-Pilot Dashboard)**: A web-based interface that allows human operators to monitor the AI's suggestions, review the validation results, and make the final decisions.
    *   *See: `dashboard/`*

6.  **Model Context Protocol (MCP) Servers**: These servers provide a structured, real-time "view" of the operational world state (e.g., crew rosters, aircraft status) for the AI models.
    *   *See: `mcp_servers/`*

## 4. Key Features

*   **Synthetic Data Generation**: Creates realistic flight, pilot, and airport data for simulation.
*   **Symbolic FDTL Validation**: Ensures all recovery plans are compliant with Indian aviation regulations.
*   **Reinforcement Learning for Optimization**: Trains an agent to find optimal recovery strategies over time.
*   **Explainable AI (XAI)**: Provides clear, human-readable justifications for its decisions.
*   **Interactive Dashboard**: Enables seamless collaboration between the AI and human operators.

## 5. Project Structure

The repository is organized into the following key directories:

| Path                  | Description                                                                 |
| --------------------- | --------------------------------------------------------------------------- |
| `brain/`              | Contains the RL orchestrator agent and its environment.                     |
| `dashboard/`          | The React-based frontend for the human-in-the-loop interface.               |
| `data/`               | (Git-ignored) Holds the generated synthetic data CSV files.                 |
| `dgca_rules/`         | The symbolic validator for DGCA FDTL rules.                                 |
| `documentation/`      | Contains all project documentation, including this README.                  |
| `guardrails/`         | Additional safety verifiers for the system.                                 |
| `llm/`                | The LLM-based Proposer/Explainer agent.                                     |
| `mcp_servers/`        | Servers that provide real-time context to the AI models.                    |
| `scripts/`            | Scripts for generating data and running demos.                              |
| `tests/`              | Unit and integration tests for the system components.                       |

## 6. Further Reading

For a deeper dive into the specific components of the Neuro-OCC system, please refer to the detailed documentation:

*   **[Main Project Overview](README.md)**
*   [Data Generation Process](Data_Generation_README.md)
*   [DGCA FDTL Rulebook Implementation](DGCA_FDTL_Rulebook_README.md)
*   [Reinforcement Learning Environment](RL_Environment_README.md)
*   [Neuro-Symbolic MVP Logic](Neuro_Symbolic_MVP_README.md)
*   [Human-in-the-Loop Co-Pilot Dashboard](Human_in_the_Loop_Dashboard_README.md)
*   [Model Context Protocol (MCP) Servers](Model_Context_Protocol_README.md)

## Portfolio Snippet

```javascript
{ 
  id: 5, 
  name: "Neuro-OCC: Federated Autonomous Recovery System", 
  description: "A groundbreaking autonomous control center that uses Neuro-Symbolic AI and Model Context Protocol (MCP) to manage airline disruptions in real-time, ensuring compliance with the 2025 DGCA FDTL norms while optimizing network recovery.", 
  slideContent: `Problem Statement: In 2025, the Indian aviation sector faced a systemic crisis. The enforcement of strict new Flight Duty Time Limitations (FDTL) by the DGCA, combined with infrastructure failures like dense fog, led to massive operational meltdowns, most notably IndiGo cancelling over 2,000 flights in a single week. The root cause is not just the weather, but the industry's reliance on static, siloed planning systems that cannot adapt to dynamic constraints in real-time. This results in thousands of stranded passengers, exhausted crew, and millions in revenue loss.

Why I Chose This: The 2025 aviation crisis is the perfect storm of regulatory pressure, operational complexity, and public impact. Solving it requires moving beyond simple software tools to building an autonomous decision-making system. This project demonstrates the ability to handle high-stakes, combinatorial optimization problems using the most advanced AI architectures available today, directly addressing a critical national infrastructure challenge.

Solution Built: Neuro-OCC is a federated autonomous recovery system that acts as a synthetic Operations Control Center. It uses a novel Neuro-Symbolic architecture where an LLM-based agent proposes recovery plans (e.g., flight swaps, cancellations) based on System 2 Chain-of-Thought reasoning. These plans are then rigorously validated by a deterministic Symbolic Logic module that encodes the 2025 DGCA FDTL laws, ensuring 100% regulatory compliance. The system ingests data via a federated Model Context Protocol (MCP) architecture, allowing it to query disparate legacy systems (Crew, Fleet, Regulations) seamlessly. It also incorporates a Mamba-based State Space Model agent for high-frequency sensor monitoring to predict aircraft maintenance issues before they cause delays.

Core Flows: Disruption Event triggers Neuro-OCC -> Mamba Agent assesses fleet health -> MCP Servers federate real-time crew/aircraft data -> Neuro-Symbolic Agent initiates System 2 reasoning loop -> LLM proposes multiple recovery scenarios -> Symbolic Logic Module validates proposals against 2025 DGCA FDTL rules -> Optimal, compliant plan is selected and executed via agentic workflows -> Real-time dashboard updates stakeholder visibility.

Impact (Projected):
- Reduction in disruption recovery time from hours to milliseconds.
- Guaranteed 100% compliance with 2025 DGCA FDTL norms, eliminating regulatory fines.
- Potential to save airlines millions in passenger compensation and operational waste.
- Reduction in cascading delays by optimizing resource allocation dynamically.

Tech Stack:
- Architecture: Neuro-Symbolic AI, Federated Model Context Protocol (MCP), Multi-Agent System
- AI/ML Models: Llama-3 (LLM for reasoning), Mamba (State Space Model for sensor data), Custom Symbolic Logic Module (Python)
- Simulation & RL: Ray RLLib, Gymnasium
- Backend: Python, FastAPI
- Frontend: React Flow (Network Graph visualization)
- Data & Infra: MCP Servers (Typescript/Python), PostgreSQL, Redis (for task queuing)

Note: This project is a "Zero-to-One" innovation. It showcases the application of cutting-edge 2026-27 AI trends—including MCP, Neuro-Symbolic AI, and System 2 reasoning—to solve a real-world, NP-hard optimization problem in a critical industry.`, 
  date: "2025-12-18", 
  demoLink: "https://github.com/Krishna-Gour/neuro-occ", 
  imagePath: "/background/projectbg-neuroocc.png", 
  highlight: true 
}
```