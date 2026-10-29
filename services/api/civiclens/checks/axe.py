"""axe-core integration for automated WCAG 2.2 AA violations.
Reference: Section 7.1 of AGENTS.md.
"""

from __future__ import annotations
from typing import Any
from civiclens.models import Evidence, CandidateFinding


AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]


import re

_SC_TAG = re.compile(r"^wcag(\d)(\d)(\d{1,2})$")


def parse_axe_violations(
    axe_results: dict[str, Any],
    scan_id: str,
    page_id: str,
    page_url: str,
    device: str
) -> tuple[list[Evidence], list[CandidateFinding]]:
    """Converts axe-core violation records into Evidence items and CandidateFindings."""
    evidence_items: list[Evidence] = []
    candidates: list[CandidateFinding] = []

    violations = axe_results.get("violations", [])
    for v_idx, v in enumerate(violations):
        rule_id = v.get("id", "axe-rule")
        help_text = v.get("help", "")
        description = v.get("description", "")
        impact = v.get("impact", "moderate")
        tags = v.get("tags", [])

        # Extract WCAG success criteria tags like "wcag143" -> "1.4.3", "wcag1410" -> "1.4.10"
        wcag_sc = None
        for tag in tags:
            m = _SC_TAG.match(tag)
            if m:
                wcag_sc = ".".join(m.groups())
                break

        for node_idx, node in enumerate(v.get("nodes", [])):
            ev_id = f"ev_axe_{page_id}_{v_idx}_{node_idx}"
            html_snippet = node.get("html", "")
            target_selectors = node.get("target", [])
            selector = " > ".join(target_selectors) if isinstance(target_selectors, list) else str(target_selectors)
            failure_summary = node.get("failureSummary", description)

            ev = Evidence(
                id=ev_id,
                scan_id=scan_id,
                page_id=page_id,
                page_url=page_url,
                device="mobile" if device == "mobile" else "desktop",
                kind="axe_violation",
                selector=selector,
                text=html_snippet[:150],
                context=failure_summary[:300],
                axe_rule_id=rule_id,
                wcag_tags=tags,
                dom_snapshot_hash=""
            )
            evidence_items.append(ev)

            # Map to CandidateFinding
            issue_type = "LOW_CONTRAST" if rule_id == "color-contrast" else (
                "MISSING_ACCESSIBLE_NAME" if "label" in rule_id or "name" in rule_id else "OTHER_AXE_RULE"
            )

            severity_hint = "blocker" if impact in ("critical", "serious") else "major"

            candidates.append(CandidateFinding(
                issue_type=issue_type,
                evidence_ids=[ev_id],
                quoted_text=html_snippet[:120],
                wcag_sc=wcag_sc,
                who_is_affected="Screen reader users and users with low vision",
                citizen_impact=f"Automated accessibility rule '{rule_id}' failed: {help_text}.",
                suggested_fix=f"Resolve violation: {failure_summary}.",
                severity_hint=severity_hint
            ))

    return evidence_items, candidates
