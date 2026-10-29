import React, { useState, useEffect } from 'react';
import { CitedFact } from '../types';
import { fetchFacts } from '../api';

interface CitizenPrototypeProps {
  t: Record<string, string>;
  lang: 'en' | 'hi';
}

export const CitizenPrototype: React.FC<CitizenPrototypeProps> = ({ t, lang }) => {
  const [facts, setFacts] = useState<CitedFact[]>([]);
  const [checkedDocs, setCheckedDocs] = useState<Record<string, boolean>>({});
  const [expandedCitation, setExpandedCitation] = useState<string | null>(null);

  useEffect(() => {
    async function loadFacts() {
      const f = await fetchFacts();
      setFacts(f);
    }
    loadFacts();
  }, []);

  const eligibilityFacts = facts.filter((f) => f.field === 'eligibility');
  const docFacts = facts.filter((f) => f.field === 'document');
  const applyLinkFact = facts.find((f) => f.field === 'apply_link');

  const toggleDoc = (id: string) => {
    setCheckedDocs((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const copyChecklist = () => {
    const listText = docFacts
      .map((d) => `[${checkedDocs[d.id] ? 'X' : ' '}] ${d.value}`)
      .join('\n');
    navigator.clipboard.writeText(`Central Sector Scholarship - Document Checklist:\n${listText}`);
    alert('Document checklist copied to clipboard!');
  };

  return (
    <main id="main-content" style={{ padding: '24px 16px', maxWidth: '720px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Banner */}
      <div
        style={{
          backgroundColor: 'var(--surface)',
          padding: '20px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-ui)'
        }}
      >
        <div style={{ display: 'inline-block', backgroundColor: 'var(--sunken)', padding: '2px 8px', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', fontWeight: 600, color: 'var(--ink-2)', marginBottom: '8px' }}>
          PROTOTYPE • REDESIGNED CITIZEN JOURNEY
        </div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '6px' }}>
          {t.proto_title}
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--ink-2)' }}>
          Every requirement below is cited directly to official government guidelines with zero hallucinations.
        </p>
      </div>

      {/* Step 1: Check Eligibility */}
      <section
        style={{
          backgroundColor: 'var(--surface)',
          padding: '20px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-ui)'
        }}
      >
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ backgroundColor: 'var(--accent)', color: '#fff', width: '24px', height: '24px', borderRadius: '50%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem' }}>1</span>
          {t.proto_step1}
        </h3>

        {eligibilityFacts.length > 0 ? (
          eligibilityFacts.map((ef) => (
            <div key={ef.id} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <p style={{ fontSize: '0.95rem', lineHeight: 1.6 }}>{ef.value}</p>
              <div>
                <button
                  onClick={() => setExpandedCitation(expandedCitation === ef.id ? null : ef.id)}
                  style={{
                    backgroundColor: 'var(--sunken)',
                    border: '1px solid var(--border-ui)',
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.75rem',
                    color: 'var(--accent)',
                    fontWeight: 600
                  }}
                >
                  {t.proto_source_chip}
                </button>
                {expandedCitation === ef.id && (
                  <div style={{ marginTop: '6px', padding: '8px', backgroundColor: 'var(--paper)', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', color: 'var(--ink-2)', border: '1px dashed var(--border-ui)' }}>
                    <strong>Cited Text:</strong> "{ef.cited_text}"
                  </div>
                )}
              </div>
            </div>
          ))
        ) : (
          <p style={{ color: 'var(--ink-2)', fontStyle: 'italic' }}>Not stated on the official page.</p>
        )}
      </section>

      {/* Step 2: Prepare Documents */}
      <section
        style={{
          backgroundColor: 'var(--surface)',
          padding: '20px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-ui)'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ backgroundColor: 'var(--accent)', color: '#fff', width: '24px', height: '24px', borderRadius: '50%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem' }}>2</span>
            {t.proto_step2}
          </h3>
          <button
            onClick={copyChecklist}
            style={{
              padding: '4px 10px',
              backgroundColor: 'var(--sunken)',
              border: '1px solid var(--border-ui)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.75rem',
              color: 'var(--ink)'
            }}
          >
            📋 Copy Checklist
          </button>
        </div>

        <p style={{ fontSize: '0.85rem', color: 'var(--ink-2)', marginBottom: '12px' }}>
          Check each document once you have scanned or arranged it. State is kept in memory only; zero personal data is collected.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {docFacts.map((df) => {
            const isChecked = !!checkedDocs[df.id];
            return (
              <label
                key={df.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '10px',
                  backgroundColor: isChecked ? 'rgba(30, 122, 70, 0.08)' : 'var(--paper)',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  border: isChecked ? '1px solid var(--pass)' : '1px solid var(--border-ui)'
                }}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => toggleDoc(df.id)}
                  style={{ width: '18px', height: '18px' }}
                />
                <span style={{ fontSize: '0.9rem', textDecoration: isChecked ? 'line-through' : 'none', flex: 1 }}>
                  {df.value}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--ink-2)' }}>
                  Verified
                </span>
              </label>
            );
          })}
        </div>
      </section>

      {/* Step 3: Apply on Official Site */}
      <section
        style={{
          backgroundColor: 'var(--surface)',
          padding: '20px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-ui)',
          textAlign: 'center'
        }}
      >
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '12px' }}>
          {t.proto_step3}
        </h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--ink-2)', marginBottom: '16px' }}>
          Ready with eligibility and documents? Proceed straight to the official application window.
        </p>

        <a
          href={applyLinkFact?.value || 'https://scholarships.gov.in/'}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'inline-block',
            padding: '12px 28px',
            backgroundColor: 'var(--accent)',
            color: '#fff',
            textDecoration: 'none',
            borderRadius: 'var(--radius-sm)',
            fontWeight: 700,
            fontSize: '1rem',
            marginBottom: '10px'
          }}
        >
          {t.proto_apply_btn} ↗
        </a>

        <div style={{ fontSize: '0.75rem', color: 'var(--pass)', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '4px' }}>
          ✓ {t.proto_domain_notice}: <strong>scholarships.gov.in</strong>
        </div>
      </section>
    </main>
  );
};
