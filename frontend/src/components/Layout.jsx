import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAuth } from '../context/AuthContext';
import Loading from './Loading';

const Layout = () => {
  const { user, loading } = useAuth();
  if (loading) return <Loading />;
  if (!user) return <Navigate to="/login" replace />;
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[var(--bg-primary)]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto no-scrollbar p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;