import React, { useEffect, useState } from 'react';
import { Search, Filter, Download, Activity, AlertTriangle, CheckCircle, XCircle, Eye, Clock, User, Server } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Modal from '../components/Modal';

const ACTION_COLORS = {
  CREATE: 'bg-success/10 text-success border-success/20',
  UPDATE: 'bg-info/10 text-info border-info/20',
  DELETE: 'bg-danger/10 text-danger border-danger/20',
  READ: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  LOGIN: 'bg-green-500/10 text-green-500 border-green-500/20',
  LOGIN_FAILED: 'bg-red-500/10 text-red-500 border-red-500/20',
  API_CALL: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
  WORKFLOW_STEP: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
  OTHER: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
};

const STATUS_ICONS = {
  SUCCESS: CheckCircle,
  FAILED: XCircle,
  PENDING: Clock,
};

const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    action: '',
    status: '',
    entity: '',
    search: '',
    from: '',
    to: '',
  });
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [selectedLog, setSelectedLog] = useState(null);
  const limit = 50;

  useEffect(() => {
    fetchStats();
    fetchLogs();
  }, []);

  useEffect(() => {
    fetchLogs();
  }, [filters, offset]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.action) params.append('action', filters.action);
      if (filters.status) params.append('status', filters.status);
      if (filters.entity) params.append('entity', filters.entity);
      if (filters.search) params.append('search', filters.search);
      if (filters.from) params.append('from', filters.from);
      if (filters.to) params.append('to', filters.to);
      params.append('limit', limit);
      params.append('offset', offset);

      const res = await api.get(`/auditlogs/?${params}`);
      setLogs(res.data.results);
      setTotal(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await api.get('/auditlogs/stats/');
      setStats(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLogDetail = async (id) => {
    try {
      const res = await api.get(`/auditlogs/${id}/`);
      setSelectedLog(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const exportCSV = () => {
    const headers = ['ID', 'User', 'Action', 'Status', 'Entity', 'Entity Name', 'Method', 'Description', 'Date'];
    const rows = logs.map(l => [
      l.id,
      l.user_name || 'System',
      l.action,
      l.status,
      l.entity_type,
      l.entity_name,
      l.http_method,
      `"${(l.description || '').replace(/"/g, '""')}"`,
      new Date(l.created_at).toLocaleString()
    ]);
    
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const hasMore = offset + limit < total;

  return (
    <div className="flex flex-col gap-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Activity className="w-5 h-5" /> Audit Logs
          </h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">Track every action across the system</p>
        </div>
        <button onClick={exportCSV} className="btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" /> Export CSV
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass-panel p-4">
            <p className="text-xs text-[var(--text-muted)] uppercase">Total Actions</p>
            <p className="text-2xl font-bold text-[var(--text-primary)] mt-1">{stats.total_actions}</p>
          </div>
          <div className="glass-panel p-4">
            <p className="text-xs text-[var(--text-muted)] uppercase">Today</p>
            <p className="text-2xl font-bold text-accent mt-1">{stats.today}</p>
          </div>
          <div className="glass-panel p-4">
            <p className="text-xs text-[var(--text-muted)] uppercase">Last 7 Days</p>
            <p className="text-2xl font-bold text-info mt-1">{stats.last_7_days}</p>
          </div>
          <div className="glass-panel p-4 border-l-2 border-l-danger">
            <p className="text-xs text-[var(--text-muted)] uppercase">Failed Actions</p>
            <p className="text-2xl font-bold text-danger mt-1">{stats.failed_actions}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="glass-panel p-4">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-4 h-4 text-[var(--text-muted)]" />
          <span className="text-sm font-medium text-[var(--text-primary)]">Filters</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
          <select
            className="input-field text-sm"
            value={filters.action}
            onChange={e => setFilters(prev => ({ ...prev, action: e.target.value, offset: 0 }))}
          >
            <option value="">All Actions</option>
            {['CREATE','UPDATE','DELETE','READ','LOGIN','LOGIN_FAILED','API_CALL','WORKFLOW_STEP','OTHER'].map(a => (
              <option key={a} value={a}>{a.replace(/_/g, ' ')}</option>
            ))}
          </select>
          <select
            className="input-field text-sm"
            value={filters.status}
            onChange={e => setFilters(prev => ({ ...prev, status: e.target.value, offset: 0 }))}
          >
            <option value="">All Status</option>
            <option value="SUCCESS">Success</option>
            <option value="FAILED">Failed</option>
            <option value="PENDING">Pending</option>
          </select>
          <input
            className="input-field text-sm"
            placeholder="Entity type..."
            value={filters.entity}
            onChange={e => setFilters(prev => ({ ...prev, entity: e.target.value, offset: 0 }))}
          />
          <input
            className="input-field text-sm"
            placeholder="Search..."
            value={filters.search}
            onChange={e => setFilters(prev => ({ ...prev, search: e.target.value, offset: 0 }))}
          />
          <input
            type="date"
            className="input-field text-sm"
            value={filters.from}
            onChange={e => setFilters(prev => ({ ...prev, from: e.target.value, offset: 0 }))}
          />
          <input
            type="date"
            className="input-field text-sm"
            value={filters.to}
            onChange={e => setFilters(prev => ({ ...prev, to: e.target.value, offset: 0 }))}
          />
        </div>
      </div>

      {/* Logs Table */}
      <div className="glass-panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--border-color)] text-[var(--text-muted)] text-left">
              <th className="px-4 py-3 font-medium">Time</th>
              <th className="px-4 py-3 font-medium">User</th>
              <th className="px-4 py-3 font-medium">Action</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Entity</th>
              <th className="px-4 py-3 font-medium">Method</th>
              <th className="px-4 py-3 font-medium">Description</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading && logs.length === 0 && (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-[var(--text-muted)]"><Loading /></td></tr>
            )}
            {logs.length === 0 && !loading && (
              <tr><td colSpan={8} className="px-4 py-8 text-center text-[var(--text-muted)]">No logs found</td></tr>
            )}
            {logs.map(log => {
              const StatusIcon = STATUS_ICONS[log.status] || Clock;
              return (
                <tr 
                  key={log.id} 
                  className="border-b border-[var(--border-color)] hover:bg-[var(--bg-input)] transition-colors cursor-pointer"
                  onClick={() => fetchLogDetail(log.id)}
                >
                  <td className="px-4 py-3 text-[var(--text-muted)] whitespace-nowrap">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <User className="w-3.5 h-3.5 text-[var(--text-muted)]" />
                      <span className="text-[var(--text-primary)]">{log.user_name || 'System'}</span>
                      <span className="text-[10px] text-[var(--text-muted)] bg-[var(--bg-input)] px-1.5 py-0.5 rounded">{log.user_role || 'N/A'}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-[10px] px-2 py-0.5 rounded border ${ACTION_COLORS[log.action] || ACTION_COLORS.OTHER}`}>
                      {log.action.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <StatusIcon className={`w-3.5 h-3.5 ${log.status === 'SUCCESS' ? 'text-success' : log.status === 'FAILED' ? 'text-danger' : 'text-warning'}`} />
                      <span className={`text-xs ${log.status === 'SUCCESS' ? 'text-success' : log.status === 'FAILED' ? 'text-danger' : 'text-warning'}`}>
                        {log.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-[var(--text-secondary)]">
                    {log.entity_type || '-'}
                  </td>
                  <td className="px-4 py-3">
                    {log.http_method && (
                      <span className="text-xs font-mono px-1.5 py-0.5 rounded bg-[var(--bg-input)] border border-[var(--border-color)]">
                        {log.http_method}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-[var(--text-secondary)] max-w-xs truncate">
                    {log.description || '-'}
                  </td>
                  <td className="px-4 py-3">
                    <Eye className="w-4 h-4 text-[var(--text-muted)]" />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        
        {/* Pagination */}
        <div className="flex items-center justify-between p-4 border-t border-[var(--border-color)]">
          <span className="text-xs text-[var(--text-muted)]">
            Showing {offset + 1}-{Math.min(offset + limit, total)} of {total}
          </span>
          <div className="flex gap-2">
            <button 
              onClick={() => setOffset(prev => Math.max(0, prev - limit))}
              disabled={offset === 0}
              className="btn-secondary text-sm py-1.5 px-3 disabled:opacity-50"
            >
              Previous
            </button>
            <button 
              onClick={() => setOffset(prev => prev + limit)}
              disabled={!hasMore}
              className="btn-secondary text-sm py-1.5 px-3 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      <Modal isOpen={!!selectedLog} onClose={() => setSelectedLog(null)} title="Audit Log Detail" size="lg">
        {selectedLog && (
          <div className="space-y-4 max-h-[70vh] overflow-y-auto no-scrollbar">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">User</p>
                <p className="text-[var(--text-primary)]">
                  {selectedLog.user?.email || 'Anonymous'} 
                  {selectedLog.user?.role && <span className="text-[var(--text-muted)] ml-2">({selectedLog.user.role})</span>}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">Time</p>
                <p className="text-[var(--text-primary)]">{new Date(selectedLog.created_at).toLocaleString()}</p>
              </div>
              <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">Action</p>
                <p className="text-[var(--text-primary)]">{selectedLog.action}</p>
              </div>
              <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">Status</p>
                <p className={selectedLog.status === 'SUCCESS' ? 'text-success' : selectedLog.status === 'FAILED' ? 'text-danger' : 'text-warning'}>
                  {selectedLog.status}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">Entity</p>
                <p className="text-[var(--text-primary)]">{selectedLog.entity_type} #{selectedLog.entity_id}</p>
              </div>
              <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">HTTP Method</p>
                <p className="text-[var(--text-primary)] font-mono">{selectedLog.http_method || 'N/A'}</p>
              </div>
            </div>

            {selectedLog.url && (
              <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">URL</p>
                <p className="text-xs font-mono text-[var(--text-primary)] break-all">{selectedLog.url}</p>
              </div>
            )}

            <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
              <p className="text-xs text-[var(--text-muted)] mb-1">Description</p>
              <p className="text-sm text-[var(--text-primary)]">{selectedLog.description}</p>
            </div>

            {selectedLog.ip_address && (
              <div className="p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <p className="text-xs text-[var(--text-muted)] mb-1">IP Address</p>
                <p className="text-sm font-mono text-[var(--text-primary)]">{selectedLog.ip_address}</p>
              </div>
            )}

            {Object.keys(selectedLog.previous_data || {}).length > 0 && (
              <div>
                <p className="text-xs text-[var(--text-muted)] mb-2">Previous Data</p>
                <pre className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-input)] p-3 rounded-lg overflow-auto max-h-40 no-scrollbar">
                  {JSON.stringify(selectedLog.previous_data, null, 2)}
                </pre>
              </div>
            )}

            {Object.keys(selectedLog.new_data || {}).length > 0 && (
              <div>
                <p className="text-xs text-[var(--text-muted)] mb-2">New Data</p>
                <pre className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-input)] p-3 rounded-lg overflow-auto max-h-40 no-scrollbar">
                  {JSON.stringify(selectedLog.new_data, null, 2)}
                </pre>
              </div>
            )}

            {selectedLog.error_message && (
              <div className="p-3 rounded-lg bg-danger/5 border border-danger/20">
                <p className="text-xs text-danger mb-1 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> Error
                </p>
                <p className="text-sm text-danger">{selectedLog.error_message}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AuditLogs;