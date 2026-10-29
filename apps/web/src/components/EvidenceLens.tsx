import React, { useEffect, useState } from 'react';
import { Finding, Evidence } from '../types';
import { fetchEvidence } from '../api';

interface EvidenceLensProps {
  finding: Finding | null;
  t: Record<string, string>;
}

export const EvidenceLens: React.FC<EvidenceLensProps> = ({ finding, t }) => {
  const [evidenceItem, setEvidenceItem] = useState<Evidence | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function loadEvidence() {
      if (!finding || !finding.evidence_ids.length) {
        setEvidenceItem(null);
        return;
      }
      setEvidenceItem(null);
      setLoading(true);
      try {
        const evList = await fetchEvidence(finding.scan_id);
        if (isMounted) {
          const match = evList.find((e) => finding.evidence_ids.includes(e.id)) || null;
          setEvidenceItem(match);
        }
      } catch (err) {
        console.error('Failed to load evidence for lens:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadEvidence();
    return () => {
      isMounted = false;
    };
  }, [finding]);

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
        {/* Real Viewport Evidence Anchor */}
        <div
          style={{
            backgroundColor: 'var(--paper)',
            border: '2px dashed var(--border-ui)',
            borderRadius: 'var(--radius-sm)',
            padding: '16px',
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
              letterSpacing: '0.05em',
              display: 'flex',
              justifyContent: 'space-between'
            }}
          >
            <span>Target Element Evidence</span>
            {evidenceItem?.device && (
              <span style={{ textTransform: 'uppercase' }}>[{evidenceItem.device}]</span>
            )}
          </div>

          <div
            style={{
              border: `2px solid ${severityColor}`,
              borderRadius: 'var(--radius-sm)',
              padding: '10px 14px',
              backgroundColor: 'var(--surface)',
              boxShadow: `0 0 0 4px ${severityColor}22`,
              display: 'block',
              marginBottom: '8px'
            }}
          >
            <span
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '0.9rem',
                backgroundColor: 'rgba(255, 235, 59, 0.35)',
                padding: '2px 6px',
                borderRadius: '3px',
                display: 'inline-block'
              }}
            >
              "{finding.quoted_text}"
            </span>
            {evidenceItem?.context && (
              <div
                style={{
                  fontSize: '0.8rem',
                  color: 'var(--ink-2)',
                  marginTop: '8px',
                  fontStyle: 'italic'
                }}
              >
                Context: {evidenceItem.context}
              </div>
            )}
          </div>

          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--ink-2)',
              marginTop: '10px',
              fontFamily: 'var(--font-mono)',
              wordBreak: 'break-all'
            }}
          >
            <div>
              <strong>Selector:</strong>{' '}
              {evidenceItem?.selector ? (
                <span style={{ color: 'var(--accent)' }}>{evidenceItem.selector}</span>
              ) : (
                <span style={{ color: 'var(--ink-2)' }}>Element selector captured in DOM snapshot</span>
              )}
            </div>
            {evidenceItem?.bbox && (
              <div style={{ marginTop: '2px' }}>
                <strong>BBox [x, y, w, h]:</strong> [{evidenceItem.bbox.join(', ')}]
              </div>
            )}
            <div style={{ marginTop: '2px' }}>
              <strong>Evidence IDs:</strong> {finding.evidence_ids.join(', ')}
            </div>
          </div>
        </div>

        {/* Issue Details */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '4px' }}>
              {finding.issue_type.replace(/_/g, ' ')}
            </h4>
            <div style={{ display: 'flex', gap: '8px', fontSize: '0.8rem', color: 'var(--ink-2)' }}>
              {finding.wcag_sc && (
                <span>
                  WCAG 2.2: <strong>{finding.wcag_sc}</strong>
                </span>
              )}
              {finding.gigw_ref && (
                <span>
                  • <strong>{finding.gigw_ref}</strong>
                </span>
              )}
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
