import React, { useState, useRef } from 'react';
import {
  Sparkles,
  Upload,
  FileText,
  Sliders,
  X,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  HelpCircle,
  ChevronDown,
  Layers,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';
import { PRESET_DOCUMENTS } from '../data/mockData';

export default function NewVerificationView({ onVerificationComplete, onOpenDocs }) {
  // Input states
  const [title, setTitle] = useState('');
  const [text, setText] = useState('');
  const [context, setContext] = useState('');
  const [topic, setTopic] = useState('History & Art');
  const [showOptions, setShowOptions] = useState(false);

  // Verification options (Section 7)
  const [verificationDepth, setVerificationDepth] = useState('standard'); // 'quick', 'standard', 'deep'
  const [evidenceSource, setEvidenceSource] = useState('hybrid');          // 'context_only', 'knowledge_base', 'hybrid'
  const [decompositionMethod, setDecompositionMethod] = useState('atomic_llm'); // 'atomic_llm', 'rule_based', 'sentence_split'
  const [verificationModel, setVerificationModel] = useState('nli');     // 'nli', 'similarity', 'llm_judge'
  const [enableCorrection, setEnableCorrection] = useState(true);
  const [correctionMode, setCorrectionMode] = useState('grounded');      // 'minimal', 'grounded'

  // Processing state & stage tracking
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  const STAGES = [
    "1. Extracting atomic claims & resolving coreferences...",
    "2. Resolving entity references & temporal boundaries...",
    "3. Retrieving candidate evidence via Hybrid RRF...",
    "4. Verifying claims with calibrated DeBERTa-v3 NLI...",
    "5. Calculating non-compensatory answer reliability R(a)...",
    "6. Generating grounded corrections for contradicted claims...",
    "7. Re-checking corrections via verify-then-accept loop...",
    "8. Finalizing claim audit and generating publication report..."
  ];

  // Presets Loader
  const loadPreset = (presetId) => {
    const doc = PRESET_DOCUMENTS.find(d => d.id === presetId);
    if (doc) {
      setTitle(doc.title);
      setText(doc.plainText);
      if (presetId === 'eiffel') {
        setContext("The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It was constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair. The tower was designed by Maurice Koechlin and Emile Nouguier, and built by Gustave Eiffel's civil engineering company.");
        setTopic("Architecture & History");
      } else if (presetId === 'apollo') {
        setContext("Apollo 11 was the American spaceflight that first landed humans on the Moon. Commander Neil Armstrong and lunar module pilot Buzz Aldrin landed the Apollo Lunar Module Eagle on July 20, 1969.");
        setTopic("Space Exploration");
      } else {
        setContext("The Renaissance was a fervent period of European cultural, artistic, political and economic rebirth following the Middle Ages. Generally described as taking place from the 14th century to the 17th century.");
        setTopic("History & Art");
      }
      setError(null);
    }
  };

  // File Upload Handler (TXT, PDF, DOCX simulation)
  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!title) {
      setTitle(file.name.replace(/\.[^/.]+$/, ""));
    }

    if (file.name.endsWith('.txt')) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setText(event.target?.result || '');
      };
      reader.readAsText(file);
    } else {
      // In browser without binary parser, read text representation
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result || '';
        // If plain text extractable
        if (typeof content === 'string') {
          setText(content);
        } else {
          setText(`[Parsed text from ${file.name}]\n\nThe document was loaded into the verification buffer.`);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleClear = () => {
    setTitle('');
    setText('');
    setContext('');
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) {
      setError("Please paste or upload the LLM text to verify.");
      return;
    }

    setIsProcessing(true);
    setError(null);
    setCurrentStageIndex(0);

    // Realistic stage progression interval while backend executes
    const stageInterval = setInterval(() => {
      setCurrentStageIndex((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 700);

    try {
      const job = await api.createVerification({
        title: title.trim() || "Untitled Verification",
        text: text.trim(),
        context: context.trim() || undefined,
        topic,
        verification_mode: verificationDepth,
        evidence_source: evidenceSource,
        decomposition_method: decompositionMethod,
        verifier_type: verificationModel,
        enable_correction: enableCorrection,
        tau_e: 0.70,
        tau_c: 0.70,
        lambda_nei: 0.50
      });

      clearInterval(stageInterval);
      setCurrentStageIndex(STAGES.length - 1);
      setTimeout(() => {
        onVerificationComplete(job);
      }, 500);
    } catch (err) {
      clearInterval(stageInterval);
      setIsProcessing(false);
      setError(err.message || "Verification pipeline failed. Check backend connection.");
    }
  };

  return (
    <div style={{ flex: 1, backgroundColor: '#FAF8F5', padding: '36px 40px', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1040px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ marginBottom: '28px' }}>
          <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
            NEW AUDIT WORKSPACE
          </div>
          <h1 className="font-serif" style={{ fontSize: '2.5rem', fontWeight: 600, color: '#1C1917', lineHeight: 1.15, marginTop: '4px' }}>
            Submit Text for Claim Verification
          </h1>
          <p style={{ fontSize: '0.88rem', color: '#57534E', marginTop: '6px' }}>
            Decompose responses into atomic claims, evaluate against authoritative evidence, and generate verify-then-accept corrections.
          </p>
        </div>

        {/* Preset Selector Banner */}
        <div
          style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E8E5DC',
            borderRadius: '12px',
            padding: '16px 20px',
            marginBottom: '24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={16} color="#5E50EE" />
            <span style={{ fontSize: '0.84rem', fontWeight: 600, color: '#1C1917' }}>
              Quick-Load Research Benchmark Presets:
            </span>
          </div>

          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => loadPreset('renaissance')}
              style={{
                backgroundColor: '#FAF8F5',
                border: '1px solid #D5D1C6',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '0.78rem',
                fontWeight: 600,
                color: '#1C1917',
                cursor: 'pointer'
              }}
            >
              The Renaissance (8 Claims)
            </button>

            <button
              type="button"
              onClick={() => loadPreset('eiffel')}
              style={{
                backgroundColor: '#FAF8F5',
                border: '1px solid #D5D1C6',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '0.78rem',
                fontWeight: 600,
                color: '#1C1917',
                cursor: 'pointer'
              }}
            >
              Eiffel Tower (Iconic Hallucination)
            </button>

            <button
              type="button"
              onClick={() => loadPreset('apollo')}
              style={{
                backgroundColor: '#FAF8F5',
                border: '1px solid #D5D1C6',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '0.78rem',
                fontWeight: 600,
                color: '#1C1917',
                cursor: 'pointer'
              }}
            >
              Apollo 11 (Entity Inversion)
            </button>
          </div>
        </div>

        {/* Main Verification Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {error && (
            <div style={{ backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '8px', padding: '12px 16px', color: '#991B1B', fontSize: '0.84rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          {/* Form Card */}
          <div style={{ backgroundColor: '#FFFFFF', border: '1px solid #E8E5DC', borderRadius: '14px', padding: '28px', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
            
            {/* Title & Topic Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '16px', marginBottom: '18px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#374151', marginBottom: '6px' }}>
                  Analysis Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. LLM Summary of 20th Century Innovations"
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    borderRadius: '6px',
                    border: '1px solid #D5D1C6',
                    backgroundColor: '#FAF8F5',
                    fontSize: '0.88rem',
                    color: '#1C1917',
                    outline: 'none'
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#374151', marginBottom: '6px' }}>
                  Topic Domain
                </label>
                <select
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    borderRadius: '6px',
                    border: '1px solid #D5D1C6',
                    backgroundColor: '#FAF8F5',
                    fontSize: '0.88rem',
                    color: '#1C1917',
                    outline: 'none'
                  }}
                >
                  <option value="History & Art">History & Art</option>
                  <option value="Science & Tech">Science & Technology</option>
                  <option value="Space Exploration">Space Exploration</option>
                  <option value="Finance & Business">Finance & Business</option>
                  <option value="Healthcare">Healthcare & Medicine</option>
                  <option value="General">General Knowledge</option>
                </select>
              </div>
            </div>

            {/* Main Text Editor & Controls (Section 7) */}
            <div style={{ marginBottom: '18px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#374151' }}>
                  LLM Response to Audit (Answer):
                </label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontSize: '0.75rem', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
                  <span>{text.length} characters</span>
                  <span>{text.trim().split(/\s+/).filter(Boolean).length} words</span>
                  {text && (
                    <button
                      type="button"
                      onClick={handleClear}
                      style={{ background: 'none', border: 'none', color: '#DC2626', cursor: 'pointer', fontSize: '0.75rem' }}
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>

              <textarea
                rows={7}
                required
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste the generated response from GPT-4, Claude, Llama 3, or Qwen to verify factual statements..."
                style={{
                  width: '100%',
                  padding: '14px',
                  borderRadius: '8px',
                  border: '1px solid #D5D1C6',
                  backgroundColor: '#FAF8F5',
                  fontSize: '0.9rem',
                  lineHeight: '1.65',
                  color: '#1C1917',
                  outline: 'none',
                  resize: 'vertical'
                }}
              />

              {/* Upload Dropzone Pill */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    accept=".txt,.pdf,.docx,.doc"
                    onChange={handleFileUpload}
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    style={{
                      backgroundColor: '#FFFFFF',
                      border: '1px solid #D5D1C6',
                      borderRadius: '6px',
                      padding: '5px 12px',
                      fontSize: '0.76rem',
                      color: '#57534E',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px'
                    }}
                  >
                    <Upload size={13} />
                    Upload File (.txt, .pdf, .docx)
                  </button>
                  <span style={{ fontSize: '0.72rem', color: '#8B857D' }}>
                    Drag & drop supported
                  </span>
                </div>
              </div>
            </div>

            {/* Optional RAG Reference Context */}
            <div style={{ marginBottom: '22px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#374151' }}>
                  Optional Reference Knowledge / Source Document (RAG Context):
                </label>
                <span style={{ fontSize: '0.75rem', color: '#78716C', fontFamily: 'var(--font-mono)' }}>
                  {context.length} chars
                </span>
              </div>
              <textarea
                rows={3}
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="Optional: Paste source reference passages or leave empty for open-domain Wikipedia knowledge base..."
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '1px solid #D5D1C6',
                  backgroundColor: '#FAF8F5',
                  fontSize: '0.86rem',
                  lineHeight: '1.6',
                  color: '#1C1917',
                  outline: 'none',
                  resize: 'vertical'
                }}
              />
            </div>

            {/* Advanced Verification Options Toggle */}
            <div style={{ borderTop: '1px solid #F3EFE7', paddingTop: '16px' }}>
              <button
                type="button"
                onClick={() => setShowOptions(!showOptions)}
                style={{
                  background: 'none',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  color: '#57534E',
                  cursor: 'pointer'
                }}
              >
                <Sliders size={14} />
                <span>Advanced Pipeline Configuration (M1–M5)</span>
                <ChevronDown size={14} style={{ transform: showOptions ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
              </button>

              {showOptions && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '14px', backgroundColor: '#FAF8F5', padding: '16px', borderRadius: '8px', border: '1px solid #E8E5DC' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#78716C', marginBottom: '4px' }}>
                      Decomposition (M1)
                    </label>
                    <select
                      value={decompositionMethod}
                      onChange={(e) => setDecompositionMethod(e.target.value)}
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #D5D1C6', fontSize: '0.78rem' }}
                    >
                      <option value="atomic_llm">Automatic LLM Few-Shot</option>
                      <option value="rule_based">Rule-Based (spaCy)</option>
                      <option value="sentence_split">Sentence Split</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#78716C', marginBottom: '4px' }}>
                      Evidence Retrieval (M2)
                    </label>
                    <select
                      value={evidenceSource}
                      onChange={(e) => setEvidenceSource(e.target.value)}
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #D5D1C6', fontSize: '0.78rem' }}
                    >
                      <option value="hybrid">Hybrid RRF (BM25 + SBERT)</option>
                      <option value="dense_sbert">Dense SBERT (MiniLM)</option>
                      <option value="bm25">Sparse BM25</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#78716C', marginBottom: '4px' }}>
                      Verifier (M3)
                    </label>
                    <select
                      value={verificationModel}
                      onChange={(e) => setVerificationModel(e.target.value)}
                      style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid #D5D1C6', fontSize: '0.78rem' }}
                    >
                      <option value="nli">DeBERTa-v3 Calibrated NLI</option>
                      <option value="similarity">TF-IDF Similarity Baseline</option>
                      <option value="llm_judge">LLM Judge</option>
                    </select>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', gridColumn: 'span 3', marginTop: '4px' }}>
                    <input
                      type="checkbox"
                      id="enableCorrection"
                      checked={enableCorrection}
                      onChange={(e) => setEnableCorrection(e.target.checked)}
                    />
                    <label htmlFor="enableCorrection" style={{ fontSize: '0.78rem', color: '#374151', fontWeight: 500 }}>
                      Enable M5 Grounded Correction (Generate minimal edits for contradicted claims and re-verify)
                    </label>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Submission / Processing Container (Section 7) */}
          {isProcessing ? (
            <div
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #5E50EE',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 4px 16px rgba(94, 80, 238, 0.12)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
                <RefreshCw size={18} className="pulse-indicator" color="#5E50EE" />
                <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1C1917' }}>
                  TruthGuard Pipeline in Progress...
                </span>
              </div>

              {/* Real 8-stage progress indicator */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {STAGES.map((stg, sIdx) => {
                  const isDone = sIdx < currentStageIndex;
                  const isCurrent = sIdx === currentStageIndex;
                  return (
                    <div
                      key={sIdx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '0.78rem',
                        color: isDone ? '#15803D' : (isCurrent ? '#5E50EE' : '#9CA3AF'),
                        fontWeight: isCurrent ? 600 : (isDone ? 500 : 400)
                      }}
                    >
                      {isDone ? (
                        <CheckCircle size={13} color="#16A34A" />
                      ) : isCurrent ? (
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#5E50EE', display: 'inline-block' }} />
                      ) : (
                        <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#D5D1C6', display: 'inline-block' }} />
                      )}
                      <span>{stg}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button
                type="submit"
                style={{
                  backgroundColor: '#1C1917',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '13px 28px',
                  fontSize: '0.92rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 12px rgba(28, 25, 23, 0.2)'
                }}
              >
                <Sparkles size={16} />
                Audit & Correct Hallucinations
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
