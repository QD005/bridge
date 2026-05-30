import React, { useEffect, useState } from 'react';
import { Bell, Check, CheckCheck, Clock, AlertTriangle, FileCheck, XCircle, Info } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import Badge from '../components/Badge';

const iconMap = {
  WORKFLOW_COMPLETED: FileCheck,
  WORKFLOW_FAILED: XCircle,
  STEP_APPROVAL: Bell,
  SERVICE_DOWN: AlertTriangle,
  AGENCY_OFFLINE: AlertTriangle,
  EXECUTION_WAITING: Clock,
  SYSTEM_ALERT: Info,
};

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchNotifications(); }, []);

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications/');
      setNotifications(res.data.notifications || []);
      setUnreadCount(res.data.unread_count || 0);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const markRead = async (id) => {
    try {
      await api.post(`/notifications/${id}/read/`);
      fetchNotifications();
    } catch (err) { console.error(err); }
  };

  const markAllRead = async () => {
    try {
      await api.post('/notifications/read-all/');
      fetchNotifications();
    } catch (err) { console.error(err); }
  };

  if (loading) return <Loading />;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="text-sm text-[var(--text-muted)] mt-1">{unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}</p>
        </div>
        {unreadCount > 0 && (
          <button onClick={markAllRead} className="btn-secondary flex items-center gap-2 text-sm">
            <CheckCheck className="w-4 h-4" /> Mark All Read
          </button>
        )}
      </div>

      <div className="space-y-2">
        {notifications.length === 0 && (
          <div className="glass-panel p-8 text-center text-[var(--text-muted)]">
            <Bell className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>No notifications yet</p>
          </div>
        )}
        {notifications.map(n => {
          const Icon = iconMap[n.type] || Bell;
          return (
            <div
              key={n.id}
              className={`glass-panel p-4 flex items-start gap-4 transition-all ${!n.is_read ? 'border-l-2 border-l-accent bg-accent/5' : ''}`}
            >
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                n.type?.includes('FAILED') || n.type?.includes('DOWN') || n.type?.includes('OFFLINE')
                  ? 'bg-danger/10 text-danger'
                  : n.type?.includes('COMPLETED')
                  ? 'bg-success/10 text-success'
                  : 'bg-accent/10 text-accent'
              }`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <h4 className="font-medium text-[var(--text-primary)]">{n.title}</h4>
                  {!n.is_read && <span className="w-2 h-2 rounded-full bg-accent" />}
                </div>
                <p className="text-sm text-[var(--text-secondary)]">{n.message}</p>
                <p className="text-xs text-[var(--text-muted)] mt-1.5 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {new Date(n.created_at).toLocaleString()}
                </p>
              </div>
              {!n.is_read && (
                <button
                  onClick={() => markRead(n.id)}
                  className="p-2 hover:bg-accent/10 rounded-lg text-[var(--text-muted)] hover:text-accent transition-colors flex-shrink-0"
                  title="Mark as read"
                >
                  <Check className="w-4 h-4" />
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Notifications;
