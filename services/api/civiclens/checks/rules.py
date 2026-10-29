"""Custom deterministic rules beyond axe-core.
Reference: Section 7.4 of AGENTS.md.
"""

from __future__ import annotations
import os
from typing import Any
from civiclens.models import Evidence, CandidateFinding, IssueType


def _load_lexicon() -> set[str]:
    lex = set()
    dir_path = os.path.dirname(__file__)
    for filename in ("lexicon_en.txt", "lexicon_hi.txt"):
        filepath = os.path.join(dir_path, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    w = line.strip().lower()
                    if w:
                        lex.add(w)
    return lex


VAGUE_LINK_LEXICON = _load_lexicon()


def check_vague_links(evidence_list: list[Evidence]) -> list[CandidateFinding]:
    """Flag links whose accessible name/text matches the vague lexicon
    or duplicate link texts pointing to different hrefs.
    """
    findings: list[CandidateFinding] = []
    seen_texts: dict[str, str] = {}

    for ev in evidence_list:
        if ev.kind != "link":
            continue

        name = (ev.accessible_name or ev.text).strip().lower()

        # Check lexicon match
        if name in VAGUE_LINK_LEXICON:
            findings.append(CandidateFinding(
                issue_type="VAGUE_LINK_TEXT",
                evidence_ids=[ev.id],
                quoted_text=ev.text or ev.accessible_name or "Click here",
                wcag_sc="2.4.4",
                who_is_affected="Screen reader users and first-time applicants",
                citizen_impact="Non-descriptive link text prevents citizens from understanding destination before activating.",
                suggested_fix=f"Replace '{ev.text}' with specific destination text such as 'Download guidelines' or 'Apply now'.",
                severity_hint="major"
            ))
            continue

        # Check duplicate names pointing to different targets
        if ev.href:
            if name in seen_texts and seen_texts[name] != ev.href:
                findings.append(CandidateFinding(
                    issue_type="VAGUE_LINK_TEXT",
                    evidence_ids=[ev.id],
                    quoted_text=ev.text or ev.accessible_name or "",
                    wcag_sc="2.4.4",
                    who_is_affected="All users navigating repetitive lists",
                    citizen_impact=f"Multiple links share identical text '{ev.text}' but lead to different destinations.",
                    suggested_fix="Distinguish each link with the scheme name or target document title.",
                    severity_hint="major"
                ))
            else:
                seen_texts[name] = ev.href

    return findings


def check_pdf_only_info(evidence_list: list[Evidence]) -> list[CandidateFinding]:
    """Flag key task information trapped inside PDF files."""
    findings: list[CandidateFinding] = []
    for ev in evidence_list:
        if ev.kind == "pdf_link" or (ev.href and ev.href.lower().endswith(".pdf")):
            if any(term in ev.text.lower() for term in ("guideline", "eligibility", "document", "notification")):
                findings.append(CandidateFinding(
                    issue_type="KEY_INFO_ONLY_IN_PDF",
                    evidence_ids=[ev.id],
                    quoted_text=ev.text,
                    wcag_sc="1.3.1",
                    who_is_affected="Mobile users on patchy connections and screen reader users",
                    citizen_impact="Crucial eligibility and document requirements are hidden inside a downloadable PDF rather than provided in accessible HTML.",
                    suggested_fix="Publish the core criteria directly on the webpage with clear headings.",
                    severity_hint="blocker"
                ))
    return findings


def check_unannounced_new_window(evidence_list: list[Evidence]) -> list[CandidateFinding]:
    """Flag target=_blank without visible or announced warning."""
    findings: list[CandidateFinding] = []
    for ev in evidence_list:
        if ev.kind == "link" and ev.context and "target=\"_blank\"" in ev.context:
            text_lower = (ev.text + " " + (ev.accessible_name or "")).lower()
            if not any(cue in text_lower for cue in ("new window", "opens in", "बाहरी लिंक", "नई विंडो")):
                findings.append(CandidateFinding(
                    issue_type="NEW_WINDOW_UNANNOUNCED",
                    evidence_ids=[ev.id],
                    quoted_text=ev.text,
                    wcag_sc="3.2.2",
                    who_is_affected="Low-vision and screen-reader users",
                    citizen_impact="Activating this link opens a new browser window without warning, disorienting navigation.",
                    suggested_fix="Add an icon and aria-label '(opens in new tab)'.",
                    severity_hint="major"
                ))
    return findings


def check_touch_targets(evidence_list: list[Evidence]) -> list[CandidateFinding]:
    """Flag interactive mobile elements under 24x24 px."""
    findings: list[CandidateFinding] = []
    for ev in evidence_list:
        if ev.device == "mobile" and ev.bbox:
            _, _, w, h = ev.bbox
            if w < 24 or h < 24:
                findings.append(CandidateFinding(
                    issue_type="SMALL_TOUCH_TARGET",
                    evidence_ids=[ev.id],
                    quoted_text=ev.text or ev.role or "button",
                    wcag_sc="2.5.8",
                    who_is_affected="Mobile users and citizens with motor impairments",
                    citizen_impact=f"Interactive target size is {int(w)}x{int(h)}px, below the 24x24px minimum.",
                    suggested_fix="Increase touch padding or min-height/min-width to at least 24px (preferably 44px).",
                    severity_hint="major"
                ))
    return findings


def check_mobile_speed(lcp_seconds: float, evidence_id: str) -> list[CandidateFinding]:
    """Flag mobile LCP > 4s on throttled slow-4G profile."""
    if lcp_seconds > 4.0:
        return [
            CandidateFinding(
                issue_type="SLOW_ON_MOBILE",
                evidence_ids=[evidence_id],
                quoted_text=f"LCP: {lcp_seconds:.2f}s",
                wcag_sc=None,
                who_is_affected="Rural citizens on 3G/4G connections",
                citizen_impact=f"Page took {lcp_seconds:.2f}s to load largest contentful paint on a throttled mobile profile.",
                suggested_fix="Compress images, eliminate render-blocking scripts, and serve lightweight HTML.",
                severity_hint="major"
            )
        ]
    return []


def run_all_deterministic_rules(
    evidence_list: list[Evidence],
    lcp_seconds: float | None = None
) -> list[CandidateFinding]:
    """Runs all custom deterministic checks against captured page evidence."""
    results: list[CandidateFinding] = []
    results.extend(check_vague_links(evidence_list))
    results.extend(check_pdf_only_info(evidence_list))
    results.extend(check_unannounced_new_window(evidence_list))
    results.extend(check_touch_targets(evidence_list))
    if lcp_seconds and evidence_list:
        results.extend(check_mobile_speed(lcp_seconds, evidence_list[0].id))
    return results
