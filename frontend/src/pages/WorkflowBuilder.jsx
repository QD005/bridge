import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Trash2, GripVertical, Save, Play, ArrowUp, ArrowDown, Settings } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

const STEP_TYPES = [
  { value: 'SERVICE', label: 'Service Call', desc: 'Call an external API' },
  { value: 'APPROVAL', label: 'Approval', desc: 'Require approval before proceeding' },
  { value: 'CONDITIONAL', label: 'Conditional', desc: 'Branch based on conditions' },
  { value: 'NOTIFICATION', label: 'Notification', desc: 'Send alert/email' },
  { value: 'MANUAL_REVIEW', label: 'Manual Review', desc: 'Officer review required' },
  { value: 'DELAY', label: 'Delay', desc: 'Wait for a specified time' },
];

const WorkflowBuilder = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [workflow, setWorkflow] = useState(null);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showStepModal, setShowStepModal] = useState(false);
  const [editingStep, setEditingStep] = useState(null);
  const [stepForm, setStepForm] = useState({
    step_type: 'SERVICE', name: '', service_id: '', order: 0,
    timeout_seconds: 30, requires_approval: false,
    is_repeatable: false, min_repetitions: 1, max_repetitions: 1,
    conditions: {}, config: {}, approver_roles: []
  });

  useEffect(() => {
    fetchWorkflow();
    api.get('/services/').then(r => setServices(r.data));
  }, [id]);

  const fetchWorkflow = async () => {
    try {
      const res = await api.get(`/workflows/${id}/`);
      setWorkflow(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveStep = async () => {
    try {
      if (editingStep) {
        await api.patch(`/workflows/${id}/steps/${editingStep.id}/`, stepForm);
      } else {
        await api.post(`/workflows/${id}/steps/`, stepForm);
      }
      setShowStepModal(false);
      setEditingStep(null);
      fetchWorkflow();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to save step');
    }
  };

  const handleDeleteStep = async (stepId) => {
    if (!confirm('Delete this step?')) return;
    try {
      await api.delete(`/workflows/${id}/steps/${stepId}/`);
      fetchWorkflow();
    } catch (err) {
      alert('Failed to delete step');
    }
  };

  const handleReorder = async (stepId, direction) => {
    const steps = [...workflow.steps];
    const idx = steps.findIndex(s => s.id === stepId);
    if (direction === 'up' && idx > 0) {
      [steps[idx], steps[idx - 1]] = [steps[idx - 1], steps[idx]];
    } else if (direction === 'down' && idx < steps.length - 1) {
      [steps[idx], steps[idx + 1]] = [steps[idx + 1], steps[idx]];
    }
    const stepOrders = steps.map((s, i) => ({ id: s.id, order: i + 1 }));
    try {
      await api.post(`/workflows/${id}/steps/reorder/`, { step_orders: stepOrders });
      fetchWorkflow();
    } catch (err) {
      alert('Failed to reorder');
    }
  };

  const openAddStep = () => {
    setEditingStep(null);
    setStepForm({
      step_type: 'SERVICE', name: '', service_id: '', order: (workflow.steps?.length || 0) + 1,
      timeout_seconds: 30, requires_approval: false,
      is_repeatable: false, min_repetitions: 1, max_repetitions: 1,
      conditions: {}, config: {}, approver_roles: []
    });
    setShowStepModal(true);
  };

  const openEditStep = (step) => {
    setEditingStep(step);
    setStepForm({
      step_type: step.step_type,
      name: step.name || '',
      service_id: step.service?.id || '',
      order: step.order,
      timeout_seconds: step.timeout_seconds || 30,
      requires_approval: step.requires_approval || false,
      is_repeatable: step.is_repeatable || false,
      min_repetitions: step.min_repetitions || 1,
      max_repetitions: step.max_repetitions || 1,
      conditions: step.conditions || {},
      config: step.config || {},
      approver_roles: step.approver_roles || []
    });
    setShowStepModal(true);
  };

  if (loading) return <Loading />;
  if (!workflow) return <div className="text-[var(--text-muted)]">Workflow not found</div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/workflows')} className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="page-title">{workflow.name}</h1>
            <Badge status={workflow.status} />
          </div>
          <p className="text-sm text-[var(--text-muted)]">{workflow.agency?.name} · {workflow.steps?.length || 0} steps</p>
        </div>
        <button onClick={openAddStep} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Step
        </button>
      </div>

      {workflow.status === 'PUBLISHED' && (
        <div className="p-3 rounded-lg bg-warning/10 border border-warning/20 text-sm text-warning flex items-center gap-2">
          <Settings className="w-4 h-4" />
          This workflow is published. Changes will create a new version.
        </div>
      )}

      <div className="space-y-3">
        {(workflow.steps || []).sort((a, b) => a.order - b.order).map((step, idx) => (
          <div key={step.id} className="glass-panel p-4 flex items-center gap-4">
            <div className="flex flex-col gap-1">
              <button onClick={() => handleReorder(step.id, 'up')} disabled={idx === 0} className="p-1 hover:bg-[var(--bg-input)] rounded disabled:opacity-30">
                <ArrowUp className="w-3 h-3 text-[var(--text-muted)]" />
              </button>
              <span className="text-xs font-mono text-[var(--text-muted)] text-center">{step.order}</span>
              <button onClick={() => handleReorder(step.id, 'down')} disabled={idx === workflow.steps.length - 1} className="p-1 hover:bg-[var(--bg-input)] rounded disabled:opacity-30">
                <ArrowDown className="w-3 h-3 text-[var(--text-muted)]" />
              </button>
            </div>

            <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-bold text-accent">{step.step_type?.slice(0, 2)}</span>
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h4 className="font-medium text-[var(--text-primary)]">{step.name || step.step_type}</h4>
                {step.is_repeatable && <Badge status="ACTIVE" text="Repeatable" />}
                {step.requires_approval && <Badge status="WARNING" text="Approval" />}
              </div>
              <p className="text-xs text-[var(--text-muted)]">
                {step.service?.name ? `${step.service.name} · ` : ''}{step.step_type}
                {step.step_type === 'SERVICE' && step.service?.full_url && ` · ${step.service.full_url}`}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button onClick={() => openEditStep(step)} className="p-2 hover:bg-[var(--bg-input)] rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
                <Settings className="w-4 h-4" />
              </button>
              <button onClick={() => handleDeleteStep(step.id)} className="p-2 hover:bg-danger/10 rounded-lg text-[var(--text-muted)] hover:text-danger transition-colors">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}

        {workflow.steps?.length === 0 && (
          <div className="text-center py-12 border-2 border-dashed border-[var(--border-color)] rounded-xl">
            <p className="text-[var(--text-muted)] mb-3">No steps defined yet</p>
            <button onClick={openAddStep} className="btn-primary inline-flex items-center gap-2">
              <Plus className="w-4 h-4" /> Add First Step
            </button>
          </div>
        )}
      </div>

      <Modal isOpen={showStepModal} onClose={() => { setShowStepModal(false); setEditingStep(null); }} title={editingStep ? 'Edit Step' : 'Add Step'} size="lg">
        <div className="space-y-4 max-h-[70vh] overflow-y-auto no-scrollbar pr-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Step Type *</label>
              <select className="input-field" value={stepForm.step_type} onChange={e => setStepForm({...stepForm, step_type: e.target.value})}>
                {STEP_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Step Name *</label>
              <input className="input-field" value={stepForm.name} onChange={e => setStepForm({...stepForm, name: e.target.value})} placeholder="e.g. Verify Director Identity" required />
            </div>
          </div>

          {stepForm.step_type === 'SERVICE' && (
            <div>
              <label className="label">Linked Service</label>
              <select className="input-field" value={stepForm.service_id} onChange={e => setStepForm({...stepForm, service_id: e.target.value})}>
                <option value="">Select service...</option>
                {services.map(s => <option key={s.id} value={s.id}>{s.name} ({s.agency_code})</option>)}
              </select>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Order</label>
              <input type="number" className="input-field" value={stepForm.order} onChange={e => setStepForm({...stepForm, order: parseInt(e.target.value)})} />
            </div>
            <div>
              <label className="label">Timeout (s)</label>
              <input type="number" className="input-field" value={stepForm.timeout_seconds} onChange={e => setStepForm({...stepForm, timeout_seconds: parseInt(e.target.value)})} />
            </div>
          </div>

          <div className="flex items-center gap-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 rounded border-[var(--border-color)] text-accent" checked={stepForm.requires_approval} onChange={e => setStepForm({...stepForm, requires_approval: e.target.checked})} />
              <span className="text-sm text-[var(--text-secondary)]">Requires Approval</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 rounded border-[var(--border-color)] text-accent" checked={stepForm.is_repeatable} onChange={e => setStepForm({...stepForm, is_repeatable: e.target.checked})} />
              <span className="text-sm text-[var(--text-secondary)]">Repeatable (multiple records)</span>
            </label>
          </div>

          {stepForm.is_repeatable && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Min Repetitions</label>
                <input type="number" className="input-field" value={stepForm.min_repetitions} onChange={e => setStepForm({...stepForm, min_repetitions: parseInt(e.target.value)})} />
              </div>
              <div>
                <label className="label">Max Repetitions (0 = unlimited)</label>
                <input type="number" className="input-field" value={stepForm.max_repetitions} onChange={e => setStepForm({...stepForm, max_repetitions: parseInt(e.target.value)})} />
              </div>
            </div>
          )}

          <div>
            <label className="label">Config (JSON)</label>
            <textarea className="input-field font-mono text-xs" rows={4} value={JSON.stringify(stepForm.config, null, 2)} onChange={e => { try { setStepForm({...stepForm, config: JSON.parse(e.target.value)}); } catch {} }} />
          </div>

          <div className="flex justify-end gap-3">
            <button onClick={() => setShowStepModal(false)} className="btn-secondary">Cancel</button>
            <button onClick={handleSaveStep} className="btn-primary flex items-center gap-2">
              <Save className="w-4 h-4" /> Save Step
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default WorkflowBuilder;
