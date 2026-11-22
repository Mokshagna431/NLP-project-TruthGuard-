import React, { useState } from 'react';
import { Search, Command, ArrowUpRight, Clock, ShieldCheck, Filter } from 'lucide-react';
import { ANALYTICS_DATA } from '../data/mockData';

export default function AnalyticsView({ onNewVerification, onOpenSearch }) {
  const [hoveredBar, setHoveredBar] = useState(null);
  const { kpis, verdictMix, topicsVolume, busiestHour, calibrationNote, dailyProofs } = ANALYTICS_DATA;

  // Maximum proof count for scaling bars
  const maxProof = Math.max(...dailyProofs.map((p) => p.count));

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: '#FAF8F5',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Top Bar: Breadcrumb, Search & Action Button (Matches Image 2) */}
      <div
        style={{
          height: '64px',
          borderBottom: '1px solid #E8E5DC',
          padding: '0 40px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: '#FAF8F5',
          position: 'sticky',
          top: 0,
          zIndex: 10
        }}
      >
        {/* Breadcrumb */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
          <span style={{ color: '#78716C', fontWeight: 400 }}>Analytics</span>
          <span style={{ color: '#A8A29E' }}>/</span>
          <span style={{ color: '#1C1917', fontWeight: 600 }}>Last 30 days</span>
        </div>

        {/* Right Search Input & New Verification Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          {/* Search or command input with ⌘K badge */}
          <div
            onClick={onOpenSearch}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              backgroundColor: '#FFFFFF',
              border: '1px solid #D5D1C6',
              borderRadius: '6px',
              padding: '6px 12px',
              fontSize: '0.82rem',
              color: '#78716C',
              cursor: 'pointer',
              width: '240px',
              justifyContent: 'space-between'
            }}
          >
            <span>Search or command</span>
            <kbd
              style={{
                backgroundColor: '#F5F3ED',
                border: '1px solid #D5D1C6',
                borderRadius: '4px',
                padding: '1px 5px',
                fontSize: '0.7rem',
                color: '#57534E',
                fontFamily: 'var(--font-mono)'
              }}
            >
              ⌘K
            </kbd>
          </div>

          {/* + New verification button (Solid black pill matching Image 2!) */}
          <button
            onClick={onNewVerification}
            style={{
              backgroundColor: '#1C1917',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              padding: '7px 16px',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'background 0.15s ease'
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#292524')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#1C1917')}
          >
            New verification
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ padding: '36px 40px', maxWidth: '1400px', width: '100%', margin: '0 auto' }}>
        {/* Page Title Group */}
        <div style={{ marginBottom: '28px' }}>
          <div
            style={{
              fontSize: '0.72rem',
              fontWeight: 600,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              color: '#78716C',
              fontFamily: 'var(--font-mono)',
              marginBottom: '4px'
            }}
          >
            LAST 30 DAYS
          </div>
          <h1
            className="font-serif"
            style={{
              fontSize: '2.5rem',
              fontWeight: 500,
              letterSpacing: '-0.02em',
              color: '#1C1917',
              lineHeight: 1.1
            }}
          >
            Analytics
          </h1>
        </div>

        {/* 4 Top KPI Metric Cards (Grid layout with clean dividers matching Image 2) */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            borderTop: '1px solid #E8E5DC',
            borderBottom: '1px solid #E8E5DC',
            padding: '24px 0',
            marginBottom: '36px'
          }}
        >
          {kpis.map((kpi, idx) => (
            <div
              key={idx}
              style={{
                borderRight: idx < kpis.length - 1 ? '1px solid #E8E5DC' : 'none',
                paddingLeft: idx === 0 ? '0' : '28px',
                paddingRight: '28px'
              }}
            >
              <div
                style={{
                  fontSize: '0.66rem',
                  fontWeight: 700,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: '#78716C',
                  marginBottom: '8px'
                }}
              >
                {kpi.label}
              </div>
              <div
                className="font-serif"
                style={{
                  fontSize: '2.2rem',
                  fontWeight: 500,
                  color: idx === 3 ? '#0D9488' : '#1C1917', // Green tint for low dispute rate
                  lineHeight: 1.1,
                  letterSpacing: '-0.02em'
                }}
              >
                {kpi.value}
              </div>
            </div>
          ))}
        </div>

        {/* Middle Two-Column Grid: Left Chart + Right Stats */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1.45fr 0.95fr',
            gap: '48px',
            marginBottom: '48px'
          }}
        >
          {/* LEFT: PROOFS PER DAY Bar Chart */}
          <div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '20px'
              }}
            >
              <span
                style={{
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: '#78716C'
                }}
              >
                PROOFS PER DAY
              </span>
              <span style={{ fontSize: '0.72rem', color: '#A8A29E', fontStyle: 'italic' }}>
                hover the bars
              </span>
            </div>

            {/* Interactive Histogram Bars */}
            <div
              style={{
                position: 'relative',
                height: '240px',
                display: 'flex',
                alignItems: 'flex-end',
                gap: '5px',
                paddingBottom: '26px',
                borderBottom: '1px solid #E8E5DC'
              }}
            >
              {dailyProofs.map((bar, idx) => {
                const heightPercent = (bar.count / maxProof) * 100;
                const isHovered = hoveredBar === idx;

                return (
                  <div
                    key={idx}
                    onMouseEnter={() => setHoveredBar(idx)}
                    onMouseLeave={() => setHoveredBar(null)}
                    style={{
                      flex: 1,
                      height: `${heightPercent}%`,
                      backgroundColor: bar.isCurrent ? '#DC2626' : isHovered ? '#78716C' : '#D5D1C6',
                      transition: 'all 0.15s ease',
                      position: 'relative',
                      cursor: 'pointer',
                      borderRadius: '1px 1px 0 0'
                    }}
                  >
                    {/* Hover tooltip */}
                    {isHovered && (
                      <div
                        style={{
                          position: 'absolute',
                          bottom: '105%',
                          left: '50%',
                          transform: 'translateX(-50%)',
                          backgroundColor: '#1C1917',
                          color: '#FFFFFF',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '0.7rem',
                          whiteSpace: 'nowrap',
                          zIndex: 20,
                          pointerEvents: 'none',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
                        }}
                      >
                        <div style={{ fontWeight: 600 }}>{bar.date}</div>
                        <div>{bar.count} proofs</div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Horizontal Timeline Labels (JUN 7, JUN 21, JUL 6 from Image 2!) */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: '8px',
                fontSize: '0.68rem',
                color: '#8B857D',
                fontFamily: 'var(--font-mono)'
              }}
            >
              <span>JUN 7</span>
              <span>JUN 21</span>
              <span>JUL 6</span>
            </div>
          </div>

          {/* RIGHT: VERDICT MIX, CALIBRATION, BUSIEST HOUR */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
            {/* Verdict Mix 30D */}
            <div>
              <div
                style={{
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: '#78716C',
                  marginBottom: '10px'
                }}
              >
                VERDICT MIX • 30D
              </div>

              {/* Stacked Progress Bar */}
              <div
                style={{
                  height: '7px',
                  width: '100%',
                  backgroundColor: '#E5E7EB',
                  borderRadius: '2px',
                  display: 'flex',
                  overflow: 'hidden',
                  marginBottom: '12px'
                }}
              >
                <div
                  style={{
                    width: `${(verdictMix.verified / verdictMix.total) * 100}%`,
                    backgroundColor: '#16A34A'
                  }}
                  title={`Verified: ${verdictMix.verified}`}
                />
                <div
                  style={{
                    width: `${(verdictMix.misleading / verdictMix.total) * 100}%`,
                    backgroundColor: '#EA580C'
                  }}
                  title={`Misleading: ${verdictMix.misleading}`}
                />
                <div
                  style={{
                    width: `${(verdictMix.falseClaims / verdictMix.total) * 100}%`,
                    backgroundColor: '#DC2626'
                  }}
                  title={`False: ${verdictMix.falseClaims}`}
                />
                <div
                  style={{
                    width: `${(verdictMix.unverified / verdictMix.total) * 100}%`,
                    backgroundColor: '#A8A29E'
                  }}
                  title={`Unverified: ${verdictMix.unverified}`}
                />
              </div>

              {/* Legend with Color Dots */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: '8px 16px',
                  fontSize: '0.78rem',
                  color: '#44403C'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#16A34A' }} />
                  <span>Verified {verdictMix.verified.toLocaleString()}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#EA580C' }} />
                  <span>Misleading {verdictMix.misleading.toLocaleString()}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#DC2626' }} />
                  <span>False {verdictMix.falseClaims.toLocaleString()}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#A8A29E' }} />
                  <span>Unverified {verdictMix.unverified.toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* Confidence Calibration */}
            <div style={{ borderTop: '1px solid #E8E5DC', paddingTop: '20px' }}>
              <div
                style={{
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: '#78716C',
                  marginBottom: '8px'
                }}
              >
                {calibrationNote.headline}
              </div>
              <p
                style={{
                  fontSize: '0.82rem',
                  lineHeight: '1.5',
                  color: '#57534E',
                  margin: 0
                }}
              >
                {calibrationNote.content}
              </p>
            </div>

            {/* Busiest Hour */}
            <div style={{ borderTop: '1px solid #E8E5DC', paddingTop: '20px' }}>
              <div
                style={{
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                  color: '#78716C',
                  marginBottom: '6px'
                }}
              >
                BUSIEST HOUR
              </div>
              <div
                style={{
                  fontSize: '1.35rem',
                  fontWeight: 700,
                  color: '#1C1917',
                  fontFamily: 'var(--font-mono)',
                  letterSpacing: '-0.02em',
                  marginBottom: '4px'
                }}
              >
                {busiestHour.time}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#78716C' }}>
                {busiestHour.description}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section: TOPICS BY VOLUME Horizontal Bars (Image 2) */}
        <div>
          <div
            style={{
              fontSize: '0.68rem',
              fontWeight: 700,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: '#78716C',
              marginBottom: '18px'
            }}
          >
            TOPICS BY VOLUME
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '800px' }}>
            {topicsVolume.map((item, idx) => (
              <div
                key={idx}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '110px 1fr 60px',
                  alignItems: 'center',
                  gap: '16px'
                }}
              >
                {/* Topic Label */}
                <span style={{ fontSize: '0.84rem', color: '#1C1917', fontWeight: 500 }}>
                  {item.topic}
                </span>

                {/* Bar Meter: Black fill on faint gray track */}
                <div
                  style={{
                    height: '14px',
                    backgroundColor: '#EAE7DF',
                    borderRadius: '2px',
                    overflow: 'hidden',
                    width: '100%'
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: `${item.percentage}%`,
                      backgroundColor: '#1C1917',
                      transition: 'width 0.4s ease'
                    }}
                  />
                </div>

                {/* Count */}
                <span
                  style={{
                    fontSize: '0.82rem',
                    color: '#1C1917',
                    fontWeight: 600,
                    fontFamily: 'var(--font-mono)',
                    textAlign: 'right'
                  }}
                >
                  {item.count}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
