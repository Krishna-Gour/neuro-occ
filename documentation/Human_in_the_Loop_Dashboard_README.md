# Human-in-the-Loop Dashboard - Production Co-Pilot Interface

## 1. Purpose: AI as a Co-Pilot in Production Airline Operations

**Neuro-OCC 2.0** is designed to be a powerful assistant, not a replacement for human expertise. In mission-critical environments like an Airline Operations Control Center (OCC), the final authority and accountability must reside with the human operator. The **Co-Pilot Dashboard** is the production-ready interface that facilitates this crucial human-AI collaboration.

The dashboard provides the human operator with a clear, real-time view of the operational network, presents the AI's suggestions in an understandable format, and empowers the operator to make the final, informed decision.

## 2. Production System Integration

The dashboard is fully integrated into the Neuro-OCC 2.0 production environment:

- **Automated Startup**: Launches automatically with `./start.sh` on port 3000
- **Real-time Data**: Connects to MCP servers for live operational data
- **API Integration**: Communicates with Brain API for AI proposals
- **Production Monitoring**: Health checks and performance metrics
- **Secure Access**: Production-ready authentication and authorization

## 3. Why Human-in-the-Loop (HITL) is Critical

*   **Accountability and Safety**: A human operator is ultimately responsible for the safety and legality of all flight operations. The AI suggests, the human decides.
*   **Context and Nuance**: An experienced operator can incorporate real-world information that may not be present in the AI's data model, such as developing weather patterns, airport-specific NOTAMs (Notice to Air Missions), or crew members who are "fit for duty" on paper but may be experiencing stress.
*   **Building Trust**: By making the AI's reasoning transparent and giving the operator the final say, the system builds trust and encourages adoption. It's a tool to augment intelligence, not replace it.

## 4. Key Technical Components

*   **`dashboard/`**: The root directory for the React-based frontend application.
*   **`dashboard/package.json`**: Defines the project's dependencies and scripts. The key libraries are:
    *   `react`: The core UI library (v18+).
    *   `reactflow`: A powerful library for creating the node-based flight network visualization.
    *   `tailwindcss`: Modern CSS framework for responsive design.
    *   `lucide-react`: For clean, modern icons.
    *   `axios`: For API communication with backend services.
*   **`dashboard/src/App.js`**: The main React component with production-ready state management and error handling.

## 5. Production User Experience: Complete Workflow

The production dashboard provides a comprehensive interaction cycle between the operator and the AI:

### Phase 1: Real-Time Network Monitoring
The dashboard displays a live map-like view created with ReactFlow, showing:
- Airports as nodes with real-time status
- Active flights as animated edges with color-coded status
- Service health indicators for all MCP servers
- System status and AI activity monitoring

### Phase 2: Disruption Detection and Alerting
- **Automated Detection**: System automatically detects disruptions from MCP data
- **Manual Injection**: Operators can simulate disruptions for training/testing
- **Multi-disruption Support**: Weather, technical, crew, and security scenarios
- **Impact Assessment**: Automatic calculation of affected flights and passengers

### Phase 3: AI Analysis and Proposal Generation
The dashboard shows real-time AI processing:
- `Analyzing disruption impact...`
- `Querying Crew MCP for pilot availability...`
- `Checking DGCA compliance...`
- `Generating recovery proposals...`

### Phase 4: Intelligent Proposal Presentation
The system presents proposals with comprehensive information:

**✅ Compliant Proposals** (Passed by Symbolic Verifier):
- **Action Details**: Specific recovery actions (swaps, delays, cancellations)
- **AI Reasoning**: Natural language explanations from the LLM
- **Compliance Status**: DGCA FDTL validation results
- **Impact Analysis**: Financial cost, passenger impact, operational metrics
- **Risk Assessment**: Safety scores and risk factors
- **Approval Workflow**: One-click execution with confirmation

**❌ Non-Compliant Proposals** (Rejected by Verifier):
- **Failure Reason**: Specific DGCA violation details
- **Educational Context**: Why the proposal failed compliance
- **No Execution Option**: Safety guardrail prevents unsafe actions

### Phase 5: Human Decision Making
Operators evaluate proposals using:
- **Multi-criteria Filtering**: Sort by cost, safety, passenger impact
- **Comparative Analysis**: Side-by-side proposal comparison
- **Historical Data**: Past performance of similar disruptions
- **Expert Override**: Ability to request alternative AI analysis

### Phase 6: Execution and Monitoring
- **One-Click Approval**: Execute approved plans instantly
- **Real-time Feedback**: Immediate visual confirmation on network map
- **Execution Tracking**: Monitor plan implementation progress
- **Rollback Capability**: Emergency reversal for critical issues

## 6. Production Features

### Advanced Visualization
- **Interactive Network Map**: Zoom, pan, filter flight routes
- **Real-time Updates**: Live data from MCP servers
- **Color-coded Status**: Green (normal), Yellow (warning), Red (critical)
- **Performance Metrics**: System response times and AI confidence scores

### Safety and Compliance
- **Regulatory Validation**: Real-time DGCA compliance checking
- **Audit Trail**: Complete log of all decisions and actions
- **Safety Overrides**: Emergency procedures for critical situations
- **Compliance Reporting**: Automated regulatory reporting

### Operational Intelligence
- **Predictive Analytics**: Anticipate potential disruptions
- **Historical Analysis**: Learn from past incident responses
- **Performance Tracking**: System effectiveness metrics
- **Crew Management**: Real-time pilot status and fatigue monitoring

## 7. Automated Production Deployment

The dashboard is fully integrated into the automated deployment:

```bash
# Single command starts the complete system
./start.sh

# This automatically:
# 1. Installs Node.js dependencies
# 2. Builds production React app
# 3. Starts dashboard on port 3000
# 4. Connects to all backend services
# 5. Performs health checks
```

## 8. Manual Development Setup

For development and testing:

1.  **Navigate to the dashboard directory**:
    ```bash
    cd dashboard
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Start development server**:
    ```bash
    npm start
    ```

4.  **Access the dashboard**:
    Open `http://localhost:3000` in your browser

## 9. Production Architecture

### Service Integration
```
┌─────────────────┐    ┌──────────────────┐
│   Dashboard     │◄──▶│   Brain API      │
│   (Port 3000)   │    │   (Port 8004)    │
└─────────────────┘    └──────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌──────────────────┐
│   Crew MCP      │    │   Fleet MCP       │
│   (Port 8001)   │    │   (Port 8002)     │
└─────────────────┘    └──────────────────┘
         │
         ▼
┌─────────────────┐
│ Regulatory MCP  │
│   (Port 8003)   │
└─────────────────┘
```

### Security and Access Control
- **Role-based Access**: Different permission levels for operators
- **Audit Logging**: All actions tracked for compliance
- **Secure Communication**: HTTPS encryption for all API calls
- **Session Management**: Secure authentication and timeout handling

## 10. Monitoring and Analytics

Production dashboard includes comprehensive monitoring:

- **User Activity**: Track operator interactions and decision patterns
- **System Performance**: Response times and error rates
- **AI Effectiveness**: Proposal acceptance rates and quality metrics
- **Safety Metrics**: Compliance violation tracking and safety incidents