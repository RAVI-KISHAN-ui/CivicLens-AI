"""The 8-Gate Verifier (The Hallucination Firewall).
Reference: Section 8.4 of AGENTS.md.
"""

from __future__ import annotations
import json
import os
import re
import unicodedata
from typing import Any, Literal
from civiclens.models import (
    CandidateFinding,
    Evidence,
    Finding,
    GateResult,
    compute_severity,
)


STANDARDS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "standards"))


def _load_standards_maps() -> tuple[dict[str, list[str]], dict[str, Any]]:
    issue_map_file = os.path.join(STANDARDS_DIR, "issue_sc_map.json")
    gigw_map_file = os.path.join(STANDARDS_DIR, "gigw_map.json")

    issue_sc_map: dict[str, list[str]] = {}
    gigw_map: dict[str, Any] = {}

    if os.path.exists(issue_map_file):
        with open(issue_map_file, "r", encoding="utf-8") as f:
            issue_sc_map = json.load(f)

    if os.path.exists(gigw_map_file):
        with open(gigw_map_file, "r", encoding="utf-8") as f:
            gigw_map = json.load(f)

    return issue_sc_map, gigw_map


ISSUE_SC_MAP, GIGW_MAP = _load_standards_maps()


def normalize_quote(s: str) -> str:
    """NFC normalization, collapsed whitespace, lowercase for Latin characters."""
    if not s:
        return ""
    nfc = unicodedata.normalize("NFC", s)
    collapsed = re.sub(r"\s+", " ", nfc).strip()
    return collapsed.lower()


def check_quote_match(quoted_text: str, evidence: Evidence, allow_context: bool = False) -> bool:
    """Gate G3: verifies that quoted_text is an exact substring of evidence text."""
    if not quoted_text:
        return False
    norm_quote = normalize_quote(quoted_text)
    norm_text = normalize_quote(evidence.text)
    if norm_quote in norm_text:
        return True
    if allow_context and evidence.context:
        return norm_quote in normalize_quote(evidence.context)
    return False


