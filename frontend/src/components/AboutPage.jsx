import React from 'react';
import { BookOpen, ShieldCheck, Cpu, Database, CheckCircle, ArrowRight } from 'lucide-react';

export default function AboutPage({ onStartVerification }) {
  return (
    <div style={{ backgroundColor: '#FAF8F5', minHeight: '100vh', padding: '60px 24px' }}>
      <div style={{ maxWidth: '880px', margin: '0 auto' }}>
        <div style={{ marginBottom: '40px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C' }}>
            RESEARCH BACKGROUND & METHODOLOGY
          </span>
          <h1 className="font-serif" style={{ fontSize: '2.8rem', fontWeight: 600, marginTop: '8px', color: '#181614', lineHeight: 1.15 }}>
            About TruthGuard
          </h1>
          <p style={{ fontSize: '1.05rem', color: '#57534E', lineHeight: '1.6', marginTop: '12px' }}>
            Evidence-Grounded, Claim-Level Detection, Scoring, and Correction of Hallucinations in Large Language Model Outputs.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          {/* Problem Statement */}
          <section style={{ backgroundColor: '#FFFFFF', padding: '28px', borderRadius: '12px', border: '1px solid #E8E5DC' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '12px', color: '#1C1917' }}>
              The Hallucination Problem in Generative AI
            </h2>
            <p style={{ fontSize: '0.9rem', color: '#44403C', lineHeight: '1.7' }}>
              Modern Large Language Models (LLMs) generate fluent, persuasive prose that frequently incorporates subtle factual fabrications, entity misattributions, and date inversions. Sentence-level classifiers or uncalibrated LLM judges fail because they obscure localized errors under high sentence-level confidence. TruthGuard operates at the atomic factual claim level, decomposing text into falsifiable propositions.
            </p>
          </section>

          {/* Epistemic Distinction */}
          <section style={{ backgroundColor: '#FFFFFF', padding: '28px', borderRadius: '12px', border: '1px solid #E8E5DC' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '12px', color: '#1C1917' }}>
              Strict Three-Way Epistemic Distinction
            </h2>
            <p style={{ fontSize: '0.9rem', color: '#44403C', lineHeight: '1.7', marginBottom: '16px' }}>
              Every claim is evaluated against authoritative retrieved evidence and assigned one of three labels:
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              <div style={{ backgroundColor: '#DCFCE7', padding: '14px', borderRadius: '8px', border: '1px solid #BBF7D0' }}>
                <div style={{ fontWeight: 700, color: '#15803D', fontSize: '0.86rem' }}>SUPPORTED (S)</div>
                <div style={{ fontSize: '0.78rem', color: '#166534', marginTop: '4px' }}>
                  Retrieved evidence entails the claim with probability P_E ≥ τ_E.
                </div>
              </div>
              <div style={{ backgroundColor: '#FED7AA', padding: '14px', borderRadius: '8px', border: '1px solid #FDBA74' }}>
                <div style={{ fontWeight: 700, color: '#9A3412', fontSize: '0.86rem' }}>CONTRADICTED (C)</div>
                <div style={{ fontSize: '0.78rem', color: '#7C2D12', marginTop: '4px' }}>
                  Retrieved evidence directly refutes the claim with P_C ≥ τ_C.
                </div>
              </div>
              <div style={{ backgroundColor: '#FEF9C3', padding: '14px', borderRadius: '8px', border: '1px solid #FDE047' }}>
                <div style={{ fontWeight: 700, color: '#854D0E', fontSize: '0.86rem' }}>NOT-ENOUGH-INFO (NEI)</div>
                <div style={{ fontSize: '0.78rem', color: '#713F12', marginTop: '4px' }}>
                  Evidence is insufficient or below retrieval gate threshold τ_r.
                </div>
              </div>
            </div>
          </section>

          {/* Non-Compensatory Scoring */}
          <section style={{ backgroundColor: '#FFFFFF', padding: '28px', borderRadius: '12px', border: '1px solid #E8E5DC' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '12px', color: '#1C1917' }}>
              Non-Compensatory Answer Reliability Formula
            </h2>
            <p style={{ fontSize: '0.9rem', color: '#44403C', lineHeight: '1.7', marginBottom: '14px' }}>
              TruthGuard models factual reliability using non-linear bounding to ensure single hallucinations are not masked:
            </p>
            <pre style={{ backgroundColor: '#FAF8F5', padding: '14px', borderRadius: '8px', border: '1px solid #E8E5DC', fontFamily: 'var(--font-mono)', fontSize: '0.84rem', color: '#1C1917' }}>
{`ρ(c) = P_E(c) + λ × P_N(c)

R(a) = min( (1 / |C|) ∑ ρ(c),  1 - max_{c} P_C(c) )`}
            </pre>
          </section>

          {/* CTA */}
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
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
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              Start Your First Verification
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
