import React, { useState, useEffect } from 'react';
import { Scan, Finding } from '../types';
import { fetchScan, fetchFindings, reviewFinding, triggerScan } from '../api';
import { FirewallCounter } from './FirewallCounter';
import { EvidenceLens } from './EvidenceLens';
import { GateTrail } from './GateTrail';

interface AuditDashboardProps {
  t: Record<string, string>;
}

export const AuditDashboard: React.FC<AuditDashboardProps> = ({ t }) => {
  const [scan, setScan] = useState<Scan | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [filter, setFilter] = useState<string>('');
  const [urlInput, setUrlInput] = useState<string>('https://scholarships.gov.in/');
  const [isScanning, setIsScanning] = useState<boolean>(false);

  useEffect(() => {
    async function loadData() {
      const s = await fetchScan();
      setScan(s);
      const f = await fetchFindings(s.id, filter || undefined);
      setFindings(f);
      if (f.length > 0) setSelectedFinding(f[0]);
    }
    loadData();
  }, [filter]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      if (target && (['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName) || target.isContentEditable)) {
        return;
      }
      if (!findings.length || !selectedFinding) return;
      const currentIndex = findings.findIndex((f) => f.id === selectedFinding.id);

      if (e.key === 'j') {
        // Next finding
        const next = findings[(currentIndex + 1) % findings.length];
        setSelectedFinding(next);
      } else if (e.key === 'k') {
        // Prev finding
        const prev = findings[(currentIndex - 1 + findings.length) % findings.length];
        setSelectedFinding(prev);
      } else if (e.key === 'a') {
        // Accept
        handleReview('accepted');
      } else if (e.key === 'd') {
        // Dismiss
        handleReview('dismissed');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [findings, selectedFinding]);

  const handleReview = async (decision: 'accepted' | 'dismissed') => {
    if (!scan || !selectedFinding) return;
    const ok = await reviewFinding(scan.id, selectedFinding.id, decision);
    if (!ok) {
      alert('Failed to save review decision to server.');
      return;
    }
    const updated = { ...selectedFinding, review: decision };
    setSelectedFinding(updated);
    setFindings(findings.map((f) => (f.id === selectedFinding.id ? updated : f)));
  };

  const handleRunScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsScanning(true);
    try {
      let s: Scan;
      if (urlInput && urlInput.trim() !== 'https://scholarships.gov.in/') {
        s = await triggerScan(urlInput.trim());
      } else {
        s = await fetchScan('scan_demo_scholarship');
      }
      setScan(s);
      const f = await fetchFindings(s.id);
      setFindings(f);
      if (f.length > 0) setSelectedFinding(f[0]);
    } catch (err: any) {
      alert(`Scan failed: ${err.message || err}`);
    } finally {
      setIsScanning(false);
    }
  };

  if (!scan) {
    return <div style={{ padding: '32px' }}>Loading CivicLens inspection engine...</div>;
  }

  return (
    <main id="main-content" style={{ padding: '24px', maxWidth: '1440px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Scan controls bar */}
      <section aria-label="Scan Configuration" style={{ backgroundColor: 'var(--surface)', padding: '16px 20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-ui)' }}>
        <form onSubmit={handleRunScan} style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '280px' }}>
            <label htmlFor="scan-url" style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, marginBottom: '4px' }}>
              {t.target_url}
            </label>
            <input
              id="scan-url"
              type="text"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-ui)',
                backgroundColor: 'var(--paper)',
                color: 'var(--ink)',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.875rem'
              }}
            />
          </div>
          <div style={{ alignSelf: 'flex-end' }}>
            <button
              type="submit"
              disabled={isScanning}
              style={{
                padding: '8px 20px',
                backgroundColor: 'var(--accent)',
                color: 'var(--accent-fg)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                fontWeight: 600,
                fontSize: '0.875rem'
              }}
            >
              {isScanning ? t.running_scan : t.run_scan}
            </button>
          </div>
        </form>
        <div style={{ fontSize: '0.75rem', color: 'var(--ink-2)', marginTop: '8px' }}>
          🛡️ {t.allowlist_notice}
        </div>
      </section>

      {/* Firewall Counter Strip */}
      <FirewallCounter
        scan={scan}
        selectedFilter={filter}
        setFilter={setFilter}
        t={t}
      />

      {/* 3-Pane Finding Detail Inspector */}
      <section
        aria-label="Finding Inspection Panels"
        className="inspection-grid"
      >
        {/* Pane 1: Finding list */}
        <div
          role="region"
          aria-label="Findings List"
          style={{
            backgroundColor: 'var(--surface)',
            border: '1px solid var(--border-ui)',
            borderRadius: 'var(--radius-md)',
            maxHeight: '750px',
            overflowY: 'auto'
          }}
        >
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-ui)', backgroundColor: 'var(--sunken)', fontWeight: 600, fontSize: '0.875rem' }}>
            Findings ({findings.length})
          </div>
          <div>
            {findings.map((f) => {
              const isSelected = selectedFinding?.id === f.id;
              const severityColor =
                f.severity === 'blocker' ? 'var(--blocker)' : f.severity === 'major' ? 'var(--major)' : 'var(--minor)';
              return (
                <button
                  key={f.id}
                  onClick={() => setSelectedFinding(f)}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '12px 14px',
                    border: 'none',
                    borderBottom: '1px solid var(--sunken)',
                    backgroundColor: isSelected ? 'var(--sunken)' : 'transparent',
                    borderLeft: isSelected ? `4px solid ${severityColor}` : '4px solid transparent',
                    cursor: 'pointer',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        fontWeight: 700,
                        color: severityColor,
                        textTransform: 'uppercase'
                      }}
                    >
                      {f.severity}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--ink-2)' }}>
                      {f.status}
                    </span>
                  </div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--ink)' }}>
                    "{f.quoted_text}"
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--ink-2)' }}>
                    {f.issue_type.replace(/_/g, ' ')}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Pane 2: Evidence Lens */}
        <EvidenceLens finding={selectedFinding} t={t} />

        {/* Pane 3: Gate Trail */}
        <GateTrail finding={selectedFinding} onReview={handleReview} t={t} />
      </section>
    </main>
  );
};
