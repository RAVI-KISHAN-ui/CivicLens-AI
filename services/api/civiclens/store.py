"""SQLite persistence for CivicLens scans, evidence, findings, and cited facts.
Reference: Section 11.1 of AGENTS.md.
"""

from __future__ import annotations
import json
import os
import sqlite3
import contextlib
from datetime import datetime, timezone
from typing import Any, Generator
from civiclens.models import Evidence, Finding, CitedFact, Scan, TaskMetrics, GateResult


DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "civiclens.db")


class Store:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextlib.contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                total_candidates INTEGER DEFAULT 0,
                verified_count INTEGER DEFAULT 0,
                needs_review_count INTEGER DEFAULT 0,
                rejected_count INTEGER DEFAULT 0,
                metrics_original TEXT,
                metrics_prototype TEXT,
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS evidence (
                id TEXT NOT NULL,
                scan_id TEXT NOT NULL,
                page_id TEXT NOT NULL,
                page_url TEXT NOT NULL,
                device TEXT NOT NULL,
                kind TEXT NOT NULL,
                selector TEXT,
                role TEXT,
                accessible_name TEXT,
                text TEXT NOT NULL,
                context TEXT DEFAULT '',
                href TEXT,
                bbox TEXT,
                crop_path TEXT,
                axe_rule_id TEXT,
                wcag_tags TEXT,
                dom_snapshot_hash TEXT,
                captured_at TEXT NOT NULL,
                PRIMARY KEY (id, scan_id),
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS findings (
                id TEXT NOT NULL,
                scan_id TEXT NOT NULL,
                source TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                evidence_ids TEXT NOT NULL,
                quoted_text TEXT NOT NULL,
                wcag_sc TEXT,
                gigw_ref TEXT,
                who_is_affected TEXT NOT NULL,
                citizen_impact TEXT NOT NULL,
                suggested_fix TEXT NOT NULL,
                severity TEXT NOT NULL,
                on_task_path INTEGER DEFAULT 1,
                status TEXT NOT NULL,
                gates TEXT,
                review TEXT DEFAULT 'unreviewed',
                PRIMARY KEY (id, scan_id),
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS facts (
                id TEXT PRIMARY KEY,
                scan_id TEXT NOT NULL,
                field TEXT NOT NULL,
                value TEXT NOT NULL,
                source_url TEXT NOT NULL,
                evidence_ids TEXT NOT NULL,
                cited_text TEXT NOT NULL,
                human_checked INTEGER DEFAULT 0,
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            );
            """)

    # --- Scans ---
    def create_scan(self, scan: Scan) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO scans (id, task_id, url, status, created_at, completed_at,
                                   total_candidates, verified_count, needs_review_count,
                                   rejected_count, metrics_original, metrics_prototype, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan.id, scan.task_id, scan.url, scan.status,
                    scan.created_at.isoformat(),
                    scan.completed_at.isoformat() if scan.completed_at else None,
                    scan.total_candidates, scan.verified_count,
                    scan.needs_review_count, scan.rejected_count,
                    json.dumps(scan.metrics_original.model_dump()) if scan.metrics_original else None,
                    json.dumps(scan.metrics_prototype.model_dump()) if scan.metrics_prototype else None,
                    scan.error_message
                )
            )

    def update_scan(self, scan: Scan) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE scans SET
                    status = ?, completed_at = ?, total_candidates = ?,
                    verified_count = ?, needs_review_count = ?, rejected_count = ?,
                    metrics_original = ?, metrics_prototype = ?, error_message = ?
                WHERE id = ?
                """,
                (
                    scan.status,
                    scan.completed_at.isoformat() if scan.completed_at else None,
                    scan.total_candidates, scan.verified_count,
                    scan.needs_review_count, scan.rejected_count,
                    json.dumps(scan.metrics_original.model_dump()) if scan.metrics_original else None,
                    json.dumps(scan.metrics_prototype.model_dump()) if scan.metrics_prototype else None,
                    scan.error_message,
                    scan.id
                )
            )

    def get_scan(self, scan_id: str) -> Scan | None:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
            if not row:
                return None
            return Scan(
                id=row["id"],
                task_id=row["task_id"],
                url=row["url"],
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
                total_candidates=row["total_candidates"],
                verified_count=row["verified_count"],
                needs_review_count=row["needs_review_count"],
                rejected_count=row["rejected_count"],
                metrics_original=TaskMetrics(**json.loads(row["metrics_original"])) if row["metrics_original"] else None,
                metrics_prototype=TaskMetrics(**json.loads(row["metrics_prototype"])) if row["metrics_prototype"] else None,
                error_message=row["error_message"]
            )

    def list_scans(self) -> list[Scan]:
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM scans ORDER BY created_at DESC").fetchall()
            scans: list[Scan] = []
            for row in rows:
                scans.append(Scan(
                    id=row["id"],
                    task_id=row["task_id"],
                    url=row["url"],
                    status=row["status"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
                    total_candidates=row["total_candidates"],
                    verified_count=row["verified_count"],
                    needs_review_count=row["needs_review_count"],
                    rejected_count=row["rejected_count"],
                    metrics_original=TaskMetrics(**json.loads(row["metrics_original"])) if row["metrics_original"] else None,
                    metrics_prototype=TaskMetrics(**json.loads(row["metrics_prototype"])) if row["metrics_prototype"] else None,
                    error_message=row["error_message"]
                ))
            return scans

    # --- Evidence ---
    def save_evidence(self, ev: Evidence) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO evidence (
                    id, scan_id, page_id, page_url, device, kind, selector,
                    role, accessible_name, text, context, href, bbox,
                    crop_path, axe_rule_id, wcag_tags, dom_snapshot_hash, captured_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ev.id, ev.scan_id, ev.page_id, ev.page_url, ev.device, ev.kind,
                    ev.selector, ev.role, ev.accessible_name, ev.text, ev.context,
                    ev.href, json.dumps(ev.bbox) if ev.bbox else None, ev.crop_path,
                    ev.axe_rule_id, json.dumps(ev.wcag_tags), ev.dom_snapshot_hash,
                    ev.captured_at.isoformat()
                )
            )

    def get_evidence_by_scan(self, scan_id: str) -> list[Evidence]:
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM evidence WHERE scan_id = ? ORDER BY captured_at ASC", (scan_id,)).fetchall()
            results = []
            for r in rows:
                results.append(Evidence(
                    id=r["id"],
                    scan_id=r["scan_id"],
                    page_id=r["page_id"],
                    page_url=r["page_url"],
                    device=r["device"],
                    kind=r["kind"],
                    selector=r["selector"],
                    role=r["role"],
                    accessible_name=r["accessible_name"],
                    text=r["text"],
                    context=r["context"] or "",
                    href=r["href"],
                    bbox=json.loads(r["bbox"]) if r["bbox"] else None,
                    crop_path=r["crop_path"],
                    axe_rule_id=r["axe_rule_id"],
                    wcag_tags=json.loads(r["wcag_tags"]) if r["wcag_tags"] else [],
                    dom_snapshot_hash=r["dom_snapshot_hash"] or "",
                    captured_at=datetime.fromisoformat(r["captured_at"])
                ))
            return results

    def get_evidence(self, scan_id: str, evidence_id: str) -> Evidence | None:
        with self._connection() as conn:
            r = conn.execute("SELECT * FROM evidence WHERE scan_id = ? AND id = ?", (scan_id, evidence_id)).fetchone()
            if not r:
                return None
            return Evidence(
                id=r["id"],
                scan_id=r["scan_id"],
                page_id=r["page_id"],
                page_url=r["page_url"],
                device=r["device"],
                kind=r["kind"],
                selector=r["selector"],
                role=r["role"],
                accessible_name=r["accessible_name"],
                text=r["text"],
                context=r["context"] or "",
                href=r["href"],
                bbox=json.loads(r["bbox"]) if r["bbox"] else None,
                crop_path=r["crop_path"],
                axe_rule_id=r["axe_rule_id"],
                wcag_tags=json.loads(r["wcag_tags"]) if r["wcag_tags"] else [],
                dom_snapshot_hash=r["dom_snapshot_hash"] or "",
                captured_at=datetime.fromisoformat(r["captured_at"])
            )

    # --- Findings ---
    def save_finding(self, f: Finding) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO findings (
                    id, scan_id, source, issue_type, evidence_ids, quoted_text,
                    wcag_sc, gigw_ref, who_is_affected, citizen_impact, suggested_fix,
                    severity, on_task_path, status, gates, review
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f.id, f.scan_id, f.source, f.issue_type,
                    json.dumps(f.evidence_ids), f.quoted_text, f.wcag_sc,
                    f.gigw_ref, f.who_is_affected, f.citizen_impact,
                    f.suggested_fix, f.severity, 1 if f.on_task_path else 0,
                    f.status, json.dumps([g.model_dump() for g in f.gates]),
                    f.review
                )
            )

    def get_findings_by_scan(
        self,
        scan_id: str,
        status: str | None = None,
        severity: str | None = None
    ) -> list[Finding]:
        query = "SELECT * FROM findings WHERE scan_id = ?"
        params: list[Any] = [scan_id]
        if status:
            query += " AND status = ?"
            params.append(status)
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        query += " ORDER BY CASE severity WHEN 'blocker' THEN 1 WHEN 'major' THEN 2 ELSE 3 END"

        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()
            findings = []
            for r in rows:
                gates_raw = json.loads(r["gates"]) if r["gates"] else []
                gates = [GateResult(**g) for g in gates_raw]
                findings.append(Finding(
                    id=r["id"],
                    scan_id=r["scan_id"],
                    source=r["source"],
                    issue_type=r["issue_type"],
                    evidence_ids=json.loads(r["evidence_ids"]),
                    quoted_text=r["quoted_text"],
                    wcag_sc=r["wcag_sc"],
                    gigw_ref=r["gigw_ref"],
                    who_is_affected=r["who_is_affected"],
                    citizen_impact=r["citizen_impact"],
                    suggested_fix=r["suggested_fix"],
                    severity=r["severity"],
                    on_task_path=bool(r["on_task_path"]),
                    status=r["status"],
                    gates=gates,
                    review=r["review"]
                ))
            return findings

    def get_finding(self, scan_id: str, finding_id: str) -> Finding | None:
        with self._connection() as conn:
            r = conn.execute("SELECT * FROM findings WHERE scan_id = ? AND id = ?", (scan_id, finding_id)).fetchone()
            if not r:
                return None
            gates_raw = json.loads(r["gates"]) if r["gates"] else []
            gates = [GateResult(**g) for g in gates_raw]
            return Finding(
                id=r["id"],
                scan_id=r["scan_id"],
                source=r["source"],
                issue_type=r["issue_type"],
                evidence_ids=json.loads(r["evidence_ids"]),
                quoted_text=r["quoted_text"],
                wcag_sc=r["wcag_sc"],
                gigw_ref=r["gigw_ref"],
                who_is_affected=r["who_is_affected"],
                citizen_impact=r["citizen_impact"],
                suggested_fix=r["suggested_fix"],
                severity=r["severity"],
                on_task_path=bool(r["on_task_path"]),
                status=r["status"],
                gates=gates,
                review=r["review"]
            )

    def update_finding_review(self, scan_id: str, finding_id: str, decision: str) -> bool:
        with self._connection() as conn:
            res = conn.execute(
                "UPDATE findings SET review = ? WHERE scan_id = ? AND id = ?",
                (decision, scan_id, finding_id)
            )
            return res.rowcount > 0

    # --- Facts ---
    def save_fact(self, fact: CitedFact) -> None:
        import uuid
        fact_id = fact.id or f"fact_{uuid.uuid4().hex[:8]}"
        fact.id = fact_id
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO facts (
                    id, scan_id, field, value, source_url, evidence_ids, cited_text, human_checked
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fact.id, fact.id.split("_")[0], fact.field, fact.value,
                    fact.source_url, json.dumps(fact.evidence_ids), fact.cited_text,
                    1 if fact.human_checked else 0
                )
            )

    def save_scan_fact(self, scan_id: str, fact: CitedFact) -> None:
        import uuid
        fact_id = fact.id or f"fact_{uuid.uuid4().hex[:8]}"
        fact.id = fact_id
        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO facts (
                    id, scan_id, field, value, source_url, evidence_ids, cited_text, human_checked
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fact.id, scan_id, fact.field, fact.value,
                    fact.source_url, json.dumps(fact.evidence_ids), fact.cited_text,
                    1 if fact.human_checked else 0
                )
            )

    def get_facts_by_scan(self, scan_id: str) -> list[CitedFact]:
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM facts WHERE scan_id = ?", (scan_id,)).fetchall()
            return [
                CitedFact(
                    id=r["id"],
                    field=r["field"],
                    value=r["value"],
                    source_url=r["source_url"],
                    evidence_ids=json.loads(r["evidence_ids"]),
                    cited_text=r["cited_text"],
                    human_checked=bool(r["human_checked"])
                )
                for r in rows
            ]

    def set_fact_checked(self, scan_id: str, fact_id: str, checked: bool = True) -> bool:
        with self._connection() as conn:
            res = conn.execute(
                "UPDATE facts SET human_checked = ? WHERE scan_id = ? AND id = ?",
                (1 if checked else 0, scan_id, fact_id)
            )
            return res.rowcount > 0
