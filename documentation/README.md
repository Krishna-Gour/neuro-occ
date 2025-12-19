# Neuro-OCC 2.0: Production-Ready Neuro-Symbolic AI for Airline Operations Control

## 1. Introduction: The Challenge of Airline Disruption Management

Airline Operations Control Centers (OCCs) are the nerve centers of daily flight operations. They are responsible for managing complex schedules, crew assignments, and aircraft routing. However, disruptions like weather, technical issues, or crew unavailability are inevitable, causing a cascade of problems that are incredibly challenging to solve manually.

The key challenges in disruption management include:

*   **Complexity**: A single disruption can have ripple effects across the entire network, affecting hundreds of flights and thousands of passengers.
*   **Regulatory Constraints**: Airlines must adhere to strict regulations from authorities like the DGCA (Directorate General of Civil Aviation), especially concerning Flight and Duty Time Limitations (FDTL) for pilots.
*   **Speed**: Recovery solutions must be found and implemented quickly to minimize costs and passenger impact.
*   **Safety**: All solutions must prioritize the safety of passengers and crew above all else.

Current methods often rely on experienced human operators, but the sheer scale and complexity of the problem can overwhelm even the most skilled teams.

## 2. Our Solution: A Neuro-Symbolic Approach

**Neuro-OCC 2.0** is a production-ready system that demonstrates how a neuro-symbolic AI can assist airline OCCs in managing disruptions more effectively. It combines the strengths of two powerful AI paradigms:

*   **Neural Networks (System 1 Thinking)**: We use Large Language Models (LLMs) for their advanced reasoning capabilities. The LLM acts as a **Goal-Oriented Proposer**, analyzing a complete "World Model" of the airline's state and generating a detailed, structured recovery plan designed to be optimal against business goals.
*   **Symbolic AI (System 2 Thinking)**: We use a symbolic rule engine as a **Verifier**. This component contains a codified representation of the DGCA FDTL rulebook, allowing it to rigorously and transparently check each action in the LLM's proposed plan for compliance.

This hybrid approach, inspired by Daniel Kahneman's "Thinking, Fast and Slow," creates a powerful **Proposer-Scorer-Verifier** loop that delivers robust, safe, and verifiably optimal solutions.

## 3. System Architecture

The Neuro-OCC system is built around a few core components that work in concert:

1.  **Brain API (FastAPI Server)**: Central AI service that orchestrates the entire reasoning workflow.
    *   *Port: 8004*

2.  **Proposer (Goal-Oriented LLM Agent)**: An LLM-based agent that analyzes a "World Model" and proposes an optimal, structured JSON recovery plan.
    *   *See: `llm/system_2_agent.py`*

3.  **Scorer (Cost Function)**: A deterministic function that calculates the quantitative cost of a proposed plan based on business rules.
    *   *See: `brain_api.py`*

4.  **Verifier (Symbolic Engine)**: A Python-based rules engine that validates each action in the proposed plan against the DGCA FDTL rulebook.
    *   *See: `dgca_rules/validator.py`*

5.  **Human-in-the-Loop Dashboard**: A modern React-based interface that allows human operators to monitor the AI's suggestions, review the validation and cost scoring, and make the final decisions.
    *   *Port: 3000*

6.  **Model Context Protocol (MCP) Servers**: These servers provide a structured, real-time "view" of the operational world state (e.g., crew rosters, aircraft status) that is used to build the World Model.
    *   *See: `mcp_servers/`*

## 4. Key Features

*   **Verifiably Optimal Plans**: A quantitative cost function provides a deterministic score for each plan.
*   **Deep Contextual Awareness**: The AI reasons over a complete, real-time "World Model".
*   **Structured Actionable Output**: Generates machine-readable JSON plans with specific, atomic actions.
*   **Goal-Oriented Reasoning**: The LLM is explicitly instructed to optimize for key business drivers.
*   **Guaranteed Regulatory Compliance**: A symbolic verifier checks every action in a proposed plan.
*   **Automated Deployment**: One-command startup with `./start.sh`
*   **Human-in-the-Loop**: AI proposal review and approval workflow.
*   **Explainable AI (XAI)**: Clear justifications for all decisions.
*   **Production Monitoring**: Health checks and service status tracking.

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

## 6. Getting Started

### Prerequisites
*   Python 3.13+
*   Node.js 16+
*   npm 8+

### Quick Start (Automated Deployment)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Krishna-Gour/neuro-occ.git
    cd neuro-occ
    ```

2.  **Configure Environment (Optional):**
    Copy `config.yaml` and set your OpenAI API keys if needed.

3.  **Run the automated startup script:**
    ```bash
    ./start.sh
    ```
    
    This will:
    - Create a Python virtual environment
    - Install all Python dependencies (FastAPI, Ray, PyTorch, OpenAI)
    - Install Node.js dependencies for the dashboard
    - Initialize SQLite database with sample data (500 pilots, 100 aircraft, 349 flights)
    - Start all MCP servers (Crew, Fleet, Regulatory)
    - Launch the Brain API with AI integration
    - Start the React dashboard with modern UI
    - Perform health checks on all services

4.  **Access the Dashboard:**
    Open your browser and navigate to: `http://localhost:3000`

