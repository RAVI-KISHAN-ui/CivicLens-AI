"""Unit tests for the 8-Gate Verifier (Hallucination Firewall).
Reference: Section 8.4 of AGENTS.md.
"""

from civiclens.scan.capture import build_evidence
from civiclens.models import CandidateFinding
from civiclens.ai.verify import verify_candidate


def test_verifier_all_gates_pass():
    ev = build_evidence(
        scan_id="scan_10", page_id="p1", page_url="https://scholarships.gov.in",
        idx=1, kind="link", text="Click here", selector="a#link_1", role="link",
        bbox=[10, 20, 100, 30]
    )
    ev_map = {ev.id: ev}

    candidate = CandidateFinding(
        issue_type="VAGUE_LINK_TEXT",
        evidence_ids=[ev.id],
        quoted_text="Click here",
        wcag_sc="2.4.4",
        who_is_affected="Screen reader users",
        citizen_impact="Non-descriptive link text prevents understanding target.",
        suggested_fix="Change link label to descriptive text.",
        severity_hint="major"
    )

    finding = verify_candidate(candidate, "scan_10", ev_map, is_self_consistent=True)
    assert finding.status == "verified"
    assert finding.severity == "major"
    assert any(g.gate == "G3_QUOTE_MATCH" and g.passed for g in finding.gates)
    assert any(g.gate == "G8_SELF_CONSISTENCY" and g.passed for g in finding.gates)


def test_verifier_gate_g2_missing_evidence_fails():
    ev = build_evidence(
        scan_id="scan_10", page_id="p1", page_url="https://scholarships.gov.in",
        idx=1, kind="link", text="Click here"
    )
    ev_map = {ev.id: ev}

    candidate = CandidateFinding(
        issue_type="VAGUE_LINK_TEXT",
        evidence_ids=["ev_non_existent"],  # Invalid ID
        quoted_text="Click here",
        wcag_sc="2.4.4",
        who_is_affected="Screen reader users",
        citizen_impact="Vague link text.",
        suggested_fix="Fix link.",
        severity_hint="major"
    )

    finding = verify_candidate(candidate, "scan_10", ev_map)
    assert finding.status == "rejected"
    g2 = next(g for g in finding.gates if g.gate == "G2_EVIDENCE_EXISTS")
    assert not g2.passed


def test_verifier_gate_g3_quote_mismatch_fails():
    ev = build_evidence(
        scan_id="scan_10", page_id="p1", page_url="https://scholarships.gov.in",
        idx=1, kind="link", text="Official Scheme Portal", selector="a#nav"
    )
    ev_map = {ev.id: ev}

    candidate = CandidateFinding(
        issue_type="VAGUE_LINK_TEXT",
        evidence_ids=[ev.id],
        quoted_text="Hallucinated Quote Never Present",
        wcag_sc="2.4.4",
        who_is_affected="Screen reader users",
        citizen_impact="Vague link text.",
        suggested_fix="Fix link.",
        severity_hint="major"
    )

    finding = verify_candidate(candidate, "scan_10", ev_map)
    assert finding.status == "rejected"
    g3 = next(g for g in finding.gates if g.gate == "G3_QUOTE_MATCH")
    assert not g3.passed


def test_verifier_gate_g5_wcag_sc_mismatch_fails():
    ev = build_evidence(
        scan_id="scan_10", page_id="p1", page_url="https://scholarships.gov.in",
        idx=1, kind="link", text="Click here", selector="a#link"
    )
    ev_map = {ev.id: ev}

    # Assigning WCAG 1.4.3 (Contrast) to VAGUE_LINK_TEXT is disallowed by standards/issue_sc_map.json
    candidate = CandidateFinding(
        issue_type="VAGUE_LINK_TEXT",
        evidence_ids=[ev.id],
        quoted_text="Click here",
        wcag_sc="1.4.3",
        who_is_affected="Screen reader users",
        citizen_impact="Vague link text.",
        suggested_fix="Fix link.",
        severity_hint="major"
    )

    finding = verify_candidate(candidate, "scan_10", ev_map)
    assert finding.status == "rejected"
    g5 = next(g for g in finding.gates if g.gate == "G5_TYPE_CHECK")
    assert not g5.passed


def test_verifier_g7_judge_rejection_veto():
    ev = build_evidence(
        scan_id="scan_10", page_id="p1", page_url="https://scholarships.gov.in",
        idx=1, kind="link", text="Click here", selector="a#link_1", role="link"
    )
    ev_map = {ev.id: ev}

    candidate = CandidateFinding(
        issue_type="VAGUE_LINK_TEXT",
        evidence_ids=[ev.id],
        quoted_text="Click here",
        wcag_sc="2.4.4",
        who_is_affected="Screen reader users",
        citizen_impact="Non-descriptive link text prevents understanding target in screen reader.",
        suggested_fix="Change link label to descriptive text.",
        severity_hint="major"
    )

    # Even with G6 and G8 passing, judge veto forces needs_review
    finding = verify_candidate(candidate, "scan_10", ev_map, is_self_consistent=True, judge_verdict="not_supported")
    assert finding.status == "needs_review"
    g7 = next(g for g in finding.gates if g.gate == "G7_INDEPENDENT_JUDGE")
    assert not g7.passed


def test_verifier_axe_impact_elevation():
    ev = build_evidence(
        scan_id="scan_10", page_id="p1", page_url="https://scholarships.gov.in",
        idx=1, kind="axe_violation", text="Critical contrast failure", selector="button#btn"
    )
    ev_map = {ev.id: ev}

    candidate = CandidateFinding(
        issue_type="OTHER_AXE_RULE",
        evidence_ids=[ev.id],
        quoted_text="Critical contrast failure",
        wcag_sc="1.4.3",
        who_is_affected="Low vision users",
        citizen_impact="Low contrast prevents readable interface components.",
        suggested_fix="Increase color contrast ratio.",
        severity_hint="blocker"
    )

    finding = verify_candidate(candidate, "scan_10", ev_map, source="axe")
    assert finding.severity == "blocker"
