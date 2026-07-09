import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { clearChat } from '../../redux/slices/chatSlice';

const styles = {
  chatContainer: {
    flex: 1,
    minHeight: 0,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    backgroundColor: '#faf8f5',
  },
  messagesArea: {
    flex: 1,
    minHeight: 0,
    overflowY: 'auto',
    padding: '20px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  messageRow: {
    display: 'flex',
    gap: '10px',
    maxWidth: '88%',
    animation: 'fadeIn 0.25s ease',
  },
  userRow: {
    alignSelf: 'flex-end',
    flexDirection: 'row-reverse',
  },
  assistantRow: {
    alignSelf: 'flex-start',
  },
  avatar: {
    width: '34px',
    height: '34px',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 800,
    fontSize: '0.75rem',
    flexShrink: 0,
    border: '2px solid var(--color-border)',
  },
  userAvatar: {
    backgroundColor: 'var(--color-accent)',
    color: '#ffffff',
  },
  assistantAvatar: {
    backgroundColor: '#ffffff',
    color: 'var(--color-primary)',
    boxShadow: 'var(--shadow-sm)',
  },
  messageBubble: {
    padding: '12px 16px',
    borderRadius: '10px',
    fontSize: '0.85rem',
    lineHeight: 1.6,
    wordBreak: 'break-word',
    border: '2px solid transparent',
    boxShadow: 'var(--shadow-sm)',
  },
  userBubble: {
    backgroundColor: 'var(--color-accent)',
    color: '#ffffff',
    borderBottomRightRadius: '2px',
    borderColor: 'var(--color-accent)',
  },
  assistantBubble: {
    backgroundColor: '#ffffff',
    color: 'var(--color-text)',
    borderBottomLeftRadius: '2px',
    borderColor: 'var(--color-border)',
  },
  errorBubble: {
    backgroundColor: '#fff5f5',
    borderColor: 'var(--color-accent)',
    color: '#b33030',
  },
  toolResultContainer: {
    marginTop: '8px',
    padding: '12px 14px',
    backgroundColor: '#f8fdf9',
    border: '2px solid #1a7a3e',
    borderRadius: '8px',
    fontSize: '0.78rem',
    boxShadow: 'var(--shadow-sm)',
  },
  toolResultTitle: {
    fontWeight: 800,
    fontSize: '0.68rem',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
    color: '#1a7a3e',
    marginBottom: '8px',
  },
  toolResultItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '4px 0',
    borderBottom: '1px dashed #d0e8d0',
    gap: '10px',
  },
  toolResultLabel: {
    color: 'var(--color-text-muted)',
    fontWeight: 600,
    textTransform: 'capitalize',
    flexShrink: 0,
  },
  toolResultValue: {
    fontWeight: 700,
    color: 'var(--color-primary)',
    textAlign: 'right',
    wordBreak: 'break-word',
  },
  // Dropdown options in chat
  optionsContainer: {
    marginTop: '10px',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  optionsLabel: {
    fontSize: '0.75rem',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
    color: 'var(--color-accent)',
  },
  optionBtn: {
    display: 'block',
    width: '100%',
    textAlign: 'left',
    padding: '10px 14px',
    backgroundColor: '#ffffff',
    border: '2.5px solid var(--color-border)',
    borderRadius: '8px',
    fontSize: '0.82rem',
    fontWeight: 600,
    color: 'var(--color-text)',
    cursor: 'pointer',
    boxShadow: 'var(--shadow-sm)',
    transition: 'all 0.12s ease',
  },
  optionBtnHover: {
    borderColor: 'var(--color-accent)',
    backgroundColor: '#fff8f0',
  },
  downloadContainer: {
    marginTop: '10px',
  },
  downloadBtn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 18px',
    backgroundColor: 'var(--color-accent)',
    color: '#ffffff',
    border: '2.5px solid var(--color-border)',
    borderRadius: '8px',
    fontWeight: 700,
    fontSize: '0.82rem',
    cursor: 'pointer',
    boxShadow: 'var(--shadow-sm)',
    transition: 'all 0.12s ease',
  },
  inputArea: {
    flexShrink: 0,
    padding: '12px 14px',
    borderTop: '3px solid var(--color-border)',
    backgroundColor: '#ffffff',
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    padding: '12px 16px',
    border: '2.5px solid var(--color-border)',
    borderRadius: '8px',
    fontSize: '0.85rem',
    fontWeight: 500,
    outline: 'none',
    backgroundColor: 'var(--color-input-bg)',
    boxShadow: 'inset 2px 2px 0px rgba(0,0,0,0.06)',
    transition: 'border-color 0.15s ease',
  },
  sendBtn: {
    padding: '10px 20px',
    backgroundColor: 'var(--color-primary)',
    color: '#ffffff',
    borderRadius: '8px',
    fontWeight: 700,
    fontSize: '0.85rem',
    border: '2.5px solid var(--color-border)',
    boxShadow: 'var(--shadow-sm)',
    whiteSpace: 'nowrap',
    letterSpacing: '0.02em',
  },
  sendBtnDisabled: {
    opacity: 0.45,
    cursor: 'not-allowed',
  },
  clearBtn: {
    padding: '6px 14px',
    fontSize: '0.7rem',
    fontWeight: 700,
    backgroundColor: 'transparent',
    border: '2px solid var(--color-border)',
    borderRadius: '6px',
    color: 'var(--color-text-muted)',
    boxShadow: 'var(--shadow-sm)',
    letterSpacing: '0.03em',
  },
  quickActions: {
    flexShrink: 0,
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    justifyContent: 'center',
    padding: '12px 16px 8px',
    borderTop: '2px solid var(--color-border)',
    backgroundColor: '#faf8f5',
  },
  quickActionBtn: {
    padding: '8px 16px',
    fontSize: '0.73rem',
    fontWeight: 700,
    border: '2.5px solid var(--color-border)',
    borderRadius: '8px',
    backgroundColor: '#ffffff',
    color: 'var(--color-text)',
    boxShadow: 'var(--shadow-sm)',
    letterSpacing: '0.02em',
    transition: 'all 0.12s ease',
  },
  typingIndicator: {
    alignSelf: 'flex-start',
    padding: '14px 20px',
    backgroundColor: '#ffffff',
    borderRadius: '10px',
    borderBottomLeftRadius: '2px',
    display: 'flex',
    gap: '5px',
    border: '2px solid var(--color-border)',
    boxShadow: 'var(--shadow-sm)',
  },
  dot: {
    width: '7px',
    height: '7px',
    borderRadius: '50%',
    backgroundColor: 'var(--color-text-muted)',
    animation: 'bounce 1.4s infinite ease-in-out',
  },
};

