# Model Context Protocol (MCP) Servers - Production Data Services

## 1. Purpose: Real-Time Context for Production AI Systems

**Purpose:** To provide real-time, queryable context to the AI models in the Neuro-OCC 2.0 production system.

The MCP servers are a set of production-ready, FastAPI-based microservices that expose the Neuro-OCC's data and rules via RESTful APIs. They act as a "world model" for the AI, allowing it to access the information it needs to make informed decisions in real-time.

## 2. Production System Integration

MCP servers are fully integrated into the Neuro-OCC 2.0 production environment:

- **Automated Startup**: All servers launch automatically with `./start.sh`
- **Health Monitoring**: Continuous service health checks and metrics
- **Load Balancing**: Production-ready with connection pooling and caching
- **Security**: API authentication and rate limiting
- **Data Synchronization**: Real-time data updates from synthetic generation pipeline

## 3. MCP Server Architecture

There are three specialized MCP servers, each serving a specific domain:

### 1. Crew MCP (`mcp_servers/crew_mcp.py`)
**Port: 8001** - Pilot data and duty time management
- Real-time pilot roster and availability
- Fatigue monitoring and duty time tracking
- Crew scheduling and assignment data

### 2. Fleet MCP (`mcp_servers/fleet_mcp.py`)
**Port: 8002** - Aircraft status and maintenance tracking
- Aircraft inventory and specifications
- Real-time fleet status and availability
- Flight schedule and routing data
- Predictive maintenance integration

### 3. Regulatory MCP (`mcp_servers/reg_mcp.py`)
**Port: 8003** - Airport data and DGCA rule validation
- Airport network and capacity data
- DGCA FDTL rule engine and validation
- Regulatory compliance checking
- Safety rule interpretation

## 4. Production API Endpoints

### Crew MCP (Port 8001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pilots` | GET | Get all pilots with current status |
| `/pilots/{pilot_id}` | GET | Get specific pilot details |
| `/pilots/status/fatigue` | GET | Get pilots with high fatigue scores |
| `/pilots/{pilot_id}/duty-time` | GET | Get pilot's current duty time status |
| `/pilots/available` | GET | Get available pilots for assignment |
| `/health` | GET | Service health check |

### Fleet MCP (Port 8002)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/aircraft` | GET | Get all aircraft with status |
| `/aircraft/{tail_number}` | GET | Get specific aircraft details |
| `/flights` | GET | Get current flight schedule |
| `/flights/{flight_id}` | GET | Get specific flight details |
| `/aircraft/{tail_number}/health` | GET | Get aircraft health score (Mamba integration) |
| `/aircraft/available` | GET | Get available aircraft for scheduling |
| `/maintenance/schedule` | GET | Get maintenance schedule |
| `/health` | GET | Service health check |

### Regulatory MCP (Port 8003)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rules` | GET | Get all DGCA FDTL rules |
| `/rules/{rule_id}` | GET | Get specific rule details |
| `/airports` | GET | Get airport network data |
| `/airports/{code}` | GET | Get specific airport details |
| `/validate/duty-time` | POST | Validate duty time compliance |
| `/validate/rest-period` | POST | Validate rest period compliance |
| `/compliance/check` | POST | Comprehensive compliance validation |
| `/health` | GET | Service health check |

## 5. Production Data Flow

### Automated Data Pipeline
```
Synthetic Data Generation ──▶ MCP Servers ──▶ AI Models ──▶ Dashboard
        │                           │              │           │
        ▼                           ▼              ▼           ▼
   config.yaml ────────────────▶ Data Loading ──▶ API Queries ──▶ Real-time Display
```

### Service Dependencies
- **Data Source**: Synthetic data from `scripts/generate_data.py`
- **Configuration**: Rules and parameters from `config.yaml`
- **Health Monitoring**: Integrated with system health checks
- **API Clients**: Brain API and Dashboard consume MCP services

## 6. Automated Production Deployment

