import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setFormField, resetForm } from '../../redux/slices/interactionSlice';

const styles = {
  formScroll: {
    flex: 1,
    minHeight: 0,
    overflowY: 'auto',
    padding: '20px',
  },
  form: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '16px',
  },
  fullWidth: {
    gridColumn: '1 / -1',
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  label: {
    fontSize: '0.75rem',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
    color: 'var(--color-text-muted)',
  },
  input: {
    padding: '10px 12px',
    border: '2px solid #d0d0d0',
    borderRadius: 'var(--radius)',
    backgroundColor: 'var(--color-input-bg)',
    fontSize: '0.85rem',
    fontWeight: 500,
    color: 'var(--color-text)',
    transition: 'border-color 0.15s ease',
    width: '100%',
    outline: 'none',
  },
  inputReadOnly: {
    cursor: 'not-allowed',
    opacity: 0.9,
  },
  inputFilled: {
    borderColor: 'var(--color-success)',
    backgroundColor: '#f8fdf9',
  },
  textarea: {
    padding: '10px 12px',
    border: '2px solid #d0d0d0',
    borderRadius: 'var(--radius)',
    backgroundColor: 'var(--color-input-bg)',
    fontSize: '0.85rem',
    fontWeight: 500,
    color: 'var(--color-text)',
    resize: 'vertical',
    minHeight: '70px',
    width: '100%',
    outline: 'none',
    fontFamily: 'var(--font-family)',
  },
  textareaReadOnly: {
    cursor: 'not-allowed',
    opacity: 0.9,
  },
  textareaFilled: {
    borderColor: 'var(--color-success)',
    backgroundColor: '#f8fdf9',
  },
  select: {
    padding: '10px 12px',
    border: '2px solid #d0d0d0',
    borderRadius: 'var(--radius)',
    backgroundColor: 'var(--color-input-bg)',
    fontSize: '0.85rem',
    fontWeight: 500,
    color: 'var(--color-text)',
    width: '100%',
    outline: 'none',
    cursor: 'pointer',
  },
  selectReadOnly: {
    cursor: 'not-allowed',
    opacity: 0.9,
  },
  selectFilled: {
    borderColor: 'var(--color-success)',
    backgroundColor: '#f8fdf9',
  },
  footer: {
    flexShrink: 0,
    padding: '14px 20px',
    borderTop: '2px solid var(--color-border)',
    backgroundColor: '#fafafa',
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
  },
  btnReset: {
    padding: '10px 24px',
    backgroundColor: 'transparent',
    border: '2px solid var(--color-border)',
    borderRadius: 'var(--radius)',
    color: 'var(--color-text)',
    fontWeight: 700,
    fontSize: '0.85rem',
    boxShadow: 'var(--shadow-sm)',
  },
  btnSave: {
    padding: '10px 24px',
    backgroundColor: 'var(--color-success)',
    border: '2px solid #1a7a3e',
    borderRadius: 'var(--radius)',
    color: '#ffffff',
    fontWeight: 700,
    fontSize: '0.85rem',
    boxShadow: 'var(--shadow-sm)',
  },
  sectionTitle: {
    gridColumn: '1 / -1',
    fontSize: '0.8rem',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: 'var(--color-accent)',
    marginTop: '8px',
    paddingBottom: '4px',
    borderBottom: '2px solid #eee',
  },
  aiIndicator: {
    display: 'inline-block',
    fontSize: '0.65rem',
    backgroundColor: 'var(--color-accent)',
    color: '#fff',
    padding: '2px 8px',
    borderRadius: '10px',
    marginLeft: '6px',
    fontWeight: 600,
  },
};

const FIELD_GROUPS = {
  hcpInfo: [
    { key: 'hcp_name', label: 'HCP Name', type: 'text' },
    { key: 'specialty', label: 'Specialty', type: 'text' },
    { key: 'hospital', label: 'Hospital / Clinic', type: 'text' },
  ],
  interactionDetails: [
    { key: 'interaction_type', label: 'Interaction Type', type: 'select', options: ['', 'In-Person Visit', 'Video Call', 'Phone Call', 'Email', 'Conference', 'Lunch Meeting'] },
    { key: 'interaction_date', label: 'Date', type: 'date' },
    { key: 'interaction_time', label: 'Time', type: 'time' },
    { key: 'attendees', label: 'Attendees', type: 'text' },
  ],
  discussion: [
    { key: 'discussion_topics', label: 'Discussion Topics', type: 'textarea' },
    { key: 'products_discussed', label: 'Products Discussed', type: 'textarea' },
    { key: 'objections', label: 'Objections Raised', type: 'textarea' },
  ],
  materials: [
    { key: 'materials_shared', label: 'Materials Shared', type: 'textarea' },
    { key: 'samples_given', label: 'Samples Given', type: 'text' },
  ],
  aiGenerated: [
    { key: 'sentiment', label: 'Sentiment', type: 'select', options: ['', 'Positive', 'Neutral', 'Negative'] },
    { key: 'summary', label: 'AI Summary', type: 'textarea' },
  ],
  followUp: [
    { key: 'follow_up_required', label: 'Follow-up Required', type: 'select', options: ['', 'yes', 'no'] },
    { key: 'follow_up_date', label: 'Follow-up Date', type: 'date' },
    { key: 'next_action', label: 'Next Action', type: 'text' },
  ],
};

