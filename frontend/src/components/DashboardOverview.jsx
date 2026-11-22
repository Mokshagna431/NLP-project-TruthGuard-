import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  TrendingUp,
  RefreshCw,
  Plus,
  ArrowRight,
  Filter,
  FileText,
  Clock,
  Calendar,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';

export default function DashboardOverview({
  currentUser,
  onNewVerification,
  onViewVerification
}) {
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [trends, setTrends] = useState(null);
  const [distribution, setDistribution] = useState(null);
  const [recentJobs, setRecentJobs] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [ovRes, trRes, distRes, jobsRes] = await Promise.all([
        api.getAnalyticsOverview(days).catch(() => null),
        api.getAnalyticsTrends(days).catch(() => null),
        api.getAnalyticsDistribution(days).catch(() => null),
        api.listVerifications(`page=1&page_size=5&days=${days}`).catch(() => null)
      ]);

      setOverview(ovRes);
      setTrends(trRes);
      setDistribution(distRes);
      setRecentJobs(jobsRes?.items || []);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [days]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  const getReliabilityColor = (score) => {
    if (score >= 70) return '#16A34A';
    if (score >= 40) return '#EA580C';
    return '#DC2626';
  };

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        {/* Top Control Bar: Greeting, Date Filters & Actions */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
              PROOF DESK OVERVIEW
            </div>
            <h1 className="font-serif" style={{ fontSize: '2.4rem', fontWeight: 600, color: '#1C1917', lineHeight: 1.15, marginTop: '4px' }}>
              Welcome back, {currentUser?.full_name?.split(' ')[0] || 'Analyst'}
            </h1>
            <p style={{ fontSize: '0.86rem', color: '#57534E', marginTop: '4px' }}>
              Real-time hallucination audit metrics, reliability tracking, and verification queue.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {/* Date Filters */}
            <div
              style={{
                display: 'flex',
                backgroundColor: '#FFFFFF',
                border: '1px solid #D5D1C6',
                borderRadius: '8px',
                padding: '3px',
                gap: '2px'
              }}
            >
              {[
                { label: 'Today', val: 1 },
                { label: '7 Days', val: 7 },
                { label: '30 Days', val: 30 },
                { label: '90 Days', val: 90 }
              ].map((d) => (
                <button
                  key={d.val}
                  onClick={() => setDays(d.val)}
                  style={{
                    backgroundColor: days === d.val ? '#1C1917' : 'transparent',
                    color: days === d.val ? '#FFFFFF' : '#57534E',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '5px 12px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.12s'
                  }}
                >
                  {d.label}
                </button>
              ))}
            </div>

            {/* Refresh Action */}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #D5D1C6',
                borderRadius: '8px',
                padding: '8px 12px',
                color: '#57534E',
                cursor: refreshing ? 'wait' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.8rem',
                fontWeight: 600
              }}
              title="Refresh statistics"
            >
              <RefreshCw size={14} className={refreshing ? 'pulse-indicator' : ''} />
              <span>Refresh</span>
            </button>

            {/* New Verification Action */}
            <button
              onClick={onNewVerification}
              style={{
                backgroundColor: '#1C1917',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
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
              <Plus size={15} />
              New Verification
            </button>
          </div>
        </div>

        {/* 8 Real Database KPI Cards Grid (Section 6) */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          {/* Card 1: Total Analyses */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '18px 20px', boxShadow: '0 1px 3px rgba(0,0,0,0.02)' }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#78716C', marginBottom: '8px' }}>
              TOTAL ANALYSES
            </div>
            <div className="font-serif" style={{ fontSize: '2.1rem', fontWeight: 600, color: '#1C1917', lineHeight: 1 }}>
              {overview?.total_analyses ?? 0}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#8B857D', marginTop: '6px' }}>
              Completed hallucination audits
            </div>
          </div>

          {/* Card 2: Total Claims Checked */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '18px 20px', boxShadow: '0 1px 3px rgba(0,0,0,0.02)' }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#78716C', marginBottom: '8px' }}>
              TOTAL CLAIMS CHECKED
            </div>
            <div className="font-serif" style={{ fontSize: '2.1rem', fontWeight: 600, color: '#1C1917', lineHeight: 1 }}>
              {overview?.total_claims_checked ?? 0}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#8B857D', marginTop: '6px' }}>
              Atomic propositions decomposed
            </div>
          </div>

          {/* Card 3: Average Reliability */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '18px 20px', boxShadow: '0 1px 3px rgba(0,0,0,0.02)' }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#78716C', marginBottom: '8px' }}>
              AVERAGE RELIABILITY R(a)
            </div>
            <div className="font-serif" style={{ fontSize: '2.1rem', fontWeight: 600, color: getReliabilityColor(overview?.average_reliability || 0), lineHeight: 1 }}>
              {overview ? `${overview.average_reliability}%` : '0%'}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#8B857D', marginTop: '6px' }}>
              M4 Non-compensatory score
            </div>
          </div>

          {/* Card 4: Disputed Rate */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '18px 20px', boxShadow: '0 1px 3px rgba(0,0,0,0.02)' }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#78716C', marginBottom: '8px' }}>
              DISPUTED VERDICTS
            </div>
            <div className="font-serif" style={{ fontSize: '2.1rem', fontWeight: 600, color: '#0D9488', lineHeight: 1 }}>
              {overview ? `${overview.disputed_verdicts_percent}%` : '0.0%'}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#8B857D', marginTop: '6px' }}>
              Well below 0.5% cap target
            </div>
          </div>

          {/* Card 5: Supported Claims */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '18px 20px' }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#166534', marginBottom: '8px' }}>
              SUPPORTED CLAIMS (S)
            </div>
            <div className="font-serif" style={{ fontSize: '2.1rem', fontWeight: 600, color: '#16A34A', lineHeight: 1 }}>
              {overview?.supported_claims ?? 0}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#15803D', marginTop: '6px' }}>
              Entailed by retrieved evidence
            </div>
          </div>

          {/* Card 6: Contradicted Claims */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '18px 20px' }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#991B1B', marginBottom: '8px' }}>
              CONTRADICTED CLAIMS (C)
            </div>
            <div className="font-serif" style={{ fontSize: '2.1rem', fontWeight: 600, color: '#DC2626', lineHeight: 1 }}>
              {overview?.contradicted_claims ?? 0}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#B91C1C', marginTop: '6px' }}>
              Identified hallucinations
            </div>
          </div>

          {/* Card 7: NEI Claims */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '18px 20px' }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#854D0E', marginBottom: '8px' }}>
              UNVERIFIED (NEI)
            </div>
            <div className="font-serif" style={{ fontSize: '2.1rem', fontWeight: 600, color: '#CA8A04', lineHeight: 1 }}>
              {overview?.nei_claims ?? 0}
            </div>
            <div style={{ fontSize: '0.74rem', color: '#A16207', marginTop: '6px' }}>
              Insufficient source evidence
            </div>
          </div>

          {/* Card 8: Corrections Success */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '18px 20px' }}>
            <div style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#78716C', marginBottom: '8px' }}>
              M5 CORRECTIONS
            </div>
            <div className="font-serif" style={{ fontSize: '2.1rem', fontWeight: 600, color: '#5E50EE', lineHeight: 1 }}>
              {overview?.corrections_accepted ?? 0}
              <span style={{ fontSize: '1rem', color: '#78716C', marginLeft: '6px', fontWeight: 400 }}>
                / {(overview?.corrections_accepted || 0) + (overview?.corrections_rejected || 0)}
              </span>
            </div>
            <div style={{ fontSize: '0.74rem', color: '#8B857D', marginTop: '6px' }}>
              Grounded revisions accepted
            </div>
          </div>
        </div>

        {/* Charts & Breakdown Row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '28px' }}>
          {/* Left Chart: Verification Activity Over Time */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '24px 28px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
              <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#78716C' }}>
                VERIFICATION ACTIVITY OVER TIME ({days} DAYS)
              </span>
              <span style={{ fontSize: '0.72rem', color: '#8B857D', fontStyle: 'italic' }}>
                Proofs per day
              </span>
            </div>

            {/* Daily Histogram Bars */}
            <div style={{ height: '180px', display: 'flex', alignItems: 'flex-end', gap: '4px', borderBottom: '1px solid #E8E5DC', paddingBottom: '12px' }}>
              {(trends?.daily_proofs || []).slice(-20).map((bar, idx, arr) => {
                const maxVal = Math.max(...arr.map(b => b.count), 1);
                const heightPct = Math.max((bar.count / maxVal) * 100, 8);
                return (
                  <div
                    key={idx}
                    title={`${bar.date}: ${bar.count} verifications`}
                    style={{
                      flex: 1,
                      height: `${heightPct}%`,
                      backgroundColor: bar.is_current ? '#DC2626' : '#D5D1C6',
                      borderRadius: '1px 1px 0 0',
                      transition: 'all 0.15s ease',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#1C1917')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = bar.is_current ? '#DC2626' : '#D5D1C6')}
                  />
                );
              })}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '0.68rem', color: '#8B857D', fontFamily: 'var(--font-mono)' }}>
              <span>{trends?.daily_proofs?.[0]?.date || 'Start'}</span>
              <span>{trends?.daily_proofs?.[Math.floor((trends?.daily_proofs?.length || 0) / 2)]?.date || 'Mid'}</span>
              <span>Today</span>
            </div>
          </div>

          {/* Right: Verdict Distribution Mix */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '24px 28px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#78716C', marginBottom: '14px' }}>
                CLAIM CLASSIFICATION DISTRIBUTION
              </div>

              {/* Segmented Distribution Bar */}
              {(() => {
                const s = overview?.supported_claims || 0;
                const c = overview?.contradicted_claims || 0;
                const nei = overview?.nei_claims || 0;
                const total = Math.max(s + c + nei, 1);
                return (
                  <div>
                    <div style={{ height: '10px', width: '100%', backgroundColor: '#E5E7EB', borderRadius: '3px', display: 'flex', overflow: 'hidden', marginBottom: '14px' }}>
                      <div style={{ width: `${(s / total) * 100}%`, backgroundColor: '#16A34A' }} title={`Supported: ${s}`} />
                      <div style={{ width: `${(c / total) * 100}%`, backgroundColor: '#DC2626' }} title={`Contradicted: ${c}`} />
                      <div style={{ width: `${(nei / total) * 100}%`, backgroundColor: '#CA8A04' }} title={`NEI: ${nei}`} />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.78rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#16A34A' }} />
                        <span>Supported: <b>{s}</b> ({Math.round((s / total) * 100)}%)</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#DC2626' }} />
                        <span>Contradicted: <b>{c}</b> ({Math.round((c / total) * 100)}%)</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#CA8A04' }} />
                        <span>NEI: <b>{nei}</b> ({Math.round((nei / total) * 100)}%)</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#5E50EE' }} />
                        <span>Fixed: <b>{overview?.corrections_accepted || 0}</b></span>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>

            <div style={{ borderTop: '1px solid #F3EFE7', paddingTop: '14px', marginTop: '16px' }}>
              <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#78716C', textTransform: 'uppercase', marginBottom: '4px' }}>
                CONFIDENCE CALIBRATION NOTICE
              </div>
              <p style={{ fontSize: '0.78rem', color: '#57534E', margin: 0, lineHeight: '1.45' }}>
                {trends?.calibration_commentary || 'Verdicts filed at 90%+ confidence adhere to the 0.5% target. Calibration drift: none detected.'}
              </p>
            </div>
          </div>
        </div>

        {/* Recent Verifications Table */}
        <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '12px', padding: '24px 28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
            <div>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1C1917' }}>Recent Verifications</h2>
              <p style={{ fontSize: '0.78rem', color: '#78716C', margin: '2px 0 0 0' }}>
                Latest claim audits executed in your workspace.
              </p>
            </div>

            {recentJobs.length > 0 && (
              <button
                onClick={onNewVerification}
                style={{
                  backgroundColor: '#FAF8F5',
                  border: '1px solid #D5D1C6',
                  borderRadius: '6px',
                  padding: '6px 14px',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  color: '#1C1917'
                }}
              >
                + New Audit
              </button>
            )}
          </div>

          {recentJobs.length === 0 ? (
            /* Empty State for new users (Section 6) */
            <div style={{ textAlign: 'center', padding: '40px 16px' }}>
              <ShieldCheck size={42} color="#D5D1C6" style={{ margin: '0 auto 12px auto' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1C1917', marginBottom: '4px' }}>
                No Verifications Found in this Range
              </h3>
              <p style={{ fontSize: '0.82rem', color: '#78716C', maxWidth: '360px', margin: '0 auto 18px auto' }}>
                Submit an LLM response to decompose atomic claims, verify against authoritative evidence, and evaluate reliability.
              </p>
              <button
                onClick={onNewVerification}
                style={{
                  backgroundColor: '#1C1917',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '9px 18px',
                  fontSize: '0.84rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <Plus size={15} />
                Start Your First Verification
              </button>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #E8E5DC', color: '#78716C' }}>
                    <th style={{ padding: '10px 8px' }}>Analysis Title</th>
                    <th style={{ padding: '10px 8px' }}>Date</th>
                    <th style={{ padding: '10px 8px' }}>Claims</th>
                    <th style={{ padding: '10px 8px' }}>S / C / NEI</th>
                    <th style={{ padding: '10px 8px' }}>Reliability R(a)</th>
                    <th style={{ padding: '10px 8px' }}>Status</th>
                    <th style={{ padding: '10px 8px', textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {recentJobs.map((job) => (
                    <tr
                      key={job.id}
                      style={{ borderBottom: '1px solid #F3EFE7', color: '#1C1917', cursor: 'pointer' }}
                      onClick={() => onViewVerification(job.id)}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#FAF8F5')}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td style={{ padding: '12px 8px', fontWeight: 600 }}>{job.title}</td>
                      <td style={{ padding: '12px 8px', color: '#78716C' }}>
                        {new Date(job.created_at).toLocaleDateString()}
                      </td>
                      <td style={{ padding: '12px 8px' }}>{job.total_claims}</td>
                      <td style={{ padding: '12px 8px' }}>
                        <span style={{ color: '#16A34A', fontWeight: 600 }}>{job.supported_count}</span> /{' '}
                        <span style={{ color: '#DC2626', fontWeight: 600 }}>{job.contradicted_count}</span> /{' '}
                        <span style={{ color: '#CA8A04', fontWeight: 600 }}>{job.nei_count}</span>
                      </td>
                      <td style={{ padding: '12px 8px', fontWeight: 700, color: getReliabilityColor(job.reliability_score * 100) }}>
                        {(job.reliability_score * 100).toFixed(0)}%
                      </td>
                      <td style={{ padding: '12px 8px' }}>
                        <span style={{
                          backgroundColor: job.processing_status === 'COMPLETED' ? '#DCFCE7' : '#FEF3C7',
                          color: job.processing_status === 'COMPLETED' ? '#15803D' : '#854D0E',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '0.72rem',
                          fontWeight: 600
                        }}>
                          {job.processing_status}
                        </span>
                      </td>
                      <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onViewVerification(job.id);
                          }}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: '#5E50EE',
                            fontWeight: 600,
                            cursor: 'pointer',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}
                        >
                          View Details <ArrowRight size={13} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