5.  **Stop the system:**
    Press `Ctrl+C` in the terminal or run:
    ```bash
    ./stop.sh
    ```

### Manual Installation (Alternative)

If you prefer manual setup:

1.  **Install Python dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Generate synthetic data:**
    ```bash
    python scripts/generate_data.py
    ```

3.  **Start MCP servers:**
    ```bash
    python mcp_servers/crew_mcp.py &
    python mcp_servers/fleet_mcp.py &
    python mcp_servers/reg_mcp.py &
    ```

4.  **Start the Brain API:**
    ```bash
    python brain/sentinel_Mamba.py
    ```

5.  **Start the Dashboard:**
    ```bash
    cd dashboard
    npm install
    npm start
    ```

## 7. Usage Guide

### Injecting Disruptions
1.  Open the dashboard at `http://localhost:3000`
2.  Click "Inject Disruption" to simulate real-world scenarios
3.  Select from available disruption types:
    - Weather delays
    - Aircraft technical issues
    - Crew unavailability
    - Security incidents

### AI Proposal Review
1.  The system will automatically generate recovery proposals
2.  Review the AI's suggestions in the proposal panel
3.  Check compliance validation results
4.  Approve or reject proposals as needed

### Monitoring & Analytics
- Real-time flight network visualization
- Service health monitoring
- Performance metrics dashboard
- Compliance violation tracking

## 8. API Endpoints

### Brain API (Port 8004)
- `POST /analyze_disruption`: Analyze disruption and generate recovery proposals
- `GET /health`: Service health check
- `POST /validate_plan`: Validate recovery plan against DGCA rules

### MCP Servers
- **Crew MCP (Port 8001)**: Pilot data and duty time management
- **Fleet MCP (Port 8002)**: Aircraft status and maintenance tracking
- **Regulatory MCP (Port 8003)**: Airport data and DGCA rule validation

## 9. Configuration

The system is configured via `config.yaml`. Key settings include:

- **LLM Configuration**: API keys, model selection, temperature settings
- **Data Generation**: Number of flights, pilots, aircraft to generate
- **Service Ports**: Custom port assignments for all services
- **Logging**: Log levels and output destinations
- **DGCA Rules**: Regulatory parameters and compliance thresholds

## 10. Testing

Run the test suite:
```bash
python -m pytest tests/
```

Key test areas:
- DGCA rule validation
- MCP server functionality
- Data generation integrity
- API endpoint testing

## 11. Further Reading

For a deeper dive into the specific components of the Neuro-OCC system, please refer to the detailed documentation:

*   **[Main Project Overview](README.md)** - This document
*   [Data Generation Process](Data_Generation_README.md) - Synthetic data creation pipeline
*   [DGCA FDTL Rulebook Implementation](DGCA_FDTL_Rulebook_README.md) - Regulatory compliance engine
*   [Reinforcement Learning Environment](RL_Environment_README.md) - RL optimization framework
*   [Neuro-Symbolic MVP Logic](Neuro_Symbolic_MVP_README.md) - Core AI architecture
*   [Human-in-the-Loop Dashboard](Human_in_the_Loop_Dashboard_README.md) - React interface design
*   [Model Context Protocol (MCP) Servers](Model_Context_Protocol_README.md) - Real-time data services
*   [Mamba Predictive Maintenance](Mamba_Predictive_Maintenance_README.md) - Aircraft health monitoring
*   [Configuration File (config.yaml)](Config_File_README.md) - System configuration guide
*   [Guardrails Module](Guardrails_README.md) - Safety and validation systems

## 12. Contributing

We welcome contributions to Neuro-OCC! Please see our contributing guidelines and code of conduct.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Submit a pull request

### Areas for Contribution
- Additional disruption types
- Enhanced DGCA rule coverage
- Improved UI/UX in dashboard
- Performance optimizations
- Additional MCP servers
- Multi-language support

## 13. License

This project is licensed under the MIT License - see the LICENSE file for details.

## 14. Acknowledgments

*   **DGCA (Directorate General of Civil Aviation)** for providing the regulatory framework
*   **OpenAI** for LLM capabilities that power the Proposer agent
*   **React & FastAPI communities** for excellent web frameworks
*   **Academic research** on neuro-symbolic AI and airline operations research

## 15. Contact

For questions, suggestions, or collaboration opportunities:

- **Email**: krishnagour.2026@gmail.com
- **GitHub**: [https://github.com/Krishna-Gour/neuro-occ](https://github.com/Krishna-Gour/neuro-occ)
- **LinkedIn**: [Krishna Gour](https://linkedin.com/in/krishna-gour)

---

**Neuro-OCC 2.0** - Revolutionizing airline operations through neuro-symbolic AI. Safe, efficient, and explainable disruption management for the aviation industry.