function InteractionForm() {
  const dispatch = useDispatch();
  const { formData, isFormPopulated } = useSelector((s) => s.interaction);

  // Left panel fields must be filled only by the AI agent (never manually by the user).
  // Keep footer actions (like reset) available, but prevent any direct edits.
  const isReadOnly = true;

  const handleChange = (field, value) => {
    if (isReadOnly) return;
    dispatch(setFormField({ field, value }));
  };

  const renderField = (field) => {
    const value = formData[field.key] || '';
    const isFilled = value !== '' && value !== null;

    if (field.type === 'select') {
      return (
        <div key={field.key} style={styles.fieldGroup}>
          <label style={styles.label}>
            {field.label}
            {isFilled && <span style={styles.aiIndicator}>AI</span>}
          </label>
          <select
            style={{
              ...styles.select,
              ...(isFilled ? styles.selectFilled : {}),
              ...(isReadOnly ? styles.selectReadOnly : {}),
            }}
            value={value}
            onChange={(e) => handleChange(field.key, e.target.value)}
            disabled={isReadOnly}
          >
            {field.options.map((opt) => (
              <option key={opt} value={opt}>
                {opt || '-- Select --'}
              </option>
            ))}
          </select>
        </div>
      );
    }

    if (field.type === 'textarea') {
      return (
        <div key={field.key} style={{ ...styles.fieldGroup, ...styles.fullWidth }}>
          <label style={styles.label}>
            {field.label}
            {isFilled && <span style={styles.aiIndicator}>AI</span>}
          </label>
          <textarea
            style={{
              ...styles.textarea,
              ...(isFilled ? styles.textareaFilled : {}),
              ...(isReadOnly ? styles.textareaReadOnly : {}),
            }}
            value={value}
            onChange={(e) => handleChange(field.key, e.target.value)}
            placeholder={field.placeholder}
            rows={3}
            disabled={isReadOnly}
          />
        </div>
      );
    }

    return (
      <div key={field.key} style={styles.fieldGroup}>
        <label style={styles.label}>
          {field.label}
          {isFilled && <span style={styles.aiIndicator}>AI</span>}
        </label>
        <input
          style={{ ...styles.input, ...(isFilled ? styles.inputFilled : {}), ...(isReadOnly ? styles.inputReadOnly : {}) }}
          type={field.type}
          value={value}
          onChange={(e) => handleChange(field.key, e.target.value)}
          placeholder={field.placeholder}
          disabled={isReadOnly}
        />
      </div>
    );
  };

  const renderSection = (title, fields) => (
    <React.Fragment key={title}>
      <div style={styles.sectionTitle}>{title}</div>
      {fields.map(renderField)}
    </React.Fragment>
  );

  return (
    <>
      <div style={styles.formScroll}>
        <div style={styles.form}>
          {renderSection('HCP Information', FIELD_GROUPS.hcpInfo)}
          {renderSection('Interaction Details', FIELD_GROUPS.interactionDetails)}
          {renderSection('Discussion', FIELD_GROUPS.discussion)}
          {renderSection('Materials & Samples', FIELD_GROUPS.materials)}
          {renderSection('AI-Generated Insights', FIELD_GROUPS.aiGenerated)}
          {renderSection('Follow-Up', FIELD_GROUPS.followUp)}
        </div>
      </div>
      <div style={styles.footer}>
        <button style={styles.btnReset} onClick={() => dispatch(resetForm())}>
          Reset Form
        </button>
        <button
          style={{
            ...styles.btnSave,
            cursor: 'not-allowed',
            opacity: 0.6,
          }}
          disabled
          title="Form fields are AI-only and cannot be edited manually."
        >
          {isFormPopulated ? 'Update Interaction' : 'Save Interaction'}
        </button>
      </div>
    </>
  );
}

export default InteractionForm;
