import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Play, CheckCircle, XCircle, Clock, AlertTriangle,
  RotateCcw, Send, FileCheck, ChevronRight, ChevronDown, ChevronUp,
  User, Building2, Hash, Plus, Check, Ban, Code, Eye
} from 'lucide-react';
import api from '../api/axios';
import Badge from '../components/Badge';
import Loading from '../components/Loading';
import Modal from '../components/Modal';
import DynamicForm from '../components/DynamicForm';
import { useWebSocket } from '../hooks/useWebSocket';

const RequestDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeStep, setActiveStep] = useState(null);
  const [submitModal, setSubmitModal] = useState(false);
  const [submitData, setSubmitData] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [completeNotes, setCompleteNotes] = useState('');
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [expandedSteps, setExpandedSteps] = useState({});
  const [stepSchemas, setStepSchemas] = useState({});
  const { messages } = useWebSocket(parseInt(id));

  useEffect(() => { fetchRequest(); }, [id]);
  useEffect(() => { if (messages.length > 0) fetchRequest(); }, [messages]);

  const fetchRequest = async () => {
    try {
      const res = await api.get(`/executions/${id}/`);
      setRequest(res.data);

      const schemas = {};
      for (const step of res.data.steps || []) {
        if (step.service?.id) {
          try {
            const sRes = await api.get(`/services/${step.service.id}/schema/`);
            schemas[step.id] = sRes.data;
          } catch (e) {
            console.log('No schema for step', step.id);
          }
        }
      }
      setStepSchemas(schemas);

      const expand = {};
      res.data.steps?.forEach(s => {
        if (['RUNNING', 'FAILED', 'WAITING', 'IN_PROGRESS'].includes(s.status)) expand[s.id] = true;
      });
      setExpandedSteps(prev => ({ ...prev, ...expand }));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (stepId) => {
    setExpandedSteps(prev => ({ ...prev, [stepId]: !prev[stepId] }));
  };

  const openSubmit = (step, prefillData = null) => {
    setActiveStep(step);
    const schema = stepSchemas[step.id];
    const initial = {};

    if (prefillData) {
      Object.assign(initial, prefillData);
    } else if (schema?.fields) {
      schema.fields.forEach(f => {
        initial[f.name] = request.payload?.[f.name] || f.default_value || '';
      });
    }

    setSubmitData(initial);
    setSubmitModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!activeStep) return;
    setSubmitting(true);
    try {
      await api.post(`/executions/${id}/steps/${activeStep.id}/submit/`, {
        payload: submitData,
      });
      setSubmitModal(false);
      setSubmitData({});
      setActiveStep(null);
      fetchRequest();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.response?.data?.errors || 'Submission failed';
      alert(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg, null, 2));
    } finally {
      setSubmitting(false);
    }
  };

  const handleCompleteStep = async (stepId) => {
    try {
      await api.post(`/executions/${id}/steps/${stepId}/complete/`, { notes: completeNotes });
      setShowCompleteModal(false);
      setCompleteNotes('');
      fetchRequest();
    } catch (err) { alert(err.response?.data?.detail || 'Failed to complete step'); }
  };

  const handleFinalComplete = async () => {
    if (!confirm('Issue final certificate and complete this request?')) return;
    try {
      await api.post(`/executions/${id}/complete/`);
      fetchRequest();
    } catch (err) { alert(err.response?.data?.detail || 'Completion failed'); }
  };

  const handleReject = async () => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;
    try {
      await api.post(`/executions/${id}/reject/`, { reason });
      fetchRequest();
    } catch (err) { alert(err.response?.data?.detail || 'Rejection failed'); }
  };

  const handleCancel = async () => {
    if (!confirm('Cancel this request?')) return;
    try {
      await api.post(`/executions/${id}/cancel/`);
      fetchRequest();
    } catch (err) { alert(err.response?.data?.detail || 'Cancel failed'); }
  };

  const getStepIcon = (status) => {
    switch (status) {
      case 'COMPLETED': return <CheckCircle className="w-5 h-5 lg:w-6 lg:h-6 text-success" />;
      case 'FAILED': return <XCircle className="w-5 h-5 lg:w-6 lg:h-6 text-danger" />;
      case 'IN_PROGRESS': return <Clock className="w-5 h-5 lg:w-6 lg:h-6 text-info animate-pulse" />;
      case 'WAITING': return <AlertTriangle className="w-5 h-5 lg:w-6 lg:h-6 text-warning" />;
      case 'SKIPPED': return <ChevronRight className="w-5 h-5 lg:w-6 lg:h-6 text-[var(--text-muted)]" />;
      default: return <div className="w-5 h-5 lg:w-6 lg:h-6 rounded-full border-2 border-[var(--border-color)]" />;
    }
  };

  if (loading) return <Loading />;
  if (!request) return <div className="text-[var(--text-muted)]">Request not found</div>;

  const allSteps = request.steps || [];
  const completedCount = allSteps.filter(s => s.status === 'COMPLETED').length;
  const allCompleted = allSteps.length > 0 && allSteps.every(s => s.status === 'COMPLETED' || s.status === 'SKIPPED');
  const isPending = request.status === 'PENDING' || request.status === 'IN_PROGRESS';

  return (
    <div className="flex flex-col gap-4 lg:gap-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 lg:gap-4">
        <button onClick={() => navigate('/requests')} className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors flex-shrink-0">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 flex-wrap">
            <h1 className="page-title text-lg lg:text-2xl truncate">{request.workflow?.name}</h1>
            <Badge status={request.status} />
          </div>
          <p className="text-xs lg:text-sm text-[var(--text-muted)]">
            Request #{request.id} · {request.workflow?.agency?.name} · {request.applicant_name || 'No applicant name'}
          </p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-auto">
          {isPending && (
            <button onClick={handleCancel} className="btn-danger text-xs lg:text-sm flex items-center gap-1.5 py-1.5 px-3">
              <Ban className="w-3.5 h-3.5" /> Cancel
            </button>
          )}
        </div>
      </div>

      {/* Applicant Info */}
      <div className="glass-panel p-4 lg:p-5">
        <h3 className="section-title mb-3">Applicant Information</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 lg:gap-4">
          <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
            <p className="text-xs text-[var(--text-muted)] uppercase">Name</p>
            <p className="text-sm font-medium text-[var(--text-primary)] mt-0.5 flex items-center gap-2">
              <User className="w-3.5 h-3.5 text-[var(--text-muted)]" /> {request.applicant_name || 'N/A'}
            </p>
          </div>
          <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
            <p className="text-xs text-[var(--text-muted)] uppercase">Contact</p>
            <p className="text-sm font-medium text-[var(--text-primary)] mt-0.5">{request.applicant_contact || 'N/A'}</p>
          </div>
          <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
            <p className="text-xs text-[var(--text-muted)] uppercase">Initiated By</p>
            <p className="text-sm font-medium text-[var(--text-primary)] mt-0.5">
              {request.initiated_by?.first_name} {request.initiated_by?.last_name}
            </p>
          </div>
        </div>
        {Object.keys(request.payload || {}).length > 0 && (
          <div className="mt-4 pt-4 border-t border-[var(--border-color)]">
            <p className="text-xs text-[var(--text-muted)] mb-2">Application Data</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 lg:gap-3">
              {Object.entries(request.payload).map(([key, value]) => (
                <div key={key} className="p-2 rounded bg-[var(--bg-input)]">
                  <p className="text-[10px] text-[var(--text-muted)] uppercase">{key.replace(/_/g, ' ')}</p>
                  <p className="text-xs font-mono text-[var(--text-primary)] truncate">{String(value)}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Progress */}
      <div className="glass-panel p-4 lg:p-5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="section-title">Progress</h3>
          <span className="text-xs lg:text-sm text-[var(--text-muted)]">{completedCount} of {allSteps.length} steps completed</span>
        </div>
        <div className="w-full h-2 lg:h-2.5 bg-[var(--bg-input)] rounded-full overflow-hidden">
          <div className="h-full bg-accent rounded-full transition-all duration-700"
            style={{ width: `${allSteps.length ? (completedCount / allSteps.length) * 100 : 0}%` }} />
        </div>
      </div>

      {/* Steps */}
      <div className="flex flex-col gap-3">
        <h3 className="section-title">Workflow Steps</h3>
        {allSteps.map((step, idx) => {
          const isExpanded = expandedSteps[step.id];
          const isCompleted = step.status === 'COMPLETED';
          const canSubmit = !isCompleted && (
            step.status === 'PENDING' ||
            step.status === 'FAILED' ||
            (step.is_repeatable && step.status === 'IN_PROGRESS')
          );
          const canComplete = !isCompleted && step.submissions?.some(s => s.status === 'SUCCESS');
          const isRepeatable = step.is_repeatable;
          const subCount = step.submissions?.length || 0;
          const schema = stepSchemas[step.id];
          const hasSchema = schema && schema.fields?.length > 0;

          return (
            <div key={step.id}
              className={`glass-panel overflow-hidden transition-all ${
                step.status === 'COMPLETED' ? 'border-l-2 border-l-success' :
                step.status === 'FAILED' ? 'border-l-2 border-l-danger' :
                step.status === 'IN_PROGRESS' ? 'border-l-2 border-l-info' :
                step.status === 'WAITING' ? 'border-l-2 border-l-warning' : ''
              }`}>
              {/* Step Header */}
              <div className="p-3 lg:p-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 cursor-pointer hover:bg-[var(--bg-input)] transition-colors"
                onClick={() => toggleExpand(step.id)}>
                <div className="flex items-center gap-3 sm:gap-4 flex-1 min-w-0">
                  <div className="flex-shrink-0">{getStepIcon(step.status)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs text-[var(--text-muted)] font-mono">Step {step.order}</span>
                      <h4 className="font-medium text-[var(--text-primary)] text-sm lg:text-base">{step.step_name || step.step_type}</h4>
                      <Badge status={step.status} />
                      {isRepeatable && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-accent/10 text-accent border border-accent/20">
                          {subCount} submission{subCount !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                    {step.service_name && (
                      <p className="text-xs text-[var(--text-muted)] mt-0.5 truncate">
                        via {step.service_name} {step.service?.agency_name && `· ${step.service.agency_name}`}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2 self-end sm:self-auto flex-shrink-0">
                  {canSubmit && (
                    <button onClick={e => { e.stopPropagation(); openSubmit(step); }}
                      className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5">
                      <Play className="w-3.5 h-3.5" />
                      {step.status === 'FAILED' ? 'Retry' : (isRepeatable ? 'Add Record' : 'Submit')}
                    </button>
                  )}
                  {canComplete && (
                    <button onClick={e => { e.stopPropagation(); setActiveStep(step); setShowCompleteModal(true); }}
                      className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5 bg-success hover:bg-success/80">
                      <Check className="w-3.5 h-3.5" /> Complete
                    </button>
                  )}
                  {isExpanded ? <ChevronUp className="w-5 h-5 text-[var(--text-muted)]" /> : <ChevronDown className="w-5 h-5 text-[var(--text-muted)]" />}
                </div>
              </div>

              {/* Expanded Details */}
              {isExpanded && (
                <div className="px-3 lg:px-4 pb-3 lg:pb-4 border-t border-[var(--border-color)]">
                  {hasSchema && (
                    <div className="mt-3 p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                      <p className="text-xs text-[var(--text-muted)] mb-2 flex items-center gap-1.5">
                        <Code className="w-3 h-3" /> Service Schema · {schema.http_method} {schema.endpoint_url}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {schema.fields.map(f => (
                          <span key={f.name} className="text-xs px-2 py-1 rounded bg-[var(--bg-primary)] border border-[var(--border-color)] text-[var(--text-secondary)]">
                            {f.label || f.name} <span className="text-[var(--text-muted)]">({f.location})</span>
                            {f.required && <span className="text-danger ml-1">*</span>}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Submissions */}
                  {step.submissions?.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">Submissions</p>
                      {step.submissions.map((sub, i) => (
                        <div key={sub.id} className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-2 gap-2">
                            <span className="text-xs font-medium text-[var(--text-primary)]">Record #{i + 1}</span>
                            <div className="flex items-center gap-2">
                              <Badge status={sub.status === 'SUCCESS' ? 'COMPLETED' : sub.status} text={sub.status} />
                              {sub.status === 'FAILED' && (
                                <button
                                  onClick={() => openSubmit(step, sub.submission_data)}
                                  className="text-xs px-2 py-1 rounded bg-warning/10 text-warning border border-warning/20 hover:bg-warning/20 transition-colors flex items-center gap-1"
                                >
                                  <RotateCcw className="w-3 h-3" /> Edit & Retry
                                </button>
                              )}
                            </div>
                          </div>
                          {sub.submission_data && Object.keys(sub.submission_data).length > 0 && (
                            <div className="mb-2">
                              <p className="text-[10px] text-[var(--text-muted)] uppercase mb-1">Submitted Data</p>
                              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                {Object.entries(sub.submission_data).map(([k, v]) => (
                                  <div key={k} className="p-1.5 rounded bg-[var(--bg-primary)]">
                                    <p className="text-[10px] text-[var(--text-muted)]">{k.replace(/_/g, ' ')}</p>
                                    <p className="text-xs font-mono text-[var(--text-primary)] truncate">{String(v)}</p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          {sub.response_data && Object.keys(sub.response_data).length > 0 && (
                            <div>
                              <p className="text-[10px] text-[var(--text-muted)] uppercase mb-1">
                                Response {sub.response_status_code && `(HTTP ${sub.response_status_code})`}
                              </p>
                              <pre className="bg-[var(--bg-primary)] p-2 rounded text-xs font-mono text-[var(--text-secondary)] overflow-auto max-h-40 no-scrollbar">
                                {JSON.stringify(sub.response_data, null, 2)}
                              </pre>
                            </div>
                          )}
                          {sub.error_message && (
                            <p className="mt-2 text-xs text-danger bg-danger/10 p-2 rounded">{sub.error_message}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {step.officer_notes && (
                    <div className="mt-3 p-3 rounded-lg bg-accent/5 border border-accent/20">
                      <p className="text-xs font-medium text-accent mb-1">Officer Notes</p>
                      <p className="text-sm text-[var(--text-primary)]">{step.officer_notes}</p>
                    </div>
                  )}

                  {step.approver && (
                    <p className="mt-2 text-xs text-[var(--text-muted)]">
                      Completed by {step.approver.first_name} {step.approver.last_name}
                      {step.approved_at && ` on ${new Date(step.approved_at).toLocaleString()}`}
                    </p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Final Actions */}
      {allCompleted && request.status !== 'COMPLETED' && request.status !== 'REJECTED' && (
        <div className="glass-panel p-4 lg:p-6 border-2 border-success/30 bg-success/5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-base lg:text-lg font-bold text-[var(--text-primary)] mb-1">All Steps Completed</h3>
              <p className="text-xs lg:text-sm text-[var(--text-secondary)]">
                All verification steps have been successfully completed. You can now issue the final certificate or reject the application.
              </p>
            </div>
            <div className="flex items-center gap-3 self-end sm:self-auto">
              <button onClick={handleReject} className="btn-danger flex items-center gap-2 text-sm">
                <XCircle className="w-4 h-4" /> Reject
              </button>
              <button onClick={handleFinalComplete} className="btn-primary flex items-center gap-2 text-sm lg:text-base py-2 lg:py-3 px-4 lg:px-6 bg-success hover:bg-success/80">
                <FileCheck className="w-4 h-4 lg:w-5 lg:h-5" /> Issue Certificate
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Submit Modal */}
      <Modal
        isOpen={submitModal}
        onClose={() => { setSubmitModal(false); setSubmitData({}); setActiveStep(null); }}
        title={`Run: ${activeStep?.step_name || 'Service Step'}`}
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4 lg:space-y-5">
          {activeStep?.service?.full_url && (
            <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
              <p className="text-xs text-[var(--text-muted)] uppercase tracking-wider mb-1">Service Endpoint</p>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-accent/10 text-accent border border-accent/20">
                  {activeStep.service.http_method || 'POST'}
                </span>
                <span className="text-xs lg:text-sm font-mono text-[var(--text-primary)] break-all">
                  {activeStep.service.full_url}
                </span>
              </div>
              <p className="text-xs text-[var(--text-muted)] mt-1">
                Agency: {activeStep.service.agency_name || 'N/A'}
              </p>
            </div>
          )}

          {stepSchemas[activeStep?.id]?.fields?.length > 0 && (
            <div className="p-3 rounded-lg bg-accent/5 border border-accent/20">
              <p className="text-xs text-accent font-medium flex items-center gap-1.5 mb-2">
                <Eye className="w-3.5 h-3.5" />
                Fill in the fields below. The backend will build the HTTP request automatically.
              </p>
              <div className="flex flex-wrap gap-2">
                {stepSchemas[activeStep.id].fields.map(f => (
                  <span key={f.name} className="text-[11px] px-2 py-1 rounded bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-secondary)]">
                    {f.label || f.name}
                    <span className="text-[var(--text-muted)] ml-1">→ {f.location}</span>
                    {f.required && <span className="text-danger ml-1">*</span>}
                  </span>
                ))}
              </div>
            </div>
          )}

          {stepSchemas[activeStep?.id]?.fields?.length > 0 ? (
            <DynamicForm
              fields={stepSchemas[activeStep.id].fields.map(f => ({
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
              }))}
              data={submitData}
              onChange={setSubmitData}
            />
          ) : (
            <div className="p-4 rounded-lg bg-warning/5 border border-warning/20">
              <p className="text-sm text-warning flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                No field schema available for this service. Enter raw JSON payload:
              </p>
              <textarea
                className="input-field font-mono text-xs mt-3"
                rows={6}
                value={JSON.stringify(submitData, null, 2)}
                onChange={e => { try { setSubmitData(JSON.parse(e.target.value)); } catch {} }}
                placeholder='{"nin": "CM1234567890AB"}'
              />
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t border-[var(--border-color)]">
            <button
              type="button"
              onClick={() => { setSubmitModal(false); setSubmitData({}); setActiveStep(null); }}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn-primary flex items-center gap-2"
            >
              {submitting ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Submit & Verify
            </button>
          </div>
        </form>
      </Modal>

      {/* Complete Step Modal */}
      <Modal isOpen={showCompleteModal} onClose={() => { setShowCompleteModal(false); setCompleteNotes(''); }} title="Complete Step" size="sm">
        <div className="space-y-4">
          <p className="text-sm text-[var(--text-secondary)]">
            Mark <strong>{activeStep?.step_name}</strong> as completed. Add any notes about the verification.
          </p>
          <div>
            <label className="label">Officer Notes</label>
            <textarea className="input-field" rows={3} value={completeNotes}
              onChange={e => setCompleteNotes(e.target.value)}
              placeholder="e.g. All director identities verified successfully." />
          </div>
          <div className="flex justify-end gap-3">
            <button onClick={() => setShowCompleteModal(false)} className="btn-secondary">Cancel</button>
            <button onClick={() => handleCompleteStep(activeStep.id)} className="btn-primary flex items-center gap-2 bg-success hover:bg-success/80">
              <Check className="w-4 h-4" /> Confirm Complete
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default RequestDetail;