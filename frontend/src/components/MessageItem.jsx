import React, { useState } from 'react';
import SourceCard from './SourceCard';
import FormattedContent from './FormattedContent';
import { submitFeedback } from '../api';

const FEEDBACK_TAGS = [
  'Missing Policy Details',
  'Math / Formula Error',
  'Incorrect Citation',
  'Outdated Rule',
  'Unclear Explanation',
];

export default function MessageItem({ message, index }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  // Feedback widget states
  const [rating, setRating] = useState(null); // 'helpful' | 'unhelpful' | null
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [selectedTags, setSelectedTags] = useState([]);
  const [comment, setComment] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRate = async (type) => {
    if (rating === type || feedbackSubmitted) return;
    setRating(type);

    if (type === 'helpful') {
      setShowFeedbackForm(false);
      setSubmittingFeedback(true);
      try {
        await submitFeedback({
          question: message.question || 'Campus Regulation Query',
          answer: message.content,
          rating: 'helpful',
          sources: message.sources || [],
        });
        setFeedbackSubmitted(true);
      } catch (err) {
        console.error('Failed to submit helpful feedback:', err);
      } finally {
        setSubmittingFeedback(false);
      }
    } else {
      // For unhelpful rating, open form for specific tags and suggestions
      setShowFeedbackForm(true);
    }
  };

  const toggleTag = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    setSubmittingFeedback(true);
    try {
      await submitFeedback({
        question: message.question || 'Campus Regulation Query',
        answer: message.content,
        rating: 'unhelpful',
        tags: selectedTags,
        comment: comment.trim(),
        sources: message.sources || [],
      });
      setFeedbackSubmitted(true);
      setShowFeedbackForm(false);
    } catch (err) {
      console.error('Failed to submit detailed feedback:', err);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const latency = message.latency_ms;

  return (
    <div
      className={`message-row ${isUser ? 'user' : 'assistant'}`}
      id={`chat-message-${index}`}
    >
      <div className={`avatar ${isUser ? 'avatar-user' : 'avatar-ai'}`}>
        {isUser ? '👤' : '✨'}
      </div>

      <div className="bubble">
        {isUser ? (
          <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
        ) : (
          <FormattedContent content={message.content} />
        )}

        {/* Footer actions & metrics for assistant replies */}
        {!isUser && (
          <div className="message-footer-bar">
            {/* Latency timing badge */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {latency && (
                <span
                  className="latency-badge"
                  title={`Retrieval: ${latency.retrieval_ms}ms, First Token: ${latency.first_token_ms || 'N/A'}ms, Total: ${latency.total_ms}ms`}
                >
                  ⚡ {(latency.total_ms / 1000).toFixed(1)}s
                  <span style={{ opacity: 0.7, marginLeft: '0.3rem', fontSize: '0.65rem' }}>
                    ({Math.round(latency.retrieval_ms)}ms search)
                  </span>
                </span>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              {/* Feedback option: Helpful / Unhelpful buttons */}
              {!feedbackSubmitted ? (
                <div className="feedback-buttons" id={`feedback-actions-${index}`}>
                  <button
                    id={`btn-helpful-${index}`}
                    className={`btn-feedback ${rating === 'helpful' ? 'active helpful' : ''}`}
                    onClick={() => handleRate('helpful')}
                    disabled={submittingFeedback}
                    title="Helpful answer"
                  >
                    👍
                  </button>
                  <button
                    id={`btn-unhelpful-${index}`}
                    className={`btn-feedback ${rating === 'unhelpful' ? 'active unhelpful' : ''}`}
                    onClick={() => handleRate('unhelpful')}
                    disabled={submittingFeedback}
                    title="Report issue or suggestion"
                  >
                    👎
                  </button>
                </div>
              ) : (
                <span className="feedback-thanks" title="Feedback saved to system log">
                  ✓ {rating === 'helpful' ? 'Helpful' : 'Feedback noted'}
                </span>
              )}

              {/* Copy button */}
              <button
                id={`btn-copy-${index}`}
                onClick={handleCopy}
                className="btn-copy-action"
                title="Copy answer text"
              >
                {copied ? '✓ Copied' : '📋 Copy'}
              </button>
            </div>
          </div>
        )}

        {/* Unhelpful Feedback Drawer */}
        {!isUser && showFeedbackForm && !feedbackSubmitted && (
          <form className="feedback-form-drawer" onSubmit={handleFeedbackSubmit}>
            <div className="feedback-form-title">
              <span>Improve this regulation answer</span>
              <button
                type="button"
                className="btn-close-feedback"
                onClick={() => setShowFeedbackForm(false)}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              What could be improved? Select tags that apply:
            </p>

            <div className="feedback-tags-container">
              {FEEDBACK_TAGS.map((tag) => (
                <button
                  type="button"
                  key={tag}
                  className={`feedback-tag-chip ${selectedTags.includes(tag) ? 'selected' : ''}`}
                  onClick={() => toggleTag(tag)}
                >
                  {tag}
                </button>
              ))}
            </div>

            <input
              type="text"
              className="feedback-comment-input"
              placeholder="Optional notes (e.g. wrong clause, missing page reference)..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.4rem' }}>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: '0.25rem 0.65rem', fontSize: '0.72rem' }}
                onClick={() => setShowFeedbackForm(false)}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                style={{ padding: '0.25rem 0.75rem', fontSize: '0.72rem' }}
                disabled={submittingFeedback}
              >
                {submittingFeedback ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </div>
          </form>
        )}

        {/* Cited Passages / Grounded Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="sources-section" id={`message-sources-${index}`}>
            <div className="sources-header">
              <span>🔍</span> Cited Sources ({message.sources.length} matching passages)
            </div>
            <div className="source-cards-grid">
              {message.sources.map((source, sIdx) => (
                <SourceCard key={sIdx} source={source} index={sIdx} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
