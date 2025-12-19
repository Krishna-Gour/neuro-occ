import React, { useCallback, useEffect, useMemo, useState } from 'react';
import ReactFlow, { Background, Controls, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Activity,
  AlertCircle,
  Brain,
  CheckCircle,
  Cloud,
  Loader2,
  MapPin,
  Plane,
  Shield,
  TrendingUp,
  Users
} from 'lucide-react';

const DEFAULT_DISRUPTION = {
  type: 'weather',
  severity: 'high',
  affected_airport: 'DEL',
  description: 'Delhi fog disruption – 30% capacity reduction'
};

const SERVICE_ENDPOINTS = [
  { key: 'crew', name: 'Crew MCP', url: 'http://localhost:8001/health' },
  { key: 'fleet', name: 'Fleet MCP', url: 'http://localhost:8002/health' },
  { key: 'reg', name: 'Regulatory MCP', url: 'http://localhost:8003/health' },
  { key: 'brain', name: 'Brain API', url: 'http://localhost:8004/health' }
];

const INITIAL_TIMELINE = [
  {
    time: new Date().toLocaleTimeString(),
    label: 'Systems online',
    detail: 'All services initialized and awaiting disruption input.'
  }
];

const numberFormatter = new Intl.NumberFormat('en-IN');

const MetricCard = ({ icon: Icon, label, value, sublabel }) => (
  <div className="metric-card">
    <div className="metric-icon">
      <Icon size={22} />
    </div>
    <div className="metric-content">
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
      {sublabel && <span className="metric-sublabel">{sublabel}</span>}
    </div>
  </div>
);

const ServicePill = ({ label, healthy }) => (
  <div className={`service-pill ${healthy ? 'healthy' : 'unhealthy'}`}>
    <span className="indicator" />
    <span>{label}</span>
  </div>
);

