import React from 'react';

const styles = {
  header: {
    backgroundColor: 'var(--color-primary)',
    color: '#ffffff',
    padding: '14px 32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottom: '4px solid var(--color-accent)',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  logoIcon: {
    width: '38px',
    height: '38px',
    backgroundColor: 'var(--color-accent)',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 800,
    fontSize: '1.1rem',
  },
  title: {
    fontSize: '1.25rem',
    fontWeight: 700,
    letterSpacing: '-0.02em',
  },
  subtitle: {
    fontSize: '0.8rem',
    fontWeight: 400,
    opacity: 0.7,
    marginTop: '-2px',
  },
  badge: {
    backgroundColor: 'var(--color-accent)',
    color: '#ffffff',
    padding: '6px 16px',
    borderRadius: '20px',
    fontSize: '0.75rem',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
};

function Header() {
  return (
    <header style={styles.header}>
      <div style={styles.logo}>
        <div style={styles.logoIcon}>HCP</div>
        <div>
          <div style={styles.title}>AI-First CRM</div>
          <div style={styles.subtitle}>Healthcare Professional Module</div>
        </div>
      </div>
      <span style={styles.badge}>LangGraph AI</span>
    </header>
  );
}

export default Header;
