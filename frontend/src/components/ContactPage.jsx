import React, { useState } from 'react';
import { Mail, MessageSquare, Send, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function ContactPage({ currentUser }) {
  const [category, setCategory] = useState('Accuracy');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState(currentUser?.email || '');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setError(null);
    try {
      await api.submitFeedback({
        category,
        message,
        email: email || undefined
      });
      setSubmitted(true);
      setMessage('');
    } catch (err) {
      setError(err.message || 'Failed to submit feedback. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#FAF8F5', minHeight: '100vh', padding: '60px 24px' }}>
      <div style={{ maxWidth: '640px', margin: '0 auto' }}>
        <div style={{ marginBottom: '32px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#78716C' }}>
            FEEDBACK & PROOF DESK INQUIRIES
          </span>
          <h1 className="font-serif" style={{ fontSize: '2.5rem', fontWeight: 600, marginTop: '8px', color: '#181614', lineHeight: 1.15 }}>
            Contact & Editorial Feedback
          </h1>
          <p style={{ fontSize: '0.95rem', color: '#57534E', lineHeight: '1.6', marginTop: '6px' }}>
            Submit bug reports, feature requests, or report hallucination classification edge cases to our research team.
          </p>
        </div>

        <div style={{ backgroundColor: '#FFFFFF', padding: '32px', borderRadius: '12px', border: '1px solid #E8E5DC', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
          {submitted ? (
            <div style={{ textAlign: 'center', padding: '24px 0' }}>
              <CheckCircle size={44} color="#16A34A" style={{ margin: '0 auto 16px auto' }} />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#1C1917', marginBottom: '8px' }}>
                Thank You for Your Feedback
              </h3>
              <p style={{ fontSize: '0.88rem', color: '#57534E', maxWidth: '380px', margin: '0 auto 20px auto' }}>
                Your commentary has been logged to the TruthGuard audit database.
              </p>
              <button
                onClick={() => setSubmitted(false)}
                style={{
                  backgroundColor: '#1C1917',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '8px 18px',
                  fontSize: '0.84rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Submit Another Response
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {error && (
                <div style={{ backgroundColor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '8px', padding: '10px 14px', color: '#991B1B', fontSize: '0.84rem' }}>
                  {error}
                </div>
              )}

              <div>
                <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 600, color: '#374151', marginBottom: '6px' }}>
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
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
                  <option value="Accuracy">Model Verification Accuracy / Classification</option>
                  <option value="Feature">Feature Request / Enhancement</option>
                  <option value="Bug">Technical Bug / Pipeline Error</option>
                  <option value="General">General Inquiry</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 600, color: '#374151', marginBottom: '6px' }}>
                  Your Email Address (Optional for follow-up)
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@organization.org"
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
                <label style={{ display: 'block', fontSize: '0.84rem', fontWeight: 600, color: '#374151', marginBottom: '6px' }}>
                  Message / Details
                </label>
                <textarea
                  rows={5}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Please describe the claim, evidence discrepancy, or inquiry..."
                  required
                  style={{
                    width: '100%',
                    padding: '12px',
                    borderRadius: '6px',
                    border: '1px solid #D5D1C6',
                    backgroundColor: '#FAF8F5',
                    fontSize: '0.88rem',
                    color: '#1C1917',
                    outline: 'none',
                    resize: 'vertical'
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                style={{
                  backgroundColor: '#1C1917',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '11px',
                  fontSize: '0.88rem',
                  fontWeight: 600,
                  cursor: loading ? 'wait' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  marginTop: '6px'
                }}
              >
                <Send size={15} />
                {loading ? 'Submitting...' : 'Send Feedback to Research Team'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
