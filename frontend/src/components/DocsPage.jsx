import React from 'react';
import { BookOpen, Terminal, Sliders, ShieldCheck, HelpCircle } from 'lucide-react';

export default function DocsPage() {
  return (
    <div style={{ backgroundColor: '#FAF8F5', minHeight: '100vh', padding: '60px 24px' }}>
      <div style={{ maxWidth: '920px', margin: '0 auto' }}>
        <div style={{ marginBottom: '36px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C' }}>
            DOCUMENTATION & USER GUIDE
          </span>
          <h1 className="font-serif" style={{ fontSize: '2.6rem', fontWeight: 600, marginTop: '8px', color: '#181614', lineHeight: 1.15 }}>
            TruthGuard Platform Reference
          </h1>
          <p style={{ fontSize: '1rem', color: '#57534E', lineHeight: '1.6', marginTop: '8px' }}>
            Learn how to submit LLM responses, interpret claim metrics, calibrate thresholds, and export reports.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
          {/* Quickstart */}
          <section style={{ backgroundColor: '#FFFFFF', padding: '26px', borderRadius: '12px', border: '1px solid #E8E5DC' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '10px' }}>1. Quickstart: Submitting Text</h2>
            <ol style={{ paddingLeft: '20px', fontSize: '0.9rem', color: '#44403C', lineHeight: '1.8' }}>
              <li>Navigate to <b>New Verification</b> from the Proof Desk sidebar.</li>
              <li>Paste an LLM response or drag-and-drop a text file (`.txt`, `.pdf`, `.docx`).</li>
              <li>(Optional) Provide reference RAG context or select hybrid retrieval.</li>
              <li>Click <b>Audit & Correct Hallucinations</b> to execute M1 through M5.</li>
            </ol>
          </section>

          {/* Hyperparameters */}
          <section style={{ backgroundColor: '#FFFFFF', padding: '26px', borderRadius: '12px', border: '1px solid #E8E5DC' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '12px' }}>2. Pipeline Hyperparameters</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.86rem' }}>
              <div style={{ borderBottom: '1px solid #F3EFE7', paddingBottom: '8px' }}>
                <span style={{ fontWeight: 700, color: '#1C1917' }}>τ_E (Entailment Threshold, default: 0.70):</span>
                <p style={{ color: '#57534E', margin: '4px 0 0 0' }}>Minimum calibrated probability required to mark an atomic claim as Supported.</p>
              </div>
              <div style={{ borderBottom: '1px solid #F3EFE7', paddingBottom: '8px' }}>
                <span style={{ fontWeight: 700, color: '#1C1917' }}>τ_C (Contradiction Threshold, default: 0.70):</span>
                <p style={{ color: '#57534E', margin: '4px 0 0 0' }}>Minimum calibrated contradiction probability to flag a claim as a hallucination.</p>
              </div>
              <div style={{ borderBottom: '1px solid #F3EFE7', paddingBottom: '8px' }}>
                <span style={{ fontWeight: 700, color: '#1C1917' }}>τ_r (Retrieval Gate, default: 0.10):</span>
                <p style={{ color: '#57534E', margin: '4px 0 0 0' }}>Claims with retrieval scores below τ_r are routed directly to NEI, bypassing NLI inference.</p>
              </div>
              <div>
                <span style={{ fontWeight: 700, color: '#1C1917' }}>λ (NEI Partial Credit, default: 0.50):</span>
                <p style={{ color: '#57534E', margin: '4px 0 0 0' }}>Weight given to neutral unverified claims when calculating individual reliability ρ(c).</p>
              </div>
            </div>
          </section>

          {/* REST API Reference */}
          <section style={{ backgroundColor: '#FFFFFF', padding: '26px', borderRadius: '12px', border: '1px solid #E8E5DC' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '10px' }}>3. REST API Integration</h2>
            <p style={{ fontSize: '0.88rem', color: '#57534E', marginBottom: '12px' }}>
              TruthGuard provides production REST endpoints with Swagger documentation at <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" style={{ color: '#2563EB' }}>http://localhost:8000/docs</a>.
            </p>
            <pre style={{ backgroundColor: '#FAF8F5', padding: '14px', borderRadius: '8px', border: '1px solid #E8E5DC', fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: '#1C1917', overflowX: 'auto' }}>
{`curl -X POST "http://localhost:8000/api/verification" \\
  -H "Authorization: Bearer <YOUR_TOKEN>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "title": "Historical Facts QA",
    "text": "The Eiffel Tower was constructed in 1892 by Leonardo da Vinci.",
    "verification_mode": "standard"
  }'`}
            </pre>
          </section>
        </div>
      </div>
    </div>
  );
}
