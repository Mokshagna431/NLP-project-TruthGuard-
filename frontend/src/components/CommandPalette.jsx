import React, { useState, useEffect } from 'react';
import { Search, CheckCircle, BarChart3, Database, FileText, X, Sparkles, BookOpen } from 'lucide-react';

export default function CommandPalette({ isOpen, onClose, onSelectAction }) {
  const [query, setQuery] = useState('');

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const actions = [
    {
      category: 'Navigation',
      items: [
        { id: 'nav-interactive-fc', title: 'Open Factcheck Workspace', subtitle: 'Two-column editor with inline highlights & instant verification', icon: Sparkles, nav: 'factcheck' },
        { id: 'nav-factcheck', title: 'Open New Verification (Batch)', subtitle: 'Submit text for claim decomposition and verification', icon: CheckCircle, nav: 'new-verification' },
        { id: 'nav-citation', title: 'Open Citation Audit Desk', subtitle: 'Verify academic DOIs, ArXiv IDs, and Crossref papers', icon: BookOpen, nav: 'citation' },
        { id: 'nav-analytics', title: 'Open Analytics Dashboard', subtitle: 'Proofs per day, verdict mix & calibration', icon: BarChart3, nav: 'analytics' },
        { id: 'nav-benchmarks', title: 'View Research Benchmark Matrix', subtitle: 'T1–T7 empirical ablation results and ECE curves', icon: FileText, nav: 'benchmarks' },
        { id: 'nav-evidence', title: 'Open Evidence Library', subtitle: 'Inspect retrieved passages & NLI logits', icon: Database, nav: 'evidence' }
      ]
    },
    {
      category: 'Presets & Cases',
      items: [
        { id: 'preset-renaissance', title: 'Load Case: The Renaissance', subtitle: 'Parafact reference sample (8 claims, 63% score)', icon: BookOpen, preset: 'renaissance' },
        { id: 'preset-eiffel', title: 'Load Case: Eiffel Tower', subtitle: 'Iconic hallucination test case', icon: Sparkles, preset: 'eiffel' },
        { id: 'preset-apollo', title: 'Load Case: Apollo 11 Mission', subtitle: 'Entity inversion test case', icon: Sparkles, preset: 'apollo' }
      ]
    }
  ];

  const filtered = actions.map(group => ({
    ...group,
    items: group.items.filter(item =>
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.subtitle.toLowerCase().includes(query.toLowerCase())
    )
  })).filter(group => group.items.length > 0);

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(28, 25, 23, 0.4)',
        backdropFilter: 'blur(3px)',
        zIndex: 50,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '120px'
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '560px',
          maxWidth: '92vw',
          backgroundColor: '#FFFFFF',
          borderRadius: '12px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.15)',
          border: '1px solid #E8E5DC',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Search Input Bar */}
        <div
          style={{
            padding: '14px 18px',
            borderBottom: '1px solid #E8E5DC',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}
        >
          <Search size={18} color="#78716C" />
          <input
            autoFocus
            type="text"
            placeholder="Search commands, navigate, or load cases..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              fontSize: '0.92rem',
              color: '#1C1917',
              fontFamily: 'inherit'
            }}
          />
          <kbd
            style={{
              backgroundColor: '#F5F3ED',
              border: '1px solid #E8E5DC',
              borderRadius: '4px',
              padding: '2px 6px',
              fontSize: '0.7rem',
              color: '#78716C'
            }}
          >
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div style={{ maxHeight: '380px', overflowY: 'auto', padding: '10px' }}>
          {filtered.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', color: '#78716C', fontSize: '0.85rem' }}>
              No commands matching "{query}"
            </div>
          ) : (
            filtered.map((group, gIdx) => (
              <div key={gIdx} style={{ marginBottom: '10px' }}>
                <div
                  style={{
                    fontSize: '0.66rem',
                    fontWeight: 700,
                    letterSpacing: '0.08em',
                    textTransform: 'uppercase',
                    color: '#9CA3AF',
                    padding: '6px 10px 4px 10px'
                  }}
                >
                  {group.category}
                </div>
                {group.items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      onSelectAction(item);
                      onClose();
                    }}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '8px 10px',
                      borderRadius: '6px',
                      border: 'none',
                      backgroundColor: 'transparent',
                      textAlign: 'left',
                      cursor: 'pointer',
                      transition: 'background 0.12s'
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#FAF8F5')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '6px',
                        backgroundColor: '#F3EFE7',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                    >
                      <item.icon size={15} color="#57534E" />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#1C1917' }}>{item.title}</div>
                      <div style={{ fontSize: '0.74rem', color: '#78716C' }}>{item.subtitle}</div>
                    </div>
                  </button>
                ))}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
