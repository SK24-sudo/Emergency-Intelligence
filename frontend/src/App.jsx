import React, { useEffect, useState } from 'react';
import { api } from './services/api';

const emptyIncident = { type: 'fire', description: '', latitude: '16.266', longitude: '73.483' };

function Navigation() {
  return <nav className="site-nav"><a className="nav-brand" href="/">SafeZone</a><div className="nav-links"><a href="/">Citizen Portal</a><a href="/control">Control Centre</a></div></nav>;
}

function CitizenPortal() {
  const [incidentForm, setIncidentForm] = useState(emptyIncident);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submitEmergency(event) {
    event.preventDefault();
    setBusy(true);
    setMessage('');
    setError('');
    try {
      const result = await api.post('/incidents', {
        ...incidentForm,
        latitude: Number(incidentForm.latitude),
        longitude: Number(incidentForm.longitude),
      });
      if (result.duplicate) {
        setMessage('This emergency report is already known to the SafeZone Control Centre.');
      } else {
        setMessage('Emergency reported successfully. Your report has been sent to the SafeZone Control Centre.');
        setIncidentForm(emptyIncident);
      }
    } catch {
      setError('Unable to submit the emergency. Please try again.');
    } finally {
      setBusy(false);
    }
  }

  return <main className="citizen-page"><Navigation /><section className="citizen-hero"><p className="kicker">PUBLIC SAFETY / RAPID REPORTING</p><h1>SafeZone</h1><p className="brand-subtitle">Emergency Intelligence &amp; Rapid Response</p><p className="brand-tagline">Report. Assess. Respond.</p><p className="citizen-description">Report an emergency and our control centre will assess and coordinate the response.</p></section><section className="citizen-form panel"><div className="panel-heading"><div><p className="eyebrow">REPORT INCIDENT</p><h2>Submit an emergency</h2></div><span className="pulse" /></div><form onSubmit={submitEmergency}><label>Emergency type<select value={incidentForm.type} onChange={(event) => setIncidentForm({ ...incidentForm, type: event.target.value })}><option value="accident">Accident</option><option value="fire">Fire</option><option value="flood">Flood</option><option value="medical">Medical Emergency</option><option value="hazard">Hazard</option><option value="unsafe_location">Unsafe Location</option><option value="missing_person">Missing Person</option><option value="other_emergency">Other Emergency</option></select></label><label>Description<textarea required value={incidentForm.description} placeholder="Describe what is happening" onChange={(event) => setIncidentForm({ ...incidentForm, description: event.target.value })} /></label><div className="form-row"><label>Latitude<input required type="number" step="any" value={incidentForm.latitude} onChange={(event) => setIncidentForm({ ...incidentForm, latitude: event.target.value })} /></label><label>Longitude<input required type="number" step="any" value={incidentForm.longitude} onChange={(event) => setIncidentForm({ ...incidentForm, longitude: event.target.value })} /></label></div><button className="primary" disabled={busy} type="submit">{busy ? 'Submitting…' : 'Submit Emergency'}</button></form>{message && <p className="success" role="status">{message}</p>}{error && <p className="citizen-error" role="alert">{error}</p>}</section></main>;
}

function formatDate(value) {
  return value ? new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—';
}

function Stat({ label, value, tone = '' }) {
  return <div className="stat"><span>{label}</span><strong className={tone}>{value}</strong></div>;
}

