import React, { useEffect, useState } from 'react';
import { Building2, Plug, Workflow, FileCheck, Activity, TrendingUp, AlertTriangle } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Badge from '../components/Badge';

const StatCard = ({ icon: Icon, label, value, color, subtext }) => (
  <div className="glass-panel p-5 flex items-start gap-4">
    <div className={`p-3 rounded-lg ${color}`}>
      <Icon className="w-5 h-5" />
    </div>
    <div>
      <p className="text-sm text-[var(--text-muted)]">{label}</p>
      <p className="text-2xl font-bold text-[var(--text-primary)] mt-0.5">{value}</p>
      {subtext && <p className="text-xs text-[var(--text-muted)] mt-1">{subtext}</p>}
    </div>
  </div>
);

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/monitoring/metrics/'),
      api.get('/monitoring/activity/?limit=10')
    ]).then(([mRes, aRes]) => {
      setMetrics(mRes.data);
      setActivity(aRes.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="page-title">National Operations Center</h1>
        <p className="text-sm text-[var(--text-muted)] mt-1">Real-time overview of government service interoperability</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Building2} label="Agencies" value={metrics?.agencies?.total || 0} color="bg-accent/10 text-accent" subtext={`${metrics?.agencies?.active || 0} active`} />
        <StatCard icon={Plug} label="Services" value={metrics?.services?.total || 0} color="bg-success/10 text-success" subtext={`${metrics?.services?.online || 0} online`} />
        <StatCard icon={Workflow} label="Workflows" value={metrics?.workflows?.published || 0} color="bg-warning/10 text-warning" subtext={`${metrics?.workflows?.total_executions || 0} executions`} />
        <StatCard icon={FileCheck} label="Requests" value={metrics?.executions?.completed || 0} color="bg-info/10 text-info" subtext={`${metrics?.executions?.pending || 0} pending`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-panel p-5">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-accent" />
            <h3 className="section-title">Live Activity Feed</h3>
          </div>
          <div className="space-y-3">
            {activity.length === 0 && <p className="text-sm text-[var(--text-muted)]">No recent activity</p>}
            {activity.map(item => (
              <div key={item.id} className="flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <Badge status={item.status} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[var(--text-primary)] truncate">{item.workflow}</p>
                  <p className="text-xs text-[var(--text-muted)]">{item.agency} · {item.initiated_by}</p>
                </div>
                <span className="text-xs text-[var(--text-muted)] whitespace-nowrap">
                  {new Date(item.started_at).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel p-5">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-success" />
            <h3 className="section-title">System Health</h3>
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-[var(--text-secondary)]">Services Online</span>
                <span className="font-medium text-[var(--text-primary)]">{Math.round((metrics?.services?.online / Math.max(metrics?.services?.total, 1)) * 100)}%</span>
              </div>
              <div className="w-full h-2 bg-[var(--bg-input)] rounded-full overflow-hidden">
                <div className="h-full bg-success rounded-full transition-all" style={{ width: `${(metrics?.services?.online / Math.max(metrics?.services?.total, 1)) * 100}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-[var(--text-secondary)]">Success Rate</span>
                <span className="font-medium text-[var(--text-primary)]">{metrics?.workflows?.success_rate || 0}%</span>
              </div>
              <div className="w-full h-2 bg-[var(--bg-input)] rounded-full overflow-hidden">
                <div className="h-full bg-accent rounded-full transition-all" style={{ width: `${metrics?.workflows?.success_rate || 0}%` }} />
              </div>
            </div>
            {metrics?.agencies?.offline > 0 && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-warning/10 border border-warning/20">
                <AlertTriangle className="w-4 h-4 text-warning flex-shrink-0" />
                <p className="text-sm text-warning">{metrics.agencies.offline} agency(s) offline</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
