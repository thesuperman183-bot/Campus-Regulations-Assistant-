import React from 'react';

export default function Navbar({ health, onReloadSample, onClearIndex, loading }) {
  const isDemo = health?.demo_mode ?? true;
  const totalChunks = health?.total_chunks ?? 0;
  const gemmaModel = health?.gemma_model ?? 'gemma-4-26b-a4b-it';

  return (
    <header className="navbar">
      <div className="brand-section">
        <div className="brand-logo" title="SSIT Campus Portal">
          🎓
        </div>
        <div className="brand-info">
          <h1>SSIT Regulations Assist</h1>
          <p>Autonomous Campus Regulations & Academic Policy System</p>
        </div>
      </div>

      <div className="nav-actions">
        {/* Live or Demo Mode Badge */}
        {isDemo ? (
          <span
            id="badge-mode-demo"
            className="badge badge-demo"
            title="Running in Demonstration Mode. Set GOOGLE_API_KEY in backend/.env for live Gemma 4 generation."
          >
            <span className="pulse-dot"></span>
            Demo Mode (Free Search)
          </span>
        ) : (
          <span
            id="badge-mode-live"
            className="badge badge-live"
            title="Connected to Google AI Studio with active Gemma 4 model."
          >
            <span className="pulse-dot"></span>
            Gemma 4 Active
          </span>
        )}

        {/* Model Spec Badge */}
        <span
          id="badge-gemma-model"
          className="badge badge-model"
          title={`Active LLM Model: ${gemmaModel}`}
        >
          {gemmaModel.replace('-it', '')}
        </span>

        {/* Chunks Count Badge */}
        <span
          id="badge-chunks-count"
          className="badge badge-chunks"
          title="Number of indexed knowledge passages in memory"
        >
          📚 {totalChunks} chunks
        </span>

        {/* Quick Action: Reload Sample */}
        <button
          id="btn-reload-sample"
          className="btn btn-secondary"
          onClick={onReloadSample}
          disabled={loading}
          title="Restore built-in SSIT CS 101 syllabus and academic regulations"
        >
          ↻ Sample Data
        </button>

        {/* Quick Action: Clear Index */}
        <button
          id="btn-clear-index"
          className="btn btn-danger"
          onClick={onClearIndex}
          disabled={loading || totalChunks === 0}
          title="Empty vector index to upload fresh custom PDFs"
        >
          Clear
        </button>
      </div>
    </header>
  );
}
