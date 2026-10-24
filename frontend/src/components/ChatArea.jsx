import React, { useRef, useEffect } from 'react';
import MessageItem from './MessageItem';
import SuggestedQuestions from './SuggestedQuestions';

export default function ChatArea({
  messages,
  input,
  setInput,
  onSend,
  loading,
  onSelectSuggestion,
}) {
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const visibleMessages = messages.filter(
    (msg) => msg.role !== 'assistant' || msg.content || (msg.sources && msg.sources.length > 0)
  );

  const isWaitingFirstToken =
    loading && (messages.length === 0 || !messages[messages.length - 1]?.content);

  return (
    <main className="chat-workspace">
      {/* Scrollable Message Timeline */}
      <div className="messages-timeline" id="messages-timeline">
        {messages.length === 0 ? (
          <div className="welcome-hero" id="welcome-hero">
            <div className="hero-icon">🏛️</div>
            <h2>SSIT Regulations Assistant</h2>
            <p>
              Ask any question regarding course grading policies, attendance requirements, academic integrity guidelines, or examination schedules.
            </p>
            <div style={{ marginTop: '1.25rem' }}>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                Try one of these sample regulation queries:
              </p>
              <SuggestedQuestions
                onSelectQuestion={onSelectSuggestion}
                disabled={loading}
              />
            </div>
          </div>
        ) : (
          <>
            {visibleMessages.map((msg, idx) => (
              <MessageItem key={idx} message={msg} index={idx} />
            ))}
          </>
        )}

        {/* Loading / Thinking Indicator (shown only while waiting for first token/response) */}
        {isWaitingFirstToken && (
          <div className="message-row assistant">
            <div className="avatar avatar-ai">✨</div>
            <div className="thinking-bubble" id="thinking-indicator">
              <span></span>
              <span></span>
              <span></span>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginLeft: '0.5rem' }}>
                Searching regulations & generating answer...
              </p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="chat-input-bar">
        <div className="input-container">
          <input
            ref={inputRef}
            id="chat-input-field"
            type="text"
            className="chat-input"
            placeholder="Ask about CGPA, late submissions, grading, attendance, exams..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            id="chat-send-btn"
            className="send-btn"
            onClick={onSend}
            disabled={loading || !input.trim()}
            title="Send Query"
          >
            ➤
          </button>
        </div>
      </div>
    </main>
  );
}
