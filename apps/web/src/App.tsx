import React, { useState, useEffect } from 'react';
import enTranslations from './i18n/en.json';
import hiTranslations from './i18n/hi.json';
import { Navbar } from './components/Navbar';
import { AuditDashboard } from './components/AuditDashboard';
import { CitizenPrototype } from './components/CitizenPrototype';
import { JourneyCompare } from './components/JourneyCompare';
import { ModelCard } from './components/ModelCard';

export function App() {
  const [currentTab, setTab] = useState<'audit' | 'prototype' | 'compare' | 'model-card'>('audit');
  const [lang, setLang] = useState<'en' | 'hi'>('en');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    try {
      const savedLang = localStorage.getItem('civiclens_lang') as 'en' | 'hi';
      if (savedLang) {
        setLang(savedLang);
        document.documentElement.lang = savedLang;
      }
      const savedTheme = localStorage.getItem('civiclens_theme') as 'light' | 'dark';
      if (savedTheme) {
        setTheme(savedTheme);
        document.documentElement.setAttribute('data-theme', savedTheme);
      }
    } catch (e) {
      // LocalStorage access handling
    }
  }, []);

  const handleSetLang = (l: 'en' | 'hi') => {
    setLang(l);
    document.documentElement.lang = l;
    try {
      localStorage.setItem('civiclens_lang', l);
    } catch (e) {}
  };

  const handleSetTheme = (th: 'light' | 'dark') => {
    setTheme(th);
    document.documentElement.setAttribute('data-theme', th);
    try {
      localStorage.setItem('civiclens_theme', th);
    } catch (e) {}
  };

  const t = lang === 'hi' ? hiTranslations : enTranslations;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        currentTab={currentTab}
        setTab={setTab}
        lang={lang}
        setLang={handleSetLang}
        theme={theme}
        setTheme={handleSetTheme}
        t={t}
      />

      <div style={{ flex: 1 }}>
        {currentTab === 'audit' && <AuditDashboard t={t} />}
        {currentTab === 'prototype' && <CitizenPrototype t={t} lang={lang} />}
        {currentTab === 'compare' && <JourneyCompare t={t} />}
        {currentTab === 'model-card' && <ModelCard />}
      </div>

      <footer
        role="contentinfo"
        style={{
          borderTop: '1px solid var(--border-ui)',
          padding: '16px 24px',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--ink-2)',
          backgroundColor: 'var(--surface)',
          marginTop: 'auto'
        }}
      >
        Automated and AI-assisted checks cover a subset of WCAG. This report is not a GIGW/STQC certification and does not replace testing with assistive-technology users.
      </footer>
    </div>
  );
}

export default App;
