"""Unit tests for the SQLite persistence store."""

import tempfile
import os
from civiclens.store import Store
from civiclens.models import Scan, Evidence, Finding, CitedFact, GateResult


def test_store_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        store = Store(db_path)

        # 1. Create scan
        scan = Scan(id="scan_01", task_id="scholarship", url="https://scholarships.gov.in/")
        store.create_scan(scan)
        retrieved = store.get_scan("scan_01")
        assert retrieved is not None
        assert retrieved.url == "https://scholarships.gov.in/"
        assert retrieved.status == "running"

        # 2. Add evidence
        ev = Evidence(
            id="ev_01_1",
            scan_id="scan_01",
            page_id="home",
            page_url="https://scholarships.gov.in/",
            device="desktop",
            kind="link",
            text="Click here",
            context="To read guidelines Click here",
            dom_snapshot_hash="abc123hash"
        )
        store.save_evidence(ev)
        evs = store.get_evidence_by_scan("scan_01")
        assert len(evs) == 1
        assert evs[0].text == "Click here"

        # 3. Add finding
        gate = GateResult(gate="G1", passed=True, hard=True, detail="Schema valid")
        finding = Finding(
            id="f_01",
            scan_id="scan_01",
            source="llm",
            issue_type="VAGUE_LINK_TEXT",
            evidence_ids=["ev_01_1"],
            quoted_text="Click here",
            who_is_affected="Screen reader users",
            citizen_impact="Vague link prevents user from knowing destination",
            suggested_fix="Rename to 'Read Scholarship Guidelines'",
            severity="major",
            status="verified",
            gates=[gate]
        )
        store.save_finding(finding)
        findings = store.get_findings_by_scan("scan_01")
        assert len(findings) == 1
        assert findings[0].issue_type == "VAGUE_LINK_TEXT"
        assert findings[0].gates[0].gate == "G1"

        # 4. Human review
        store.update_finding_review("scan_01", "f_01", "accepted")
        updated_f = store.get_finding("scan_01", "f_01")
        assert updated_f.review == "accepted"

        # 5. Cited facts
        fact = CitedFact(
            id="fact_01",
            field="eligibility",
            value="College students with > 80% in Class 12",
            source_url="https://scholarships.gov.in/",
            evidence_ids=["ev_01_1"],
            cited_text="College students with > 80%",
            human_checked=False
        )
        store.save_scan_fact("scan_01", fact)
        facts = store.get_facts_by_scan("scan_01")
        assert len(facts) == 1
        assert facts[0].field == "eligibility"
        assert not facts[0].human_checked

        store.set_fact_checked("scan_01", "fact_01", True)
        assert store.get_facts_by_scan("scan_01")[0].human_checked
