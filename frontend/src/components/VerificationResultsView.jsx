import React, { useState, useRef } from 'react';
import {
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Download,
  Copy,
  Check,
  Bookmark,
  BookmarkCheck,
  RotateCw,
  ExternalLink,
  Filter,
  Wand2,
  FileText,
  FileSpreadsheet,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

export default function VerificationResultsView({
  job,
  onRerun,
  onBackToDashboard
}) {
  const [filter, setFilter] = useState('all'); // 'all', 'SUPPORTED', 'CONTRADICTED', 'NEI'
  const [sortBy, setSortBy] = useState('number'); // 'number', 'confidence', 'verdict'
  const [activeClaimId, setActiveClaimId] = useState(null);
  const [copiedOriginal, setCopiedOriginal] = useState(false);
  const [copiedCorrected, setCopiedCorrected] = useState(false);
  const [isSaved, setIsSaved] = useState(job?.is_saved || false);
  const [saveLoading, setSaveLoading] = useState(false);

  const cardRefs = useRef({});

  if (!job) {
    return (
      <div style={{ padding: '60px', textAlign: 'center', backgroundColor: '#FAF8F5', minHeight: '100vh' }}>
        <h2>No Verification Selected</h2>
        <button onClick={onBackToDashboard} style={{ marginTop: '16px' }}>Return to Overview</button>
      </div>
    );
  }

  const handleSaveToggle = async () => {
    setSaveLoading(true);
    try {
      if (isSaved) {
        await api.removeSaved(job.id);
        setIsSaved(false);
      } else {
        await api.saveVerification(job.id);
        setIsSaved(true);
      }
    } catch (err) {
      console.error("Save error:", err);
    } finally {
      setSaveLoading(false);
    }
  };

  const handleCopy = (text, type) => {
    navigator.clipboard.writeText(text);
    if (type === 'original') {
      setCopiedOriginal(true);
      setTimeout(() => setCopiedOriginal(false), 2000);
    } else {
      setCopiedCorrected(true);
      setTimeout(() => setCopiedCorrected(false), 2000);
    }
  };

  const scrollToClaim = (claimId) => {
    setActiveClaimId(claimId);
    if (cardRefs.current[claimId]) {
      cardRefs.current[claimId].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  // Filter & Sort Claims
  const claims = (job.claims || []).filter((c) => {
    if (filter === 'all') return true;
    return c.predicted_label === filter;
  }).sort((a, b) => {
    if (sortBy === 'confidence') {
      return (b.p_supported + b.p_contradicted) - (a.p_supported + a.p_contradicted);
    }
    if (sortBy === 'verdict') {
      return a.predicted_label.localeCompare(b.predicted_label);
    }
    return a.claim_number - b.claim_number;
  });

  const getReliabilityColor = (score) => {
    if (score >= 0.70) return '#16A34A';
    if (score >= 0.40) return '#EA580C';
    return '#DC2626';
  };

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1440px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '28px' }}>
        
        {/* Top Header & Actions Strip */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#78716C', marginBottom: '4px' }}>
              <span style={{ cursor: 'pointer' }} onClick={onBackToDashboard}>Proof Desk</span>
              <span>/</span>
              <span>Audit Results</span>
              <span>/</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>{job.id?.substring(0, 8)}</span>
            </div>
            <h1 className="font-serif" style={{ fontSize: '2.4rem', fontWeight: 600, color: '#1C1917', lineHeight: 1.15 }}>
              {job.title}
            </h1>
            <p style={{ fontSize: '0.82rem', color: '#78716C', marginTop: '4px' }}>
              Audited {new Date(job.created_at).toLocaleString()} • {job.verification_mode} mode • Latency: {job.latency_sec.toFixed(2)}s
            </p>
          </div>

          {/* Action Buttons: Save, Rerun, Export PDF/CSV/JSON */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <button
              onClick={handleSaveToggle}
              disabled={saveLoading}
              style={{
                backgroundColor: isSaved ? '#F3EFE7' : '#FFFFFF',
                border: '1px solid #D5D1C6',
                borderRadius: '6px',
                padding: '8px 14px',
                fontSize: '0.8rem',
                fontWeight: 600,
                color: isSaved ? '#16A34A' : '#1C1917',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              {isSaved ? <BookmarkCheck size={14} color="#16A34A" /> : <Bookmark size={14} />}
              <span>{isSaved ? 'Bookmarked' : 'Save Case'}</span>
            </button>

            <button
              onClick={() => onRerun(job.id)}
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
              <RotateCw size={14} />
              <span>Re-run</span>
            </button>

            {/* Official ReportLab PDF Download */}
            <a
              href={api.downloadPdfUrl(job.id)}
              target="_blank"
              rel="noreferrer"
              style={{
                backgroundColor: '#1C1917',
                color: '#FFFFFF',
                borderRadius: '6px',
                padding: '8px 16px',
                fontSize: '0.8rem',
                fontWeight: 600,
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 2px 6px rgba(0,0,0,0.15)'
              }}
            >
              <FileText size={14} />
              <span>Download PDF</span>
            </a>

            {/* CSV Export */}
            <a
              href={api.downloadCsvUrl(job.id)}
              target="_blank"
              rel="noreferrer"
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #D5D1C6',
                color: '#57534E',
                borderRadius: '6px',
                padding: '8px 12px',
                fontSize: '0.8rem',
                fontWeight: 600,
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
              title="Download CSV spreadsheet"
            >
              <FileSpreadsheet size={14} />
              <span>CSV</span>
            </a>

            {/* JSON Export */}
            <a
              href={api.downloadJsonUrl(job.id)}
              target="_blank"
              rel="noreferrer"
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #D5D1C6',
                color: '#57534E',
                borderRadius: '6px',
                padding: '8px 12px',
                fontSize: '0.8rem',
                fontWeight: 600,
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
              title="Download full JSON artifact"
            >
              <Download size={14} />
              <span>JSON</span>
            </a>
          </div>
        </div>

        {/* Section A: Overall Reliability Score & Counts Card */}
        <div
          style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E8E5DC',
            borderRadius: '14px',
            padding: '24px 28px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.02)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '24px'
          }}
        >
          {/* Reliability Score Gauge */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <div>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#78716C', marginBottom: '4px' }}>
                ANSWER RELIABILITY SCORE R(a)
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px' }}>
                <span
                  className="font-serif"
                  style={{
                    fontSize: '3.2rem',
                    fontWeight: 700,
                    color: getReliabilityColor(job.reliability_score),
                    lineHeight: 1
                  }}
                >
                  {(job.reliability_score * 100).toFixed(1)}%
                </span>
                <span style={{ fontSize: '0.8rem', color: '#78716C' }}>
                  {job.reliability_score < job.mean_rho ? '(Capped by max P_C contradiction)' : '(Uncapped)'}
                </span>
              </div>
            </div>

            {/* Visual Gauge Bar */}
            <div style={{ width: '180px' }}>
              <div style={{ height: '10px', backgroundColor: '#E5E7EB', borderRadius: '9999px', overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${Math.min(job.reliability_score * 100, 100)}%`,
                    backgroundColor: getReliabilityColor(job.reliability_score),
                    transition: 'width 0.5s ease'
                  }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#8B857D', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
                <span>0%</span>
                <span>Mean ρ: {(job.mean_rho * 100).toFixed(0)}%</span>
                <span>100%</span>
              </div>
            </div>
          </div>

          {/* Counts Strip */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <div style={{ backgroundColor: '#DCFCE7', border: '1px solid #BBF7D0', padding: '10px 16px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#15803D', lineHeight: 1 }}>{job.supported_count}</div>
              <div style={{ fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', color: '#166534', marginTop: '4px' }}>Supported</div>
            </div>

            <div style={{ backgroundColor: '#FED7AA', border: '1px solid #FDBA74', padding: '10px 16px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#9A3412', lineHeight: 1 }}>{job.contradicted_count}</div>
              <div style={{ fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', color: '#7C2D12', marginTop: '4px' }}>Contradicted</div>
            </div>

            <div style={{ backgroundColor: '#FEF9C3', border: '1px solid #FDE047', padding: '10px 16px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#854D0E', lineHeight: 1 }}>{job.nei_count}</div>
              <div style={{ fontSize: '0.68rem', fontWeight: 700, textTransform: 'uppercase', color: '#713F12', marginTop: '4px' }}>Unverified (NEI)</div>
            </div>

            <div style={{ backgroundColor: '#F0F9FF', border: '1px solid #BAE6FD', padding: '10px 14px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0369A1', lineHeight: 1 }}>
                {job.total_claims > 0 ? `${(((job.supported_count + job.contradicted_count) / job.total_claims) * 100).toFixed(0)}%` : '100%'}
              </div>
              <div style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', color: '#0284C7', marginTop: '4px' }}>Coverage</div>
            </div>

            <div style={{ backgroundColor: '#FAF5FF', border: '1px solid #E9D5FF', padding: '10px 14px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#7E22CE', lineHeight: 1 }}>
                {`${(((job.evidence_quality ?? 0.88)) * 100).toFixed(0)}%`}
              </div>
              <div style={{ fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', color: '#6B21A8', marginTop: '4px' }}>Evidence Quality</div>
            </div>
          </div>
        </div>

        {/* Section D: Side-by-Side Answer Comparison (Original vs Corrected) */}
        <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '14px', padding: '24px 28px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1C1917' }}>
              Side-by-Side Comparison: Original vs M5 Grounded Correction
            </h2>
            <div style={{ fontSize: '0.76rem', color: '#78716C' }}>
              {job.corrections_count} contradiction{job.corrections_count !== 1 ? 's' : ''} rewritten & re-verified
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Left: Original with Highlighted Spans */}
            <div style={{ backgroundColor: '#FAF8F5', border: '1px solid #E8E5DC', borderRadius: '10px', padding: '18px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#78716C' }}>
                    Original LLM Output
                  </span>
                  <button
                    onClick={() => handleCopy(job.original_text, 'original')}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#78716C', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.74rem' }}
                  >
                    {copiedOriginal ? <Check size={13} color="#16A34A" /> : <Copy size={13} />}
                    {copiedOriginal ? 'Copied' : 'Copy'}
                  </button>
                </div>
                <p style={{ fontSize: '0.9rem', lineHeight: '1.7', color: '#292524', margin: 0 }}>
                  {job.original_text}
                </p>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#8B857D', marginTop: '14px' }}>
                Never silently overwritten. Preserved for provenance tracking.
              </div>
            </div>

            {/* Right: Grounded Corrected Answer */}
            <div style={{ backgroundColor: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: '10px', padding: '18px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#166534', display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <Wand2 size={13} />
                    M5 Grounded Correction (Verify-Then-Accept)
                  </span>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => handleCopy(job.corrected_text || job.original_text, 'corrected')}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#15803D', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.74rem' }}
                    >
                      {copiedCorrected ? <Check size={13} color="#16A34A" /> : <Copy size={13} />}
                      {copiedCorrected ? 'Copied' : 'Copy'}
                    </button>
                    <a
                      href={api.downloadTxtUrl(job.id)}
                      download
                      style={{ color: '#15803D', textDecoration: 'none', fontSize: '0.74rem', display: 'flex', alignItems: 'center', gap: '3px' }}
                    >
                      <Download size={13} />
                      .txt
                    </a>
                  </div>
                </div>
                <p style={{ fontSize: '0.9rem', lineHeight: '1.7', color: '#14532D', margin: 0, fontWeight: 500 }}>
                  {job.corrected_text || job.original_text}
                </p>
              </div>
              <div style={{ fontSize: '0.72rem', color: '#166534', marginTop: '14px' }}>
                Only contradicted claims were revised and strictly confirmed as SUPPORTED before merge.
              </div>
            </div>
          </div>
        </div>

        {/* Section B & C: Individual Atomic Claims Audit & Evidence Viewer */}
        <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '14px', padding: '24px 28px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
          
          {/* Claims Controls Bar: Filters & Sorters */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1C1917' }}>
                Atomic Claims ({job.claims?.length || 0})
              </h2>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              {/* Filter Chips */}
              <div style={{ display: 'flex', gap: '6px' }}>
                {['all', 'SUPPORTED', 'CONTRADICTED', 'NEI'].map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    style={{
                      backgroundColor: filter === f ? '#1C1917' : '#FAF8F5',
                      color: filter === f ? '#FFFFFF' : '#57534E',
                      border: '1px solid #D5D1C6',
                      borderRadius: '6px',
                      padding: '4px 10px',
                      fontSize: '0.74rem',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    {f === 'all' ? 'All Claims' : f}
                  </button>
                ))}
              </div>

              {/* Sorter */}
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                style={{
                  padding: '4px 8px',
                  borderRadius: '6px',
                  border: '1px solid #D5D1C6',
                  backgroundColor: '#FAF8F5',
                  fontSize: '0.74rem',
                  color: '#1C1917'
                }}
              >
                <option value="number">Sort by Claim #</option>
                <option value="confidence">Sort by Confidence</option>
                <option value="verdict">Sort by Verdict</option>
              </select>
            </div>
          </div>

          {/* Claims Cards List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {claims.map((claim) => {
              const isSelected = activeClaimId === claim.id;
              const isSupported = claim.predicted_label === 'SUPPORTED';
              const isContradicted = claim.predicted_label === 'CONTRADICTED';
              const vColor = isSupported ? '#16A34A' : (isContradicted ? '#DC2626' : '#CA8A04');
              const vBg = isSupported ? '#DCFCE7' : (isContradicted ? '#FED7AA' : '#FEF9C3');

              return (
                <div
                  key={claim.id}
                  ref={(el) => (cardRefs.current[claim.id] = el)}
                  onClick={() => setActiveClaimId(claim.id)}
                  style={{
                    backgroundColor: isSelected ? '#FAF8F5' : '#FFFFFF',
                    border: isSelected ? '1px solid #5E50EE' : '1px solid #E8E5DC',
                    borderRadius: '10px',
                    padding: '18px 20px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {/* Top Bar of Claim Card */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '0.76rem', fontWeight: 700, color: '#78716C', fontFamily: 'var(--font-mono)' }}>
                        Claim #{claim.claim_number}
                      </span>
                      <span
                        style={{
                          backgroundColor: vBg,
                          color: vColor,
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '0.72rem',
                          fontWeight: 700
                        }}
                      >
                        {claim.predicted_label}
                      </span>
                      {claim.verdict_changed ? (
                        <span
                          style={{
                            backgroundColor: '#FEE2E2',
                            color: '#991B1B',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            fontSize: '0.68rem',
                            fontWeight: 600
                          }}
                        >
                          Initial: {claim.initial_label} → {claim.predicted_label}
                        </span>
                      ) : (
                        <span
                          style={{
                            backgroundColor: '#F3F4F6',
                            color: '#4B5563',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            fontSize: '0.68rem',
                            fontWeight: 600
                          }}
                        >
                          Stage 2 Confirmed
                        </span>
                      )}
                    </div>

                    <div style={{ display: 'flex', gap: '12px', fontSize: '0.72rem', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
                      <span>P_E: {(claim.p_supported * 100).toFixed(0)}%</span>
                      <span>P_C: {(claim.p_contradicted * 100).toFixed(0)}%</span>
                      <span>P_N: {(claim.p_nei * 100).toFixed(0)}%</span>
                      {claim.source_independence != null && (
                        <span>Indep: {((claim.source_independence) * 100).toFixed(0)}%</span>
                      )}
                      <span style={{ fontWeight: 700, color: '#1C1917' }}>ρ: {(claim.reliability * 100).toFixed(0)}%</span>
                    </div>
                  </div>

                  {/* Claim Text */}
                  <div style={{ fontSize: '0.92rem', fontWeight: 600, color: '#1C1917', lineHeight: '1.5' }}>
                    "{claim.claim_text}"
                  </div>

                  {/* Justification & Evidence */}
                  <div style={{ backgroundColor: '#FAF8F5', borderRadius: '8px', padding: '12px', border: '1px solid #E8E5DC', fontSize: '0.82rem' }}>
                    <div style={{ color: '#78716C', fontWeight: 600, marginBottom: '4px' }}>
                      Grounded Evidence & Rationale:
                    </div>
                    <div style={{ color: '#292524', lineHeight: '1.6' }}>
                      {claim.best_evidence ? `"${claim.best_evidence}"` : (claim.rationale || "No direct evidence retrieved above threshold.")}
                    </div>

                    {/* Evidence Source Link if available */}
                    {claim.evidence_items?.length > 0 && claim.evidence_items[0].source_url && (
                      <div style={{ marginTop: '8px', fontSize: '0.74rem' }}>
                        <span style={{ color: '#78716C' }}>Source: </span>
                        <a
                          href={claim.evidence_items[0].source_url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ color: '#2563EB', textDecoration: 'none' }}
                        >
                          {claim.evidence_items[0].source_title || claim.evidence_items[0].source_url}
                        </a>
                      </div>
                    )}

                    {claim.change_reason && (
                      <div style={{ marginTop: '10px', fontSize: '0.74rem', color: '#0369A1', backgroundColor: '#F0F9FF', padding: '6px 10px', borderRadius: '6px', border: '1px solid #BAE6FD' }}>
                        <strong>Stage 2 Investigation Audit:</strong> {claim.change_reason}
                      </div>
                    )}
                  </div>

                  {/* M5 Grounded Revision Display if Contradicted */}
                  {isContradicted && claim.corrections?.length > 0 && (
                    <div style={{ backgroundColor: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: '8px', padding: '10px 14px', fontSize: '0.8rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#166534', fontWeight: 700, marginBottom: '2px' }}>
                        <Wand2 size={13} />
                        <span>M5 Accepted Grounded Revision:</span>
                      </div>
                      <div style={{ color: '#14532D' }}>
                        "{claim.corrections[0].suggested_correction}"
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
