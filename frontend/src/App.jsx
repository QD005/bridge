import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Agencies from './pages/Agencies';
import AgencyDetail from './pages/AgencyDetail';
import Services from './pages/Services';
import ServiceDetail from './pages/ServiceDetail';
import Workflows from './pages/Workflows';
import WorkflowBuilder from './pages/WorkflowBuilder';
import Requests from './pages/Requests';
import RequestDetail from './pages/RequestDetail';
import Collaboration from './pages/Collaboration';
import AuditLogs from './pages/AuditLogs';
import Notifications from './pages/Notifications';
import Settings from './pages/Settings';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/agencies" element={<Agencies />} />
              <Route path="/agencies/:id" element={<AgencyDetail />} />
              <Route path="/services" element={<Services />} />
              <Route path="/services/:id" element={<ServiceDetail />} />
              <Route path="/workflows" element={<Workflows />} />
              <Route path="/workflows/:id" element={<WorkflowBuilder />} />
              <Route path="/requests" element={<Requests />} />
              <Route path="/requests/:id" element={<RequestDetail />} />
              <Route path="/collaboration" element={<Collaboration />} />
              <Route path="/audit-logs" element={<AuditLogs />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