const ProposalCard = ({ proposal, onApprove, isApproved }) => {
  const compliant = proposal.compliant;
  return (
    <div className={`proposal-card ${isApproved ? 'approved' : ''}`}>
      <div className="proposal-header">
        <div className={`badge ${compliant ? 'badge-success' : 'badge-warning'}`}>
          {compliant ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
          <span>{compliant ? 'Regulatory Safe' : 'Action Requires Attention'}</span>
        </div>
        <span className="proposal-source">{proposal.source}</span>
      </div>
      <h4>{proposal.action}</h4>
      <p className="proposal-reason">{proposal.reason}</p>
      <div className="proposal-meta">
        <span>Impact: {proposal.savings}</span>
        <span>Disruption: {proposal.disruption_type?.toUpperCase()} · {proposal.severity?.toUpperCase()}</span>
      </div>
      {proposal.violations && proposal.violations.length > 0 && (
        <div className="violations">
          <span>Violations flagged:</span>
          <ul>
            {proposal.violations.map((violation, idx) => (
              <li key={idx}>{violation.description}</li>
            ))}
          </ul>
        </div>
      )}
      <button
        className="cta-button"
        disabled={isApproved}
        onClick={() => onApprove(proposal)}
      >
        {isApproved ? 'Approved' : 'Approve Plan'}
      </button>
    </div>
  );
};

const TimelineItem = ({ item }) => (
  <div className="timeline-item">
    <div className="timeline-marker" />
    <div className="timeline-content">
      <span className="timeline-time">{item.time}</span>
      <h5>{item.label}</h5>
      <p>{item.detail}</p>
    </div>
  </div>
);

function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [approvedSolution, setApprovedSolution] = useState(null);
  const [thinking, setThinking] = useState(false);
  const [systemStatus, setSystemStatus] = useState({ pilots: 0, aircraft: 0, flights: 0, airports: 0 });
  const [serviceHealth, setServiceHealth] = useState({ crew: false, fleet: false, reg: false, brain: false });
  const [disruptionTypes, setDisruptionTypes] = useState([]);
  const [selectedDisruption, setSelectedDisruption] = useState(DEFAULT_DISRUPTION);
  const [timeline, setTimeline] = useState(INITIAL_TIMELINE);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const appendTimeline = useCallback((entry) => {
    setTimeline((prev) => [...prev.slice(-11), entry]);
  }, []);

  const fetchSystemSnapshot = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const requests = [
        fetch('http://localhost:8003/airports'),
        fetch('http://localhost:8002/flights'),
        fetch('http://localhost:8001/pilots'),
        fetch('http://localhost:8002/aircraft'),
        fetch('http://localhost:8004/disruption-types')
      ];

      const healthRequests = SERVICE_ENDPOINTS.map((service) => fetch(service.url));

      const [airportsRes, flightsRes, pilotsRes, aircraftRes, disruptionRes] = await Promise.all(requests);
      const healthResults = await Promise.allSettled(healthRequests);

      const airports = airportsRes.ok ? await airportsRes.json() : [];
      const flights = flightsRes.ok ? await flightsRes.json() : [];
      const pilots = pilotsRes.ok ? await pilotsRes.json() : [];
      const aircraft = aircraftRes.ok ? await aircraftRes.json() : [];
      const disruptionTypePayload = disruptionRes.ok ? await disruptionRes.json() : [];

      setDisruptionTypes(disruptionTypePayload);

      const airportNodes = Array.isArray(airports)
        ? airports.slice(0, 12).map((airport, index) => ({
            id: airport.code || airport.id || `airport-${index}`,
            position: {
              x: (index % 4) * 210 + 40,
              y: Math.floor(index / 4) * 170 + 40
            },
            data: { label: `${airport.name} (${airport.code || airport.id})` },
            style: {
              background: '#0f172a',
              border: '1px solid rgba(148, 163, 184, 0.25)',
              color: '#e2e8f0',
              borderRadius: 12,
              padding: 12,
              fontSize: 12
            }
          }))
        : [];

      const filteredFlights = Array.isArray(flights) ? flights : [];
      const flightEdges = filteredFlights.slice(0, 16)
        .map((flight, index) => ({
          id: `f-${index}`,
          source: flight.origin,
          target: flight.destination,
          label: flight.flight_id || flight.flight_number,
          animated: true,
          style: { stroke: '#38bdf8', strokeWidth: 2 },
          labelStyle: { fill: '#94a3b8', fontSize: 10 }
        }))
        .filter((edge) => airportNodes.find((node) => node.id === edge.source) && airportNodes.find((node) => node.id === edge.target));

      setNodes(airportNodes);
      setEdges(flightEdges);

      setSystemStatus({
        pilots: pilots.length,
        aircraft: aircraft.length,
        flights: filteredFlights.length,
        airports: airports.length
      });

      const healthSnapshot = SERVICE_ENDPOINTS.reduce((acc, service, idx) => {
        acc[service.key] = healthResults[idx].status === 'fulfilled' && healthResults[idx].value.ok;
        return acc;
      }, {});
      setServiceHealth(healthSnapshot);
    } catch (err) {
      console.error('Failed to load system snapshot', err);
      setError('Unable to connect to one or more backend services.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSystemSnapshot();
    const interval = setInterval(fetchSystemSnapshot, 60000);
    return () => clearInterval(interval);
  }, [fetchSystemSnapshot]);

  useEffect(() => {
    if (disruptionTypes.length === 0) {
      return;
    }
    const activeType = disruptionTypes.find((item) => item.type === selectedDisruption.type);
    if (activeType && !activeType.severities?.includes(selectedDisruption.severity)) {
      setSelectedDisruption({
        ...selectedDisruption,
        severity: activeType.severities?.[0] || selectedDisruption.severity
      });
    }
  }, [disruptionTypes, selectedDisruption]);

  const severityOptions = useMemo(() => {
    const activeType = disruptionTypes.find((item) => item.type === selectedDisruption.type);
    return activeType?.severities || ['low', 'medium', 'high'];
  }, [disruptionTypes, selectedDisruption.type]);

  const metrics = useMemo(() => ([
    { icon: Users, label: 'Pilots', value: numberFormatter.format(systemStatus.pilots) },
    { icon: Plane, label: 'Aircraft', value: numberFormatter.format(systemStatus.aircraft) },
    { icon: Activity, label: 'Flights', value: numberFormatter.format(systemStatus.flights) },
    { icon: MapPin, label: 'Airports', value: numberFormatter.format(systemStatus.airports) }
  ]), [systemStatus]);

  const triggerDisruption = async () => {
    appendTimeline({
      time: new Date().toLocaleTimeString(),
      label: 'Disruption injected',
      detail: `${selectedDisruption.type.toUpperCase()} at ${selectedDisruption.affected_airport} (${selectedDisruption.severity.toUpperCase()})`
    });

    setThinking(true);
    setProposals([]);
    setApprovedSolution(null);

    const highlightedEdges = edges.map((edge) => {
      const isAffected = edge.source === selectedDisruption.affected_airport || edge.target === selectedDisruption.affected_airport;
      return {
        ...edge,
        style: {
          ...(edge.style || {}),
          stroke: isAffected ? '#f97316' : '#38bdf8',
          strokeWidth: isAffected ? 3 : 2
        },
        animated: isAffected
      };
    });
    setEdges(highlightedEdges);

    try {
      const response = await fetch('http://localhost:8004/generate-recovery-proposals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedDisruption)
      });

      if (!response.ok) {
        throw new Error('Brain API returned an error');
      }

      const data = await response.json();
      setProposals(data);
      appendTimeline({
        time: new Date().toLocaleTimeString(),
        label: 'Recovery strategies generated',
        detail: `${data.length} candidate plans prepared by Neuro-OCC.`
      });
    } catch (err) {
      console.error('Failed to generate proposals', err);
      const fallback = [
        {
          id: 1,
          action: 'Delay departures by 120 minutes (Fallback)',
          reason: 'Standard weather recovery protocol enacted automatically.',
          savings: '₹450K',
          compliant: true,
          violations: [],
          source: 'Fallback',
          disruption_type: selectedDisruption.type,
          severity: selectedDisruption.severity
        }
      ];
      setProposals(fallback);
      appendTimeline({
        time: new Date().toLocaleTimeString(),
        label: 'Fallback plans applied',
        detail: 'LLM unavailable; generated deterministic contingency playbook.'
      });
    } finally {
      setThinking(false);
    }
  };

  const handleApprove = (proposal) => {
    setApprovedSolution(proposal);
    appendTimeline({
      time: new Date().toLocaleTimeString(),
      label: 'Plan approved',
      detail: `Authorized action: ${proposal.action}`
    });
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1><Brain size={24} /> Neuro-OCC Operations Control</h1>
          <p>Federated neuro-symbolic decisioning for disruption recovery.</p>
        </div>
        <div className="header-status">
          <Shield size={18} />
          <span>
            {Object.values(serviceHealth).every(Boolean)
              ? 'All services healthy'
              : 'Service connectivity degraded'}
          </span>
        </div>
      </header>

      {error && (
        <div className="alert-banner">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <main className="app-main">
        <section className="metric-grid">
          {metrics.map((metric) => (
            <MetricCard key={metric.label} {...metric} />
          ))}
        </section>

        <section className="content-grid">
          <div className="flow-card panel-card">
            <div className="panel-header">
              <h2>Network Situation Picture</h2>
              <span className="panel-subtitle">Real-time airline graph with disruption overlays</span>
            </div>
            <div className="flow-container">
              {nodes.length === 0 && !loading ? (
                <div className="empty-state">
                  <Cloud size={20} />
                  <span>No network data available</span>
                </div>
              ) : (
                <ReactFlow nodes={nodes} edges={edges} fitView minZoom={0.5} maxZoom={1.5}>
                  <MiniMap style={{ background: '#020617' }} />
                  <Controls />
                  <Background gap={20} color="#1e293b" />
                </ReactFlow>
              )}
              {loading && (
                <div className="loading-overlay">
                  <Loader2 className="spin" size={22} />
                  <span>Synchronizing network state...</span>
                </div>
              )}
            </div>
          </div>

          <div className="side-panel">
            <div className="panel-card">
              <div className="panel-header">
                <h2>Inject Disruption</h2>
                <span className="panel-subtitle">Simulate real-world irregular operations</span>
              </div>
              <div className="form-grid">
                <label>
                  Disruption Type
                  <select
                    value={selectedDisruption.type}
                    onChange={(e) => setSelectedDisruption((prev) => ({ ...prev, type: e.target.value }))}
                  >
                    {disruptionTypes.length > 0
                      ? disruptionTypes.map((item) => (
                          <option key={item.type} value={item.type}>
                            {item.name}
                          </option>
                        ))
                      : ['weather', 'technical', 'crew', 'security', 'air_traffic'].map((type) => (
                          <option key={type} value={type}>
                            {type.replace('_', ' ')}
                          </option>
                        ))}
                  </select>
                </label>
                <label>
                  Severity
                  <select
                    value={selectedDisruption.severity}
                    onChange={(e) => setSelectedDisruption((prev) => ({ ...prev, severity: e.target.value }))}
                  >
                    {severityOptions.map((level) => (
                      <option key={level} value={level}>
                        {level.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Impacted Airport
                  <input
                    value={selectedDisruption.affected_airport}
                    onChange={(e) => setSelectedDisruption((prev) => ({ ...prev, affected_airport: e.target.value.toUpperCase() }))}
                    placeholder="e.g. DEL"
                  />
                </label>
                <label className="form-wide">
                  Operator Notes
                  <textarea
                    rows={3}
                    value={selectedDisruption.description}
                    onChange={(e) => setSelectedDisruption((prev) => ({ ...prev, description: e.target.value }))}
                  />
                </label>
                <button className="cta-button primary" onClick={triggerDisruption} disabled={thinking}>
                  {thinking ? 'Computing recovery paths...' : 'Generate Recovery Plans'}
                </button>
              </div>
              {disruptionTypes.length > 0 && (
                <div className="helper">
                  <span>Common actions:</span>
                  <ul>
                    {(disruptionTypes.find((item) => item.type === selectedDisruption.type)?.common_actions || []).map((action) => (
                      <li key={action}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="panel-card">
              <div className="panel-header">
                <h2>Service Health</h2>
                <span className="panel-subtitle">Core microservices powering Neuro-OCC</span>
              </div>
              <div className="service-grid">
                {SERVICE_ENDPOINTS.map((service) => (
                  <ServicePill key={service.key} label={service.name} healthy={serviceHealth[service.key]} />
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="panel-card proposals-section">
          <div className="panel-header inline">
            <div>
              <h2>Recommended Recovery Strategies</h2>
              <span className="panel-subtitle">System 2 reasoning pipeline output</span>
            </div>
            {thinking && (
              <span className="thinking">
                <Loader2 className="spin" size={16} />
                Evaluating search tree...
              </span>
            )}
          </div>

          {proposals.length === 0 && !thinking && (
            <div className="empty-state">
              <TrendingUp size={20} />
              <span>No proposals generated yet.</span>
            </div>
          )}

          <div className="proposal-grid">
            {proposals.map((proposal) => (
              <ProposalCard
                key={proposal.id}
                proposal={proposal}
                onApprove={handleApprove}
                isApproved={approvedSolution?.id === proposal.id}
              />
            ))}
          </div>
        </section>

        <section className="panel-card timeline-section">
          <div className="panel-header">
            <h2>Operations Timeline</h2>
            <span className="panel-subtitle">Chronological log of Neuro-OCC reasoning</span>
          </div>
          <div className="timeline-list">
            {timeline.map((item, idx) => (
              <TimelineItem key={`${item.time}-${idx}`} item={item} />
            ))}
          </div>
        </section>
      </main>

      <footer className="app-footer">
        <span>Neuro-OCC • Federated Autonomous Recovery System</span>
        <span>LLM x Symbolic x RL x MCP</span>
      </footer>
    </div>
  );
}

export default App;

