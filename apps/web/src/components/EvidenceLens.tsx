import React from 'react';
import { Finding } from '../types';

interface EvidenceLensProps {
  finding: Finding | null;
  t: Record<string, string>;
}

export const EvidenceLens: React.FC<EvidenceLensProps> = ({ finding, t }) => {
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
        Select a finding to inspect the evidence lens and verification trail.
      </div>
    );
  }

  const severityColor =
    finding.severity === 'blocker'
      ? 'var(--blocker)'
      : finding.severity === 'major'
      ? 'var(--major)'
      : 'var(--minor)';

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
        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{t.evidence_lens}</span>
        <span
          style={{
            backgroundColor: severityColor,
            color: '#fff',
            fontSize: '0.75rem',
            padding: '2px 8px',
            borderRadius: 'var(--radius-sm)',
            fontWeight: 700,
            textTransform: 'uppercase'
          }}
        >
          {finding.severity}
        </span>
      </div>

      <div style={{ padding: '16px' }}>
        {/* Simulated Zoomed Viewport with Focus Ring */}
        <div
          style={{
            backgroundColor: 'var(--paper)',
            border: '2px dashed var(--border-ui)',
            borderRadius: 'var(--radius-sm)',
            padding: '20px',
            marginBottom: '16px',
            position: 'relative'
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--ink-2)',
              marginBottom: '6px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}
          >
            Target Element Snapshot (Zoomed 1.5×)
          </div>

          <div
            style={{
              border: `2px solid ${severityColor}`,
              borderRadius: 'var(--radius-sm)',
              padding: '10px 14px',
              backgroundColor: 'var(--surface)',
              boxShadow: `0 0 0 4px ${severityColor}33`,
              display: 'inline-block'
            }}
          >
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.9rem',
                backgroundColor: 'rgba(255, 235, 59, 0.35)',
                padding: '2px 6px',
                borderRadius: '3px'
              }}
            >
              "{finding.quoted_text}"
            </span>
          </div>

          <div style={{ fontSize: '0.75rem', color: 'var(--ink-2)', marginTop: '10px', fontFamily: 'var(--font-mono)' }}>
            Selector: a#guidelines • Evidence: {finding.evidence_ids.join(', ')}
          </div>
        </div>

        {/* Issue Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '4px' }}>
              {finding.issue_type.replace(/_/g, ' ')}
            </h4>
            <div style={{ display: 'flex', gap: '8px', fontSize: '0.8rem', color: 'var(--ink-2)' }}>
              {finding.wcag_sc && <span>WCAG 2.2: <strong>{finding.wcag_sc}</strong></span>}
              {finding.gigw_ref && <span>• <strong>{finding.gigw_ref}</strong></span>}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--ink-2)' }}>Who is affected:</div>
            <div style={{ fontSize: '0.875rem' }}>{finding.who_is_affected}</div>
          </div>

          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--ink-2)' }}>Citizen Impact:</div>
            <div style={{ fontSize: '0.875rem' }}>{finding.citizen_impact}</div>
          </div>

          <div
            style={{
              padding: '10px 12px',
              backgroundColor: 'var(--sunken)',
              borderLeft: '3px solid var(--accent)',
              borderRadius: '0 var(--radius-sm) var(--radius-sm) 0'
            }}
          >
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent)' }}>Concrete Fix:</div>
            <div style={{ fontSize: '0.875rem' }}>{finding.suggested_fix}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