function App() {
  if (window.location.pathname !== '/control') {
    return <CitizenPortal />;
  }

  const [data, setData] = useState({ incidents: [], alerts: [], assets: [], missions: [], persons: [] });
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [assetChoice, setAssetChoice] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [incidentFilter, setIncidentFilter] = useState('all');

  async function refresh() {
    try {
      setError('');
      const [incidents, alerts, assets, missions, persons] = await Promise.all([
        api.get('/incidents'), api.get('/alerts'), api.get('/assets'), api.get('/missions'), api.get('/persons'),
      ]);
      setData({ incidents, alerts, assets, missions, persons });
      setSelectedIncident((current) => current || incidents[0] || null);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  useEffect(() => { refresh(); }, []);

  async function analyze(incident) {
    try {
      setError('');
      const result = await api.post(`/incidents/${incident.id}/analyze`, {});
      setAnalysis(result);
      setSelectedIncident(incident);
    } catch (requestError) { setError(requestError.message); }
  }

  async function dispatch() {
    if (!selectedIncident || !assetChoice) return;
    try {
      setBusy(true);
      await api.post('/dispatch', { incident_id: selectedIncident.id, asset_id: Number(assetChoice) });
      setAssetChoice('');
      await refresh();
    } catch (requestError) { setError(requestError.message); }
    finally { setBusy(false); }
  }

  async function updateMission(mission, status) {
    try {
      await api.post(`/missions/${mission.id}/status`, { status, latitude: selectedIncident?.latitude, longitude: selectedIncident?.longitude });
      await refresh();
    } catch (requestError) { setError(requestError.message); }
  }

  const availableAssets = data.assets.filter((asset) => asset.status.toLowerCase() === 'available');
  const categories = [
    { key: 'fire', label: 'Fire', icon: '🔥' },
    { key: 'flood', label: 'Flood', icon: '🌊' },
    { key: 'accident', label: 'Accident', icon: '🚑' },
    { key: 'hazard', label: 'Hazard', icon: '⚠️' },
  ];
  const filteredIncidents = incidentFilter === 'all'
    ? data.incidents
    : data.incidents.filter((incident) => String(incident.type).toLowerCase() === incidentFilter);
  const points = [
    ...data.incidents.map((item) => ({ ...item, label: `Incident ${item.id}`, kind: 'incident' })),
    ...data.assets.map((item) => ({ ...item, label: item.name, kind: 'asset' })),
    ...data.persons.map((item) => ({ ...item, label: item.name || `Person ${item.id}`, kind: 'person' })),
  ].filter((point) => point.latitude != null && point.longitude != null);

  return (
    <main>
      <Navigation />
      <header className="topbar">
        <div><p className="kicker">PUBLIC SAFETY / RAPID RESPONSE</p><h1>SafeZone Control Centre</h1><p className="brand-subtitle">Emergency Intelligence &amp; Rapid Response</p><p className="brand-tagline">Report. Assess. Respond.</p><p className="control-description">Monitor reported emergencies, assess priority, and coordinate response assets.</p></div>
        <button className="refresh" onClick={refresh}>Refresh state</button>
      </header>
      {error && <div className="error" role="alert">{error}<button onClick={() => setError('')}>Dismiss</button></div>}

      <section className="stats">
        <Stat label="Incidents" value={data.incidents.length} />
        <Stat label="Active missions" value={data.missions.filter((item) => item.status !== 'search_complete' && item.status !== 'complete').length} tone="amber" />
        <Stat label="Available assets" value={availableAssets.length} tone="green" />
        <Stat label="People located" value={data.persons.length} tone="red" />
      </section>

      <section className="workspace">
        <div className="column">
          <div className="panel overview-panel"><div className="panel-heading"><div><p className="eyebrow">EMERGENCY OVERVIEW</p><h2>Reported emergency categories</h2></div><span className="count">{data.incidents.length}</span></div><div className="category-grid"><button className={`category-card ${incidentFilter === 'all' ? 'selected' : ''}`} onClick={() => setIncidentFilter('all')}><strong>◉ ALL</strong><b>{data.incidents.length}</b><small>View emergencies</small></button>{categories.map((category) => { const count = data.incidents.filter((incident) => String(incident.type).toLowerCase() === category.key).length; return <button className={`category-card ${incidentFilter === category.key ? 'selected' : ''}`} key={category.key} onClick={() => setIncidentFilter(category.key)}><strong>{category.icon} {category.label.toUpperCase()}</strong><b>{count}</b><small>View incidents</small></button>; })}</div></div>
          <div className="panel list-panel"><div className="panel-heading"><div><p className="eyebrow">{incidentFilter === 'all' ? 'ALL EMERGENCIES' : `${incidentFilter.toUpperCase()} EMERGENCIES`}</p><h2>Reported Emergencies</h2></div><span className="count">{filteredIncidents.length}</span></div>
            {filteredIncidents.length === 0 ? <p className="empty">No active {incidentFilter === 'all' ? '' : incidentFilter + ' '}emergencies.</p> : <div className="incident-list">{filteredIncidents.slice().reverse().map((incident) => <button className={`incident-row ${selectedIncident?.id === incident.id ? 'selected' : ''}`} key={incident.id} onClick={() => { setSelectedIncident(incident); analyze(incident); }}><span className="incident-mark">!</span><span><strong>{incident.type}</strong><small>{incident.description || 'No description'} · {incident.latitude}, {incident.longitude}</small></span><span className={`badge ${incident.severity}`}>{incident.severity || '—'} · {incident.priority || '—'}</span></button>)}</div>}
          </div>
        </div>

        <div className="column wide">
          <div className="panel map-panel"><div className="panel-heading"><div><p className="eyebrow">LIVE INCIDENT LOCATIONS</p><h2>Coordinate overview</h2></div><span className="map-key"><i className="dot red" /> incidents <i className="dot blue" /> assets <i className="dot gold" /> people</span></div><div className="map"><div className="grid-lines" />{points.map((point, index) => <span key={`${point.kind}-${point.id}`} title={`${point.label}: ${point.latitude}, ${point.longitude}`} className={`map-point ${point.kind}`} style={{ left: `${30 + ((Number(point.longitude) * 19 + index * 11) % 55)}%`, top: `${25 + ((Number(point.latitude) * 13 + index * 17) % 48)}%` }} />)}<div className="map-coordinates">{selectedIncident ? `${selectedIncident.latitude}° N  /  ${selectedIncident.longitude}° E` : 'Awaiting coordinates'}</div></div></div>
          <div className="panel response-panel"><div className="panel-heading"><div><p className="eyebrow">SAFEZONE INTELLIGENCE</p><h2>{selectedIncident ? 'Emergency Details' : 'Select an incident'}</h2></div>{selectedIncident && <span className={`badge ${selectedIncident.severity}`}>{selectedIncident.severity || 'unrated'}</span>}</div>{selectedIncident ? <><div className="incident-detail"><p><span>Type</span><strong>{selectedIncident.type}</strong></p><p><span>Description</span><strong>{selectedIncident.description || 'No description'}</strong></p><p><span>Location</span><strong>{selectedIncident.latitude}, {selectedIncident.longitude}</strong></p><p><span>Status</span><strong>{selectedIncident.status || 'reported'}</strong></p></div><div className="analysis"><div><span>Incident type</span><strong>{analysis?.classification || selectedIncident.type}</strong></div><div><span>Severity</span><strong>{analysis?.severity || selectedIncident.severity || '—'}</strong></div><div><span>Priority</span><strong>{analysis?.priority || selectedIncident.priority || '—'}</strong></div><div><span>Duplicate detection</span><strong>Checked on report</strong></div><div className="recommendation"><span>Recommendation</span><strong>{analysis?.recommendation || 'Analyze this incident to get a recommendation.'}</strong></div></div><div className="dispatch-row"><select value={assetChoice} onChange={(event) => setAssetChoice(event.target.value)}><option value="">Choose available asset</option>{availableAssets.map((asset) => <option key={asset.id} value={asset.id}>{asset.name} · {asset.type}</option>)}</select><button className="primary" disabled={!assetChoice || busy} onClick={dispatch}>Dispatch asset</button></div></> : <p className="empty">Click a reported emergency to view details and coordinate a response.</p>}</div>
          {selectedIncident && <div className="panel assets-panel"><div className="panel-heading"><div><p className="eyebrow">RESPONSE ASSETS</p><h2>Available Response Assets</h2></div><span className="count">{availableAssets.length}</span></div>{availableAssets.length === 0 ? <p className="empty">No available response assets.</p> : <div className="asset-list">{availableAssets.map((asset) => <div className="asset-row" key={asset.id}><span className="asset-icon">{asset.type.toLowerCase() === 'robot' ? '🤖' : '🚁'}</span><span><strong>{asset.name}</strong><small>{asset.type} · {asset.status}</small></span></div>)}</div>}</div>}
          <div className="panel people-panel"><div className="panel-heading"><div><p className="eyebrow">PEOPLE / DETECTIONS</p><h2>People located</h2></div><span className="count">{data.persons.length}</span></div>{data.persons.length === 0 ? <p className="empty">No people detected.</p> : <div className="person-list">{data.persons.map((person) => <div className="person-row" key={person.id}><span className="person-icon">+</span><span><strong>{person.name || `Person ${person.id}`}</strong><small>Incident {person.incident_id} · {person.status || 'reported'} · {person.latitude}, {person.longitude}</small></span></div>)}</div>}</div>
          <div className="panel missions-panel"><div className="panel-heading"><div><p className="eyebrow">ASSIGNMENTS</p><h2>Missions</h2></div></div>{data.missions.length === 0 ? <p className="empty">No missions assigned.</p> : <div className="mission-list">{data.missions.slice().reverse().map((mission) => <div className="mission-row" key={mission.id}><span className="mission-id">M-{String(mission.id).padStart(2, '0')}</span><span><strong>Incident {mission.incident_id} → Asset {mission.asset_id}</strong><small>Created {formatDate(mission.created_at)}</small></span><select value={mission.status} onChange={(event) => updateMission(mission, event.target.value)}><option>assigned</option><option>dispatched</option><option>searching</option><option>search_complete</option><option>complete</option></select></div>)}</div>}</div>
        </div>
      </section>
    </main>
  );
}

export default App;
