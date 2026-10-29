import React from 'react';
import { Scan } from '../types';

interface FirewallCounterProps {
  scan: Scan;
  selectedFilter: string;
  setFilter: (filter: string) => void;
  t: Record<string, string>;
}

export const FirewallCounter: React.FC<FirewallCounterProps> = ({
  scan,
  selectedFilter,
  setFilter,
  t
}) => {
  return (
    <div
      role="region"
      aria-label="Firewall Statistics"
      style={{
        backgroundColor: 'var(--sunken)',
        padding: '12px 20px',
        borderRadius: 'var(--radius-sm)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        border: '1px solid var(--border-ui)'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
        <span style={{ fontWeight: 700 }} className="tabular-nums">
          {scan.total_candidates}
        </span>
        <span style={{ color: 'var(--ink-2)' }}>{t.firewall_summary}</span>

        <button
          onClick={() => setFilter(selectedFilter === 'verified' ? '' : 'verified')}
          style={{
            background: selectedFilter === 'verified' ? 'var(--pass)' : 'transparent',
            color: selectedFilter === 'verified' ? '#fff' : 'var(--pass)',
            border: '1px solid var(--pass)',
            padding: '2px 8px',
            borderRadius: 'var(--radius-sm)',
            fontWeight: 600,
            fontSize: '0.85rem'
          }}
        >
          ✓ {scan.verified_count} {t.verified}
        </button>

        <span style={{ color: 'var(--border-ui)' }}>·</span>

        <button
          onClick={() => setFilter(selectedFilter === 'needs_review' ? '' : 'needs_review')}
          style={{
            background: selectedFilter === 'needs_review' ? 'var(--major)' : 'transparent',
            color: selectedFilter === 'needs_review' ? '#fff' : 'var(--major)',
            border: '1px solid var(--major)',
            padding: '2px 8px',
            borderRadius: 'var(--radius-sm)',
            fontWeight: 600,
            fontSize: '0.85rem'
          }}
        >
          ? {scan.needs_review_count} {t.needs_review}
        </button>

        <span style={{ color: 'var(--border-ui)' }}>·</span>

        <button
          onClick={() => setFilter(selectedFilter === 'rejected' ? '' : 'rejected')}
          style={{
            background: selectedFilter === 'rejected' ? 'var(--blocker)' : 'transparent',
            color: selectedFilter === 'rejected' ? '#fff' : 'var(--blocker)',
            border: '1px solid var(--blocker)',
            padding: '2px 8px',
            borderRadius: 'var(--radius-sm)',
            fontWeight: 600,
            fontSize: '0.85rem'
          }}
        >
          ✕ {scan.rejected_count} {t.rejected}
        </button>
      </div>

      <div style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>
        {t.keyboard_shortcuts}
      </div>
    </div>
  );
};
