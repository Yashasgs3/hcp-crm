import React, { useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import InteractionForm from '../../components/Form/InteractionForm';
import ChatPanel from '../../components/Chat/ChatPanel';
import { updateFormData, setInteractionId } from '../../redux/slices/interactionSlice';
import { sendChatMessage, addUserMessage } from '../../redux/slices/chatSlice';

const styles = {
  container: {
    flex: 1,
    display: 'flex',
    padding: '20px',
    gap: '24px',
    height: 'calc(100vh - 90px)',
    maxHeight: 'calc(100vh - 90px)',
    minHeight: 0,
    overflow: 'hidden',
  },
  leftPanel: {
    flex: '0 0 55%',
    maxWidth: '55%',
    minHeight: 0,
    maxHeight: '100%',
    backgroundColor: 'var(--color-surface)',
    border: '3px solid var(--color-border)',
    borderRadius: 'var(--radius)',
    boxShadow: 'var(--shadow-md)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  rightPanel: {
    flex: '1 1 auto',
    minWidth: 0,
    minHeight: 0,
    maxHeight: '100%',
    backgroundColor: 'var(--color-surface)',
    border: '3px solid var(--color-border)',
    borderRadius: 'var(--radius)',
    boxShadow: 'var(--shadow-md)',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  panelHeader: {
    padding: '14px 20px',
    borderBottom: '2px solid var(--color-border)',
    backgroundColor: '#fafafa',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexShrink: 0,
  },
  panelTitle: {
    fontSize: '0.9rem',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
    color: 'var(--color-primary)',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  indicator: {
    width: '10px',
    height: '10px',
    borderRadius: '50%',
    backgroundColor: 'var(--color-success)',
    display: 'inline-block',
    flexShrink: 0,
  },
  toolBadges: {
    display: 'flex',
    gap: '6px',
    flexWrap: 'wrap',
    padding: '12px 20px',
    borderBottom: '2px solid var(--color-border)',
    backgroundColor: '#fff',
    flexShrink: 0,
  },
  toolBadge: {
    padding: '4px 12px',
    borderRadius: '20px',
    fontSize: '0.7rem',
    fontWeight: 700,
    letterSpacing: '0.03em',
    backgroundColor: '#eef0f7',
    color: 'var(--color-primary)',
    border: '1.5px solid var(--color-border)',
  },
  activeTool: {
    backgroundColor: 'var(--color-accent)',
    color: '#ffffff',
    border: '1.5px solid var(--color-accent)',
  },
};

const TOOLS = [
  { id: 'log', label: 'Log Interaction' },
  { id: 'edit', label: 'Edit Interaction' },
  { id: 'followup', label: 'Follow-up' },
  { id: 'insights', label: 'HCP Insights' },
  { id: 'materials', label: 'Materials' },
];

function LogInteraction() {
  const dispatch = useDispatch();
  const { formData, interactionId, isFormPopulated } = useSelector((s) => s.interaction);
  const { lastIntent, loading } = useSelector((s) => s.chat);

  const activeTool = lastIntent || null;

  const handleSendMessage = useCallback(
    (message) => {
      if (!message.trim()) return;
      dispatch(addUserMessage(message));
      dispatch(
        sendChatMessage({
          message,
          interactionId,
          extractedData: isFormPopulated ? formData : {},
        })
      ).then((result) => {
        if (result.meta.requestStatus === 'fulfilled') {
          const payload = result.payload;
          if (payload?.extracted_data) {
            dispatch(updateFormData(payload.extracted_data));
          }
          if (payload?.interaction_id) {
            dispatch(setInteractionId(payload.interaction_id));
          }
          if (payload?.tool_result?.interaction) {
            dispatch(updateFormData(payload.tool_result.interaction));
          }
          if (payload?.tool_result?.updated_fields) {
            dispatch(updateFormData(payload.tool_result.updated_fields));
          }
        }
      });
    },
    [dispatch, interactionId, formData, isFormPopulated]
  );

  return (
    <div style={styles.container}>
      {/* Left Panel: AI-Populated Form */}
      <div style={styles.leftPanel}>
        <div style={styles.panelHeader}>
          <div style={styles.panelTitle}>
            <span style={styles.indicator} />
            Interaction Details
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500 }}>
            AI-Populated
          </span>
        </div>
        <div style={styles.toolBadges}>
          {TOOLS.map((tool) => (
            <span
              key={tool.id}
              style={{
                ...styles.toolBadge,
                ...(activeTool === tool.id ? styles.activeTool : {}),
              }}
            >
              {tool.label}
            </span>
          ))}
        </div>
        <InteractionForm />
      </div>

      {/* Right Panel: Chat Interface */}
      <div style={styles.rightPanel}>
        <div style={styles.panelHeader}>
          <div style={styles.panelTitle}>
            <span style={{ ...styles.indicator, backgroundColor: loading ? 'var(--color-warning)' : 'var(--color-success)' }} />
            AI Assistant Chat
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500 }}>
            {loading ? 'Processing...' : 'llama-3.3-70b'}
          </span>
        </div>
        <ChatPanel onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
}

export default LogInteraction;
