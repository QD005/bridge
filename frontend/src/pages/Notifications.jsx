import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Bell, Check, CheckCheck, Clock, AlertTriangle, FileCheck, XCircle, Info, Zap, MessageSquare, Shield } from 'lucide-react';
import api from '../api/axios';
import Loading from '../components/Loading';
import eventBus from '../utils/events';

const iconMap = {
  WORKFLOW_STARTED: Zap,
  WORKFLOW_COMPLETED: FileCheck,
  WORKFLOW_FAILED: XCircle,
  WORKFLOW_REJECTED: XCircle,
  WORKFLOW_CANCELLED: Info,
  STEP_COMPLETED: FileCheck,
  STEP_FAILED: XCircle,
  STEP_APPROVAL: Bell,
  TASK_ASSIGNED: Bell,
  TASK_UPDATED: Check,
  NEW_MESSAGE: MessageSquare,
  MENTION: MessageSquare,
  SERVICE_DOWN: AlertTriangle,
  SERVICE_UP: FileCheck,
  AGENCY_OFFLINE: AlertTriangle,
  AGENCY_ONLINE: FileCheck,
  EXECUTION_WAITING: Clock,
  CERTIFICATE_ISSUED: FileCheck,
  SYSTEM_ALERT: Info,
  FAILED_LOGIN: Shield,
  PASSWORD_CHANGED: Shield,
};

