import React, { useState, useEffect } from 'react';
import { BookmarkCheck, Trash2, ArrowRight, FileText, RefreshCw, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

export default function SavedCasesView({ onViewVerification, onNewVerification }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSaved = async () => {
    setLoading(true);
    try {
      const res = await api.listSaved();
      setItems(res || []);
    } catch (err) {
      console.error("Saved cases fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleRemove = async (id) => {
    try {
      await api.removeSaved(id);
      fetchSaved();
    } catch (err) {
      console.error("Remove saved error:", err);
    }
  };

  const getReliabilityColor = (score) => {
    if (score >= 0.7) return '#16A34A';
    if (score >= 0.4) return '#EA580C';
    return '#DC2626';
  };

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        <div>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
            BOOKMARKED ANALYSES
          </div>
          <h1 className="font-serif" style={{ fontSize: '2.5rem', fontWeight: 600, color: '#1C1917', lineHeight: 1.15, marginTop: '4px' }}>
            Saved Results & Case Files
          </h1>
          <p style={{ fontSize: '0.86rem', color: '#57534E', marginTop: '4px' }}>
            Quick access to your bookmarked hallucination audits and critical verified cases.
          </p>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px', color: '#78716C' }}>
            <RefreshCw size={20} className="pulse-indicator" style={{ margin: '0 auto 8px auto' }} />
            Loading saved cases...
          </div>
        ) : items.length === 0 ? (
          <div style={{ backgroundColor: '#FFFFFF', borderRadius: '12px', border: '1px solid #E8E5DC', padding: '60px 24px', textAlign: 'center' }}>
            <BookmarkCheck size={42} color="#D5D1C6" style={{ margin: '0 auto 12px auto' }} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1C1917', marginBottom: '4px' }}>
              No Saved Results Yet
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#78716C', maxWidth: '380px', margin: '0 auto 18px auto' }}>
              Bookmark important analyses from the verification results or history screen to keep them organized here.
            </p>
            <button
              onClick={onNewVerification}
              style={{ backgroundColor: '#1C1917', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '8px 16px', fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer' }}
            >
              Start New Verification
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '18px' }}>
            {items.map((job) => (
              <div
                key={job.id}
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #E8E5DC',
                  borderRadius: '12px',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '14px',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.02)'
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 700, fontSize: '0.96rem', color: '#1C1917' }}>
                      {job.title}
                    </div>
                    <span style={{ fontSize: '1.2rem', fontWeight: 800, color: getReliabilityColor(job.reliability_score), fontFamily: 'var(--font-mono)' }}>
                      {(job.reliability_score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <p style={{ fontSize: '0.84rem', color: '#57534E', lineHeight: '1.5', margin: '0 0 12px 0', maxHeight: '60px', overflow: 'hidden' }}>
                    {job.original_text}
                  </p>

                  <div style={{ display: 'flex', gap: '10px', fontSize: '0.74rem', color: '#78716C', borderTop: '1px solid #F3EFE7', paddingTop: '10px' }}>
                    <span>{job.total_claims} Claims</span>
                    <span>•</span>
                    <span style={{ color: '#16A34A' }}>{job.supported_count} Supported</span>
                    <span>•</span>
                    <span style={{ color: '#DC2626' }}>{job.contradicted_count} Contradicted</span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '8px' }}>
                  <button
                    onClick={() => handleRemove(job.id)}
                    style={{ background: 'none', border: 'none', color: '#DC2626', fontSize: '0.75rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    <Trash2 size={13} />
                    Remove Bookmark
                  </button>

                  <button
                    onClick={() => onViewVerification(job.id)}
                    style={{
                      backgroundColor: '#1C1917',
                      color: '#FFFFFF',
                      border: 'none',
                      borderRadius: '6px',
                      padding: '6px 12px',
                      fontSize: '0.78rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    View Case <ArrowRight size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
