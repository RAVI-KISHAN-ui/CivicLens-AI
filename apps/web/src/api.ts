import { Scan, Finding, Evidence, CitedFact, TaskMetrics } from './types';
import demoData from '../../../fixtures/demo/scan_scholarship.json';

const API_BASE = '/api';

export async function fetchScan(scanId: string = 'scan_demo_scholarship'): Promise<Scan> {
  try {
    const res = await fetch(`${API_BASE}/scans/${scanId}`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('API unavailable, falling back to embedded demo scan fixture.');
  }
  return demoData.scan as Scan;
}

export async function fetchFindings(
  scanId: string = 'scan_demo_scholarship',
  status?: string,
  severity?: string
): Promise<Finding[]> {
  try {
    let url = `${API_BASE}/scans/${scanId}/findings`;
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (severity) params.append('severity', severity);
    if (params.toString()) url += `?${params.toString()}`;

    const res = await fetch(url);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('API unavailable, using demo fixture findings.');
  }

  let list = demoData.findings as Finding[];
  if (status) list = list.filter((f) => f.status === status);
  if (severity) list = list.filter((f) => f.severity === severity);
  return list;
}

export async function reviewFinding(
  scanId: string,
  findingId: string,
  decision: 'accepted' | 'dismissed'
): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/findings/${scanId}/${findingId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision })
    });
    return res.ok;
  } catch (e) {
    return true;
  }
}

export async function fetchFacts(scanId: string = 'scan_demo_scholarship'): Promise<CitedFact[]> {
  try {
    const res = await fetch(`${API_BASE}/scans/${scanId}/facts`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('API unavailable, using demo facts.');
  }
  return demoData.facts as CitedFact[];
}

export async function checkFact(scanId: string, factId: string, checked: boolean): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/facts/${scanId}/${factId}/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ checked })
    });
    return res.ok;
  } catch (e) {
    return true;
  }
}

export async function fetchCompare(scanId: string = 'scan_demo_scholarship'): Promise<{
  original: TaskMetrics;
  prototype: TaskMetrics;
}> {
  try {
    const res = await fetch(`${API_BASE}/scans/${scanId}/compare`);
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn('API unavailable, using demo comparison metrics.');
  }
  return {
    original: demoData.scan.metrics_original as TaskMetrics,
    prototype: demoData.scan.metrics_prototype as TaskMetrics
  };
}
