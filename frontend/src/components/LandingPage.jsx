import React, { useState } from 'react';
import {
  ShieldCheck,
  Sparkles,
  ArrowRight,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Layers,
  Database,
  Sliders,
  FileText,
  Lock,
  ChevronDown,
  ExternalLink,
  Code2
} from 'lucide-react';

export default function LandingPage({ onStartVerification, onOpenAuth, currentUser }) {
  const [activeFaq, setActiveFaq] = useState(null);

  const faqs = [
    {
      q: "How does TruthGuard differ from standard similarity or LLM-as-a-judge approaches?",
      a: "Standard approaches either compute shallow semantic similarity (which fails on negation and entity swaps) or rely on uncalibrated LLM prompts. TruthGuard extracts coreference-resolved atomic claims, retrieves evidence via Reciprocal Rank Fusion (RRF), and verifies claims using a temperature-calibrated DeBERTa-v3 NLI model with strict 3-way epistemic classification (Supported, Contradicted, NEI)."
    },
    {
      q: "Why is a claim classified as NOT-ENOUGH-INFO (NEI) rather than Contradicted?",
      a: "Rule 3 of scientific verification: lack of evidence is not proof of falsehood. If retrieved knowledge does not conclusively confirm or refute an assertion, TruthGuard designates it as NEI to avoid falsely penalizing novel or out-of-corpus claims."
    },
    {
      q: "What is the Non-Compensatory Reliability Equation in M4?",
      a: "Overall answer reliability is defined as R(a) = min(mean(rho(c)), 1 - max(P_C)). This ensures that even if 9 out of 10 claims are factual, a single critical contradiction severely caps overall reliability, preventing dangerous hallucinations from being hidden by high averages."
    },
    {
      q: "How does the Grounded Correction (M5) loop work?",
      a: "When a claim is contradicted, TruthGuard generates a minimal grounded edit using the strongest retrieved evidence and immediately submits the edit for independent re-verification. The correction is accepted into the final answer only if the re-verification result is strictly SUPPORTED."
    }
  ];

  return (
    <div style={{ backgroundColor: '#FAF8F5', minHeight: '100vh', color: '#1C1917' }}>
      {/* HERO SECTION */}
      <section
        style={{
          padding: '80px 24px 64px 24px',
          maxWidth: '1200px',
          margin: '0 auto',
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}
      >
        {/* Release Pill Badge */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#F3EFE7',
            border: '1px solid #E5E1D6',
            borderRadius: '9999px',
            padding: '5px 14px',
            fontSize: '0.78rem',
            fontWeight: 600,
            color: '#44403C',
            marginBottom: '24px'
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#16A34A' }} />
          TruthGuard v2.0 • Evidence-Grounded Claim Verification & Grounded Correction
        </div>

        {/* Hero Headline */}
        <h1
          className="font-serif"
          style={{
            fontSize: 'clamp(2.5rem, 5vw, 4rem)',
            fontWeight: 600,
            letterSpacing: '-0.03em',
            lineHeight: 1.12,
            maxWidth: '920px',
            marginBottom: '20px',
            color: '#181614'
          }}
        >
          Trust Every Claim. <br />
          <span style={{ fontStyle: 'italic', color: '#57534E' }}>Verify Every Answer.</span>
        </h1>

        <p
          style={{
            fontSize: '1.1rem',
            lineHeight: 1.6,
            color: '#57534E',
            maxWidth: '680px',
            marginBottom: '36px'
          }}
        >
          The evidence-grounded AI hallucination detection, scoring, and correction platform.
          Extract atomic claims, verify against authoritative evidence, and eliminate hallucinations with calibrated confidence.
        </p>

        {/* CTA Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap', justifyContent: 'center' }}>
          <button
            onClick={onStartVerification}
            style={{
              backgroundColor: '#1C1917',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              padding: '14px 28px',
              fontSize: '0.95rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 4px 14px rgba(28, 25, 23, 0.2)',
              transition: 'transform 0.15s ease'
            }}
          >
            {currentUser ? 'Open Proof Desk' : 'Start Free Verification'}
            <ArrowRight size={16} />
          </button>

          {!currentUser && (
            <button
              onClick={() => onOpenAuth('login')}
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #D5D1C6',
                color: '#1C1917',
                borderRadius: '8px',
                padding: '14px 24px',
                fontSize: '0.95rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Sign In to Account
            </button>
          )}
        </div>
      </section>

      {/* INTERACTIVE DEMONSTRATION PREVIEW */}
      <section style={{ padding: '0 24px 80px 24px', maxWidth: '1240px', margin: '0 auto' }}>
        <div
          style={{
            backgroundColor: '#FFFFFF',
            borderRadius: '16px',
            border: '1px solid #E8E5DC',
            boxShadow: '0 12px 36px rgba(0,0,0,0.04)',
            overflow: 'hidden'
          }}
        >
          {/* Header Bar */}
          <div
            style={{
              padding: '16px 24px',
              borderBottom: '1px solid #E8E5DC',
              backgroundColor: '#FAF8F5',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#EF4444' }} />
              <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#F59E0B' }} />
              <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: '#10B981' }} />
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#78716C', marginLeft: '12px' }}>
                TruthGuard Live Audit Preview • The Renaissance Benchmark
              </span>
            </div>

            <button
              onClick={onStartVerification}
              style={{
                backgroundColor: '#5E50EE',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 14px',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Sparkles size={13} />
              Open Interactive Workbench →
            </button>
          </div>

          {/* Dual Panel Preview Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', minHeight: '380px' }}>
            {/* Left: Highlighted text */}
            <div style={{ padding: '28px', borderRight: '1px solid #E8E5DC' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#78716C', textTransform: 'uppercase', marginBottom: '12px' }}>
                Input LLM Text with Token Highlights
              </div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '14px' }}>The Renaissance</h3>
              <p style={{ fontSize: '0.9rem', lineHeight: '1.8', color: '#374151' }}>
                <span className="highlight-inaccurate">
                  The Renaissance, a period of cultural and artistic flourishing, spanned from the 17th to 20th centuries, centered in Asia.
                </span>{' '}
                <span className="highlight-accurate">
                  This era witnessed a revival of classical Greek and Roman knowledge, leading to significant advancements in various fields.
                </span>
              </p>
              <div style={{ marginTop: '20px' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '6px' }}>Artistic Revolution</h4>
                <p style={{ fontSize: '0.9rem', lineHeight: '1.8', color: '#374151' }}>
                  One of the most notable developments was the emergence of groundbreaking artistic styles. Leonardo da Vinci created iconic masterpieces such as the Mona Lisa.{' '}
                  <span className="highlight-inaccurate">
                    Da Vinci created the Statue of David.
                  </span>
                </p>
              </div>
            </div>

            {/* Right: Claim Audits */}
            <div style={{ padding: '28px', backgroundColor: '#FAF8F5', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#78716C', textTransform: 'uppercase', marginBottom: '4px' }}>
                Claim-Level Calibrated Verifications
              </div>

              {/* Card 1 */}
              <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '10px', padding: '14px 16px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#EA580C', marginBottom: '4px' }}>
                  CONTRADICTED (P_C = 96%)
                </div>
                <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#1C1917', marginBottom: '4px' }}>
                  "The Renaissance spanned from the 17th to 20th centuries, centered in Asia."
                </div>
                <div style={{ fontSize: '0.78rem', color: '#57534E' }}>
                  <b>Grounded Justification:</b> Historical consensus confirms the Renaissance occurred from the 14th to 17th centuries in Europe.
                </div>
              </div>

              {/* Card 2 */}
              <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '10px', padding: '14px 16px' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#16A34A', marginBottom: '4px' }}>
                  SUPPORTED (P_E = 94%)
                </div>
                <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#1C1917', marginBottom: '4px' }}>
                  "This era witnessed a revival of classical Greek and Roman knowledge."
                </div>
                <div style={{ fontSize: '0.78rem', color: '#57534E' }}>
                  <b>Grounded Justification:</b> Entailed by academic historiography on classical antiquity revival.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* M1-M5 PIPELINE ARCHITECTURE */}
      <section style={{ padding: '80px 24px', backgroundColor: '#F5F3ED', borderTop: '1px solid #E8E5DC', borderBottom: '1px solid #E8E5DC' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '56px' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C' }}>
              RESEARCH-GROUNDED METHODOLOGY
            </span>
            <h2 className="font-serif" style={{ fontSize: '2.5rem', fontWeight: 600, marginTop: '8px', color: '#181614' }}>
              The 5-Module Verification Pipeline
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
            {[
              {
                step: 'M1',
                title: 'Decomposition',
                desc: 'Coreference resolution + atomic claim extraction with character offset tracking.'
              },
              {
                step: 'M2',
                title: 'Evidence Retrieval',
                desc: 'BM25 + SBERT hybrid Reciprocal Rank Fusion with Cross-Encoder re-ranking.'
              },
              {
                step: 'M3',
                title: 'NLI Verification',
                desc: 'Calibrated DeBERTa-v3 NLI with sentence max aggregation & conservative tie-breaking.'
              },
              {
                step: 'M4',
                title: 'Reliability Scoring',
                desc: 'Non-compensatory R(a) = min(mean rho, 1 - max P_C). A single contradiction caps score.'
              },
              {
                step: 'M5',
                title: 'Grounded Revision',
                desc: 'Verify-then-accept loop rewriting contradicted spans and re-checking against evidence.'
              }
            ].map((m, idx) => (
              <div
                key={idx}
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #E8E5DC',
                  borderRadius: '12px',
                  padding: '20px 16px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px'
                }}
              >
                <span
                  style={{
                    fontSize: '0.8rem',
                    fontWeight: 700,
                    color: '#5E50EE',
                    fontFamily: 'var(--font-mono)'
                  }}
                >
                  {m.step}
                </span>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#1C1917' }}>{m.title}</h3>
                <p style={{ fontSize: '0.8rem', color: '#57534E', lineHeight: '1.5', margin: 0 }}>
                  {m.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ SECTION */}
      <section style={{ padding: '80px 24px', maxWidth: '860px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '48px' }}>
          <h2 className="font-serif" style={{ fontSize: '2.4rem', fontWeight: 600 }}>
            Frequently Asked Questions
          </h2>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {faqs.map((f, i) => (
            <div
              key={i}
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #E8E5DC',
                borderRadius: '10px',
                padding: '18px 22px',
                cursor: 'pointer'
              }}
              onClick={() => setActiveFaq(activeFaq === i ? null : i)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#1C1917' }}>{f.q}</span>
                <ChevronDown
                  size={16}
                  style={{
                    transform: activeFaq === i ? 'rotate(180deg)' : 'none',
                    transition: 'transform 0.2s'
                  }}
                />
              </div>
              {activeFaq === i && (
                <p style={{ fontSize: '0.86rem', color: '#57534E', marginTop: '12px', lineHeight: '1.6', margin: '12px 0 0 0' }}>
                  {f.a}
                </p>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* FOOTER */}
      <footer style={{ backgroundColor: '#1C1917', color: '#D5D1C6', padding: '48px 36px', borderTop: '1px solid #292524' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div className="font-serif" style={{ fontSize: '1.3rem', fontWeight: 700, color: '#FFFFFF' }}>
              TruthGuard
            </div>
            <p style={{ fontSize: '0.78rem', color: '#8B857D', marginTop: '4px' }}>
              Evidence-Grounded Hallucination Detection & Grounded Correction Platform.
            </p>
          </div>

          <div style={{ fontSize: '0.8rem', color: '#8B857D' }}>
            © 2026 TruthGuard Platform. Built per GenAI Research Specifications.
          </div>
        </div>
      </footer>
    </div>
  );
}
