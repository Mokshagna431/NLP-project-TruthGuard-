import React from 'react';
import { ShieldCheck, User, LogOut, LayoutDashboard, ChevronRight } from 'lucide-react';

export default function Navbar({
  currentView,
  setCurrentView,
  currentUser,
  onOpenAuth,
  onLogout
}) {
  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 40,
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E8E5DC',
        padding: '0 36px',
        height: '66px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        boxShadow: '0 1px 3px rgba(0,0,0,0.02)'
      }}
    >
      {/* Brand Logo & Name */}
      <div
        onClick={() => setCurrentView('landing')}
        style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}
      >
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #1C1917 0%, #44403C 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 6px rgba(0,0,0,0.15)'
          }}
        >
          <ShieldCheck size={20} color="#FFFFFF" />
        </div>
        <div>
          <span
            className="font-serif"
            style={{ fontSize: '1.25rem', fontWeight: 700, color: '#1C1917', letterSpacing: '-0.02em' }}
          >
            TruthGuard
          </span>
          <span style={{ fontSize: '0.68rem', color: '#78716C', marginLeft: '6px', fontWeight: 600 }}>
            v2.0 PROOF DESK
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ display: 'flex', alignItems: 'center', gap: '28px' }}>
        {[
          { id: 'landing', label: 'Home' },
          { id: 'about', label: 'About' },
          { id: 'docs', label: 'Documentation' },
          { id: 'contact', label: 'Contact & Feedback' }
        ].map((item) => {
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '0.86rem',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? '#1C1917' : '#57534E',
                cursor: 'pointer',
                padding: '6px 0',
                position: 'relative'
              }}
              onMouseEnter={(e) => (e.target.style.color = '#1C1917')}
              onMouseLeave={(e) => {
                if (!isActive) e.target.style.color = '#57534E';
              }}
            >
              {item.label}
              {isActive && (
                <span
                  style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: '2px',
                    backgroundColor: '#1C1917',
                    borderRadius: '2px'
                  }}
                />
              )}
            </button>
          );
        })}
      </nav>

      {/* Action Buttons / User Menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {currentUser ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button
              onClick={() => setCurrentView('dashboard')}
              style={{
                backgroundColor: '#1C1917',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 16px',
                fontSize: '0.84rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}
            >
              <LayoutDashboard size={15} />
              Proof Desk
            </button>

            <button
              onClick={onLogout}
              style={{
                backgroundColor: '#FAF8F5',
                border: '1px solid #D5D1C6',
                color: '#57534E',
                borderRadius: '6px',
                padding: '7px 12px',
                fontSize: '0.8rem',
                fontWeight: 500,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
              title="Log out"
            >
              <LogOut size={14} />
              Logout
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={() => onOpenAuth('login')}
              style={{
                background: 'none',
                border: '1px solid transparent',
                borderRadius: '6px',
                padding: '8px 14px',
                fontSize: '0.84rem',
                fontWeight: 600,
                color: '#1C1917',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#F5F3ED')}
              onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
            >
              Sign In
            </button>

            <button
              onClick={() => onOpenAuth('register')}
              style={{
                backgroundColor: '#1C1917',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '6px',
                padding: '8px 18px',
                fontSize: '0.84rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
              }}
            >
              Try TruthGuard
              <ChevronRight size={14} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
