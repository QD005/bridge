import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg-primary)] p-4">
      <div className="w-full max-w-sm lg:max-w-md">
        {/* Logo */}
        <div className="text-center mb-6 lg:mb-8">
          <div className="w-14 h-14 lg:w-16 lg:h-16 rounded-2xl flex items-center justify-center mx-auto mb-3 lg:mb-4 shadow-lg shadow-accent/20">
            <img
              src="/logo.png"
              alt="Uganda Coat of Arms"
              className="w-10 h-10 lg:w-12 lg:h-12 object-contain"
            />
          </div>
          <h1 className="text-xl lg:text-2xl font-bold text-[var(--text-primary)]">Bridge Uganda</h1>
          <p className="text-xs lg:text-sm text-[var(--text-muted)] mt-1">National Interoperability Platform</p>
        </div>

        {/* Form */}
        <div className="glass-panel p-6 lg:p-8">
          <h2 className="text-base lg:text-lg font-semibold text-[var(--text-primary)] mb-4 lg:mb-6">Sign In</h2>

          {/* Error */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-danger/10 border border-danger/20 text-danger text-xs lg:text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label className="label flex items-center gap-2 text-xs lg:text-sm">
                <Mail className="w-3.5 h-3.5 lg:w-4 lg:h-4 text-[var(--text-muted)]" />
                Email Address
              </label>
              <input
                type="email"
                className="input-field text-sm"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="officer@agency.go.ug"
                required
              />
            </div>

            {/* Password */}
            <div>
              <label className="label flex items-center gap-2 text-xs lg:text-sm">
                <Lock className="w-3.5 h-3.5 lg:w-4 lg:h-4 text-[var(--text-muted)]" />
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="input-field pr-10 text-sm"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-2.5 flex items-center justify-center gap-2 text-sm"
            >
              {loading ? (
                <div className="w-4 h-4 lg:w-5 lg:h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                'Sign In'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;