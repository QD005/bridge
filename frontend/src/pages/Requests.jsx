import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, Filter, ArrowRight, User, Calendar } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Badge from '../components/Badge';
import Modal from '../components/Modal';
import DynamicForm from '../components/DynamicForm';

const Requests = () => {
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showNewModal, setShowNewModal] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [formData, setFormData] = useState({});
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchRequests();
    api.get('/workflows/?status=PUBLISHED').then(r => setWorkflows(r.data));
  }, []);

  const fetchRequests = async () => {
    try {
      const res = await api.get('/executions/');
      setRequests(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleWorkflowSelect = (wf) => {
    setSelectedWorkflow(wf);
    // Build initial form data from all service fields across steps
    const initial = { applicant_name: '', applicant_contact: '' };
    wf.steps?.forEach(step => {
      if (step.service?.field_definitions) {
        step.service.field_definitions.forEach(field => {
          initial[field.name] = '';
        });
      }
    });
    setFormData(initial);
  };

  const handleCreate = async () => {
    if (!selectedWorkflow) return;
    setCreating(true);
    try {
      const res = await api.post('/executions/', {
        workflow_id: selectedWorkflow.id,
        applicant_name: formData.applicant_name,
        applicant_contact: formData.applicant_contact,
        payload: formData,
      });
      setShowNewModal(false);
      setSelectedWorkflow(null);
      setFormData({});
      navigate(`/requests/${res.data.id}`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create request');
    } finally {
      setCreating(false);
    }
  };

  const filtered = requests.filter(r =>
    r.applicant_name?.toLowerCase().includes(search.toLowerCase()) ||
    r.workflow_name?.toLowerCase().includes(search.toLowerCase()) ||
    r.id?.toString().includes(search)
  );

  if (loading) return <Loading />;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Service Requests</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">Process citizen applications through agency workflows</p>
        </div>
        <button onClick={() => setShowNewModal(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Request
        </button>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
          <input
            type="text"
            className="input-field pl-10"
            placeholder="Search requests..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="glass-panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--border-color)] text-[var(--text-muted)] text-left">
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Applicant</th>
              <th className="px-4 py-3 font-medium">Workflow</th>
              <th className="px-4 py-3 font-medium">Agency</th>
              <th className="px-4 py-3 font-medium">Progress</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Date</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-[var(--text-muted)]">No requests found</td></tr>
            )}
            {filtered.map(req => (
              <tr key={req.id} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-input)] transition-colors cursor-pointer" onClick={() => navigate(`/requests/${req.id}`)}>
                <td className="px-4 py-3 font-mono text-[var(--text-muted)]">#{req.id}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-[var(--text-muted)]" />
                    <span className="font-medium text-[var(--text-primary)]">{req.applicant_name || 'Unknown'}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-[var(--text-secondary)]">{req.workflow_name}</td>
                <td className="px-4 py-3 text-[var(--text-secondary)]">{req.agency_name}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-[var(--bg-input)] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-accent rounded-full"
                        style={{ width: `${req.total_steps ? (req.completed_steps / req.total_steps) * 100 : 0}%` }}
                      />
                    </div>
                    <span className="text-xs text-[var(--text-muted)]">{req.completed_steps || 0}/{req.total_steps || 0}</span>
                  </div>
                </td>
                <td className="px-4 py-3"><Badge status={req.status} /></td>
                <td className="px-4 py-3 text-[var(--text-muted)] whitespace-nowrap">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5" />
                    {new Date(req.started_at).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <ArrowRight className="w-4 h-4 text-[var(--text-muted)]" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* New Request Modal */}
      <Modal isOpen={showNewModal} onClose={() => { setShowNewModal(false); setSelectedWorkflow(null); }} title="New Service Request" size="lg">
        {!selectedWorkflow ? (
          <div className="space-y-3">
            <p className="text-sm text-[var(--text-muted)] mb-3">Select a workflow to process a new application:</p>
            {workflows.map(wf => (
              <button
                key={wf.id}
                onClick={() => handleWorkflowSelect(wf)}
                className="w-full text-left p-4 rounded-lg border border-[var(--border-color)] hover:border-accent hover:bg-accent/5 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">{wf.name}</p>
                    <p className="text-xs text-[var(--text-muted)] mt-0.5">{wf.agency_name} · {wf.step_count} steps</p>
                  </div>
                  <ArrowRight className="w-4 h-4 text-[var(--text-muted)]" />
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-3 rounded-lg bg-accent/5 border border-accent/20">
              <p className="text-sm font-medium text-accent">{selectedWorkflow.name}</p>
              <p className="text-xs text-[var(--text-muted)]">{selectedWorkflow.agency_name}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Applicant Name *</label>
                <input
                  className="input-field"
                  value={formData.applicant_name || ''}
                  onChange={e => setFormData({ ...formData, applicant_name: e.target.value })}
                  placeholder="e.g. Daniel Kato"
                  required
                />
              </div>
              <div>
                <label className="label">Applicant Contact</label>
                <input
                  className="input-field"
                  value={formData.applicant_contact || ''}
                  onChange={e => setFormData({ ...formData, applicant_contact: e.target.value })}
                  placeholder="Phone or email"
                />
              </div>
            </div>

            {/* Dynamic fields from workflow steps */}
            {selectedWorkflow.steps?.map(step => {
              if (!step.service?.field_definitions?.length) return null;
              return (
                <div key={step.id} className="border-t border-[var(--border-color)] pt-4">
                  <p className="text-sm font-medium text-[var(--text-secondary)] mb-3 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-accent/10 text-accent text-xs flex items-center justify-center font-bold">{step.order}</span>
                    {step.name || step.step_type}
                  </p>
                  <DynamicForm
                    fields={step.service.field_definitions}
                    data={formData}
                    onChange={setFormData}
                  />
                </div>
              );
            })}

            <div className="flex justify-end gap-3 pt-2">
              <button onClick={() => setSelectedWorkflow(null)} className="btn-secondary">Back</button>
              <button onClick={handleCreate} disabled={creating || !formData.applicant_name} className="btn-primary flex items-center gap-2">
                {creating ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <Plus className="w-4 h-4" />}
                Create Request
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Requests;
