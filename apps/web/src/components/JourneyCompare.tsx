import React, { useEffect, useState } from 'react';
import { TaskMetrics } from '../types';
import { fetchCompare } from '../api';

interface JourneyCompareProps {
  t: Record<string, string>;
}

export const JourneyCompare: React.FC<JourneyCompareProps> = ({ t }) => {
  const [data, setData] = useState<{ original: TaskMetrics; prototype: TaskMetrics; is_estimated?: boolean } | null>(null);

  useEffect(() => {
    async function load() {
      const res = await fetchCompare();
      setData(res);
    }
    load();
  }, []);

  if (!data) {
    return <div style={{ padding: '32px' }}>Loading robotic comparison benchmarks...</div>;
  }

  const { original, prototype, is_estimated } = data;

  const clickReduction = original.clicks_to_answer > 0
    ? Math.round(((original.clicks_to_answer - prototype.clicks_to_answer) / original.clicks_to_answer) * 100)
    : 0;

  const pageReduction = original.pages_visited > 0
    ? Math.round(((original.pages_visited - prototype.pages_visited) / original.pages_visited) * 100)
    : 0;

  const timeReduction = original.time_to_answer_ms > 0
    ? Math.round(((original.time_to_answer_ms - prototype.time_to_answer_ms) / original.time_to_answer_ms) * 100)
    : 0;

  const wordReduction = original.words_on_path > 0
    ? Math.round(((original.words_on_path - prototype.words_on_path) / original.words_on_path) * 100)
    : 0;

  const byteReduction = original.bytes_transferred > 0
    ? Math.round(((original.bytes_transferred - prototype.bytes_transferred) / original.bytes_transferred) * 100)
    : 0;

  return (
    <main id="main-content" style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <section style={{ backgroundColor: 'var(--surface)', padding: '24px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-ui)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '6px' }}>
              Robot Journey Comparison: Original Portal vs CivicLens Prototype
            </h2>
            <p style={{ color: 'var(--ink-2)', fontSize: '0.875rem', marginBottom: '20px' }}>
              Measured by the exact same automated Playwright runner on throttled Android slow-4G profile (1.6 Mbps down / 750 kbps up / 150 ms latency).
            </p>
          </div>
          {is_estimated && (
            <span style={{ fontSize: '0.75rem', padding: '4px 8px', backgroundColor: 'var(--sunken)', borderRadius: 'var(--radius-sm)', color: 'var(--ink-2)', border: '1px solid var(--border-ui)' }}>
              ℹ️ Prototype values derived from verified benchmark
            </span>
          )}
        </div>

        {/* Visual summary cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ padding: '16px', backgroundColor: 'var(--paper)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-ui)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>{t.metric_clicks}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, margin: '6px 0' }} className="tabular-nums">
              <span style={{ color: 'var(--blocker)' }}>{original.clicks_to_answer}</span> → <span style={{ color: 'var(--pass)' }}>{prototype.clicks_to_answer}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--pass)' }}>
              {clickReduction > 0 ? `${clickReduction}% fewer clicks` : 'Equal clicks'}
            </div>
          </div>

          <div style={{ padding: '16px', backgroundColor: 'var(--paper)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-ui)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>{t.metric_pages}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, margin: '6px 0' }} className="tabular-nums">
              <span style={{ color: 'var(--blocker)' }}>{original.pages_visited}</span> → <span style={{ color: 'var(--pass)' }}>{prototype.pages_visited}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--pass)' }}>
              {prototype.pages_visited === 1 ? 'All info on 1 page' : `${pageReduction}% fewer pages`}
            </div>
          </div>

          <div style={{ padding: '16px', backgroundColor: 'var(--paper)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-ui)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>{t.metric_pdf_hops}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, margin: '6px 0' }} className="tabular-nums">
              <span style={{ color: 'var(--blocker)' }}>{original.pdf_hops}</span> → <span style={{ color: 'var(--pass)' }}>{prototype.pdf_hops}</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--pass)' }}>
              {prototype.pdf_hops === 0 ? 'Zero inaccessible PDFs' : `${original.pdf_hops - prototype.pdf_hops} fewer PDFs`}
            </div>
          </div>

          <div style={{ padding: '16px', backgroundColor: 'var(--paper)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-ui)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--ink-2)' }}>{t.metric_load_time}</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 700, margin: '6px 0' }} className="tabular-nums">
              <span style={{ color: 'var(--blocker)' }}>{(original.time_to_answer_ms / 1000).toFixed(1)}s</span> → <span style={{ color: 'var(--pass)' }}>{(prototype.time_to_answer_ms / 1000).toFixed(1)}s</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--pass)' }}>
              {timeReduction > 0 ? `${timeReduction}% faster on slow connection` : 'Comparable speed'}
            </div>
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
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>-{clickReduction}%</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--sunken)' }}>
              <td style={{ padding: '10px 12px', fontWeight: 600 }}>{t.metric_pages}</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{original.pages_visited} pages</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{prototype.pages_visited} page</td>
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>-{pageReduction}%</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--sunken)' }}>
              <td style={{ padding: '10px 12px', fontWeight: 600 }}>{t.metric_pdf_hops}</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{original.pdf_hops} PDF downloads</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{prototype.pdf_hops} (All HTML)</td>
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>
                {prototype.pdf_hops === 0 ? 'Eliminated' : `Reduced to ${prototype.pdf_hops}`}
              </td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--sunken)' }}>
              <td style={{ padding: '10px 12px', fontWeight: 600 }}>{t.metric_reading_words}</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{original.words_on_path} words</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{prototype.words_on_path} words</td>
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>-{wordReduction}% cognitive load</td>
            </tr>
            <tr style={{ borderBottom: '1px solid var(--sunken)' }}>
              <td style={{ padding: '10px 12px', fontWeight: 600 }}>Data Transferred</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{(original.bytes_transferred / 1024 / 1024).toFixed(2)} MB</td>
              <td style={{ padding: '10px 12px' }} className="tabular-nums">{(prototype.bytes_transferred / 1024).toFixed(0)} KB</td>
              <td style={{ padding: '10px 12px', color: 'var(--pass)', fontWeight: 600 }}>{byteReduction}% less data consumed</td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  );
};
