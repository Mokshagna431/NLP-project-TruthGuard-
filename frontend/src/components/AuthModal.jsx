import React, { useState } from 'react';
import { X, Lock, Mail, User, Eye, EyeOff, ShieldCheck, ArrowRight } from 'lucide-react';
import { api, setToken, setUser } from '../services/api';

export default function AuthModal({ isOpen, onClose, initialMode = 'login', onAuthSuccess }) {
  const [mode, setMode] = useState(initialMode); // 'login', 'register', 'forgot'
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  // Form Fields
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(true);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);
    setLoading(true);

    try {
      if (mode === 'register') {
        if (password !== confirmPassword) {
          throw new Error('Passwords do not match.');
        }
        if (!termsAccepted) {
          throw new Error('You must accept the terms of service.');
        }
        const res = await api.register({
          full_name: fullName,
          username,
          email,
          password,
          terms_accepted: termsAccepted
        });
        setToken(res.access_token);
        setUser(res.user);
        onAuthSuccess(res.user);
        onClose();
      } else if (mode === 'login') {
        const res = await api.login({
          email,
          password
        });
        setToken(res.access_token);
        setUser(res.user);
        onAuthSuccess(res.user);
        onClose();
      } else if (mode === 'forgot') {
        const res = await api.forgotPassword(email);
        setSuccessMsg(res.message || 'Password reset link sent to your email.');
      }
    } catch (err) {
      setError(err.message || 'Authentication error. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(28, 25, 23, 0.45)',
        backdropFilter: 'blur(3px)',
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '440px',
          maxWidth: '100%',
          backgroundColor: '#FFFFFF',
          borderRadius: '14px',
          boxShadow: '0 24px 48px rgba(0,0,0,0.18)',
          border: '1px solid #E8E5DC',
          overflow: 'hidden'
        }}
      >
        {/* Top Header */}
        <div
          style={{
            padding: '20px 24px',
            borderBottom: '1px solid #E8E5DC',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: '#FAF8F5'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '26px',
                height: '26px',
                borderRadius: '6px',
                backgroundColor: '#1C1917',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <ShieldCheck size={16} color="#FFFFFF" />
            </div>
            <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1C1917' }}>
              TruthGuard Proof Desk
            </span>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#78716C' }}
          >
            <X size={17} />
          </button>
        </div>

        {/* Form Body */}
        <div style={{ padding: '24px' }}>
          <h2 className="font-serif" style={{ fontSize: '1.5rem', fontWeight: 600, color: '#181614', marginBottom: '6px' }}>
            {mode === 'register' ? 'Create Proof Desk Account' : mode === 'login' ? 'Welcome Back' : 'Reset Password'}
          </h2>
          <p style={{ fontSize: '0.82rem', color: '#78716C', marginBottom: '20px' }}>
            {mode === 'register'
              ? 'Register to audit LLM claims, track reliability history, and export PDF reports.'
              : mode === 'login'
              ? 'Enter your credentials to access your personal verification workspace.'
              : 'Enter your registered email address to receive password recovery instructions.'}
          </p>

          {error && (
            <div
              style={{
                backgroundColor: '#FEF2F2',
                border: '1px solid #FECACA',
                borderRadius: '8px',
                padding: '10px 14px',
                color: '#991B1B',
                fontSize: '0.82rem',
                marginBottom: '16px'
              }}
            >
              {error}
            </div>
          )}

          {successMsg && (
            <div
              style={{
                backgroundColor: '#DCFCE7',
                border: '1px solid #BBF7D0',
                borderRadius: '8px',
                padding: '10px 14px',
                color: '#166534',
                fontSize: '0.82rem',
                marginBottom: '16px'
              }}
            >
              {successMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {mode === 'register' && (
              <>
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#44403C', marginBottom: '4px' }}>
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Dr. Miriam Okafor"
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: '6px',
                      border: '1px solid #D5D1C6',
                      backgroundColor: '#FAF8F5',
                      fontSize: '0.86rem',
                      outline: 'none'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#44403C', marginBottom: '4px' }}>
                    Username
                  </label>
                  <input
                    type="text"
                    required
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="e.g. mokafor"
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: '6px',
                      border: '1px solid #D5D1C6',
                      backgroundColor: '#FAF8F5',
                      fontSize: '0.86rem',
                      outline: 'none'
                    }}
                  />
                </div>
              </>
            )}

            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#44403C', marginBottom: '4px' }}>
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@organization.com"
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  borderRadius: '6px',
                  border: '1px solid #D5D1C6',
                  backgroundColor: '#FAF8F5',
                  fontSize: '0.86rem',
                  outline: 'none'
                }}
              />
            </div>

            {mode !== 'forgot' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <label style={{ fontSize: '0.78rem', fontWeight: 600, color: '#44403C' }}>Password</label>
                  {mode === 'login' && (
                    <button
                      type="button"
                      onClick={() => setMode('forgot')}
                      style={{ background: 'none', border: 'none', color: '#5E50EE', fontSize: '0.74rem', cursor: 'pointer' }}
                    >
                      Forgot password?
                    </button>
                  )}
                </div>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    style={{
                      width: '100%',
                      padding: '9px 36px 9px 12px',
                      borderRadius: '6px',
                      border: '1px solid #D5D1C6',
                      backgroundColor: '#FAF8F5',
                      fontSize: '0.86rem',
                      outline: 'none'
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#78716C' }}
                  >
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>
            )}

            {mode === 'register' && (
              <>
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#44403C', marginBottom: '4px' }}>
                    Confirm Password
                  </label>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    style={{
                      width: '100%',
                      padding: '9px 12px',
                      borderRadius: '6px',
                      border: '1px solid #D5D1C6',
                      backgroundColor: '#FAF8F5',
                      fontSize: '0.86rem',
                      outline: 'none'
                    }}
                  />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                  <input
                    type="checkbox"
                    id="terms"
                    checked={termsAccepted}
                    onChange={(e) => setTermsAccepted(e.target.checked)}
                  />
                  <label htmlFor="terms" style={{ fontSize: '0.75rem', color: '#57534E' }}>
                    I accept the TruthGuard terms of research service and privacy policy.
                  </label>
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{
                backgroundColor: '#1C1917',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '6px',
                padding: '11px',
                fontSize: '0.88rem',
                fontWeight: 600,
                cursor: loading ? 'wait' : 'pointer',
                marginTop: '10px'
              }}
            >
              {loading ? 'Processing...' : mode === 'register' ? 'Create Account' : mode === 'login' ? 'Sign In' : 'Send Reset Link'}
            </button>
          </form>

          {/* Mode Switching Footer */}
          <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.8rem', color: '#78716C' }}>
            {mode === 'login' ? (
              <span>
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setMode('register');
                    setError(null);
                  }}
                  style={{ background: 'none', border: 'none', color: '#1C1917', fontWeight: 700, cursor: 'pointer' }}
                >
                  Sign up free
                </button>
              </span>
            ) : (
              <span>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setMode('login');
                    setError(null);
                  }}
                  style={{ background: 'none', border: 'none', color: '#1C1917', fontWeight: 700, cursor: 'pointer' }}
                >
                  Sign in
                </button>
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