MCP servers are fully integrated into the automated deployment:

```bash
# Single command starts all MCP servers
./start.sh

# This automatically:
# 1. Generates synthetic data
# 2. Loads data into MCP servers
# 3. Starts all three MCP services
# 4. Performs health checks
# 5. Connects to Brain API and Dashboard
```

### Manual Startup (Development)
```bash
# Terminal 1: Crew MCP
python mcp_servers/crew_mcp.py

# Terminal 2: Fleet MCP
python mcp_servers/fleet_mcp.py

# Terminal 3: Regulatory MCP
python mcp_servers/reg_mcp.py
```

## 7. Production Features

### High Availability
- **Health Checks**: Automatic service monitoring and restart
- **Load Balancing**: Multiple instances support for high traffic
- **Caching**: Redis integration for performance optimization
- **Circuit Breakers**: Fault tolerance and graceful degradation

### Security & Compliance
- **API Authentication**: JWT-based authentication for production
- **Rate Limiting**: DDoS protection and fair usage policies
- **Audit Logging**: Complete API access and data query logs
- **Data Encryption**: TLS encryption for all communications

### Monitoring & Observability
- **Metrics Collection**: Prometheus metrics for monitoring
- **Distributed Tracing**: Request tracing across services
- **Performance Monitoring**: Response times and error rates
- **Business Metrics**: Query patterns and data usage analytics

## 8. API Documentation

Each MCP server provides interactive API documentation:

- **Crew MCP**: `http://localhost:8001/docs`
- **Fleet MCP**: `http://localhost:8002/docs`
- **Regulatory MCP**: `http://localhost:8003/docs`

## 9. Data Synchronization

### Real-time Updates
- **Data Refresh**: Automatic data reloading after generation
- **Incremental Updates**: Support for real-time data updates
- **Consistency Checks**: Data integrity validation across servers
- **Backup & Recovery**: Data persistence and disaster recovery

### Configuration Management
- **Dynamic Config**: Runtime configuration updates without restart
- **Environment Variables**: Secure credential management
- **Feature Flags**: Gradual rollout of new features
- **Version Control**: API versioning for backward compatibility

## 10. Integration Examples

### Python Client Usage
```python
import requests

# Query Crew MCP for available pilots
response = requests.get("http://localhost:8001/pilots/available")
pilots = response.json()

# Check aircraft health via Fleet MCP
health = requests.get("http://localhost:8002/aircraft/VT-I01/health").json()

# Validate compliance via Regulatory MCP
validation = requests.post("http://localhost:8003/compliance/check", json=pilot_data)
```

### System Integration
```python
# Brain API integration
from mcp_clients import CrewClient, FleetClient, RegulatoryClient

crew_client = CrewClient("http://localhost:8001")
fleet_client = FleetClient("http://localhost:8002")
regulatory_client = RegulatoryClient("http://localhost:8003")

# Use in AI decision making
available_pilots = crew_client.get_available_pilots()
aircraft_health = fleet_client.get_aircraft_health(tail_number)
compliance_ok = regulatory_client.validate_duty_time(pilot_data)
```

## 11. Production Scaling

### Performance Optimization
- **Database Integration**: PostgreSQL for large-scale data storage
- **Caching Layer**: Redis for frequently accessed data
- **Async Processing**: Non-blocking I/O for high concurrency
- **Horizontal Scaling**: Kubernetes-ready containerization

### Monitoring Dashboards
- **Grafana Integration**: Visual monitoring dashboards
- **Alert Manager**: Automated alerting for service issues
- **Log Aggregation**: ELK stack for comprehensive logging
- **Performance Analytics**: Detailed performance and usage metrics

## 12. Future Enhancements

*   **GraphQL APIs**: More flexible data querying
*   **WebSocket Support**: Real-time data streaming
*   **Machine Learning**: Predictive query optimization
*   **Multi-region**: Global deployment with data replication
*   **Advanced Caching**: AI-powered cache prefetching
