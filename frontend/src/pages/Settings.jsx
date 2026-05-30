import React, { useState } from 'react';
import { User, Shield, Bell, Palette, Save, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import api from '../api/axios';

const Settings = () => {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('profile');
  const [saved, setSaved] = useState(false);
  const [profile, setProfile] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone_number: user?.phone_number || '',
  });

  const handleSaveProfile = async () => {
    try {
      await api.patch('/auth/profile/', profile);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      alert('Failed to update profile');
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'appearance', label: 'Appearance', icon: Palette },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="page-title">Settings</h1>
        <p className="text-sm text-[var(--text-muted)] mt-1">Manage your account and preferences</p>
      </div>

      <div className="flex gap-6">
        {/* Tabs */}
        <div className="w-56 flex-shrink-0 space-y-1">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-accent/10 text-accent'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-input)] hover:text-[var(--text-primary)]'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="flex-1 glass-panel p-6">
          {activeTab === 'profile' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Profile Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">First Name</label>
                  <input className="input-field" value={profile.first_name} onChange={e => setProfile({...profile, first_name: e.target.value})} />
                </div>
                <div>
                  <label className="label">Last Name</label>
                  <input className="input-field" value={profile.last_name} onChange={e => setProfile({...profile, last_name: e.target.value})} />
                </div>
                <div>
                  <label className="label">Email</label>
                  <input className="input-field" value={user?.email || ''} disabled />
                </div>
                <div>
                  <label className="label">Phone Number</label>
                  <input className="input-field" value={profile.phone_number} onChange={e => setProfile({...profile, phone_number: e.target.value})} placeholder="+256..." />
                </div>
              </div>
              <div className="pt-4">
                <button onClick={handleSaveProfile} className="btn-primary flex items-center gap-2">
                  {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
                  {saved ? 'Saved!' : 'Save Changes'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Security</h3>
              <div className="space-y-4 max-w-md">
                <div>
                  <label className="label">Current Password</label>
                  <input type="password" className="input-field" placeholder="••••••••" />
                </div>
                <div>
                  <label className="label">New Password</label>
                  <input type="password" className="input-field" placeholder="••••••••" />
                </div>
                <div>
                  <label className="label">Confirm New Password</label>
                  <input type="password" className="input-field" placeholder="••••••••" />
                </div>
                <button className="btn-primary">Update Password</button>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Notification Preferences</h3>
              <div className="space-y-3">
                {[
                  { label: 'Workflow completions', desc: 'Get notified when a workflow finishes' },
                  { label: 'Approval requests', desc: 'Get notified when your approval is needed' },
                  { label: 'Service outages', desc: 'Get notified when a service goes offline' },
                  { label: 'System alerts', desc: 'Get notified about system-wide events' },
                ].map((pref, i) => (
                  <label key={i} className="flex items-start gap-3 p-3 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)] cursor-pointer hover:border-accent/30 transition-colors">
                    <input type="checkbox" defaultChecked className="w-4 h-4 mt-0.5 rounded border-[var(--border-color)] text-accent" />
                    <div>
                      <p className="text-sm font-medium text-[var(--text-primary)]">{pref.label}</p>
                      <p className="text-xs text-[var(--text-muted)]">{pref.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Appearance</h3>
              <div className="flex items-center justify-between p-4 rounded-lg bg-[var(--bg-input)] border border-[var(--border-color)]">
                <div>
                  <p className="text-sm font-medium text-[var(--text-primary)]">Theme</p>
                  <p className="text-xs text-[var(--text-muted)]">Choose between light and dark mode</p>
                </div>
                <button
                  onClick={toggleTheme}
                  className="px-4 py-2 rounded-lg bg-accent text-white text-sm font-medium hover:bg-accent-hover transition-colors"
                >
                  {theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
