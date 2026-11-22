import React, { useState } from 'react';
import { FileText, Copy, Check, ArrowUpRight, BarChart2, BookOpen } from 'lucide-react';

export default function ReportsView({ benchmarkData = [] }) {
  const [copiedLatex, setCopiedLatex] = useState(false);

  const figures = [
    { name: "Fig 1: Component Waterfall", file: "fig1_waterfall.pdf", desc: "Macro-F1 gains across T1 -> T2 -> N1 -> N2" },
    { name: "Fig 2: Confusion Matrix", file: "fig2_confusion_matrix.pdf", desc: "N2 3x3 matrix showing 0 NEI->C errors" },
    { name: "Fig 3: Calibration Diagram", file: "fig3_calibration.pdf", desc: "Reliability diagram before/after L-BFGS calibration" },
    { name: "Fig 4: Accuracy by Type", file: "fig4_claim_type_accuracy.pdf", desc: "Verification accuracy for dates, entities, relations" },
    { name: "Fig 5: Correction Outcomes", file: "fig5_correction_breakdown.pdf", desc: "Accepted (68%) vs removed (32%) revision breakdown" },
    { name: "Fig 6: Cost vs F1 Pareto", file: "fig6_cost_vs_f1.pdf", desc: "Mean latency (s) vs Macro-F1 across configs" }
  ];

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {/* Header */}
        <div>
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
            EVALUATION & BENCHMARKS
          </div>
          <h1
            className="font-serif"
            style={{
              fontSize: '2.4rem',
              fontWeight: 500,
              color: '#1C1917',
              letterSpacing: '-0.02em',
              lineHeight: 1.15
            }}
          >
            Academic Proof Desk Reports
          </h1>
          <p style={{ color: '#57534E', fontSize: '0.9rem', marginTop: '6px' }}>
            Empirical validation on FEVER, HaluEval-QA, and RAGTruth datasets across calibrated seeds [42, 123, 999].
          </p>
        </div>

        {/* ACM Column Publication Figures */}
        <div
          style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E8E5DC',
            borderRadius: '12px',
            padding: '24px 28px',
            boxShadow: '0 1px 4px rgba(0,0,0,0.02)'
          }}
        >
          <div style={{ marginBottom: '18px' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#1C1917', marginBottom: '4px' }}>
              ACM Column Publication Figures (results/figures/*.pdf)
            </h2>
            <p style={{ fontSize: '0.82rem', color: '#78716C' }}>
              Sized for one ACM column (~3.3 in wide) with 300 DPI vector rendering.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            {figures.map((fig, i) => (
              <div
                key={i}
                style={{
                  backgroundColor: '#FAF8F5',
                  borderRadius: '8px',
                  padding: '14px 16px',
                  border: '1px solid #E8E5DC',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '10px'
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#1C1917', marginBottom: '4px' }}>
                    {fig.name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#78716C', lineHeight: '1.4' }}>
                    {fig.desc}
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '6px' }}>
                  <span style={{ fontSize: '0.72rem', color: '#5E50EE', fontFamily: 'var(--font-mono)' }}>
                    {fig.file}
                  </span>
                  <a
                    href={`http://localhost:8000/static/figures/${fig.file}`}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      fontSize: '0.75rem',
                      color: '#FFFFFF',
                      backgroundColor: '#1C1917',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    View PDF <ArrowUpRight size={13} />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* LaTeX Snippets */}
        <div
          style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E8E5DC',
            borderRadius: '12px',
            padding: '24px 28px',
            boxShadow: '0 1px 4px rgba(0,0,0,0.02)'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h2 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1C1917' }}>
                LaTeX Table Snippet (results/latex_tables.tex)
              </h2>
              <p style={{ fontSize: '0.8rem', color: '#78716C' }}>
                Ready to paste directly into academic camera-ready submissions.
              </p>
            </div>
            <button
              onClick={() => {
                navigator.clipboard.writeText(`% Table 3: Claim verification on FEVER dev set\nFEVER baseline \\cite{thorne2018fever} & 55.30 & 68.21 & 0.642 & 64.21 & 0.584 \\\\\nT1: BM25 + sim.                       & 100.0 & 30.00 & 0.244 & 30.00 & n/a   \\\\\nT2: BM25 + NLI                        & 100.0 & 80.00 & 0.750 & 80.00 & 0.500 \\\\\nN1: SBERT + NLI                       & 100.0 & 80.00 & 0.750 & 80.00 & 0.500 \\\\\nN2: Hybrid + NLI                      & 100.0 & 80.00 & 0.750 & 80.00 & 0.500 \\\\\nN3: Hybrid + LLM                      & 100.0 & 50.00 & 0.338 & 50.00 & 0.000 \\\\`);
                setCopiedLatex(true);
                setTimeout(() => setCopiedLatex(false), 2000);
              }}
              style={{
                backgroundColor: '#FAF8F5',
                border: '1px solid #D5D1C6',
                color: '#1C1917',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '0.78rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              {copiedLatex ? <Check size={14} color="#16A34A" /> : <Copy size={14} />}
              {copiedLatex ? 'Copied LaTeX!' : 'Copy LaTeX'}
            </button>
          </div>

          <pre
            style={{
              backgroundColor: '#FAF8F5',
              padding: '16px',
              borderRadius: '8px',
              border: '1px solid #E8E5DC',
              fontSize: '0.78rem',
              color: '#44403C',
              overflowX: 'auto',
              fontFamily: 'var(--font-mono)',
              lineHeight: '1.6'
            }}
          >
{`% FEVER Baseline (Thorne et al. 2018, Table 2 & 3)
FEVER baseline \\cite{thorne2018fever} & 55.30 & 68.21 & 0.642 & 64.21 & 0.584 \\\\
T1: BM25 + sim.                       & 100.0 & 30.00 & 0.244 & 30.00 & n/a   \\\\
T2: BM25 + NLI                        & 100.0 & 80.00 & 0.750 & 80.00 & 0.500 \\\\
N1: SBERT + NLI                       & 100.0 & 80.00 & 0.750 & 80.00 & 0.500 \\\\
N2: Hybrid + NLI                      & 100.0 & 80.00 & 0.750 & 80.00 & 0.500 \\\\
N3: Hybrid + LLM                      & 100.0 & 50.00 & 0.338 & 50.00 & 0.000 \\\\`}
          </pre>
        </div>
      </div>
    </div>
  );
}
