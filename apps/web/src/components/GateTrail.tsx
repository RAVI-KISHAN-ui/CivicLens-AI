import React from 'react';
import { Finding } from '../types';

interface GateTrailProps {
  finding: Finding | null;
  onReview: (decision: 'accepted' | 'dismissed') => void;
  t: Record<string, string>;
}

export const GateTrail: React.FC<GateTrailProps> = ({ finding, onReview, t }) => {
  if (!finding) {
    return (
      <div
        style={{
          padding: '32px',
          backgroundColor: 'var(--surface)',
          border: '1px solid var(--border-ui)',
          borderRadius: 'var(--radius-md)',
          textAlign: 'center',
          color: 'var(--ink-2)'
        }}
      >
        Verification gates trail will appear here.
      </div>
    );
  }

  return (
    <div
      style={{
        backgroundColor: 'var(--surface)',
        border: '1px solid var(--border-ui)',
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden'
      }}
    >
      <div
        style={{
          padding: '12px 16px',
          borderBottom: '1px solid var(--border-ui)',
          backgroundColor: 'var(--sunken)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{t.how_we_verified}</span>
        <span
          style={{
            fontSize: '0.8rem',
            fontWeight: 700,
            color:
              finding.status === 'verified'
                ? 'var(--pass)'
                : finding.status === 'rejected'
                ? 'var(--blocker)'
                : 'var(--major)'
          }}
        >
          {finding.status.toUpperCase()}
        </span>
      </div>

      <div style={{ padding: '16px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
          {finding.gates.map((g, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px',
                padding: '6px 8px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: g.passed ? 'transparent' : 'rgba(180, 35, 24, 0.08)',
                fontSize: '0.85rem'
              }}
            >
              <span style={{ fontWeight: 700, color: g.passed ? 'var(--pass)' : 'var(--blocker)' }}>
                {g.passed ? '✓' : '✕'}
              </span>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600 }}>{g.gate}</span>
                  <span
                    style={{
                      fontSize: '0.7rem',
                      padding: '1px 4px',
                      borderRadius: '3px',
                      backgroundColor: g.hard ? 'var(--sunken)' : 'transparent',
                      color: 'var(--ink-2)',
                      border: '1px solid var(--border-ui)'
                    }}
                  >
                    {g.hard ? 'HARD' : 'SOFT'}
                  </span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--ink-2)', marginTop: '2px' }}>
                  {g.detail}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Human in the loop review buttons */}
        <div
          style={{
            borderTop: '1px solid var(--border-ui)',
            paddingTop: '16px',
            display: 'flex',
            gap: '8px',
            justifyContent: 'flex-end',
            alignItems: 'center'
          }}
        >
          <span style={{ fontSize: '0.8rem', color: 'var(--ink-2)', marginRight: 'auto' }}>
            Review: <strong>{finding.review}</strong>
          </span>
          <button
            onClick={() => onReview('accepted')}
            style={{
              padding: '6px 14px',
              backgroundColor: finding.review === 'accepted' ? 'var(--pass)' : 'transparent',
              color: finding.review === 'accepted' ? '#fff' : 'var(--pass)',
              border: '1px solid var(--pass)',
              borderRadius: 'var(--radius-sm)',
              fontWeight: 600,
              fontSize: '0.85rem'
            }}
          >
            ✓ {t.btn_accept}
          </button>
          <button
            onClick={() => onReview('dismissed')}
            style={{
              padding: '6px 14px',
              backgroundColor: finding.review === 'dismissed' ? 'var(--blocker)' : 'transparent',
              color: finding.review === 'dismissed' ? '#fff' : 'var(--blocker)',
              border: '1px solid var(--blocker)',
              borderRadius: 'var(--radius-sm)',
              fontWeight: 600,
              fontSize: '0.85rem'
            }}
          >
            ✕ {t.btn_dismiss}
          </button>
        </div>
      </div>
    </div>
  );
};
