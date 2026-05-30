import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, ArrowRight, Activity, Globe, Hash } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

const Services = () => {
  const navigate = useNavigate();
  const [services, setServices] = useState([]);
  const [agencies, setAgencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    agency_id: '', name: '', description: '', endpoint_url: '', http_method: 'GET',
    status: 'ACTIVE', timeout_seconds: 30, headers: {},
    request_schema: {}, response_schema: {}, field_definitions: []
  });

  useEffect(() => {
    fetchData();
    api.get('/agencies/').then(r => setAgencies(r.data));
  }, []);

  const fetchData = async () => {
    try {
      const res = await api.get('/services/');
      setServices(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleCreate = async () => {
    try {
      await api.post('/services/', form);
      setShowModal(false);
      setForm({ agency_id: '', name: '', description: '', endpoint_url: '', http_method: 'GET', status: 'ACTIVE', timeout_seconds: 30, headers: {}, request_schema: {}, response_schema: {}, field_definitions: [] });
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create service');
    }
  };

  const filtered = services.filter(s =>
    s.name?.toLowerCase().includes(search.toLowerCase()) ||
    s.agency_name?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <Loading />;

  return (
    <div className="flex flex-col gap-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Service Registry</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">API endpoints published by government agencies</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Register Service
        </button>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
        <input className="input-field pl-10" placeholder="Search services..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      <div className="glass-panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--border-color)] text-[var(--text-muted)] text-left">
              <th className="px-4 py-3 font-medium">Service</th>
              <th className="px-4 py-3 font-medium">Agency</th>
              <th className="px-4 py-3 font-medium">Method</th>
              <th className="px-4 py-3 font-medium">Fields</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Health</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && <tr><td colSpan={7} className="px-4 py-8 text-center text-[var(--text-muted)]">No services found</td></tr>}
            {filtered.map(s => (
              <tr key={s.id} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-input)] transition-colors cursor-pointer" onClick={() => navigate(`/services/${s.id}`)}>
                <td className="px-4 py-3">
                  <p className="font-medium text-[var(--text-primary)]">{s.name}</p>
                  <p className="text-xs text-[var(--text-muted)] font-mono truncate max-w-xs">{s.full_url}</p>
                </td>
                <td className="px-4 py-3 text-[var(--text-secondary)]">{s.agency_name}</td>
                <td className="px-4 py-3">
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-[var(--bg-input)] border border-[var(--border-color)]">{s.http_method}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-xs flex items-center gap-1 text-[var(--text-muted)]">
                    <Hash className="w-3 h-3" /> {s.service_fields?.length || 0}
                  </span>
                </td>
                <td className="px-4 py-3"><Badge status={s.status} /></td>
                <td className="px-4 py-3"><Badge status={s.health_status} text={s.health_status} /></td>
                <td className="px-4 py-3"><ArrowRight className="w-4 h-4 text-[var(--text-muted)]" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Register Service" size="xl">
        <div className="space-y-4 max-h-[70vh] overflow-y-auto no-scrollbar pr-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Agency *</label>
              <select className="input-field" value={form.agency_id} onChange={e => setForm({...form, agency_id: e.target.value})} required>
                <option value="">Select agency...</option>
                {agencies.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Service Name *</label>
              <input className="input-field" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="e.g. Verify Identity" required />
            </div>
            <div>
              <label className="label">HTTP Method</label>
              <select className="input-field" value={form.http_method} onChange={e => setForm({...form, http_method: e.target.value})}>
                {['GET','POST','PUT','PATCH','DELETE'].map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Endpoint URL *</label>
              <input className="input-field" value={form.endpoint_url} onChange={e => setForm({...form, endpoint_url: e.target.value})} placeholder="/api/v1/verify or full URL" required />
            </div>
            <div>
              <label className="label">Timeout (seconds)</label>
              <input type="number" className="input-field" value={form.timeout_seconds} onChange={e => setForm({...form, timeout_seconds: parseInt(e.target.value)})} />
            </div>
            <div>
              <label className="label">Status</label>
              <select className="input-field" value={form.status} onChange={e => setForm({...form, status: e.target.value})}>
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">Description</label>
            <textarea className="input-field" rows={2} value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="What does this service do?" />
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={() => setShowModal(false)} className="btn-secondary">Cancel</button>
            <button onClick={handleCreate} className="btn-primary">Register Service</button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Services;