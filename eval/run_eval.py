"""Evaluation harness for CivicLens AI.
Reference: Section 10 of AGENTS.md.
"""

from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timezone

# Ensure services/api is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVICES_DIR = os.path.join(BASE_DIR, "services", "api")
if SERVICES_DIR not in sys.path:
    sys.path.insert(0, SERVICES_DIR)

from civiclens.models import CandidateFinding, Evidence
from civiclens.ai.verify import verify_candidate


def run_evaluation() -> dict:
    eval_dir = os.path.join(BASE_DIR, "eval")
    redteam_file = os.path.join(eval_dir, "redteam", "redteam_cases.json")
    golden_file = os.path.join(eval_dir, "golden", "scholarship_golden.json")
    fixture_file = os.path.join(BASE_DIR, "fixtures", "demo", "scan_scholarship.json")
    reports_dir = os.path.join(eval_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Load fixture evidence
    evidence_map: dict[str, Evidence] = {}
    if not os.path.exists(fixture_file):
        print(f"Error: Required demo fixture file {fixture_file} not found.", file=sys.stderr)
        sys.exit(1)

    with open(fixture_file, "r", encoding="utf-8") as f:
        fixture_data = json.load(f)
        for ev_data in fixture_data.get("evidence", []):
            ev = Evidence(**ev_data)
            ev.scan_id = "eval_scan"
            evidence_map[ev.id] = ev

    # 2. Run Red-Team Cases against the Hallucination Firewall
    if not os.path.exists(redteam_file):
        print(f"Error: Red-team benchmark file {redteam_file} not found.", file=sys.stderr)
        sys.exit(1)

    with open(redteam_file, "r", encoding="utf-8") as f:
        redteam_cases = json.load(f)

    if not redteam_cases:
        print("Error: Red-team test suite contains 0 test cases.", file=sys.stderr)
        sys.exit(1)

    caught_count = 0
    redteam_results = []
    for case in redteam_cases:
        expected_gate = case.get("expected_caught_by")
        cand = CandidateFinding(
            issue_type=case["issue_type"],
            evidence_ids=case["evidence_ids"],
            quoted_text=case["quoted_text"],
            wcag_sc=case.get("wcag_sc"),
            who_is_affected=case["who_is_affected"],
            citizen_impact=case["citizen_impact"],
            suggested_fix=case["suggested_fix"],
            severity_hint=case["severity_hint"]
        )
        finding = verify_candidate(cand, "eval_scan", evidence_map)
        rejected = finding.status == "rejected"
        failed_gates = [g.gate for g in finding.gates if not g.passed]

        is_verified_catch = rejected and (expected_gate in failed_gates if expected_gate else True)
        if is_verified_catch:
            caught_count += 1

        redteam_results.append({
            "id": case["id"],
            "status": finding.status,
            "failed_gates": failed_gates,
            "expected_caught_by": expected_gate,
            "verified_catch": is_verified_catch
        })

    catch_rate = (caught_count / len(redteam_cases)) * 100.0

    # 3. Dynamic Precision & Evidence Integrity Evaluation against Golden Benchmark
    if not os.path.exists(golden_file):
        print(f"Error: Golden benchmark file {golden_file} not found.", file=sys.stderr)
        sys.exit(1)

    with open(golden_file, "r", encoding="utf-8") as f:
        golden_cases = json.load(f)

    if not golden_cases:
        print("Error: Golden benchmark file contains 0 cases.", file=sys.stderr)
        sys.exit(1)

    verified_findings = [f for f in fixture_data.get("findings", []) if f.get("status") == "verified"]

    # Precision: share of verified findings that match an accepted golden case
    matched_verified = 0
    for vf in verified_findings:
        if any(g["issue_type"] == vf.get("issue_type") for g in golden_cases):
            matched_verified += 1
    verified_precision = round(matched_verified / len(verified_findings), 2) if verified_findings else 1.0

    # Evidence integrity: share of verified findings where all cited evidence items exist in scan
    intact_count = 0
    for vf in verified_findings:
        ev_ids = vf.get("evidence_ids", [])
        if ev_ids and all(eid in evidence_map for eid in ev_ids):
            intact_count += 1
    evidence_integrity = round(intact_count / len(verified_findings), 2) if verified_findings else 1.0

    # 4. Check prototype fact faithfulness (grounded citations)
    facts = fixture_data.get("facts", [])
    grounded_facts = [f for f in facts if f.get("evidence_ids") and f.get("source_url")]
    prototype_fact_faithfulness = round(len(grounded_facts) / len(facts), 2) if facts else 1.0

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "verified_precision": verified_precision,
            "evidence_integrity": evidence_integrity,
            "firewall_catch_rate_percent": round(catch_rate, 2),
            "prototype_fact_faithfulness": prototype_fact_faithfulness,
            "redteam_total": len(redteam_cases),
            "redteam_caught": caught_count
        },
        "redteam_details": redteam_results
    }

    # Save dated report
    timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(reports_dir, f"eval_report_{timestamp_slug}.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"=== CivicLens AI Evaluation Summary ===")
    print(f"Report saved to: {report_path}")
    print(f"Firewall Catch Rate: {catch_rate:.1f}% ({caught_count}/{len(redteam_cases)}) [Target: >= 95%]")
    print(f"Verified Precision: {verified_precision * 100:.1f}% ({matched_verified}/{len(verified_findings)} verified findings match golden set)")
    print(f"Evidence Integrity: {evidence_integrity * 100:.1f}% ({intact_count}/{len(verified_findings)} verified findings have intact evidence)")
    print(f"Prototype Fact Faithfulness: {prototype_fact_faithfulness * 100:.1f}%")

    if catch_rate < 95.0:
        print(f"Error: Firewall catch rate {catch_rate:.1f}% falls below required 95% threshold.", file=sys.stderr)
        sys.exit(1)

    return report


if __name__ == "__main__":
    run_evaluation()
