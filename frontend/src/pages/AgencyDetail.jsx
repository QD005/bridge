import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Globe, Phone, Mail, Activity, Plug, CheckCircle } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Badge from '../components/Badge';

const AgencyDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [agency, setAgency] = useState(null);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get(`/agencies/${id}/`),
      api.get(`/services/?agency=${id}`)
    ]).then(([aRes, sRes]) => {
      setAgency(aRes.data);
      setServices(sRes.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Loading />;
  if (!agency) return <div className="text-[var(--text-muted)]">Agency not found</div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/agencies')} className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="page-title">{agency.name}</h1>
            <Badge status={agency.status} />
          </div>
          <p className="text-sm text-[var(--text-muted)]">{agency.code} · {agency.agency_type}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-5">
            <h3 className="section-title mb-3">Agency Details</h3>
            <p className="text-sm text-[var(--text-secondary)] mb-4">{agency.description || 'No description available.'}</p>
            <div className="grid grid-cols-2 gap-4 text-sm">
              {agency.contact_email && <div className="flex items-center gap-2 text-[var(--text-secondary)]"><Mail className="w-4 h-4 text-[var(--text-muted)]" /> {agency.contact_email}</div>}
              {agency.contact_phone && <div className="flex items-center gap-2 text-[var(--text-secondary)]"><Phone className="w-4 h-4 text-[var(--text-muted)]" /> {agency.contact_phone}</div>}
              {agency.website && <div className="flex items-center gap-2 text-[var(--text-secondary)]"><Globe className="w-4 h-4 text-[var(--text-muted)]" /> {agency.website}</div>}
              <div className="flex items-center gap-2 text-[var(--text-secondary)]"><Activity className="w-4 h-4 text-[var(--text-muted)]" /> {agency.authentication_type}</div>
            </div>
          </div>

          <div className="glass-panel p-5">
            <h3 className="section-title mb-3">Registered Services ({services.length})</h3>
            <div className="space-y-2">
              {services.length === 0 && <p className="text-sm text-[var(--text-muted)]">No services registered.</p>}
              {services.map(s => (
                <div key={s.id} className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                  <div>
                    <p className="text-sm font-medium text-[var(--text-primary)]">{s.name}</p>
                    <p className="text-xs text-[var(--text-muted)] font-mono">{s.http_method} {s.full_url}</p>
                  </div>
                  <Badge status={s.status} />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="glass-panel p-5">
            <h3 className="section-title mb-3">Health Status</h3>
            <button
              onClick={async () => {
                try {
                  const res = await api.post(`/agencies/${id}/test/`);
                  alert(`Status: ${res.data.health_status} (${res.data.response_time_ms}ms)`);
                } catch (err) {
                  alert('Health check failed: ' + (err.response?.data?.detail || err.message));
                }
              }}
              className="w-full btn-primary flex items-center justify-center gap-2"
            >
              <CheckCircle className="w-4 h-4" /> Test Connectivity
            </button>
          </div>

          <div className="glass-panel p-5">
            <h3 className="section-title mb-3">Auth Config</h3>
            <pre className="text-xs font-mono text-[var(--text-secondary)] bg-[var(--bg-input)] p-3 rounded-lg overflow-auto max-h-48 no-scrollbar">
              {JSON.stringify(agency.auth_config || {}, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgencyDetail;
