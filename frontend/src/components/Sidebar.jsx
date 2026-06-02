import React, { useEffect, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Building2, Plug, Workflow, FileCheck,
  MessageSquare, Bell, ClipboardList, Settings,
  ChevronRight, X
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import eventBus from '../utils/events';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/agencies', icon: Building2, label: 'Agencies' },
  { path: '/services', icon: Plug, label: 'Services' },
  { path: '/workflows', icon: Workflow, label: 'Workflows' },
  { path: '/requests', icon: FileCheck, label: 'Requests' },
  { path: '/collaboration', icon: MessageSquare, label: 'Collaboration' },
  { path: '/audit-logs', icon: ClipboardList, label: 'Audit Logs' },
  { path: '/notifications', icon: Bell, label: 'Notifications' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

const Sidebar = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const location = useLocation();
  const [unreadMessages, setUnreadMessages] = useState(0);

  // Sum unread_count from all conversations
  const fetchUnreadMessages = async () => {
    try {
      const res = await api.get('/collaboration/');
      const total = (res.data || []).reduce((sum, c) => sum + (c.unread_count || 0), 0);
      setUnreadMessages(total);
    } catch (err) {
      // Silently fail — sidebar shouldn't crash if chat API is down
    }
  };

  useEffect(() => {
    fetchUnreadMessages();

    // Real-time update from Collaboration component
    const unsubCount = eventBus.on('chat-unread-updated', ({ count }) => {
      setUnreadMessages(count);
    });

    // Refresh immediately when a new message arrives via WS
    const unsubNew = eventBus.on('chat-new-message', fetchUnreadMessages);

    // Fallback poll every 30s when Collaboration is unmounted
    const interval = setInterval(fetchUnreadMessages, 30000);

    return () => {
      unsubCount();
      unsubNew();
      clearInterval(interval);
    };
  }, []);

  // Clear badge when user opens the chat page
  useEffect(() => {
    if (location.pathname === '/collaboration' || location.pathname.startsWith('/collaboration/')) {
      setUnreadMessages(0);
      // Optional: tell backend everything is seen
      // api.post('/collaboration/mark-all-read/').catch(() => {});
    }
  }, [location.pathname]);

  return (
    <aside
      className={`
        fixed lg:static inset-y-0 left-0 z-40
        w-64 h-screen flex-shrink-0 bg-[var(--sidebar-bg)] border-r border-[var(--border-color)]
        flex flex-col no-scrollbar overflow-y-auto
        transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}
    >
      {/* Logo area */}
      <div className="h-14 lg:h-16 flex items-center justify-between px-4 lg:px-5 border-b border-[var(--border-color)] flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center">
            <img
              src="/logo.png"
              alt="Uganda Coat of Arms"
              className="w-8 h-8 object-contain"
            />
          </div>
          <div>
            <h1 className="font-bold text-[var(--text-primary)] leading-tight">Bridge</h1>
            <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider">Uganda</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="lg:hidden p-1.5 rounded-lg hover:bg-[var(--bg-input)] text-[var(--text-muted)]"
          aria-label="Close menu"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* User mini profile */}
      <div className="px-4 py-3 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center text-accent font-semibold text-sm">
            {user?.first_name?.[0]}{user?.last_name?.[0]}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-[var(--text-primary)] truncate">
              {user?.first_name} {user?.last_name}
            </p>
            <p className="text-xs text-[var(--text-muted)] truncate">
              {user?.role?.replace(/_/g, ' ')}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
          const isChat = item.path === '/collaboration';
          const showBadge = isChat && unreadMessages > 0 && !isActive;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-accent/10 text-accent'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-input)] hover:text-[var(--text-primary)]'
                }`
              }
            >
              <Icon className="w-4.5 h-4.5 flex-shrink-0" />
              <span className="flex-1">{item.label}</span>

              <div className="ml-auto flex items-center gap-1">
                {showBadge && (
                  <span className="min-w-[18px] h-[18px] px-1 rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center">
                    {unreadMessages > 99 ? '99+' : unreadMessages}
                  </span>
                )}
                {isActive && <ChevronRight className="w-4 h-4 flex-shrink-0" />}
              </div>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-[var(--border-color)] text-xs text-[var(--text-muted)] text-center">
        v2.0.0 · National Interoperability
      </div>
    </aside>
  );
};

export default Sidebar;