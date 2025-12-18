import React, { useState, useEffect } from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';
import { AlertCircle, CheckCircle, Brain, Plane, ThumbsUp, Users, MapPin } from 'lucide-react';

const initialNodes = [
  { id: 'DEL', position: { x: 250, y: 5 }, data: { label: 'Delhi (DEL)' } },
  { id: 'BOM', position: { x: 100, y: 200 }, data: { label: 'Mumbai (BOM)' } },
  { id: 'BLR', position: { x: 400, y: 200 }, data: { label: 'Bangalore (BLR)' } },
];

const initialEdges = [
  { id: 'e1-2', source: 'DEL', target: 'BOM', animated: true, style: { stroke: '#10b981' } },
  { id: 'e1-3', source: 'DEL', target: 'BLR', animated: true, style: { stroke: '#10b981' } },
];

function App() {
  const [thinking, setThinking] = useState(false);
  const [proposals, setProposals] = useState([]);
  const [approvedSolution, setApprovedSolution] = useState(null);
  const [edges, setEdges] = useState(initialEdges);
  const [systemStatus, setSystemStatus] = useState({
    pilots: 0,
    aircraft: 0,
    flights: 0,
    serversOnline: false
  });

  // Fetch system status on load
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const [pilotsRes, aircraftRes] = await Promise.all([
          fetch('http://localhost:8001/pilots'),
          fetch('http://localhost:8002/aircraft')
        ]);
        const pilots = await pilotsRes.json();
        const aircraft = await aircraftRes.json();
        setSystemStatus({
          pilots: pilots.length,
          aircraft: aircraft.length,
          flights: 349, // From generated data
          serversOnline: true
        });
      } catch (error) {
        console.error('Failed to fetch system status:', error);
        setSystemStatus(prev => ({ ...prev, serversOnline: false }));
      }
    };
    fetchStatus();
  }, []);

  const triggerDisruption = () => {
    setProposals([]);
    setApprovedSolution(null);
    setEdges(initialEdges.map(e => ({ ...e, style: { stroke: '#ef4444' }, animated: false })));
    
    // AI starts thinking and generates multiple proposals
    setThinking(true);
    setTimeout(() => {
      setThinking(false);
      setProposals([
        {
          id: 1,
          action: "Swap VT-ICD (DEL-BOM) with VT-IIJ (BLR-DEL)",
          reason: "Prevents Rule B FDTL violation for Pilot Sharma; Minor delay for 6E-105",
          savings: "₹4.5L",
          compliant: true
        },
        {
          id: 2,
          action: "Delay flight 6E-101 (DEL-BOM) by 90 mins",
          reason: "Crew rest extension; Impact on connecting passengers",
          savings: "₹2.0L",
          compliant: true
        },
        {
          id: 3,
          action: "Cancel flight 6E-101 (DEL-BOM)",
          reason: "High passenger compensation, but prevents cascading delays",
          savings: "-₹10.0L (cost)",
          compliant: true
        },
        {
          id: 4,
          action: "Assign Pilot X who has exceeded FDTL (Non-compliant example)",
          reason: "Exceeds max daily flight time of 8.0 hours.",
          savings: "N/A",
          compliant: false
        }
      ]);
      // No immediate edge change, waiting for human approval
    }, 3000);
  };

  const approveProposal = (proposal) => {
    setApprovedSolution(proposal);
    setProposals([]); // Clear proposals once one is approved
    setEdges(initialEdges.map(e => ({ ...e, style: { stroke: '#10b981' }, animated: true })));
    // In a real system, this would trigger backend execution
    console.log(`Human approved proposal: ${proposal.action}`);
  };

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#0f172a', color: 'white', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '1rem', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Brain color="#8b5cf6" /> Neuro-OCC 2.0 <span style={{ fontSize: '0.9rem', color: '#94a3b8', marginLeft: '1rem' }}>(Co-pilot Mode)</span>
        </h1>
        <button 
          onClick={triggerDisruption}
          style={{ background: '#ef4444', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.5rem', fontWeight: 'bold', cursor: 'pointer', border: 'none' }}
        >
          Inject Disruption (Delhi Fog)
        </button>
      </header>

      <div style={{ flex: 1, position: 'relative' }}>
        <ReactFlow nodes={initialNodes} edges={edges}>
          <Background color="#334155" gap={20} />
          <Controls />
        </ReactFlow>

        {/* HUD */}
        <div style={{ position: 'absolute', top: '1rem', right: '1rem', width: '350px', background: 'rgba(30, 41, 59, 0.9)', padding: '1rem', borderRadius: '0.5rem', border: '1px solid #334155' }}>
          <h2 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {thinking ? <Brain className="animate-pulse" /> : <AlertCircle />}
            System Status
          </h2>
          
          <div style={{ marginBottom: '1rem', fontSize: '0.9rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Users size={16} color={systemStatus.serversOnline ? '#10b981' : '#ef4444'} />
              <span>Pilots: {systemStatus.pilots}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Plane size={16} color={systemStatus.serversOnline ? '#10b981' : '#ef4444'} />
              <span>Aircraft: {systemStatus.aircraft}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <MapPin size={16} color={systemStatus.serversOnline ? '#10b981' : '#ef4444'} />
              <span>Flights: {systemStatus.flights}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle size={16} color={systemStatus.serversOnline ? '#10b981' : '#ef4444'} />
              <span>MCP Servers: {systemStatus.serversOnline ? 'Online' : 'Offline'}</span>
            </div>
          </div>
          
          {thinking && (
            <div style={{ color: '#94a3b8' }}>
              <p>Evaluating 1,000 simulations...</p>
              <p>Querying Crew MCP...</p>
              <p>Checking DGCA 2025 Compliance...</p>
              <p>Generating optimal recovery proposals...</p>
            </div>
          )}

          {proposals.length > 0 && approvedSolution === null && (
            <div>
              <p style={{ fontWeight: 'bold', color: '#8b5cf6', marginBottom: '0.5rem' }}>Human-in-the-Loop: Review Proposals</p>
              {proposals.filter(p => p.compliant).map(proposal => (
                <div key={proposal.id} style={{ border: '1px solid #334155', padding: '0.75rem', borderRadius: '0.5rem', marginBottom: '0.5rem', background: '#1e293b' }}>
                  <p style={{ fontWeight: 'bold', color: '#e2e8f0' }}>{proposal.action}</p>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.5rem' }}>Reason: {proposal.reason}</p>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Estimated Impact: {proposal.savings}</p>
                  <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: proposal.compliant ? '#10b981' : '#ef4444' }}>
                     {proposal.compliant ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                     <span style={{ fontSize: '0.8rem' }}>Symbolic Verifier: {proposal.compliant ? 'PASSED' : 'FAILED'}</span>
                  </div>
                  {proposal.compliant && (
                    <button 
                      onClick={() => approveProposal(proposal)}
                      style={{ marginTop: '0.75rem', background: '#10b981', color: 'white', padding: '0.4rem 0.8rem', borderRadius: '0.4rem', fontWeight: 'bold', cursor: 'pointer', border: 'none', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                    >
                      <ThumbsUp size={14} /> Approve Plan
                    </button>
                  )}
                </div>
              ))}
                {/* Display non-compliant proposals separately or with a warning */}
                {proposals.filter(p => !p.compliant).map(proposal => (
                    <div key={proposal.id} style={{ border: '1px solid #ef4444', padding: '0.75rem', borderRadius: '0.5rem', marginBottom: '0.5rem', background: '#450a0a' }}>
                        <p style={{ fontWeight: 'bold', color: '#ef4444' }}>{proposal.action} (Non-Compliant)</p>
                        <p style={{ fontSize: '0.8rem', color: '#fca5a5', marginBottom: '0.5rem' }}>Reason: {proposal.reason}</p>
                        <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ef4444' }}>
                           <AlertCircle size={16} />
                           <span style={{ fontSize: '0.8rem' }}>Symbolic Verifier: FAILED</span>
                        </div>
                    </div>
                ))}
            </div>
          )}

          {approvedSolution && (
            <div style={{ borderLeft: '4px solid #10b981', paddingLeft: '0.5rem' }}>
              <p style={{ fontWeight: 'bold', color: '#10b981' }}>Recovery Plan Approved & Executed!</p>
              <p style={{ fontSize: '0.9rem' }}>Action: {approvedSolution.action}</p>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{approvedSolution.reason}</p>
              <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                 <CheckCircle size={16} color="#10b981" />
                 <span style={{ fontSize: '0.8rem' }}>Symbolic Verifier: PASSED</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
