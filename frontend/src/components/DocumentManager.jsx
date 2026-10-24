import React, { useRef, useState } from 'react';

export default function DocumentManager({
  indexedDocuments = [],
  totalChunks = 0,
  onUpload,
  uploading,
}) {
  const fileInputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Please upload a valid PDF document.');
      return;
    }
    onUpload(file);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <aside className="sidebar">
      {/* Upload Regulations PDF Card */}
      <div className="panel-card" id="document-upload-card">
        <h3>
          <span>📤</span> Ingest Regulation PDF
        </h3>
        <p>
          Upload college handbooks, course syllabi, or exam bylaws. Chunks will preserve original PDF page numbers and document names.
        </p>

        <input
          ref={fileInputRef}
          type="file"
          id="pdf-file-input"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={handleChange}
        />

        <div
          id="pdf-dropzone"
          className={`dropzone ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="dropzone-icon">📑</div>
          <p>{uploading ? 'Parsing PDF & Encoding Chunks...' : 'Drop PDF here or click to browse'}</p>
          <span className="subtext">Auto-chunks & creates MiniLM embeddings</span>
        </div>
      </div>

      {/* Indexed Documents Registry */}
      <div className="panel-card" id="indexed-docs-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>
            <span>📚</span> Indexed Regulations
          </h3>
          <span className="badge badge-chunks">{totalChunks} chunks</span>
        </div>

        {indexedDocuments.length === 0 ? (
          <p style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>
            No documents indexed. Click "Sample Data" in the top bar to load the starter syllabus, or drop a PDF above.
          </p>
        ) : (
          <div className="doc-list" id="doc-list-container">
            {indexedDocuments.map((doc, i) => (
              <div className="doc-item" key={i} id={`doc-item-${i}`}>
                <span className="doc-name" title={doc}>
                  📄 {doc}
                </span>
                <span style={{ color: 'var(--accent-emerald)', fontSize: '0.75rem', fontWeight: 600 }}>
                  Active
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Architecture & RAG Info Card */}
      <div className="panel-card" style={{ borderColor: 'rgba(99, 102, 241, 0.2)' }}>
        <h3>
          <span>⚡</span> Hackathon Tech Stack
        </h3>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
          <li>🔹 <strong>LLM:</strong> Google Gemma 4 via AI Studio</li>
          <li>🔹 <strong>Embeddings:</strong> all-MiniLM-L6-v2</li>
          <li>🔹 <strong>Chunking:</strong> 150 words / 30 word overlap</li>
          <li>🔹 <strong>Backend:</strong> FastAPI (Python 3)</li>
          <li>🔹 <strong>Frontend:</strong> React.js</li>
        </ul>
      </div>
    </aside>
  );
}
