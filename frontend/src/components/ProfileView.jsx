import React, { useState, useEffect } from 'react';
import { User, Lock, Mail, ShieldCheck, Check, AlertCircle } from 'lucide-react';
import { api, setUser } from '../services/api';

export default function ProfileView({ currentUser, onUpdateUser, onLogout }) {
  const [fullName, setFullName] = useState(currentUser?.full_name || '');
  const [username, setUsername] = useState(currentUser?.username || '');
  const [email] = useState(currentUser?.email || '');
  
  // Password Change
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Statuses
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [profileError, setProfileError] = useState(null);
  const [passSuccess, setPassSuccess] = useState(false);
  const [passError, setPassError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userStats, setUserStats] = useState(null);

  useEffect(() => {
    api.getMe()
      .then((res) => {
        setUserStats(res);
        setFullName(res.full_name);
        setUsername(res.username);
      })
      .catch(() => {});
  }, []);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setProfileError(null);
    setProfileSuccess(false);
    setLoading(true);

    try {
      const updated = await api.updateProfile({
        full_name: fullName,
        username
      });
      setUser(updated);
      onUpdateUser(updated);
      setProfileSuccess(true);
      setTimeout(() => setProfileSuccess(false), 3000);
    } catch (err) {
      setProfileError(err.message || 'Failed to update profile.');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setPassError(null);
    setPassSuccess(false);

    if (newPassword !== confirmPassword) {
      setPassError("New passwords do not match.");
      return;
    }

    try {
      await api.changePassword({
        current_password: currentPassword,
        new_password: newPassword
      });
      setPassSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setTimeout(() => setPassSuccess(false), 3000);
    } catch (err) {
      setPassError(err.message || 'Failed to change password.');
    }
  };

  const handleDeleteAccount = async () => {
    if (window.confirm("CAUTION: Are you sure you want to permanently delete your account and all associated verification records? This action cannot be reversed.")) {
      try {
        await api.deleteAccount();
        onLogout();
      } catch (err) {
        alert("Failed to delete account: " + err.message);
      }
    }
  };

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        {/* Header */}
        <div>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
            USER ACCOUNT
          </div>
          <h1 className="font-serif" style={{ fontSize: '2.5rem', fontWeight: 600, color: '#1C1917', lineHeight: 1.15, marginTop: '4px' }}>
            Profile & Proof Desk Identity
          </h1>
          <p style={{ fontSize: '0.86rem', color: '#57534E', marginTop: '4px' }}>
            Manage your credentials, editorial attribution, and account security.
          </p>
        </div>

        {/* Stats Summary Strip */}
        <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '20px 24px', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '0.7rem', color: '#78716C', fontWeight: 700, textTransform: 'uppercase' }}>Total Verifications</div>
            <div className="font-serif" style={{ fontSize: '1.8rem', fontWeight: 700, color: '#1C1917', marginTop: '4px' }}>
              {userStats?.total_verifications || 0}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '0.7rem', color: '#78716C', fontWeight: 700, textTransform: 'uppercase' }}>Avg Reliability R(a)</div>
            <div className="font-serif" style={{ fontSize: '1.8rem', fontWeight: 700, color: '#16A34A', marginTop: '4px' }}>
              {userStats?.average_reliability || 0}%
            </div>
          </div>
          <div>
            <div style={{ fontSize: '0.7rem', color: '#78716C', fontWeight: 700, textTransform: 'uppercase' }}>Detected Hallucinations</div>
            <div className="font-serif" style={{ fontSize: '1.8rem', fontWeight: 700, color: '#DC2626', marginTop: '4px' }}>
              {userStats?.total_inaccurate_claims || 0}
            </div>
          </div>
        </div>

        {/* Profile Details Form */}
        <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '28px', boxShadow: '0 1px 4px rgba(0,0,0,0.02)' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1C1917', marginBottom: '6px' }}>
            General Information
          </h2>
          <p style={{ fontSize: '0.8rem', color: '#78716C', marginBottom: '20px' }}>
            Update your public author name and Proof Desk username.
          </p>

          {profileSuccess && (
            <div style={{ backgroundColor: '#DCFCE7', border: '1px solid #BBF7D0', color: '#166534', padding: '10px 14px', borderRadius: '6px', fontSize: '0.82rem', marginBottom: '16px' }}>
              Profile updated successfully.
            </div>
          )}

          {profileError && (
            <div style={{ backgroundColor: '#FEF2F2', border: '1px solid #FECACA', color: '#991B1B', padding: '10px 14px', borderRadius: '6px', fontSize: '0.82rem', marginBottom: '16px' }}>
              {profileError}
            </div>
          )}

          <form onSubmit={handleUpdateProfile} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
                Full Name
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', fontSize: '0.86rem' }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
                  Username
                </label>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', fontSize: '0.86rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
                  Email Address
                </label>
                <input
                  type="email"
                  disabled
                  value={email}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #E8E5DC', backgroundColor: '#F3EFE7', fontSize: '0.86rem', color: '#78716C', cursor: 'not-allowed' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '6px' }}>
              <button
                type="submit"
                disabled={loading}
                style={{ backgroundColor: '#1C1917', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '9px 18px', fontSize: '0.84rem', fontWeight: 600, cursor: 'pointer' }}
              >
                Save Changes
              </button>
            </div>
          </form>
        </div>

        {/* Change Password Form */}
        <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '28px' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1C1917', marginBottom: '6px' }}>
            Change Password
          </h2>
          <p style={{ fontSize: '0.8rem', color: '#78716C', marginBottom: '20px' }}>
            Ensure your account is protected with a strong, distinct password.
          </p>

          {passSuccess && (
            <div style={{ backgroundColor: '#DCFCE7', border: '1px solid #BBF7D0', color: '#166534', padding: '10px 14px', borderRadius: '6px', fontSize: '0.82rem', marginBottom: '16px' }}>
              Password updated successfully.
            </div>
          )}

          {passError && (
            <div style={{ backgroundColor: '#FEF2F2', border: '1px solid #FECACA', color: '#991B1B', padding: '10px 14px', borderRadius: '6px', fontSize: '0.82rem', marginBottom: '16px' }}>
              {passError}
            </div>
          )}

          <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
                Current Password
              </label>
              <input
                type="password"
                required
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', fontSize: '0.86rem' }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
                  New Password
                </label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', fontSize: '0.86rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
                  Confirm New Password
                </label>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', fontSize: '0.86rem' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '6px' }}>
              <button
                type="submit"
                style={{ backgroundColor: '#1C1917', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '9px 18px', fontSize: '0.84rem', fontWeight: 600, cursor: 'pointer' }}
              >
                Update Password
              </button>
            </div>
          </form>
        </div>

        {/* Danger Zone: Account Deletion */}
        <div style={{ border: '1px solid #FECACA', backgroundColor: '#FFF5F5', borderRadius: '12px', padding: '24px' }}>
          <h3 style={{ fontSize: '0.96rem', fontWeight: 700, color: '#991B1B', marginBottom: '4px' }}>
            Danger Zone
          </h3>
          <p style={{ fontSize: '0.8rem', color: '#7F1D1D', marginBottom: '14px' }}>
            Permanently delete your account, your personal verification history, and all stored claim audit data.
          </p>
          <button
            type="button"
            onClick={handleDeleteAccount}
            style={{ backgroundColor: '#DC2626', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '8px 16px', fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer' }}
          >
            Delete My Account & Data
          </button>
        </div>
      </div>
    </div>
  );
}
