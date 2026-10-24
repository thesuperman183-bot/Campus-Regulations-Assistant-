import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import DocumentManager from './components/DocumentManager';
import ChatArea from './components/ChatArea';
import {
  fetchHealth,
  askQuestionStream,
  uploadDocument,
  loadSampleDocument,
  clearKnowledgeBase,
} from './api';

export default function App() {
  const [health, setHealth] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (text, type = 'info') => {
    setToast({ text, type });
    setTimeout(() => {
      setToast(null);
    }, 4000);
  };

  const refreshHealth = async () => {
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err) {
      console.warn('Backend currently offline or starting up:', err.message);
    }
  };

  useEffect(() => {
    refreshHealth();
    const interval = setInterval(refreshHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSendQuery = async (queryText) => {
    const textToSend = (queryText || input).trim();
    if (!textToSend || loading) return;

    const userMessage = { role: 'user', content: textToSend };
    const assistantPlaceholder = {
      role: 'assistant',
      question: textToSend,
      content: '',
      sources: [],
      demoMode: false,
      latency_ms: null,
      streaming: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantPlaceholder]);
    setInput('');
    setLoading(true);

    try {
      await askQuestionStream(textToSend, 3, {
        onSources: (sources, demoMode, latency) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === 'assistant') {
              updated[updated.length - 1] = {
                ...last,
                sources,
                demoMode,
                latency_ms: latency,
              };
            }
            return updated;
          });
        },
        onToken: (token) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === 'assistant') {
              updated[updated.length - 1] = {
                ...last,
                content: last.content + token,
              };
            }
            return updated;
          });
        },
        onDone: (latencyMetrics) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === 'assistant') {
              updated[updated.length - 1] = {
                ...last,
                streaming: false,
                latency_ms: latencyMetrics,
              };
            }
            return updated;
          });
          setLoading(false);
          refreshHealth();
        },
        onError: (err) => {
          console.error('Streaming query error:', err);
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.role === 'assistant') {
              updated[updated.length - 1] = {
                ...last,
                content: last.content || `⚠️ Error: ${err.message}`,
                streaming: false,
              };
            }
            return updated;
          });
          setLoading(false);
          showToast(err.message, 'error');
        },
      });
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === 'assistant') {
          updated[updated.length - 1] = {
            ...last,
            content: `⚠️ Failed to get answer: ${err.message}. Please verify the backend is running.`,
            streaming: false,
          };
        }
        return updated;
      });
      setLoading(false);
      showToast(err.message, 'error');
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    try {
      const res = await uploadDocument(file);
      showToast(`✓ Ingested '${file.name}' (${res.pages_count} pages, ${res.chunks_count} chunks)`, 'success');
      refreshHealth();
    } catch (err) {
      showToast(`Upload failed: ${err.message}`, 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleReloadSample = async () => {
    try {
      const res = await loadSampleDocument();
      showToast(`✓ Restored '${res.document}' (${res.chunks_count} chunks)`, 'success');
      refreshHealth();
    } catch (err) {
      showToast(`Failed: ${err.message}`, 'error');
    }
  };

  const handleClearIndex = async () => {
    if (!window.confirm('Clear all indexed regulations from memory?')) return;
    try {
      await clearKnowledgeBase();
      showToast('Knowledge base cleared', 'info');
      refreshHealth();
    } catch (err) {
      showToast(`Failed: ${err.message}`, 'error');
    }
  };

  return (
    <div className="app-container">
      <Navbar
        health={health}
        onReloadSample={handleReloadSample}
        onClearIndex={handleClearIndex}
        loading={loading || uploading}
      />

      <div className="main-content">
        <DocumentManager
          indexedDocuments={health?.indexed_documents || []}
          totalChunks={health?.total_chunks || 0}
          onUpload={handleUpload}
          uploading={uploading}
        />

        <ChatArea
          messages={messages}
          input={input}
          setInput={setInput}
          onSend={() => handleSendQuery()}
          loading={loading}
          onSelectSuggestion={(q) => handleSendQuery(q)}
        />
      </div>

      {toast && (
        <div className="toast" id="system-toast">
          <span>{toast.type === 'error' ? '❌' : toast.type === 'success' ? '✅' : 'ℹ️'}</span>
          <span>{toast.text}</span>
        </div>
      )}
    </div>
  );
}
