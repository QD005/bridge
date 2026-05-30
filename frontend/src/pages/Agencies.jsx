import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, Globe, Phone, Mail, Activity } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Badge from '../components/Badge';

const Agencies = () => {
  const navigate = useNavigate();
  const [agencies, setAgencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api.get('/agencies/').then(r => setAgencies(r.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  const filtered = agencies.filter(a =>
    a.name?.toLowerCase().includes(search.toLowerCase()) ||
    a.code?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <Loading />;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Agencies</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">Government agencies connected to GovBridge</p>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
        <input className="input-field pl-10" placeholder="Search agencies..." value={search} onChange={e => setSearch(e.target.value)} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map(agency => (
          <div
            key={agency.id}
            onClick={() => navigate(`/agencies/${agency.id}`)}
            className="glass-panel p-5 cursor-pointer hover:border-accent/30 transition-all group"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center text-accent font-bold text-sm">
                {agency.code?.slice(0, 5)}
              </div>
              <Badge status={agency.status} />
            </div>
            <h3 className="font-semibold text-[var(--text-primary)] mb-1 group-hover:text-accent transition-colors">{agency.name}</h3>
            <p className="text-xs text-[var(--text-muted)] mb-3">{agency.agency_type || 'Government Agency'}</p>
            <div className="space-y-1.5 text-xs text-[var(--text-muted)]">
              {agency.contact_email && <div className="flex items-center gap-1.5"><Mail className="w-3 h-3" /> {agency.contact_email}</div>}
              {agency.contact_phone && <div className="flex items-center gap-1.5"><Phone className="w-3 h-3" /> {agency.contact_phone}</div>}
              {agency.website && <div className="flex items-center gap-1.5"><Globe className="w-3 h-3" /> {agency.website}</div>}
            </div>
            <div className="mt-3 pt-3 border-t border-[var(--border-color)] flex items-center gap-2 text-xs text-[var(--text-muted)]">
              <Activity className="w-3 h-3" />
              {agency.authentication_type} auth
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Agencies;
