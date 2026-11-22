import React, { useState, useEffect } from 'react';
import { Settings, Moon, Sun, Bell, Sliders, Shield, Download, Trash2, Check } from 'lucide-react';
import { api } from '../services/api';

export default function SettingsView({ onLogout }) {
  const [theme, setTheme] = useState('light');
  const [language, setLanguage] = useState('en');
  const [defaultMode, setDefaultMode] = useState('standard');
  const [defaultCorrection, setDefaultCorrection] = useState('grounded');
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [verifAlerts, setVerifAlerts] = useState(true);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSettings()
      .then((res) => {
        setTheme(res.theme || 'light');
        setLanguage(res.language || 'en');
        setDefaultMode(res.default_verification_mode || 'standard');
        setDefaultCorrection(res.default_correction_mode || 'grounded');
        const notifs = res.notification_preferences || {};
        setEmailAlerts(notifs.email_alerts ?? true);
        setVerifAlerts(notifs.verification_complete ?? true);
      })
      .catch((err) => console.error("Settings load error:", err))
      .finally(() => setLoading(false));
  }, []);

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    try {
      await api.updateSettings({
        theme,
        language,
        default_verification_mode: defaultMode,
        default_correction_mode: defaultCorrection,
        notification_preferences: {
          email_alerts: emailAlerts,
          verification_complete: verifAlerts
        }
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert("Failed to save settings: " + err.message);
    }
  };

  const handleDownloadPersonalData = async () => {
    try {
      const history = await api.listVerifications('page=1&page_size=100');
      const blob = new Blob([JSON.stringify(history, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `TruthGuard_Personal_Data_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
    } catch (err) {
      alert("Could not export data: " + err.message);
    }
  };

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        <div>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
            WORKSPACE PREFERENCES
          </div>
          <h1 className="font-serif" style={{ fontSize: '2.5rem', fontWeight: 600, color: '#1C1917', lineHeight: 1.15, marginTop: '4px' }}>
            System Settings
          </h1>
          <p style={{ fontSize: '0.86rem', color: '#57534E', marginTop: '4px' }}>
            Configure model thresholds, default verification pipelines, and notification dispatches.
          </p>
        </div>

        {savedSuccess && (
          <div style={{ backgroundColor: '#DCFCE7', border: '1px solid #BBF7D0', color: '#166534', padding: '12px 16px', borderRadius: '8px', fontSize: '0.84rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Check size={16} />
            <span>Preferences saved successfully to database.</span>
          </div>
        )}

        <form onSubmit={handleSaveSettings} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Appearance Section */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '24px' }}>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1C1917', marginBottom: '4px' }}>
              Appearance
            </h2>
            <p style={{ fontSize: '0.78rem', color: '#78716C', marginBottom: '16px' }}>
              Select your preferred visual theme for the Proof Desk workbench.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              {[
                { id: 'light', label: 'Editorial Warm (Default)', icon: Sun },
                { id: 'dark', label: 'Dark Obsidian', icon: Moon },
                { id: 'system', label: 'System Automatic', icon: Sliders }
              ].map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setTheme(opt.id)}
                  style={{
                    backgroundColor: theme === opt.id ? '#F5F3ED' : '#FFFFFF',
                    border: theme === opt.id ? '2px solid #1C1917' : '1px solid #D5D1C6',
                    borderRadius: '8px',
                    padding: '14px',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '8px',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    color: '#1C1917'
                  }}
                >
                  <opt.icon size={18} />
                  <span>{opt.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Verification Pipeline Defaults */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '24px' }}>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1C1917', marginBottom: '4px' }}>
              Pipeline Defaults
            </h2>
            <p style={{ fontSize: '0.78rem', color: '#78716C', marginBottom: '16px' }}>
              Configure your default execution parameters for new verification submissions.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
                  Default Verification Depth
                </label>
                <select
                  value={defaultMode}
                  onChange={(e) => setDefaultMode(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', fontSize: '0.86rem' }}
                >
                  <option value="quick">Quick (BM25 + Sentence SBERT)</option>
                  <option value="standard">Standard (Hybrid RRF + DeBERTa-v3 NLI)</option>
                  <option value="deep">Deep (Cross-Encoder Re-rank + Multi-round M5)</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
                  Default Grounded Correction Mode
                </label>
                <select
                  value={defaultCorrection}
                  onChange={(e) => setDefaultCorrection(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: '6px', border: '1px solid #D5D1C6', backgroundColor: '#FAF8F5', fontSize: '0.86rem' }}
                >
                  <option value="grounded">Evidence-Grounded Revision (M5)</option>
                  <option value="minimal">Minimal Token Removal</option>
                  <option value="none">Audit Only (No Rewriting)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '24px' }}>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1C1917', marginBottom: '4px' }}>
              Notification Preferences
            </h2>
            <p style={{ fontSize: '0.78rem', color: '#78716C', marginBottom: '16px' }}>
              Manage alerts dispatched upon pipeline completion or critical hallucination detections.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#1C1917' }}>Verification Completion Alerts</div>
                  <div style={{ fontSize: '0.75rem', color: '#78716C' }}>Notify when long-running multi-claim batch audits finish processing.</div>
                </div>
                <input
                  type="checkbox"
                  checked={verifAlerts}
                  onChange={(e) => setVerifAlerts(e.target.checked)}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid #F3EFE7', paddingTop: '10px' }}>
                <div>
                  <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#1C1917' }}>Critical Hallucination Alerts</div>
                  <div style={{ fontSize: '0.75rem', color: '#78716C' }}>Flag severe contradictions with P_C ≥ 0.90 requiring editorial sign-off.</div>
                </div>
                <input
                  type="checkbox"
                  checked={emailAlerts}
                  onChange={(e) => setEmailAlerts(e.target.checked)}
                />
              </div>
            </div>
          </div>

          {/* Privacy & Data Portability */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '24px' }}>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1C1917', marginBottom: '4px' }}>
              Privacy & Data Portability
            </h2>
            <p style={{ fontSize: '0.78rem', color: '#78716C', marginBottom: '14px' }}>
              Export an archive of all your verification jobs, claims, and reliability logs.
            </p>
            <button
              type="button"
              onClick={handleDownloadPersonalData}
              style={{
                backgroundColor: '#FAF8F5',
                border: '1px solid #D5D1C6',
                borderRadius: '6px',
                padding: '8px 14px',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: '#1C1917',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Download size={14} />
              Export Full Personal Data (JSON)
            </button>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="submit"
              style={{
                backgroundColor: '#1C1917',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '6px',
                padding: '11px 24px',
                fontSize: '0.88rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Save All Settings
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
