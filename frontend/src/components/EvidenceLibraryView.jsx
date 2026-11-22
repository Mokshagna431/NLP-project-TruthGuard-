import React, { useState } from 'react';
import { Database, Search, CheckCircle, ExternalLink, Sliders, ShieldCheck } from 'lucide-react';

export default function EvidenceLibraryView() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCorpus, setSelectedCorpus] = useState('all');

  const evidenceItems = [
    {
      id: 'ev-1',
      source: 'Wikipedia: Renaissance',
      url: 'https://en.wikipedia.org/wiki/Renaissance',
      domain: 'History & Art',
      text: 'The Renaissance was a fervent period of European cultural, artistic, political and economic "rebirth" following the Middle Ages. Generally described as taking place from the 14th century to the 17th century, the Renaissance promoted the rediscovery of classical philosophy, literature and art.',
      retrieverScore: 0.94,
      crossEncoderScore: 0.91,
      retrievalType: 'Hybrid RRF (BM25 + SBERT)'
    },
    {
      id: 'ev-2',
      source: 'Wikipedia: David (Michelangelo)',
      url: 'https://en.wikipedia.org/wiki/David_(Michelangelo)',
      domain: 'Art History',
      text: 'David is a masterpiece of Renaissance sculpture, created in marble between 1501 and 1504 by the Italian artist Michelangelo. David is a 5.17-metre marble statue of the Biblical figure David, a favoured subject in the art of Florence.',
      retrieverScore: 0.98,
      crossEncoderScore: 0.96,
      retrievalType: 'Hybrid RRF (BM25 + SBERT)'
    },
    {
      id: 'ev-3',
      source: 'Wikipedia: Eiffel Tower',
      url: 'https://en.wikipedia.org/wiki/Eiffel_Tower',
      domain: 'Architecture',
      text: 'The Eiffel Tower was constructed from 1887 to 1889 as the centerpiece of the 1889 World\'s Fair. It was designed by Maurice Koechlin and Émile Nouguier, and built by Gustave Eiffel\'s civil engineering company.',
      retrieverScore: 0.99,
      crossEncoderScore: 0.97,
      retrievalType: 'Dense SBERT (all-MiniLM-L6-v2)'
    },
    {
      id: 'ev-4',
      source: 'NASA Apollo 11 Mission Archive',
      url: 'https://www.nasa.gov/mission_pages/apollo/missions/apollo11.html',
      domain: 'Space Exploration',
      text: 'Commander Neil Armstrong and lunar module pilot Buzz Aldrin landed the Apollo Lunar Module Eagle on July 20, 1969. Armstrong became the first person to step onto the lunar surface six hours and 39 minutes later.',
      retrieverScore: 0.97,
      crossEncoderScore: 0.95,
      retrievalType: 'BM25 Sparse'
    }
  ];

  const filtered = evidenceItems.filter(item =>
    item.source.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.domain.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '24px' }}>
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
            TRUTHGUARD GROUNDED RETRIEVAL (M2)
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
            Evidence Library
          </h1>
          <p style={{ color: '#57534E', fontSize: '0.9rem', marginTop: '6px' }}>
            Multi-source factual corpus indexed via Reciprocal Rank Fusion (RRF) with MiniLM cross-encoder re-ranking.
          </p>
        </div>

        {/* Search & Filter Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            backgroundColor: '#FFFFFF',
            border: '1px solid #E8E5DC',
            borderRadius: '10px',
            padding: '12px 18px',
            marginBottom: '24px',
            boxShadow: '0 2px 6px rgba(0,0,0,0.02)'
          }}
        >
          <Search size={18} color="#78716C" />
          <input
            type="text"
            placeholder="Search verified corpus passages, entities, or URLs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              fontSize: '0.9rem',
              fontFamily: 'inherit',
              color: '#1C1917'
            }}
          />
          <span style={{ fontSize: '0.78rem', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
            {filtered.length} passages indexed
          </span>
        </div>

        {/* Evidence List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {filtered.map((item) => (
            <div
              key={item.id}
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #E8E5DC',
                borderRadius: '12px',
                padding: '20px 24px',
                boxShadow: '0 1px 4px rgba(0,0,0,0.02)'
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '10px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#1C1917' }}>
                    {item.source}
                  </span>
                  <span
                    style={{
                      fontSize: '0.72rem',
                      backgroundColor: '#F3EFE7',
                      color: '#57534E',
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontWeight: 500
                    }}
                  >
                    {item.domain}
                  </span>
                </div>

                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    color: '#2563EB',
                    fontSize: '0.78rem',
                    textDecoration: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  View Source <ExternalLink size={13} />
                </a>
              </div>

              <p style={{ fontSize: '0.88rem', color: '#374151', lineHeight: '1.65', marginBottom: '14px' }}>
                "{item.text}"
              </p>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '20px',
                  borderTop: '1px solid #F3EFE7',
                  paddingTop: '12px',
                  fontSize: '0.75rem',
                  color: '#78716C',
                  fontFamily: 'var(--font-mono)'
                }}
              >
                <span>Index Mode: {item.retrievalType}</span>
                <span>Recall Score: {(item.retrieverScore * 100).toFixed(0)}%</span>
                <span>Cross-Encoder Re-rank: {(item.crossEncoderScore * 100).toFixed(0)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
