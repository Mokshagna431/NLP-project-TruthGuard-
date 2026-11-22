import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Users,
  CheckCircle,
  Database,
  Cpu,
  Activity,
  Search,
  Lock,
  Unlock,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import { api } from '../services/api';

export default function AdminDashboard() {
  const [overview, setOverview] = useState(null);
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [togglingId, setTogglingId] = useState(null);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [ovRes, usersRes] = await Promise.all([
        api.getAdminOverview(),
        api.listAdminUsers(search ? `search=${encodeURIComponent(search)}` : '')
      ]);
      setOverview(ovRes);
      setUsers(usersRes.users || []);
    } catch (err) {
      console.error("Admin data fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchAdminData();
  };

  const handleToggleStatus = async (userId, currentStatus) => {
    setTogglingId(userId);
    try {
      await api.toggleUserStatus(userId, !currentStatus);
      fetchAdminData();
    } catch (err) {
      alert("Failed to update user status: " + err.message);
    } finally {
      setTogglingId(null);
    }
  };

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '28px' }}>
        
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#DC2626', fontFamily: 'var(--font-mono)' }}>
              ADMINISTRATOR CONSOLE (RBAC PROTECTED)
            </div>
            <h1 className="font-serif" style={{ fontSize: '2.5rem', fontWeight: 600, color: '#1C1917', lineHeight: 1.15, marginTop: '4px' }}>
              Platform Operations & Governance
            </h1>
            <p style={{ fontSize: '0.86rem', color: '#57534E', marginTop: '4px' }}>
              Manage registered users, inspect hardware load, review audit trails, and check ML model availability.
            </p>
          </div>

          <button
            onClick={fetchAdminData}
            style={{
              backgroundColor: '#FFFFFF',
              border: '1px solid #D5D1C6',
              borderRadius: '6px',
              padding: '8px 14px',
              fontSize: '0.8rem',
              fontWeight: 600,
              color: '#1C1917',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <RefreshCw size={14} />
            Refresh Telemetry
          </button>
        </div>

        {/* 4 Metric Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '20px' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#78716C', textTransform: 'uppercase' }}>Total Registered Users</div>
            <div className="font-serif" style={{ fontSize: '2.2rem', fontWeight: 700, color: '#1C1917', marginTop: '4px' }}>
              {overview?.total_users || 0}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#16A34A', marginTop: '4px' }}>
              {overview?.active_users || 0} currently active
            </div>
          </div>

          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '20px' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#78716C', textTransform: 'uppercase' }}>Total Verifications</div>
            <div className="font-serif" style={{ fontSize: '2.2rem', fontWeight: 700, color: '#1C1917', marginTop: '4px' }}>
              {overview?.total_verifications || 0}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#78716C', marginTop: '4px' }}>
              Across all user accounts
            </div>
          </div>

          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '20px' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#78716C', textTransform: 'uppercase' }}>Total Claims Audited</div>
            <div className="font-serif" style={{ fontSize: '2.2rem', fontWeight: 700, color: '#1C1917', marginTop: '4px' }}>
              {overview?.total_claims_processed || 0}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#78716C', marginTop: '4px' }}>
              Atomic propositions stored
            </div>
          </div>

          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '20px' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#78716C', textTransform: 'uppercase' }}>CPU / Memory Utilization</div>
            <div className="font-serif" style={{ fontSize: '1.8rem', fontWeight: 700, color: '#1C1917', marginTop: '6px' }}>
              {overview?.cpu_percent || 0}% / {overview?.memory_percent || 0}%
            </div>
            <div style={{ fontSize: '0.74rem', color: '#16A34A', marginTop: '4px' }}>
              Intel 12-Core Multi-Thread
            </div>
          </div>
        </div>

        {/* Loaded ML Models Banner */}
        <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '20px 24px' }}>
          <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#78716C', textTransform: 'uppercase', marginBottom: '10px' }}>
            Loaded Pipeline Model Caches
          </div>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {(overview?.loaded_models || [
              "DeBERTa-v3-large (Calibrated NLI)",
              "all-MiniLM-L6-v2 (Dense SBERT)",
              "ms-marco-MiniLM-L-6-v2 (CrossEncoder)",
              "spaCy Coref & Sentencizer"
            ]).map((m, idx) => (
              <span
                key={idx}
                style={{
                  backgroundColor: '#FAF8F5',
                  border: '1px solid #D5D1C6',
                  borderRadius: '6px',
                  padding: '5px 12px',
                  fontSize: '0.76rem',
                  fontFamily: 'var(--font-mono)',
                  color: '#1C1917',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#16A34A' }} />
                {m}
              </span>
            ))}
          </div>
        </div>

        {/* User Management Section */}
        <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
            <div>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1C1917' }}>User Governance</h2>
              <p style={{ fontSize: '0.78rem', color: '#78716C' }}>Inspect account status and enforce policy moderation.</p>
            </div>

            <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                placeholder="Search username or email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid #D5D1C6', fontSize: '0.8rem', outline: 'none' }}
              />
              <button
                type="submit"
                style={{ backgroundColor: '#1C1917', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '6px 12px', fontSize: '0.8rem', cursor: 'pointer' }}
              >
                Search
              </button>
            </form>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #E8E5DC', color: '#78716C' }}>
                  <th style={{ padding: '10px 8px' }}>User</th>
                  <th style={{ padding: '10px 8px' }}>Email</th>
                  <th style={{ padding: '10px 8px' }}>Role</th>
                  <th style={{ padding: '10px 8px' }}>Verifications</th>
                  <th style={{ padding: '10px 8px' }}>Status</th>
                  <th style={{ padding: '10px 8px', textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} style={{ borderBottom: '1px solid #F3EFE7' }}>
                    <td style={{ padding: '12px 8px', fontWeight: 600 }}>{u.full_name} ({u.username})</td>
                    <td style={{ padding: '12px 8px', color: '#57534E' }}>{u.email}</td>
                    <td style={{ padding: '12px 8px' }}>
                      <span style={{ backgroundColor: u.role === 'admin' ? '#FEF3C7' : '#F3EFE7', color: u.role === 'admin' ? '#B45309' : '#57534E', padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700 }}>
                        {u.role.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '12px 8px' }}>{u.verifications_count}</td>
                    <td style={{ padding: '12px 8px' }}>
                      <span style={{ color: u.is_active ? '#16A34A' : '#DC2626', fontWeight: 600 }}>
                        {u.is_active ? 'Active' : 'Suspended'}
                      </span>
                    </td>
                    <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                      {u.role !== 'admin' && (
                        <button
                          onClick={() => handleToggleStatus(u.id, u.is_active)}
                          disabled={togglingId === u.id}
                          style={{
                            backgroundColor: u.is_active ? '#FEF2F2' : '#F0FDF4',
                            border: u.is_active ? '1px solid #FECACA' : '1px solid #BBF7D0',
                            color: u.is_active ? '#DC2626' : '#16A34A',
                            borderRadius: '4px',
                            padding: '4px 10px',
                            fontSize: '0.74rem',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          {u.is_active ? 'Suspend' : 'Reactivate'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
