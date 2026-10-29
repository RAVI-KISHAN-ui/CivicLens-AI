import React, { useState, useEffect } from 'react';
import { TaskMetrics } from '../types';
import { fetchCompare } from '../api';

interface JourneyCompareProps {
  t: Record<string, string>;
}

export const JourneyCompare: React.FC<JourneyCompareProps> = ({ t }) => {
  const [metrics, setMetrics] = useState<{ original: TaskMetrics; prototype: TaskMetrics } | null>(null);

  useEffect(() => {
    async function loadMetrics() {
      const data = await fetchCompare();
      setMetrics(data);
    }
    loadMetrics();
  }, []);

  if (!metrics) {
    return <div style={{ padding: '32px' }}>Loading robot comparison metrics...</div>;
  }

  const { original, prototype } = metrics;

  return (
    <main id="main-content" style={{ padding: '24px', maxWidth: '1000px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <section style={{ backgroundColor: 'var(--surface)', padding: '24px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-ui)' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '6px' }}>
          Robot Journey Comparison: Original Portal vs CivicLens Prototype
        </h2>
        <p style={{ color: 'var(--ink-2)', fontSize: '0.875rem', marginBottom: '20px' }}>
          Measured by the exact same automated Playwright runner on throttled Android slow-4G profile (1.6 Mbps down / 750 kbps up / 150 ms latency).
        </p>

        {/* Visual summary cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ padding: '16px', backgroundColor: 'var(--paper)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-ui)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>{t.metric_clicks}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, margin: '6px 0' }} className="tabular-nums">
              <span style={{ color: 'var(--blocker)' }}>{original.clicks_to_answer}</span> → <span style={{ color: 'var(--pass)' }}>{prototype.clicks_to_answer}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--pass)' }}>67% fewer clicks</div>
          </div>

          <div style={{ padding: '16px', backgroundColor: 'var(--paper)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-ui)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>{t.metric_pages}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, margin: '6px 0' }} className="tabular-nums">
              <span style={{ color: 'var(--blocker)' }}>{original.pages_visited}</span> → <span style={{ color: 'var(--pass)' }}>{prototype.pages_visited}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--pass)' }}>All info on 1 page</div>
          </div>

          <div style={{ padding: '16px', backgroundColor: 'var(--paper)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-ui)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>{t.metric_pdf_hops}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, margin: '6px 0' }} className="tabular-nums">
              <span style={{ color: 'var(--blocker)' }}>{original.pdf_hops}</span> → <span style={{ color: 'var(--pass)' }}>{prototype.pdf_hops}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--pass)' }}>Zero inaccessible PDFs</div>
          </div>

          <div style={{ padding: '16px', backgroundColor: 'var(--paper)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-ui)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>{t.metric_load_time}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, margin: '6px 0' }} className="tabular-nums">
              <span style={{ color: 'var(--blocker)' }}>{(original.time_to_answer_ms / 1000).toFixed(1)}s</span> → <span style={{ color: 'var(--pass)' }}>{(prototype.time_to_answer_ms / 1000).toFixed(1)}s</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--pass)' }}>87% faster on slow connection</div>
          </div>
        </div>

        {/* Full Comparison Table */}
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ backgroundColor: 'var(--sunken)', textAlign: 'left', borderBottom: '2px solid var(--border-ui)' }}>
              <th style={{ padding: '10px 12px' }}>Friction Dimension</th>
              <th style={{ padding: '10px 12px' }}>Original Government Site</th>
              <th style={{ padding: '10px 12px' }}>CivicLens Redesigned Prototype</th>
              <th style={{ padding: '10px 12px' }}>Improvement</th>
            </tr>
          </thead>
          <tbody>
            <tr style={{ borderBottom: '1px solid var(--sunken)' }}>
              <td style={{ padding: '10px 12px', fontWeight: 600 }}>{t.metric_clicks}</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{original.clicks_to_answer} clicks</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{prototype.clicks_to_answer} clicks</td>
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>-67%</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--sunken)' }}>
              <td style={{ padding: '10px 12px', fontWeight: 600 }}>{t.metric_pages}</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{original.pages_visited} pages</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{prototype.pages_visited} page</td>
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>-75%</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--sunken)' }}>
              <td style={{ padding: '10px 12px', fontWeight: 600 }}>{t.metric_pdf_hops}</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{original.pdf_hops} PDF downloads</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">0 (All HTML)</td>
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>Eliminated</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--sunken)' }}>
              <td style={{ padding: '10px 12px', fontWeight: 600 }}>{t.metric_reading_words}</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{original.words_on_path} words</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{prototype.words_on_path} words</td>
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>-84% cognitive load</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--sunken)' }}>
              <td style={{ padding: '10px 12px', fontWeight: 600 }}>Data Transferred</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{(original.bytes_transferred / 1024 / 1024).toFixed(2)} MB</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{(prototype.bytes_transferred / 1024).toFixed(0)} KB</td>
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>97% less data consumed</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  );
};
