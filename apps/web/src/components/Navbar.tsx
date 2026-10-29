import React from 'react';

interface NavbarProps {
  currentTab: 'audit' | 'prototype' | 'compare' | 'model-card';
  setTab: (tab: 'audit' | 'prototype' | 'compare' | 'model-card') => void;
  lang: 'en' | 'hi';
  setLang: (lang: 'en' | 'hi') => void;
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
  t: Record<string, string>;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setTab,
  lang,
  setLang,
  theme,
  setTheme,
  t
}) => {
  return (
    <header
      role="banner"
      style={{
        backgroundColor: 'var(--surface)',
        borderBottom: '1px solid var(--border-ui)',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: 'var(--accent)' }}>●</span> {t.brand}
          </h1>
          <p style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>{t.tagline}</p>
        </div>
      </div>

      <nav role="navigation" aria-label="Main Navigation" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        {(['audit', 'prototype', 'compare', 'model-card'] as const).map((tab) => {
          const isActive = currentTab === tab;
          const labels: Record<string, string> = {
            audit: t.nav_audit,
            prototype: t.nav_prototype,
            compare: t.nav_compare,
            'model-card': t.nav_model_card
          };
          return (
            <button
              key={tab}
              onClick={() => setTab(tab)}
              style={{
                padding: '6px 14px',
                borderRadius: 'var(--radius-sm)',
                border: isActive ? '1px solid var(--accent)' : '1px solid transparent',
                backgroundColor: isActive ? 'var(--sunken)' : 'transparent',
                color: isActive ? 'var(--accent)' : 'var(--ink)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.875rem'
              }}
            >
              {labels[tab]}
            </button>
          );
        })}

        <div style={{ marginLeft: '12px', display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button
            onClick={() => setLang(lang === 'en' ? 'hi' : 'en')}
            aria-label="Switch Language"
            style={{
              padding: '4px 10px',
              border: '1px solid var(--border-ui)',
              borderRadius: 'var(--radius-sm)',
              background: 'transparent',
              fontSize: '0.8rem',
              color: 'var(--ink)'
            }}
          >
            {lang === 'en' ? 'हिं (Hindi)' : 'EN (English)'}
          </button>
          <button
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            aria-label="Toggle Theme"
            style={{
              padding: '4px 10px',
              border: '1px solid var(--border-ui)',
              borderRadius: 'var(--radius-sm)',
              background: 'transparent',
              fontSize: '0.8rem',
              color: 'var(--ink)'
            }}
          >
            {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
          </button>
        </div>
      </nav>
    </header>
  );
};
