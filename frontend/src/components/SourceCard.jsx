import React, { useState } from 'react';

export default function SourceCard({ source, index }) {
  const [expanded, setExpanded] = useState(false);
  const similarityPercent = source.score ? Math.round(source.score * 100) : null;

  return (
    <div className="source-card" id={`source-card-${index}`}>
      <div className="source-meta">
        <span className="source-doc" title={source.document}>
          📄 {source.document}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span className="source-page" title="Original Page in Source Document">
            Page {source.page}
          </span>
          {similarityPercent !== null && (
            <span
              className="source-score"
              title={`Cosine Similarity Score: ${(source.score).toFixed(3)}`}
            >
              {similarityPercent}% match
            </span>
          )}
        </div>
      </div>

      <div
        className="source-snippet"
        style={{
          display: expanded ? 'block' : '-webkit-box',
          cursor: 'pointer',
        }}
        onClick={() => setExpanded(!expanded)}
        title="Click to expand/collapse full passage"
      >
        "{source.text}"
      </div>

      <div style={{ marginTop: '0.35rem', textAlign: 'right' }}>
        <button
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--accent-cyan)',
            fontSize: '0.68rem',
            cursor: 'pointer',
            padding: 0,
            textDecoration: 'underline',
          }}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'Show less' : 'View full passage'}
        </button>
      </div>
    </div>
  );
}
