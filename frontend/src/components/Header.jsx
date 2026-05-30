import React from 'react';
import { Sun, Moon, LogOut, Bell } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();

  return (
    <header className="h-16 flex-shrink-0 bg-[var(--header-bg)] border-b border-[var(--border-color)] flex items-center justify-between px-6 sticky top-0 z-20">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-[var(--text-primary)] hidden md:block">
          National Operations Center
        </h2>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-[var(--bg-input)] text-[var(--text-muted)] transition-colors"
          title="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        <button className="p-2 rounded-lg hover:bg-[var(--bg-input)] text-[var(--text-muted)] transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger rounded-full" />
        </button>

        <div className="h-6 w-px bg-[var(--border-color)] mx-1" />

        <button
          onClick={logout}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-danger/10 text-[var(--text-muted)] hover:text-danger transition-colors text-sm font-medium"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
};

export default Header;