const colorMap = {
  WORKFLOW_STARTED: 'bg-accent/10 text-accent',
  WORKFLOW_COMPLETED: 'bg-success/10 text-success',
  WORKFLOW_FAILED: 'bg-danger/10 text-danger',
  WORKFLOW_REJECTED: 'bg-danger/10 text-danger',
  WORKFLOW_CANCELLED: 'bg-gray-500/10 text-gray-500',
  STEP_COMPLETED: 'bg-success/10 text-success',
  STEP_FAILED: 'bg-danger/10 text-danger',
  STEP_APPROVAL: 'bg-warning/10 text-warning',
  TASK_ASSIGNED: 'bg-accent/10 text-accent',
  TASK_UPDATED: 'bg-success/10 text-success',
  NEW_MESSAGE: 'bg-accent/10 text-accent',
  MENTION: 'bg-warning/10 text-warning',
  SERVICE_DOWN: 'bg-danger/10 text-danger',
  SERVICE_UP: 'bg-success/10 text-success',
  AGENCY_OFFLINE: 'bg-danger/10 text-danger',
  AGENCY_ONLINE: 'bg-success/10 text-success',
  EXECUTION_WAITING: 'bg-warning/10 text-warning',
  CERTIFICATE_ISSUED: 'bg-success/10 text-success',
  SYSTEM_ALERT: 'bg-info/10 text-info',
  FAILED_LOGIN: 'bg-danger/10 text-danger',
  PASSWORD_CHANGED: 'bg-success/10 text-success',
  default: 'bg-accent/10 text-accent',
};

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const reconnectAttempts = useRef(0);

  const getWsUrl = () => {
    let wsUrl = import.meta.env.VITE_WS_URL || 'wss://bridge.xoratechnologies.com/ws';
    wsUrl = wsUrl.replace(/\/$/, '');
    if (!wsUrl.endsWith('/ws')) wsUrl += '/ws';
    const token = localStorage.getItem('access_token');
    if (token) {
      wsUrl += `/notifications/?token=${token}`;
    } else {
      wsUrl += '/notifications/';
    }
    return wsUrl;
  };

  const fetchNotifications = useCallback(async () => {
    try {
      const res = await api.get('/notifications/');
      setNotifications(res.data.notifications || []);
      setUnreadCount(res.data.unread_count || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const markRead = async (id) => {
    try {
      await api.post(`/notifications/${id}/read/`);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
      const newCount = Math.max(0, unreadCount - 1);
      setUnreadCount(newCount);
      eventBus.emit('notification-read', { id });
    } catch (err) {
      console.error(err);
    }
  };

  const markAllRead = async () => {
    try {
      await api.post('/notifications/read-all/');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
      eventBus.emit('notifications-all-read');
    } catch (err) {
      console.error(err);
    }
  };

  // Listen for mark-read from Header dropdown
  useEffect(() => {
    const refresh = async () => {
      try {
        const res = await api.get('/notifications/');
        setNotifications(res.data.notifications || []);
        setUnreadCount(res.data.unread_count || 0);
      } catch (err) {
        console.error(err);
      }
    };
    const unsubRead = eventBus.on('notification-read', refresh);
    const unsubAll = eventBus.on('notifications-all-read', refresh);
    return () => {
      unsubRead();
      unsubAll();
    };
  }, []);

  // WebSocket — no polling, empty deps (page mounts once)
  useEffect(() => {
    let ws = null;
    let mounted = true;
    reconnectAttempts.current = 0;
    const MAX_RECONNECT = 10;
    const BASE_DELAY = 2000;

    const connectWS = () => {
      const token = localStorage.getItem('access_token');
      if (!token || !mounted) return;

      if (reconnectAttempts.current < 3) {
        console.log('Notifications WS connecting...');
      }

      ws = new WebSocket(getWsUrl());
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mounted) { ws.close(); return; }
        reconnectAttempts.current = 0;
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        if (!mounted) return;
        const data = JSON.parse(event.data);
        if (data.type === 'unread_count') setUnreadCount(data.count);
        if (data.type === 'new_notification') {
          setNotifications(prev => [data.data, ...prev]);
          setUnreadCount(prev => prev + 1);
        }
      };

      ws.onclose = (e) => {
        if (!mounted) return;
        setWsConnected(false);
        if (e.code !== 1000 && reconnectAttempts.current < MAX_RECONNECT) {
          reconnectAttempts.current += 1;
          const delay = Math.min(BASE_DELAY * reconnectAttempts.current, 30000);
          reconnectTimer.current = setTimeout(connectWS, delay);
        } else if (reconnectAttempts.current >= MAX_RECONNECT) {
          console.warn('Notifications WS: max reconnect attempts reached.');
        }
      };

      ws.onerror = () => {
        // Empty — browser hides WS failure details. onclose handles backoff.
      };
    };

    const startTimer = setTimeout(() => {
      if (mounted) {
        fetchNotifications();
        connectWS();
      }
    }, 0);

    return () => {
      mounted = false;
      clearTimeout(startTimer);
      clearTimeout(reconnectTimer.current);
      if (ws) {
        ws.onopen = null;
        ws.onmessage = null;
        ws.onclose = null;
        ws.onerror = null;
        ws.close();
      }
      wsRef.current = null;
    };
  }, [fetchNotifications]);

  if (loading) return <Loading />;

  return (
    <div className="space-y-4 lg:space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="page-title text-lg lg:text-2xl">Notifications</h1>
          <p className="text-xs lg:text-sm text-[var(--text-muted)] mt-1">
            {unreadCount} unread {wsConnected ? '• Live' : '• Offline'}
          </p>
        </div>
        {unreadCount > 0 && (
          <button onClick={markAllRead} className="btn-secondary flex items-center gap-2 text-sm self-start sm:self-auto">
            <CheckCheck className="w-4 h-4" /> Mark All Read
          </button>
        )}
      </div>

      <div className="space-y-2 lg:space-y-3">
        {notifications.length === 0 && (
          <div className="glass-panel p-8 lg:p-12 text-center text-[var(--text-muted)]">
            <Bell className="w-10 h-10 lg:w-12 lg:h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">No notifications yet</p>
          </div>
        )}
        {notifications.map(n => {
          const Icon = iconMap[n.type] || Bell;
          const colorClass = colorMap[n.type] || colorMap.default;
          return (
            <div
              key={n.id}
              className={`glass-panel p-3 lg:p-4 flex items-start gap-3 lg:gap-4 transition-all ${!n.is_read ? 'border-l-2 border-l-accent bg-accent/5' : ''}`}
            >
              <div className={`w-8 h-8 lg:w-10 lg:h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${colorClass}`}>
                <Icon className="w-4 h-4 lg:w-5 lg:h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <h4 className="font-medium text-[var(--text-primary)] text-sm lg:text-base truncate">{n.title}</h4>
                  {!n.is_read && <span className="w-2 h-2 rounded-full bg-accent flex-shrink-0" />}
                </div>
                <p className="text-xs lg:text-sm text-[var(--text-secondary)]">{n.message}</p>
                <div className="flex items-center gap-3 mt-1.5">
                  <span className="text-xs text-[var(--text-muted)] flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(n.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                  </span>
                  {n.link && <a href={n.link} className="text-xs text-accent hover:underline">View →</a>}
                </div>
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