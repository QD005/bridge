import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, ArrowRight, GitBranch, Layers, Copy, Archive } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

const Workflows = () => {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState([]);
  const [agencies, setAgencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', agency_id: '' });

  useEffect(() => {
    fetchData();
    api.get('/agencies/').then(r => setAgencies(r.data));
  }, []);

  const fetchData = async () => {
    try {
      const res = await api.get('/workflows/');
      setWorkflows(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      const res = await api.post('/workflows/', form);
      setShowModal(false);
      setForm({ name: '', description: '', agency_id: '' });
      navigate(`/workflows/${res.data.id}`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create workflow');
    }
  };

  const handlePublish = async (id) => {
    try {
      await api.post(`/workflows/${id}/publish/`);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to publish');
    }
  };

  const filtered = workflows.filter(w =>
    w.name?.toLowerCase().includes(search.toLowerCase()) ||
    w.agency_name?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <Loading />;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Workflows</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">Multi-agency process definitions</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Create Workflow
        </button>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
        <input className="input-field pl-10" placeholder="Search workflows..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.length === 0 && <p className="text-[var(--text-muted)] col-span-full">No workflows found</p>}
        {filtered.map(wf => (
          <div key={wf.id} className="glass-panel p-5 hover:border-accent/30 transition-all group">
            <div className="flex items-start justify-between mb-3">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                <GitBranch className="w-5 h-5 text-accent" />
              </div>
              <Badge status={wf.status} />
            </div>
            <h3 className="font-semibold text-[var(--text-primary)] mb-1 group-hover:text-accent transition-colors cursor-pointer" onClick={() => navigate(`/workflows/${wf.id}`)}>
              {wf.name}
            </h3>
            <p className="text-xs text-[var(--text-muted)] mb-3">{wf.agency_name} · v{wf.version} · {wf.step_count} steps</p>
            <div className="flex items-center gap-2">
              {wf.status === 'DRAFT' && (
                <button onClick={() => handlePublish(wf.id)} className="btn-primary text-xs py-1.5 px-3 flex-1">
                  Publish
                </button>
              )}
              <button onClick={() => navigate(`/workflows/${wf.id}`)} className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1">
                Edit <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Create Workflow" size="md">
        <div className="space-y-4">
          <div>
            <label className="label">Name *</label>
            <input className="input-field" value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="e.g. Business License Approval" required />
          </div>
          <div>
            <label className="label">Agency *</label>
            <select className="input-field" value={form.agency_id} onChange={e => setForm({...form, agency_id: e.target.value})} required>
              <option value="">Select agency...</option>
              {agencies.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Description</label>
            <textarea className="input-field" rows={3} value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Describe the workflow purpose..." />
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={() => setShowModal(false)} className="btn-secondary">Cancel</button>
            <button onClick={handleCreate} className="btn-primary">Create</button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Workflows;
