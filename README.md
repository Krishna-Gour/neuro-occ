# Neuro-OCC

A proof-of-concept neuro-symbolic AI system for exploring disruption management in airline operations.

## Overview

This project experiments with combining large language models (LLMs) and symbolic rules to assist with airline operations control center (OCC) tasks. It's focused on handling disruptions like crew unavailability or technical issues, while ensuring compliance with aviation regulations.

## Components

- **LLM Agent**: Uses an LLM to generate potential recovery plans based on disruption scenarios.
- **Symbolic Validator**: Checks proposed plans against codified DGCA FDTL rules for compliance.
- **RL Orchestrator**: A reinforcement learning agent that optimizes the interaction between proposer and verifier.
- **Dashboard**: A simple web interface for human oversight and decision-making.
- **MCP Servers**: Provide structured data access for operational context (e.g., crew, aircraft status).
- **Data Generation**: Scripts to create synthetic flight, pilot, and airport data for testing.

## Project Structure

- `brain/`: RL environment and agents
- `dashboard/`: React frontend
- `data/`: Generated CSV files (git-ignored)
- `dgca_rules/`: Rule validation logic
- `documentation/`: Detailed docs
- `guardrails/`: Additional checks
- `llm/`: LLM-based agents
- `mcp_servers/`: Context servers
- `scripts/`: Data generation and demos
- `tests/`: Unit tests

## Setup

Requires Python 3.10+, Node.js for dashboard. See `requirements.txt` and `documentation/` for details.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Krishna-Gour/neuro-occ.git
   cd neuro-occ
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

3. **Generate synthetic data:**
   ```bash
   python scripts/generate_data.py
   ```

4. **Launch MCP servers** (run in separate terminals or background):
   ```bash
   # Crew data server
   python mcp_servers/crew_mcp.py &

   # Fleet data server
   python mcp_servers/fleet_mcp.py &

   # Regulatory data server
   python mcp_servers/reg_mcp.py &
   ```

5. **Start the dashboard:**
   ```bash
   cd dashboard
   npm install
   npm start
   ```
   Access at `http://localhost:3000`.

6. **Run the MVP demo:**
   ```bash
   PYTHONPATH=. python scripts/mvp_demo.py
   ```

This is an experimental project, not a production system.