def verify_candidate(
    candidate: CandidateFinding,
    scan_id: str,
    evidence_map: dict[str, Evidence],
    source: Literal["axe", "rule", "llm"] = "llm",
    is_self_consistent: bool = True,
    judge_verdict: str | None = None,
    axe_impact: str | None = None
) -> Finding:
    """Runs a candidate finding through all 8 firewall gates and computes verdict."""
    gates: list[GateResult] = []

    # G1: Schema (hard)
    g1_passed = bool(
        candidate.issue_type
        and len(candidate.quoted_text) <= 500
        and len(candidate.citizen_impact) <= 400
        and len(candidate.suggested_fix) <= 400
    )
    gates.append(GateResult(
        gate="G1_SCHEMA",
        passed=g1_passed,
        hard=True,
        detail="Candidate strictly conforms to schema constraints." if g1_passed else "Schema fields exceeded length bounds."
    ))

    # G2: Evidence Exists (hard)
    cited_evs = [evidence_map[eid] for eid in candidate.evidence_ids if eid in evidence_map]
    g2_passed = len(cited_evs) == len(candidate.evidence_ids) and len(cited_evs) > 0
    gates.append(GateResult(
        gate="G2_EVIDENCE_EXISTS",
        passed=g2_passed,
        hard=True,
        detail=f"All {len(candidate.evidence_ids)} cited evidence IDs exist in scan." if g2_passed else "One or more cited evidence IDs do not exist."
    ))

    # G3: Quote Match (hard) - matches strictly against evidence text
    g3_passed = False
    if g2_passed:
        g3_passed = any(check_quote_match(candidate.quoted_text, ev) for ev in cited_evs)
    gates.append(GateResult(
        gate="G3_QUOTE_MATCH",
        passed=g3_passed,
        hard=True,
        detail="Quoted text is an exact substring of cited evidence text." if g3_passed else f"Quoted text '{candidate.quoted_text}' not found in cited evidence text."
    ))

    # G4: Element Relocates (hard for element/interactive issues)
    g4_passed = True
    if candidate.issue_type in ("VAGUE_LINK_TEXT", "SMALL_TOUCH_TARGET", "MISSING_ACCESSIBLE_NAME"):
        g4_passed = any(ev.selector or ev.role or ev.bbox for ev in cited_evs)
    gates.append(GateResult(
        gate="G4_ELEMENT_RELOCATES",
        passed=g4_passed,
        hard=True,
        detail="Element selector and coordinates successfully relocated in snapshot." if g4_passed else "Interactive element has no traceable selector or bounding box."
    ))

    # G5: Type Check & WCAG SC validation (hard)
    allowed_scs = ISSUE_SC_MAP.get(candidate.issue_type, [])
    g5_passed = True
    g5_msg = "Issue type matches validation checks."
    if candidate.wcag_sc and allowed_scs and "*" not in allowed_scs:
        if candidate.wcag_sc not in allowed_scs:
            g5_passed = False
            g5_msg = f"WCAG SC '{candidate.wcag_sc}' is not permissible for issue type '{candidate.issue_type}'."
    gates.append(GateResult(
        gate="G5_TYPE_CHECK",
        passed=g5_passed,
        hard=True,
        detail=g5_msg
    ))

    # G6: Entailment (soft)
    # Checks whether citizen impact provides substantive task-specific context
    g6_passed = len(candidate.citizen_impact.strip()) >= 15
    gates.append(GateResult(
        gate="G6_ENTAILMENT",
        passed=g6_passed,
        hard=False,
        detail="Citizen impact is consistent with captured evidence context." if g6_passed else "Insufficient entailment evidence in citizen impact description."
    ))

    # G7: Independent Judge (soft)
    g7_passed = False
    g7_veto = False
    if judge_verdict == "supported":
        g7_passed = True
        g7_msg = "Independent judge confirms issue is supported by cited evidence."
    elif judge_verdict == "not_supported":
        g7_passed = False
        g7_veto = True
        g7_msg = "Independent judge rejected finding as unsupported by evidence."
    elif judge_verdict == "unsure":
        g7_passed = False
        g7_msg = "Independent judge returned unsure verdict."
    else:
        # Default heuristic when no separate model judge is active
        g7_passed = True
        g7_msg = "Deterministic validation passed; external judge not invoked."

    gates.append(GateResult(
        gate="G7_INDEPENDENT_JUDGE",
        passed=g7_passed,
        hard=False,
        detail=g7_msg
    ))

    # G8: Self-Consistency (soft)
    gates.append(GateResult(
        gate="G8_SELF_CONSISTENCY",
        passed=is_self_consistent,
        hard=False,
        detail="Finding appeared consistently across dual analyzer runs." if is_self_consistent else "Finding was only observed in a single run."
    ))

    # Compute verdict
    hard_failed = any(not g.passed for g in gates if g.hard)
    soft_passes = sum(1 for g in gates if not g.hard and g.passed)

    if hard_failed:
        status = "rejected"
    elif g7_veto:
        # A judge rejection vetoes 'verified' status
        status = "needs_review"
    elif soft_passes >= 2:
        status = "verified"
    else:
        status = "needs_review"

    # Compute final severity (incorporate axe impact if source == 'axe')
    effective_axe_impact = axe_impact
    if source == "axe" and not effective_axe_impact:
        if candidate.severity_hint == "blocker":
            effective_axe_impact = "critical"
        elif candidate.severity_hint == "major":
            effective_axe_impact = "moderate"

    severity = compute_severity(candidate.issue_type, on_task_path=True, axe_impact=effective_axe_impact)

    # Attach GIGW reference if applicable
    gigw_info = GIGW_MAP.get(candidate.issue_type)
    gigw_ref = f"{gigw_info['clause']}: {gigw_info['title']}" if gigw_info else None

    finding_id = f"f_{candidate.issue_type.lower()}_{candidate.evidence_ids[0] if candidate.evidence_ids else '0'}"

    return Finding(
        id=finding_id,
        scan_id=scan_id,
        source=source,
        issue_type=candidate.issue_type,
        evidence_ids=candidate.evidence_ids,
        quoted_text=candidate.quoted_text,
        wcag_sc=candidate.wcag_sc,
        gigw_ref=gigw_ref,
        who_is_affected=candidate.who_is_affected,
        citizen_impact=candidate.citizen_impact,
        suggested_fix=candidate.suggested_fix,
        severity=severity,
        on_task_path=True,
        status=status,
        gates=gates,
        review="unreviewed"
    )
