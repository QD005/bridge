import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Play, Globe, Activity, Clock, Code, Plus, Trash2,
  Save, Eye, Zap, CheckCircle, AlertTriangle, Hash, Type, Calendar,
  Mail, Phone, FileText, ToggleLeft, Shield
} from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Badge from '../components/Badge';
import Modal from '../components/Modal';
import DynamicForm from '../components/DynamicForm';

const FIELD_TYPES = [
  { value: 'text', label: 'Text', icon: Type },
  { value: 'number', label: 'Number', icon: Hash },
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'date', label: 'Date', icon: Calendar },
  { value: 'select', label: 'Select', icon: ToggleLeft },
  { value: 'textarea', label: 'Textarea', icon: FileText },
  { value: 'file', label: 'File', icon: FileText },
  { value: 'checkbox', label: 'Checkbox', icon: CheckCircle },
  { value: 'phone', label: 'Phone', icon: Phone },
  { value: 'password', label: 'Password', icon: Shield },
];

const LOCATIONS = [
  { value: 'query', label: 'Query Parameter' },
  { value: 'body', label: 'Request Body' },
  { value: 'header', label: 'HTTP Header' },
  { value: 'path', label: 'URL Path' },
];

const ServiceDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [service, setService] = useState(null);
  const [schema, setSchema] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('details');

  // Field builder state
  const [showFieldModal, setShowFieldModal] = useState(false);
  const [editingField, setEditingField] = useState(null);
  const [fieldForm, setFieldForm] = useState({
    name: '', label: '', field_type: 'text', required: false, location: 'query',
    placeholder: '', help_text: '', default_value: '',
    validation_regex: '', min_length: '', max_length: '',
    options: '', order: 0, is_sensitive: false
  });

  // Preview / Execute state
  const [previewValues, setPreviewValues] = useState({});
  const [previewResult, setPreviewResult] = useState(null);
  const [executeResult, setExecuteResult] = useState(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => { fetchData(); }, [id]);

  const fetchData = async () => {
    try {
      const [sRes, schemaRes] = await Promise.all([
        api.get(`/services/${id}/`),
        api.get(`/services/${id}/schema/`)
      ]);
      setService(sRes.data);
      setSchema(schemaRes.data);
      // Init preview values from schema
      const init = {};
      schemaRes.data.fields?.forEach(f => init[f.name] = f.default_value || '');
      setPreviewValues(init);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleSaveField = async () => {
    try {
      const payload = {
        ...fieldForm,
        options: fieldForm.options ? fieldForm.options.split(',').map(s => s.trim()) : []
      };
      if (editingField) {
        await api.patch(`/services/${id}/fields/${editingField.id}/`, payload);
      } else {
        await api.post(`/services/${id}/fields/`, payload);
      }
      setShowFieldModal(false);
      setEditingField(null);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Failed to save field');
    }
  };

  const handleDeleteField = async (fieldId) => {
    if (!confirm('Delete this field?')) return;
    try {
      await api.delete(`/services/${id}/fields/${fieldId}/`);
      fetchData();
    } catch (err) { alert('Failed to delete field'); }
  };

  const openAddField = () => {
    setEditingField(null);
    setFieldForm({
      name: '', label: '', field_type: 'text', required: false, location: 'query',
      placeholder: '', help_text: '', default_value: '',
      validation_regex: '', min_length: '', max_length: '',
      options: '', order: (service.service_fields?.length || 0) + 1, is_sensitive: false
    });
    setShowFieldModal(true);
  };

  const openEditField = (field) => {
    setEditingField(field);
    setFieldForm({
      name: field.name || '',
      label: field.label || '',
      field_type: field.field_type || 'text',
      required: !!field.required,
      location: field.location || 'query',
      placeholder: field.placeholder || '',
      help_text: field.help_text || '',
      default_value: field.default_value || '',
      validation_regex: field.validation_regex || '',
      min_length: field.min_length || '',
      max_length: field.max_length || '',
      options: Array.isArray(field.options) ? field.options.join(', ') : '',
      order: field.order || 0,
      is_sensitive: !!field.is_sensitive
    });
    setShowFieldModal(true);
  };

  const handlePreview = async () => {
    setTesting(true);
    try {
      const res = await api.post(`/services/${id}/preview/`, { raw_values: previewValues });
      setPreviewResult(res.data);
      setExecuteResult(null);
    } catch (err) {
      setPreviewResult({ error: err.response?.data?.detail || err.response?.data?.errors || 'Preview failed' });
    } finally { setTesting(false); }
  };

  const handleExecute = async () => {
    setTesting(true);
    try {
      const res = await api.post(`/services/${id}/execute/`, { raw_values: previewValues });
      setExecuteResult(res.data);
      setPreviewResult(null);
    } catch (err) {
      setExecuteResult({ error: err.response?.data?.detail || err.response?.data?.errors || 'Execution failed' });
    } finally { setTesting(false); }
  };

  if (loading) return <Loading />;
  if (!service) return <div className="text-[var(--text-muted)]">Service not found</div>;

  const fields = service.service_fields || [];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/services')} className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="page-title">{service.name}</h1>
            <Badge status={service.status} />
          </div>
          <p className="text-sm text-[var(--text-muted)]">{service.agency?.name} · {service.http_method} {service.full_url}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-[var(--border-color)]">
        {[
          { id: 'details', label: 'Details', icon: Globe },
          { id: 'fields', label: `Fields (${fields.length})`, icon: Hash },
          { id: 'preview', label: 'Preview & Test', icon: Eye },
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-accent text-accent'
                  : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-primary)]'
              }`}
            >
              <Icon className="w-4 h-4" /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* DETAILS TAB */}
      {activeTab === 'details' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="glass-panel p-5">
              <h3 className="section-title mb-3">Service Details</h3>
              <p className="text-sm text-[var(--text-secondary)] mb-4">{service.description || 'No description.'}</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                  <p className="text-xs text-[var(--text-muted)] mb-1">Endpoint</p>
                  <p className="font-mono text-[var(--text-primary)] break-all">{service.full_url}</p>
                </div>
                <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                  <p className="text-xs text-[var(--text-muted)] mb-1">Method</p>
                  <p className="font-mono text-[var(--text-primary)]">{service.http_method}</p>
                </div>
                <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                  <p className="text-xs text-[var(--text-muted)] mb-1">Timeout</p>
                  <p className="text-[var(--text-primary)]">{service.timeout_seconds}s</p>
                </div>
                <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                  <p className="text-xs text-[var(--text-muted)] mb-1">Version</p>
                  <p className="text-[var(--text-primary)]">{service.version || 'v1'}</p>
                </div>
              </div>
            </div>

            <div className="glass-panel p-5">
              <h3 className="section-title mb-3">Request Schema (Legacy)</h3>
              <pre className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-input)] p-3 rounded-lg overflow-auto max-h-48 no-scrollbar">
                {JSON.stringify(service.request_schema || {}, null, 2)}
              </pre>
            </div>
          </div>

          <div className="space-y-4">
            <div className="glass-panel p-5">
              <h3 className="section-title mb-3">Health</h3>
              <div className="flex items-center gap-2 mb-3">
                <Activity className={`w-5 h-5 ${service.health_status === 'ONLINE' ? 'text-success' : service.health_status === 'DEGRADED' ? 'text-warning' : 'text-danger'}`} />
                <span className="font-medium text-[var(--text-primary)]">{service.health_status}</span>
              </div>
            </div>
            <div className="glass-panel p-5">
              <h3 className="section-title mb-3">Auth Config</h3>
              <pre className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-input)] p-3 rounded-lg overflow-auto max-h-48 no-scrollbar">
                {JSON.stringify(service.agency?.auth_config || {}, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* FIELDS TAB */}
      {activeTab === 'fields' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-[var(--text-primary)]">Field Definitions</h3>
              <p className="text-sm text-[var(--text-muted)]">Define how the frontend collects data and where each field goes in the HTTP request.</p>
            </div>
            <button onClick={openAddField} className="btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4" /> Add Field
            </button>
          </div>

          {fields.length === 0 && (
            <div className="glass-panel p-8 text-center text-[var(--text-muted)] border-2 border-dashed border-[var(--border-color)]">
              <Hash className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p>No fields defined yet. Add fields so the frontend can auto-generate forms.</p>
            </div>
          )}

          <div className="space-y-2">
            {fields.sort((a, b) => (a.order || 0) - (b.order || 0)).map(field => (
              <div key={field.id} className="glass-panel p-4 flex items-center gap-4">
                <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center text-accent font-bold text-xs">
                  {field.order}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-[var(--text-primary)]">{field.label || field.name}</span>
                    <span className="text-xs font-mono text-[var(--text-muted)] bg-[var(--bg-input)] px-2 py-0.5 rounded border border-[var(--border-color)]">{field.name}</span>
                    {field.required && <Badge status="ACTIVE" text="Required" />}
                    {field.is_sensitive && <Badge status="WARNING" text="Sensitive" />}
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-[var(--text-muted)]">
                    <span className="flex items-center gap-1"><Type className="w-3 h-3" /> {field.field_type}</span>
                    <span className="flex items-center gap-1"><Globe className="w-3 h-3" /> {field.location}</span>
                    {field.validation_regex && <span className="font-mono">regex</span>}
                    {field.min_length && <span>min:{field.min_length}</span>}
                    {field.max_length && <span>max:{field.max_length}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => openEditField(field)} className="p-2 hover:bg-[var(--bg-input)] rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
                    <Code className="w-4 h-4" />
                  </button>
                  <button onClick={() => handleDeleteField(field.id)} className="p-2 hover:bg-danger/10 rounded-lg text-[var(--text-muted)] hover:text-danger transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PREVIEW & TEST TAB */}
      {activeTab === 'preview' && schema && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="glass-panel p-5">
              <h3 className="section-title mb-3 flex items-center gap-2">
                <Eye className="w-4 h-4" /> Test Form (Auto-Generated)
              </h3>
              <p className="text-xs text-[var(--text-muted)] mb-4">
                This is exactly how the form will appear to Operations Officers. Fill values and preview the HTTP request.
              </p>
              <DynamicForm
                fields={schema.fields?.map(f => ({
                  name: f.name,
                  label: f.label,
                  type: f.type,
                  required: f.required,
                  placeholder: f.placeholder,
                  help_text: f.help_text,
                  validation_regex: f.validation_regex,
                  min_length: f.min_length,
                  max_length: f.max_length,
                  options: f.options,
                  order: f.order,
                })) || []}
                data={previewValues}
                onChange={setPreviewValues}
              />
              <div className="flex gap-3 mt-6 pt-4 border-t border-[var(--border-color)]">
                <button onClick={handlePreview} disabled={testing} className="btn-secondary flex items-center gap-2 flex-1 justify-center">
                  <Eye className="w-4 h-4" /> {testing ? 'Building...' : 'Preview Request'}
                </button>
                <button onClick={handleExecute} disabled={testing} className="btn-primary flex items-center gap-2 flex-1 justify-center">
                  <Zap className="w-4 h-4" /> {testing ? 'Executing...' : 'Execute'}
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {previewResult && !previewResult.error && (
              <div className="glass-panel p-5">
                <h3 className="section-title mb-3 flex items-center gap-2">
                  <Code className="w-4 h-4" /> Request Preview
                </h3>
                <pre className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-input)] p-3 rounded-lg overflow-auto max-h-96 no-scrollbar whitespace-pre-wrap">
                  {previewResult.preview}
                </pre>
              </div>
            )}

            {previewResult?.error && (
              <div className="glass-panel p-5 border-l-2 border-l-danger">
                <h3 className="section-title mb-3 text-danger flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" /> Preview Error
                </h3>
                <pre className="text-xs font-mono text-danger bg-danger/5 p-3 rounded-lg overflow-auto max-h-48 no-scrollbar">
                  {typeof previewResult.error === 'string' ? previewResult.error : JSON.stringify(previewResult.error, null, 2)}
                </pre>
              </div>
            )}

            {executeResult && !executeResult.error && (
              <div className="space-y-4">
                <div className="glass-panel p-5">
                  <h3 className="section-title mb-3 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-success" /> Execution Result
                  </h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-[var(--text-muted)]">Status:</span>
                      <Badge status={executeResult.health_status || 'ONLINE'} text={executeResult.response?.status_code?.toString()} />
                      <span className="text-[var(--text-muted)]">{executeResult.response?.response_time_ms}ms</span>
                    </div>
                    <div>
                      <p className="text-xs text-[var(--text-muted)] mb-1">Request Built</p>
                      <pre className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-input)] p-3 rounded-lg overflow-auto max-h-40 no-scrollbar">
                        {JSON.stringify(executeResult.request_built, null, 2)}
                      </pre>
                    </div>
                    <div>
                      <p className="text-xs text-[var(--text-muted)] mb-1">Response Body</p>
                      <pre className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-input)] p-3 rounded-lg overflow-auto max-h-60 no-scrollbar">
                        {JSON.stringify(executeResult.response?.body, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {executeResult?.error && (
              <div className="glass-panel p-5 border-l-2 border-l-danger">
                <h3 className="section-title mb-3 text-danger flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" /> Execution Error
                </h3>
                <pre className="text-xs font-mono text-danger bg-danger/5 p-3 rounded-lg overflow-auto max-h-48 no-scrollbar">
                  {typeof executeResult.error === 'string' ? executeResult.error : JSON.stringify(executeResult.error, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}

      {/* FIELD MODAL */}
      <Modal isOpen={showFieldModal} onClose={() => { setShowFieldModal(false); setEditingField(null); }}
        title={editingField ? 'Edit Field' : 'Add Field'} size="lg">
        <div className="space-y-4 max-h-[70vh] overflow-y-auto no-scrollbar pr-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Field Name (technical key) *</label>
              <input className="input-field" value={fieldForm.name} onChange={e => setFieldForm({...fieldForm, name: e.target.value})}
                placeholder="e.g. nin, tin, company_name" required />
            </div>
            <div>
              <label className="label">Display Label *</label>
              <input className="input-field" value={fieldForm.label} onChange={e => setFieldForm({...fieldForm, label: e.target.value})}
                placeholder="e.g. National ID Number" required />
            </div>
            <div>
              <label className="label">Field Type</label>
              <select className="input-field" value={fieldForm.field_type} onChange={e => setFieldForm({...fieldForm, field_type: e.target.value})}>
                {FIELD_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Location (where it goes in HTTP request) *</label>
              <select className="input-field" value={fieldForm.location} onChange={e => setFieldForm({...fieldForm, location: e.target.value})}>
                {LOCATIONS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
              </select>
              <p className="text-xs text-[var(--text-muted)] mt-1">query=URL params, body=JSON payload, header=HTTP header, path=URL segment</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Placeholder</label>
              <input className="input-field" value={fieldForm.placeholder} onChange={e => setFieldForm({...fieldForm, placeholder: e.target.value})}
                placeholder="e.g. CM1234567890AB" />
            </div>
            <div>
              <label className="label">Default Value</label>
              <input className="input-field" value={fieldForm.default_value} onChange={e => setFieldForm({...fieldForm, default_value: e.target.value})} />
            </div>
          </div>

          <div>
            <label className="label">Help Text (shown below field)</label>
            <input className="input-field" value={fieldForm.help_text} onChange={e => setFieldForm({...fieldForm, help_text: e.target.value})}
              placeholder="e.g. Enter the 14-character NIN from the NIRA card" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="label">Validation Regex</label>
              <input className="input-field font-mono text-xs" value={fieldForm.validation_regex} onChange={e => setFieldForm({...fieldForm, validation_regex: e.target.value})}
                placeholder="^CM[0-9]{10}[A-Z]{2}$" />
            </div>
            <div>
              <label className="label">Min Length</label>
              <input type="number" className="input-field" value={fieldForm.min_length} onChange={e => setFieldForm({...fieldForm, min_length: e.target.value})} />
            </div>
            <div>
              <label className="label">Max Length</label>
              <input type="number" className="input-field" value={fieldForm.max_length} onChange={e => setFieldForm({...fieldForm, max_length: e.target.value})} />
            </div>
          </div>

          {fieldForm.field_type === 'select' && (
            <div>
              <label className="label">Options (comma-separated)</label>
              <input className="input-field" value={fieldForm.options} onChange={e => setFieldForm({...fieldForm, options: e.target.value})}
                placeholder="Option 1, Option 2, Option 3" />
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Order</label>
              <input type="number" className="input-field" value={fieldForm.order} onChange={e => setFieldForm({...fieldForm, order: parseInt(e.target.value) || 0})} />
            </div>
          </div>

          <div className="flex items-center gap-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 rounded border-[var(--border-color)] text-accent"
                checked={fieldForm.required} onChange={e => setFieldForm({...fieldForm, required: e.target.checked})} />
              <span className="text-sm text-[var(--text-secondary)]">Required field</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 rounded border-[var(--border-color)] text-accent"
                checked={fieldForm.is_sensitive} onChange={e => setFieldForm({...fieldForm, is_sensitive: e.target.checked})} />
              <span className="text-sm text-[var(--text-secondary)]">Sensitive (masked in logs)</span>
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button onClick={() => setShowFieldModal(false)} className="btn-secondary">Cancel</button>
            <button onClick={handleSaveField} className="btn-primary flex items-center gap-2">
              <Save className="w-4 h-4" /> {editingField ? 'Update Field' : 'Save Field'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ServiceDetail;