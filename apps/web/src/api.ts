import { Scan, Finding, Evidence, CitedFact, TaskMetrics } from './types';
import demoData from '../../../fixtures/demo/scan_scholarship.json';

const API_BASE = '/api';

export async function fetchScan(scanId: string = 'scan_demo_scholarship'): Promise<Scan> {
  try {
    const res = await fetch(`${API_BASE}/scans/${scanId}`);
    if (res.ok) return await res.json();
  } catch (e) {
    if (scanId === 'scan_demo_scholarship') {
      console.warn('API unavailable, falling back to embedded demo scan fixture.');
      return demoData.scan as Scan;
    }
    throw e;
  }
  if (scanId === 'scan_demo_scholarship') {
    return demoData.scan as Scan;
  }
  throw new Error(`Failed to fetch scan ${scanId}`);
}

export async function triggerScan(url: string, taskId: string = 'scholarship-eligibility-docs'): Promise<Scan> {
  const res = await fetch(`${API_BASE}/scans`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, task_id: taskId })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to start scan' }));
    throw new Error(err.detail || 'Failed to start scan');
  }
  return await res.json();
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
    if (scanId === 'scan_demo_scholarship') {
      console.warn('API unavailable, using demo fixture findings.');
    } else {
      throw e;
    }
  }

  if (scanId === 'scan_demo_scholarship') {
    let list = demoData.findings as unknown as Finding[];
    if (status) list = list.filter((f) => f.status === status);
    if (severity) list = list.filter((f) => f.severity === severity);
    return list;
  }
  return [];
}

export async function fetchEvidence(scanId: string = 'scan_demo_scholarship'): Promise<Evidence[]> {
  try {
    const res = await fetch(`${API_BASE}/scans/${scanId}/evidence`);
    if (res.ok) return await res.json();
  } catch (e) {
    if (scanId === 'scan_demo_scholarship') {
      console.warn('API unavailable, using demo fixture evidence.');
    }
  }
  if (scanId === 'scan_demo_scholarship') {
    return (demoData.evidence || []) as unknown as Evidence[];
  }
  return [];
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
    if (scanId === 'scan_demo_scholarship') {
      console.warn('API unavailable; local review state saved for demo scan.');
      return true;
    }
    console.error('Failed to submit finding review:', e);
    return false;
  }
}

export async function fetchFacts(scanId: string = 'scan_demo_scholarship'): Promise<CitedFact[]> {
  try {
    const res = await fetch(`${API_BASE}/scans/${scanId}/facts`);
    if (res.ok) return await res.json();
  } catch (e) {
    if (scanId === 'scan_demo_scholarship') {
      console.warn('API unavailable, using demo facts.');
    }
  }
  if (scanId === 'scan_demo_scholarship') {
    return demoData.facts as CitedFact[];
  }
  return [];
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
    console.error('Failed to update fact checked status:', e);
    return false;
  }
}

export async function fetchCompare(scanId: string = 'scan_demo_scholarship'): Promise<{
  original: TaskMetrics;
  prototype: TaskMetrics;
  is_estimated?: boolean;
}> {
  try {
    const res = await fetch(`${API_BASE}/scans/${scanId}/compare`);
    if (res.ok) return await res.json();
  } catch (e) {
    if (scanId === 'scan_demo_scholarship') {
      console.warn('API unavailable, using demo comparison metrics.');
    }
  }
  return {
    original: demoData.scan.metrics_original as TaskMetrics,
    prototype: demoData.scan.metrics_prototype as TaskMetrics,
    is_estimated: true
  };
}
