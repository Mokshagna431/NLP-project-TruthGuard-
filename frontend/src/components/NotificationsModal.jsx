import React from 'react';
import { Bell, Check, X, AlertTriangle, ShieldCheck, Clock } from 'lucide-react';

export default function NotificationsModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const notifications = [
    {
      id: 1,
      title: 'New Disputed Claim Flagged',
      time: '12m ago',
      desc: 'Article "The Renaissance" contains 3 contradicted claims requiring editor sign-off.',
      unread: true,
      icon: AlertTriangle,
      color: '#EA580C'
    },
    {
      id: 2,
      title: 'Calibration Health Check Passed',
      time: '2h ago',
      desc: 'DeBERTa-v3 NLI Expected Calibration Error (ECE) is 0.041, below target drift threshold.',
      unread: false,
      icon: ShieldCheck,
      color: '#16A34A'
    },
    {
      id: 3,
      title: 'Wire Ingest Completed',
      time: '4h ago',
      desc: 'Processed 156 incoming articles from Reuters & AP wire with automated atomic splitting.',
      unread: false,
      icon: Clock,
      color: '#5E50EE'
    }
  ];

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(28, 25, 23, 0.35)',
        backdropFilter: 'blur(3px)',
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '460px',
          maxWidth: '92vw',
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
          border: '1px solid #E8E5DC',
          overflow: 'hidden'
        }}
      >
        <div
          style={{
            padding: '16px 20px',
            borderBottom: '1px solid #E8E5DC',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bell size={16} color="#1C1917" />
            <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1C1917' }}>Proof Desk Alerts</span>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#78716C' }}
          >
            <X size={16} />
          </button>
        </div>

        <div style={{ maxHeight: '360px', overflowY: 'auto', padding: '12px' }}>
          {notifications.map((n) => {
            const Icon = n.icon;
            return (
              <div
                key={n.id}
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  backgroundColor: n.unread ? '#FAF8F5' : '#FFFFFF',
                  border: n.unread ? '1px solid #E8E5DC' : '1px solid transparent',
                  marginBottom: '8px',
                  display: 'flex',
                  gap: '12px'
                }}
              >
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    backgroundColor: '#F3EFE7',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}
                >
                  <Icon size={16} color={n.color} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                    <span style={{ fontSize: '0.84rem', fontWeight: 600, color: '#1C1917' }}>{n.title}</span>
                    <span style={{ fontSize: '0.72rem', color: '#78716C' }}>{n.time}</span>
                  </div>
                  <p style={{ fontSize: '0.78rem', color: '#57534E', margin: 0, lineHeight: '1.45' }}>
                    {n.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        <div
          style={{
            padding: '12px 18px',
            borderTop: '1px solid #E8E5DC',
            backgroundColor: '#FAF8F5',
            display: 'flex',
            justifyContent: 'flex-end'
          }}
        >
          <button
            onClick={onClose}
            style={{
              backgroundColor: '#1C1917',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              padding: '6px 14px',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Mark all as read
          </button>
        </div>
      </div>
    </div>
  );
}
