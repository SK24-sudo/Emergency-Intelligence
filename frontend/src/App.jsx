import React, { useEffect, useState } from 'react';
import { api } from './services/api';

const emptyIncident = { type: 'fire', description: '', latitude: '16.266', longitude: '73.483' };

function formatDate(value) {
  return value ? new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—';
}

function Stat({ label, value, tone = '' }) {
  return <div className="stat"><span>{label}</span><strong className={tone}>{value}</strong></div>;
}

function App() {
  const [data, setData] = useState({ incidents: [], alerts: [], assets: [], missions: [], persons: [] });
  const [incidentForm, setIncidentForm] = useState(emptyIncident);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [assetChoice, setAssetChoice] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

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

  async function createIncident(event) {
    event.preventDefault();
    setBusy(true);
    try {
      const created = await api.post('/incidents', {
        ...incidentForm,
        latitude: Number(incidentForm.latitude),
        longitude: Number(incidentForm.longitude),
      });
      if (created.duplicate) {
        setError(created.message);
        setSelectedIncident(data.incidents.find((item) => item.id === created.incident_id) || null);
      } else {
        setSelectedIncident(created);
        setAnalysis({ classification: created.classification, severity: created.severity, priority: created.priority, recommendation: created.recommendation });
        setIncidentForm(emptyIncident);
      }
      await refresh();
    } catch (requestError) { setError(requestError.message); }
    finally { setBusy(false); }
  }

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
  const points = [
    ...data.incidents.map((item) => ({ ...item, label: `Incident ${item.id}`, kind: 'incident' })),
    ...data.assets.map((item) => ({ ...item, label: item.name, kind: 'asset' })),
    ...data.persons.map((item) => ({ ...item, label: item.name || `Person ${item.id}`, kind: 'person' })),
  ].filter((point) => point.latitude != null && point.longitude != null);

  return (
    <main>
      <header className="topbar">
        <div><p className="kicker">FIELD OPERATIONS / LIVE</p><h1>Emergency Intelligence</h1></div>
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
          <div className="panel create-panel">
            <div className="panel-heading"><div><p className="eyebrow">NEW REPORT</p><h2>Log an incident</h2></div><span className="pulse" /></div>
            <form onSubmit={createIncident}>
              <label>Type<select value={incidentForm.type} onChange={(event) => setIncidentForm({ ...incidentForm, type: event.target.value })}><option>fire</option><option>flood</option><option>medical</option><option>collapse</option></select></label>
              <label>Description<textarea required value={incidentForm.description} placeholder="What is happening?" onChange={(event) => setIncidentForm({ ...incidentForm, description: event.target.value })} /></label>
              <div className="form-row"><label>Latitude<input required type="number" step="any" value={incidentForm.latitude} onChange={(event) => setIncidentForm({ ...incidentForm, latitude: event.target.value })} /></label><label>Longitude<input required type="number" step="any" value={incidentForm.longitude} onChange={(event) => setIncidentForm({ ...incidentForm, longitude: event.target.value })} /></label></div>
              <button className="primary" disabled={busy} type="submit">{busy ? 'Sending…' : 'Create incident'}</button>
            </form>
          </div>
          <div className="panel list-panel"><div className="panel-heading"><div><p className="eyebrow">INCOMING SIGNALS</p><h2>Incidents</h2></div><span className="count">{data.incidents.length}</span></div>
            {data.incidents.length === 0 ? <p className="empty">No incidents in the current feed.</p> : <div className="incident-list">{data.incidents.slice().reverse().map((incident) => <button className={`incident-row ${selectedIncident?.id === incident.id ? 'selected' : ''}`} key={incident.id} onClick={() => { setSelectedIncident(incident); analyze(incident); }}><span className="incident-mark">!</span><span><strong>{incident.type}</strong><small>{incident.description || 'No description'}</small></span><span className={`badge ${incident.severity}`}>{incident.priority || '—'}</span></button>)}</div>}
          </div>
        </div>

        <div className="column wide">
          <div className="panel map-panel"><div className="panel-heading"><div><p className="eyebrow">COORDINATE OVERVIEW</p><h2>Operational map</h2></div><span className="map-key"><i className="dot red" /> incidents <i className="dot blue" /> assets <i className="dot gold" /> people</span></div><div className="map"><div className="grid-lines" />{points.map((point, index) => <span key={`${point.kind}-${point.id}`} title={`${point.label}: ${point.latitude}, ${point.longitude}`} className={`map-point ${point.kind}`} style={{ left: `${30 + ((Number(point.longitude) * 19 + index * 11) % 55)}%`, top: `${25 + ((Number(point.latitude) * 13 + index * 17) % 48)}%` }} />)}<div className="map-coordinates">{selectedIncident ? `${selectedIncident.latitude}° N  /  ${selectedIncident.longitude}° E` : 'Awaiting coordinates'}</div></div></div>
          <div className="panel response-panel"><div className="panel-heading"><div><p className="eyebrow">RESPONSE CONTROL</p><h2>{selectedIncident ? `Incident ${selectedIncident.id}` : 'Select an incident'}</h2></div>{selectedIncident && <span className={`badge ${selectedIncident.severity}`}>{selectedIncident.severity || 'unrated'}</span>}</div>{selectedIncident ? <><div className="analysis"><div><span>Classification</span><strong>{analysis?.classification || selectedIncident.type}</strong></div><div><span>Priority</span><strong>{analysis?.priority || selectedIncident.priority || '—'}</strong></div><div className="recommendation"><span>Recommendation</span><strong>{analysis?.recommendation || 'Analyze this incident to get a recommendation.'}</strong></div></div><div className="dispatch-row"><select value={assetChoice} onChange={(event) => setAssetChoice(event.target.value)}><option value="">Choose available asset</option>{availableAssets.map((asset) => <option key={asset.id} value={asset.id}>{asset.name} · {asset.type}</option>)}</select><button className="primary" disabled={!assetChoice || busy} onClick={dispatch}>Dispatch asset</button></div></> : <p className="empty">Create or select an incident to coordinate a response.</p>}</div>
          <div className="panel missions-panel"><div className="panel-heading"><div><p className="eyebrow">ASSIGNMENTS</p><h2>Missions</h2></div></div>{data.missions.length === 0 ? <p className="empty">No missions assigned.</p> : <div className="mission-list">{data.missions.slice().reverse().map((mission) => <div className="mission-row" key={mission.id}><span className="mission-id">M-{String(mission.id).padStart(2, '0')}</span><span><strong>Incident {mission.incident_id} → Asset {mission.asset_id}</strong><small>Created {formatDate(mission.created_at)}</small></span><select value={mission.status} onChange={(event) => updateMission(mission, event.target.value)}><option>assigned</option><option>dispatched</option><option>searching</option><option>search_complete</option><option>complete</option></select></div>)}</div>}</div>
        </div>
      </section>
    </main>
  );
}

export default App;
