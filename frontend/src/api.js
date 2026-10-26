/**
 * SSIT Campus Regulations Assistant - API Service Client
 * Connects React UI to FastAPI backend endpoints.
 * Supports both streaming (SSE) and synchronous endpoints.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'https://campus-regulations-assistant-backend.onrender.com';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed (${res.status})`);
  }
  return res.json();
}

export async function askQuestion(question, topK = 3) {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question, top_k: topK }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Query failed (${res.status})`);
  }

  return res.json();
}

/**
 * Streams answer tokens in real time via Server-Sent Events (SSE).
 * Greatly reduces perceived response latency from ~10s to ~1s.
 */
export async function askQuestionStream(
  question,
  topK = 3,
  { onSources, onToken, onDone, onError } = {}
) {
  try {
    const res = await fetch(`${API_BASE}/query/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question, top_k: topK }),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Query failed (${res.status})`);
    }

    if (!res.body) {
      throw new Error('ReadableStream not supported by this browser.');
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split('\n\n');
      buffer = blocks.pop() || ''; // retain trailing uncompleted slice

      for (const block of blocks) {
        const line = block.trim();
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'sources' && onSources) {
              onSources(data.sources, data.demo_mode, data.latency_ms);
            } else if (data.type === 'token' && onToken) {
              onToken(data.token);
            } else if (data.type === 'done' && onDone) {
              onDone(data.latency_ms);
            } else if (data.type === 'error' && onError) {
              onError(new Error(data.error));
            }
          } catch (e) {
            console.warn('Failed to parse SSE payload:', line);
          }
        }
      }
    }
  } catch (err) {
    if (onError) onError(err);
    else throw err;
  }
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to upload document (${res.status})`);
  }

  return res.json();
}

export async function loadSampleDocument() {
  const res = await fetch(`${API_BASE}/api/documents/sample`, {
    method: 'POST',
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to reload sample syllabus (${res.status})`);
  }

  return res.json();
}

export async function clearKnowledgeBase() {
  const res = await fetch(`${API_BASE}/documents/clear`, {
    method: 'POST',
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to clear knowledge base (${res.status})`);
  }

  return res.json();
}

/**
 * Submits user rating & feedback for an answer.
 */
export async function submitFeedback({
  question,
  answer,
  rating,
  tags = [],
  comment = '',
  sources = [],
}) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      answer,
      rating,
      tags,
      comment,
      sources,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Feedback submission failed (${res.status})`);
  }

  return res.json();
}

