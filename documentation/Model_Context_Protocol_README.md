# Model Context Protocol (MCP) Servers

**Purpose:** To provide real-time, queryable context to the AI models in the Neuro-OCC system.

The MCP servers are a set of lightweight, FastAPI-based microservices that expose the Neuro-OCC's data and rules via a simple REST API. They act as a "world model" for the AI, allowing it to access the information it needs to make informed decisions.

There are three MCP servers, each with a specific domain:

1.  **Crew MCP (`mcp_servers/crew_mcp.py`):** Provides information about pilots.
2.  **Fleet MCP (`mcp_servers/fleet_mcp.py`):** Provides information about aircraft and flights.
3.  **Regulations MCP (`mcp_servers/reg_mcp.py`):** Provides a machine-readable version of the DGCA FDTL rules.

## How it Works

Each MCP server is a standalone FastAPI application. They load data from the `data/` directory and expose it through a series of API endpoints.

### Crew MCP

*   **Host:** `localhost:8001`
*   **Endpoints:**
    *   `/pilots`: Get a list of all pilots.
    *   `/pilots/{pilot_id}`: Get the details of a specific pilot.
    *   `/pilots/status/fatigue`: Get a list of pilots with a high fatigue score.

### Fleet MCP

*   **Host:** `localhost:8002`
*   **Endpoints:**
    *   `/aircraft`: Get a list of all aircraft.
    *   `/aircraft/{tail_number}`: Get the details of a specific aircraft.
    *   `/flights`: Get a list of all flights.
    *   `/aircraft/{tail_number}/mamba-score`: Get the health score for a specific aircraft (in a real system, this would query a predictive maintenance model like Mamba).

### Regulations MCP

*   **Host:** `localhost:8003`
*   **Endpoints:**
    *   `/rules`: Get a list of all DGCA FDTL rules.
    *   `/rules/{rule_id}`: Get the details of a specific rule.
    *   `/verify/rest`: Check if a given rest period is compliant with the rules for consecutive night duties.

## How to Run

To run the MCP servers, you will need to have Python and `uvicorn` installed.

You can run each server in a separate terminal session:

```bash
# Terminal 1: Crew MCP
uvicorn mcp_servers.crew_mcp:app --host 0.0.0.0 --port 8001
```

```bash
# Terminal 2: Fleet MCP
uvicorn mcp_servers.fleet_mcp:app --host 0.0.0.0 --port 8002
```

```bash
# Terminal 3: Regulations MCP
uvicorn mcp_servers.reg_mcp:app --host 0.0.0.0 --port 8003
```

Once running, you can access the API documentation for each server by visiting `http://localhost:<port>/docs` in your web browser.
