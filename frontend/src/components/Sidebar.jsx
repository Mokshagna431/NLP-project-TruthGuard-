import React from 'react';
import {
  LayoutDashboard,
  CheckCircle,
  History,
  BookmarkCheck,
  BarChart3,
  User,
  Settings,
  HelpCircle,
  ShieldAlert,
  LogOut,
  Bell,
  Sparkles,
  Database,
  BookOpen,
  Award
} from 'lucide-react';

export default function Sidebar({
  activeNav,
  setActiveNav,
  currentUser,
  notificationsCount = 1,
  onOpenNotifications,
  onLogout
}) {
  const isAdmin = currentUser?.role === 'admin';

  const navSections = [
    {
      title: 'VERIFY',
      items: [
        { id: 'overview', label: 'Overview', icon: LayoutDashboard },
        { id: 'factcheck', label: 'Fact Check', icon: Sparkles },
        { id: 'new-verification', label: 'New Verification', icon: CheckCircle },
        { id: 'citation', label: 'Citation Audit', icon: BookOpen },
        { id: 'history', label: 'Verification History', icon: History },
        { id: 'saved', label: 'Saved Results', icon: BookmarkCheck }
      ]
    },
    {
      title: 'ANALYSIS & REPORTS',
      items: [
        { id: 'analytics', label: 'Analytics', icon: BarChart3 },
        { id: 'evidence', label: 'Evidence Library', icon: Database },
        { id: 'benchmarks', label: 'Research Matrix', icon: Award }
      ]
    },
    {
      title: 'ACCOUNT & SYSTEM',
      items: [
        { id: 'profile', label: 'Profile', icon: User },
        { id: 'settings', label: 'Settings', icon: Settings },
        ...(isAdmin ? [{ id: 'admin', label: 'Admin Dashboard', icon: ShieldAlert }] : [])
      ]
    }
  ];

  return (
    <aside
      style={{
        width: '240px',
        minWidth: '240px',
        backgroundColor: '#FAF8F5',
        borderRight: '1px solid #E8E5DC',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '100vh',
        position: 'sticky',
        top: 0,
        userSelect: 'none',
        zIndex: 20
      }}
    >
      {/* Top Header & Navigation Links */}
      <div style={{ overflowY: 'auto', padding: '24px 16px 12px 16px' }}>
        {/* Brand */}
        <div
          onClick={() => setActiveNav('overview')}
          style={{ marginBottom: '28px', paddingLeft: '8px', cursor: 'pointer' }}
        >
          <div
            className="font-serif"
            style={{
              fontSize: '1.45rem',
              fontWeight: 700,
              letterSpacing: '-0.02em',
              color: '#181614',
              lineHeight: 1.15
            }}
          >
            TruthGuard
          </div>
          <div
            style={{
              fontSize: '0.62rem',
              fontWeight: 600,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              color: '#8B857D',
              marginTop: '4px',
              fontFamily: 'var(--font-mono)'
            }}
          >
            THE MERIDIAN • PROOF DESK
          </div>
        </div>

        {/* Section Groups */}
        {navSections.map((sec, idx) => (
          <div key={idx} style={{ marginBottom: '22px' }}>
            <div
              style={{
                fontSize: '0.65rem',
                fontWeight: 700,
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                color: '#9CA3AF',
                marginBottom: '8px',
                paddingLeft: '10px'
              }}
            >
              {sec.title}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              {sec.items.map((item) => {
                const isActive = activeNav === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveNav(item.id)}
                    style={{
                      position: 'relative',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      border: 'none',
                      background: isActive ? '#EAE6DC' : 'transparent',
                      color: isActive ? '#1A1816' : '#57534E',
                      fontWeight: isActive ? 600 : 400,
                      fontSize: '0.84rem',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'background 0.12s ease, color 0.12s ease'
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) e.currentTarget.style.backgroundColor = '#F2EFE9';
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    {/* Active Accent Bar */}
                    {isActive && (
                      <span
                        style={{
                          position: 'absolute',
                          left: 0,
                          top: '18%',
                          bottom: '18%',
                          width: '3px',
                          backgroundColor: '#DC2626',
                          borderRadius: '0 2px 2px 0'
                        }}
                      />
                    )}
                    <item.icon size={15} strokeWidth={isActive ? 2.2 : 1.7} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Bottom Footer */}
      <div
        style={{
          borderTop: '1px solid #E8E5DC',
          padding: '14px 16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          backgroundColor: '#FAF8F5'
        }}
      >
        <button
          onClick={onOpenNotifications}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            width: '100%',
            padding: '7px 10px',
            borderRadius: '6px',
            border: 'none',
            background: 'transparent',
            color: '#57534E',
            fontSize: '0.82rem',
            cursor: 'pointer',
            textAlign: 'left'
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#F2EFE9')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
            <Bell size={15} />
            <span>Notifications</span>
          </div>
          {notificationsCount > 0 && (
            <span
              style={{
                backgroundColor: '#DC2626',
                color: '#FFFFFF',
                borderRadius: '10px',
                padding: '1px 6px',
                fontSize: '0.68rem',
                fontWeight: 700
              }}
            >
              {notificationsCount}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveNav('help')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '9px',
            width: '100%',
            padding: '7px 10px',
            borderRadius: '6px',
            border: 'none',
            background: 'transparent',
            color: '#57534E',
            fontSize: '0.82rem',
            cursor: 'pointer',
            textAlign: 'left'
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#F2EFE9')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          <HelpCircle size={15} />
          <span>Help & Support</span>
        </button>

        {/* User Card */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginTop: '8px',
            padding: '8px 10px',
            borderRadius: '8px',
            backgroundColor: '#F3EFE7',
            border: '1px solid #E5E1D6'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
            <div
              style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                backgroundColor: '#1C1917',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.72rem',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                flexShrink: 0
              }}
            >
              {currentUser?.username?.substring(0, 2).toUpperCase() || 'TG'}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
              <span
                style={{
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  color: '#1C1917',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}
              >
                {currentUser?.full_name || 'Guest User'}
              </span>
              <span style={{ fontSize: '0.66rem', color: '#78716C' }}>
                {isAdmin ? 'Administrator' : 'Proof Desk Analyst'}
              </span>
            </div>
          </div>

          <button
            onClick={onLogout}
            title="Log out"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: '#78716C',
              padding: '4px'
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#DC2626')}
            onMouseLeave={(e) => (e.currentTarget.style.color = '#78716C')}
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </aside>
  );
}
