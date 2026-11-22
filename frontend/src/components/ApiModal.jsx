import React from 'react';
import { Sliders, X, Terminal, Cpu, Check, Copy } from 'lucide-react';

export default function ApiSettingsModal({ isOpen, onClose, backendHealthy, backendInfo }) {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(28, 25, 23, 0.4)',
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
          width: '580px',
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
            <Terminal size={17} color="#5E50EE" />
            <span style={{ fontSize: '0.98rem', fontWeight: 700, color: '#1C1917' }}>
              TruthGuard REST API & Model Config
            </span>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#78716C' }}
          >
            <X size={16} />
          </button>
        </div>

        <div style={{ padding: '20px', maxHeight: '480px', overflowY: 'auto' }}>
          {/* Status Badge */}
          <div
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              backgroundColor: backendHealthy ? '#DCFCE7' : '#FEF2F2',
              border: backendHealthy ? '1px solid #BBF7D0' : '1px solid #FECACA',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '18px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: backendHealthy ? '#16A34A' : '#DC2626'
                }}
              />
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: backendHealthy ? '#166534' : '#991B1B' }}>
                {backendHealthy ? 'FastAPI Backend Online (Port 8000)' : 'FastAPI Backend Offline (Preset Mode Active)'}
              </span>
            </div>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              style={{
                fontSize: '0.75rem',
                color: backendHealthy ? '#15803D' : '#991B1B',
                fontWeight: 600,
                textDecoration: 'none'
              }}
            >
              Open Swagger Docs →
            </a>
          </div>

          {/* Quick Endpoint Example */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#78716C', textTransform: 'uppercase', marginBottom: '6px' }}>
              POST /api/pipeline
            </div>
            <pre
              style={{
                backgroundColor: '#FAF8F5',
                border: '1px solid #E8E5DC',
                borderRadius: '8px',
                padding: '12px',
                fontSize: '0.76rem',
                color: '#1C1917',
                fontFamily: 'var(--font-mono)',
                overflowX: 'auto',
                lineHeight: '1.5'
              }}
            >
{`curl -X POST "http://localhost:8000/api/pipeline" \\
  -H "Content-Type: application/json" \\
  -d '{"answer": "The Eiffel Tower was built in 1892."}'`}
            </pre>
          </div>

          {/* Calibration & Hyperparameters Info */}
          <div style={{ fontSize: '0.8rem', color: '#57534E', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #F3EFE7', paddingBottom: '6px' }}>
              <span style={{ fontWeight: 600 }}>Entailment Threshold (τ_E):</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>0.70</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #F3EFE7', paddingBottom: '6px' }}>
              <span style={{ fontWeight: 600 }}>Contradiction Threshold (τ_C):</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>0.70</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #F3EFE7', paddingBottom: '6px' }}>
              <span style={{ fontWeight: 600 }}>Retrieval Gate (τ_r):</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>0.10</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #F3EFE7', paddingBottom: '6px' }}>
              <span style={{ fontWeight: 600 }}>NEI Credit Parameter (λ):</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>0.50</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #F3EFE7', paddingBottom: '6px' }}>
              <span style={{ fontWeight: 600 }}>NLI Verifier:</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>DeBERTa-v3-large</span>
            </div>
          </div>
        </div>

        <div
          style={{
            padding: '12px 20px',
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
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