const QUICK_ACTIONS = [
  { label: 'Log Interaction', placeholder: 'Describe the meeting or interaction...' },
  { label: 'Edit Field', placeholder: 'name is Dr. Smith, hospital is Apollo...' },
  { label: 'Get Insights', placeholder: 'Show insights for Dr. Smith' },
  { label: 'Follow-up', placeholder: 'Suggest follow-up for last interaction' },
  { label: 'Materials', placeholder: 'Recommend materials for this HCP' },
];

/**
 * Download a base64 string as a file in the browser.
 */
function downloadBase64File(base64Data, filename, mimeType = 'application/pdf') {
  const byteChars = atob(base64Data);
  const byteNums = new Array(byteChars.length);
  for (let i = 0; i < byteChars.length; i++) {
    byteNums[i] = byteChars.charCodeAt(i);
  }
  const byteArr = new Uint8Array(byteNums);
  const blob = new Blob([byteArr], { type: mimeType });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function formatToolResult(toolResult) {
  if (!toolResult || typeof toolResult !== 'object') return null;

  const lines = [];
  if (toolResult.interaction) {
    const fields = ['hcp_name', 'specialty', 'hospital', 'sentiment', 'summary'];
    fields.forEach((f) => {
      if (toolResult.interaction[f]) {
        lines.push({ label: f.replace(/_/g, ' '), value: toolResult.interaction[f] });
      }
    });
  }
  if (toolResult.updated_fields) {
    Object.entries(toolResult.updated_fields).forEach(([k, v]) => {
      lines.push({ label: `updated ${k.replace(/_/g, ' ')}`, value: v });
    });
  }
  if (toolResult.followup) {
    const f = toolResult.followup;
    if (f.suggested_date) lines.push({ label: 'follow-up date', value: f.suggested_date });
    if (f.suggested_action) lines.push({ label: 'action', value: f.suggested_action });
    if (f.priority) lines.push({ label: 'priority', value: f.priority });
    if (f.reasoning) lines.push({ label: 'reasoning', value: f.reasoning });
  }
  if (toolResult.insights) {
    const i = toolResult.insights;
    if (i.total_interactions !== undefined) lines.push({ label: 'total interactions', value: i.total_interactions });
    if (i.sentiment_trend) lines.push({ label: 'trend', value: i.sentiment_trend });
    if (i.recommended_approach) lines.push({ label: 'approach', value: i.recommended_approach });
  }
  if (toolResult.recommendations) {
    const r = toolResult.recommendations;
    if (r.priority_material) lines.push({ label: 'priority material', value: r.priority_material });
    if (r.rationale) lines.push({ label: 'rationale', value: r.rationale });
  }

  if (lines.length === 0) return null;

  return (
    <div style={styles.toolResultContainer}>
      <div style={styles.toolResultTitle}>Tool Output</div>
      {lines.map((line, i) => (
        <div key={i} style={styles.toolResultItem}>
          <span style={styles.toolResultLabel}>{line.label}</span>
          <span style={styles.toolResultValue}>{String(line.value)}</span>
        </div>
      ))}
    </div>
  );
}

/**
 * Render clickable dropdown options for fields like interaction_type, sentiment.
 */
function OptionsSelector({ field, values, onSelect }) {
  const fieldLabel = field.replace(/_/g, ' ');

  return (
    <div style={styles.optionsContainer}>
      <div style={styles.optionsLabel}>Select {fieldLabel}:</div>
      {values.map((opt) => (
        <button
          key={opt}
          style={styles.optionBtn}
          onClick={() => onSelect(field, opt)}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--color-accent)';
            e.currentTarget.style.backgroundColor = '#fff8f0';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--color-border)';
            e.currentTarget.style.backgroundColor = '#ffffff';
          }}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

/**
 * Render a download button for brochure PDF.
 */
function DownloadBrochure({ base64Data, filename }) {
  const handleDownload = () => {
    downloadBase64File(base64Data, filename || 'brochure.pdf', 'application/pdf');
  };

  return (
    <div style={styles.downloadContainer}>
      <button style={styles.downloadBtn} onClick={handleDownload}>
        <span>📄</span>
        <span>Download Brochure PDF</span>
      </button>
    </div>
  );
}

function ChatPanel({ onSendMessage }) {
  const [input, setInput] = useState('');
  const dispatch = useDispatch();
  const { messages, loading, error } = useSelector((s) => s.chat);
  const messagesEndRef = useRef(null);
  // Track which option messages have been handled (to prevent stale UI)
  const resolvedOptionRef = useRef(new Set());

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-download brochure when a message with brochure_pdf arrives
  useEffect(() => {
    if (messages.length === 0) return;
    const lastMsg = messages[messages.length - 1];
    if (lastMsg?.toolResult?.brochure_pdf && lastMsg?.toolResult?.requires_download) {
      const { brochure_pdf, brochure_filename } = lastMsg.toolResult;
      // Small delay so the UI renders first
      setTimeout(() => {
        downloadBase64File(brochure_pdf, brochure_filename || 'brochure.pdf', 'application/pdf');
      }, 300);
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickAction = (placeholder) => {
    if (loading) return;
    setInput(placeholder);
  };

  // Called when user clicks a dropdown option in chat
  const handleOptionSelect = useCallback(
    (field, value) => {
      if (loading) return;
      // Auto-send the selection as a chat message: "field is value"
      const message = `${field.replace(/_/g, ' ')} is ${value}`;
      onSendMessage(message);
    },
    [loading, onSendMessage]
  );

  return (
    <div style={styles.chatContainer}>
      <div style={styles.messagesArea}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              ...styles.messageRow,
              ...(msg.role === 'user' ? styles.userRow : styles.assistantRow),
            }}
          >
            <div
              style={{
                ...styles.avatar,
                ...(msg.role === 'user' ? styles.userAvatar : styles.assistantAvatar),
              }}
            >
              {msg.role === 'user' ? 'U' : 'AI'}
            </div>
            <div>
              <div
                style={{
                  ...styles.messageBubble,
                  ...(msg.role === 'user'
                    ? styles.userBubble
                    : msg.isError
                    ? styles.errorBubble
                    : styles.assistantBubble),
                }}
              >
                {msg.content}
              </div>
              {/* Render dropdown options if tool result has them */}
              {msg.toolResult?.options && (
                <OptionsSelector
                  field={msg.toolResult.options.field}
                  values={msg.toolResult.options.values}
                  onSelect={handleOptionSelect}
                />
              )}
              {/* Render tool result data */}
              {msg.toolResult && formatToolResult(msg.toolResult)}
              {/* Render download button for brochure (manual fallback) */}
              {msg.toolResult?.brochure_pdf && (
                <DownloadBrochure
                  base64Data={msg.toolResult.brochure_pdf}
                  filename={msg.toolResult.brochure_filename}
                />
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ ...styles.messageRow, ...styles.assistantRow }}>
            <div style={{ ...styles.avatar, ...styles.assistantAvatar }}>AI</div>
            <div style={styles.typingIndicator}>
              <div style={styles.dot} />
              <div style={{ ...styles.dot, animationDelay: '0.2s' }} />
              <div style={{ ...styles.dot, animationDelay: '0.4s' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
        {error && (
          <div style={{ alignSelf: 'center', color: '#cc3333', fontSize: '0.8rem', fontWeight: 500 }}>
            {error}
          </div>
        )}
      </div>
      <div style={styles.inputArea}>
        <button style={styles.clearBtn} onClick={() => dispatch(clearChat())} title="Clear chat">
          Clear
        </button>
        <input
          style={styles.input}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type what you want the agent to do..."
          disabled={loading}
        />
        <button
          style={{
            ...styles.sendBtn,
            ...(loading || !input.trim() ? styles.sendBtnDisabled : {}),
          }}
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? '...' : 'Send'}
        </button>
      </div>
      <div style={styles.quickActions}>
        {QUICK_ACTIONS.map((action) => (
          <button
            key={action.label}
            style={styles.quickActionBtn}
            onClick={() => handleQuickAction(action.placeholder)}
            disabled={loading}
          >
            {action.label}
          </button>
        ))}
      </div>
      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-6px); }
        }
      `}</style>
    </div>
  );
}

export default ChatPanel;
