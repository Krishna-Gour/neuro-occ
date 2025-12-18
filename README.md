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
*   [Mamba Predictive Maintenance](Mamba_Predictive_Maintenance_README.md)
*   [Configuration File (config.yaml)](Config_File_README.md)
*   [Guardrails Module](Guardrails_README.md)
