import React, { useEffect, useState, useRef } from 'react';
import { Sun, Moon, LogOut, Bell, Menu, CheckCheck, Clock } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import eventBus from '../utils/events';

const Header = ({ onMenuClick }) => {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const dropdownRef = useRef(null);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const reconnectAttempts = useRef(0);
  const lastUserId = useRef(null);

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

  const fetchNotifications = async () => {
    try {
      const res = await api.get('/notifications/?limit=5');
      setNotifications(res.data.notifications || []);
      setUnreadCount(res.data.unread_count || 0);
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    }
  };

  const markRead = async (id, e) => {
    e?.stopPropagation();
    try {
      await api.post(`/notifications/${id}/read/`);
      setNotifications(prev => prev.map(n => 
        n.id === id ? { ...n, is_read: true } : n
      ));
      setUnreadCount(prev => Math.max(0, prev - 1));
      eventBus.emit('notification-read', { id });
    } catch (err) {
      console.error('Failed to mark read:', err);
    }
  };

  const markAllRead = async (e) => {
    e?.stopPropagation();
    try {
      await api.post('/notifications/read-all/');
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
      eventBus.emit('notifications-all-read');
    } catch (err) {
      console.error('Failed to mark all read:', err);
    }
  };

  // Listen for mark-read from Notifications page
  useEffect(() => {
    const refresh = () => {
      api.get('/notifications/?limit=5')
        .then(res => {
          setNotifications(res.data.notifications || []);
          setUnreadCount(res.data.unread_count || 0);
        })
        .catch(() => {});
    };
    const unsubRead = eventBus.on('notification-read', refresh);
    const unsubAll = eventBus.on('notifications-all-read', refresh);
    return () => {
      unsubRead();
      unsubAll();
    };
  }, []);

  // WebSocket — depends on user.id primitive only
  useEffect(() => {
    const userId = user?.id;
    if (!userId) return;

    // Prevent reconnecting if already connected for this same user
    if (lastUserId.current === userId && wsRef.current) return;
    lastUserId.current = userId;

    let ws = null;
    let mounted = true;
    reconnectAttempts.current = 0;
    const MAX_RECONNECT = 10;
    const BASE_DELAY = 2000;

    const connectWS = () => {
      const token = localStorage.getItem('access_token');
      if (!token || !mounted) return;

      if (reconnectAttempts.current < 3) {
        console.log('Header WS connecting...');
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
          setNotifications(prev => [data.data, ...prev.slice(0, 4)]);
          setUnreadCount(prev => prev + 1);
        }
      };

      ws.onclose = (event) => {
        if (!mounted) return;
        setWsConnected(false);
        if (event.code !== 1000 && reconnectAttempts.current < MAX_RECONNECT) {
          reconnectAttempts.current += 1;
          const delay = Math.min(BASE_DELAY * reconnectAttempts.current, 30000);
          reconnectTimer.current = setTimeout(connectWS, delay);
        } else if (reconnectAttempts.current >= MAX_RECONNECT) {
          console.warn('Header WS: max reconnect attempts reached.');
        }
      };

      ws.onerror = () => {
        // Empty — browser hides WS failure details. onclose handles backoff.
      };
    };

    // StrictMode-safe: delay by one tick
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
  }, [user?.id]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleNotificationClick = (notif) => {
    if (!notif.is_read) markRead(notif.id);
    if (notif.link) window.location.href = notif.link;
    setShowDropdown(false);
  };

  return (
    <header className="h-14 lg:h-16 flex-shrink-0 bg-[var(--header-bg)] border-b border-[var(--border-color)] flex items-center justify-between px-4 lg:px-6 sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 -ml-2 rounded-lg hover:bg-[var(--bg-input)] text-[var(--text-muted)] transition-colors"
          aria-label="Open menu"
        >
          <Menu className="w-5 h-5" />
        </button>
        <h2 className="text-base lg:text-lg font-semibold text-[var(--text-primary)]">
          National Operations Center
        </h2>
      </div>

      <div className="flex items-center gap-2 lg:gap-3">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-[var(--bg-input)] text-[var(--text-muted)] transition-colors"
          title="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 lg:w-5 lg:h-5" /> : <Moon className="w-4 h-4 lg:w-5 lg:h-5" />}
        </button>

        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => {
              setShowDropdown(!showDropdown);
              if (!showDropdown) fetchNotifications();
            }}
            className="p-2 rounded-lg hover:bg-[var(--bg-input)] text-[var(--text-muted)] transition-colors relative"
          >
            <Bell className="w-4 h-4 lg:w-5 lg:h-5" />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center px-1 border-2 border-[var(--header-bg)]">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
            <span className={`absolute bottom-0.5 right-0.5 w-1.5 h-1.5 rounded-full border border-[var(--header-bg)] ${
              wsConnected ? 'bg-success' : 'bg-warning'
            }`} />
          </button>

          {showDropdown && (
            <div className="absolute right-0 top-full mt-2 w-80 lg:w-96 glass-panel shadow-xl border border-[var(--border-color)] rounded-xl overflow-hidden z-50">
              <div className="p-3 border-b border-[var(--border-color)] flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-[var(--text-primary)] text-sm">Notifications</h3>
                  <p className="text-xs text-[var(--text-muted)]">
                    {unreadCount} unread {wsConnected ? '• Live' : '• Offline'}
                  </p>
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    className="text-xs text-accent hover:text-accent-hover flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-accent/10 transition-colors"
                  >
                    <CheckCheck className="w-3 h-3" />
                    Mark all
                  </button>
                )}
              </div>

              <div className="max-h-80 overflow-y-auto no-scrollbar">
                {notifications.length === 0 ? (
                  <div className="p-8 text-center text-[var(--text-muted)]">
                    <Bell className="w-8 h-8 mx-auto mb-2 opacity-30" />
                    <p className="text-sm">No notifications</p>
                  </div>
                ) : (
                  notifications.map(notif => (
                    <div
                      key={notif.id}
                      onClick={() => handleNotificationClick(notif)}
                      className={`p-3 border-b border-[var(--border-color)] cursor-pointer transition-colors ${
                        !notif.is_read ? 'bg-accent/5 hover:bg-accent/10' : 'hover:bg-[var(--bg-input)]'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {!notif.is_read && (
                          <span className="w-2 h-2 rounded-full bg-accent mt-1.5 flex-shrink-0" />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className={`text-sm font-medium truncate ${
                            !notif.is_read ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'
                          }`}>
                            {notif.title}
                          </p>
                          <p className="text-xs text-[var(--text-muted)] mt-0.5 line-clamp-2">
                            {notif.message}
                          </p>
                          <div className="flex items-center gap-2 mt-1.5">
                            <span className="text-[10px] text-[var(--text-muted)] flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                            {notif.link && (
                              <span className="text-[10px] text-accent">View →</span>
                            )}
                          </div>
                        </div>
                        {!notif.is_read && (
                          <button
                            onClick={(e) => markRead(notif.id, e)}
                            className="p-1 hover:bg-accent/20 rounded text-accent"
                            title="Mark as read"
                          >
                            <CheckCheck className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="p-2 border-t border-[var(--border-color)] text-center">
                <button
                  onClick={() => { window.location.href = '/notifications'; setShowDropdown(false); }}
                  className="text-xs text-accent hover:text-accent-hover font-medium py-1"
                >
                  View all notifications
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="h-5 lg:h-6 w-px bg-[var(--border-color)] mx-0.5" />

        <button
          onClick={logout}
          className="flex items-center gap-1.5 lg:gap-2 px-2 lg:px-3 py-1.5 rounded-lg hover:bg-danger/10 text-[var(--text-muted)] hover:text-danger transition-colors text-sm font-medium"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
};

export default Header;