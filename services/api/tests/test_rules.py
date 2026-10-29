"""Unit tests for custom deterministic accessibility & usability rules.
Reference: Section 7.4 of AGENTS.md.
"""

from civiclens.scan.capture import build_evidence
from civiclens.checks.rules import (
    check_vague_links,
    check_pdf_only_info,
    check_unannounced_new_window,
    check_touch_targets,
    check_mobile_speed,
    run_all_deterministic_rules,
)


def test_check_vague_links_lexicon():
    ev1 = build_evidence(
        scan_id="s1", page_id="p1", page_url="https://portal.gov.in",
        idx=1, kind="link", text="Click here", accessible_name="Click here", href="/next"
    )
    ev2 = build_evidence(
        scan_id="s1", page_id="p1", page_url="https://portal.gov.in",
        idx=2, kind="link", text="यहाँ क्लिक करें", accessible_name="यहाँ क्लिक करें", href="/hindi"
    )
    ev_good = build_evidence(
        scan_id="s1", page_id="p1", page_url="https://portal.gov.in",
        idx=3, kind="link", text="Apply for Scholarship 2026", accessible_name="Apply for Scholarship 2026", href="/apply"
    )

    findings = check_vague_links([ev1, ev2, ev_good])
    assert len(findings) == 2
    assert all(f.issue_type == "VAGUE_LINK_TEXT" for f in findings)
    assert findings[0].wcag_sc == "2.4.4"


def test_check_pdf_only_info():
    ev_pdf = build_evidence(
        scan_id="s1", page_id="p1", page_url="https://portal.gov.in",
        idx=1, kind="pdf_link", text="Download Scholarship Guidelines (PDF)", href="/files/rules.pdf"
    )
    findings = check_pdf_only_info([ev_pdf])
    assert len(findings) == 1
    assert findings[0].issue_type == "KEY_INFO_ONLY_IN_PDF"
    assert findings[0].severity_hint == "blocker"


def test_check_touch_targets():
    ev_small = build_evidence(
        scan_id="s1", page_id="p1", page_url="https://portal.gov.in",
        idx=1, kind="element", text="Menu", device="mobile", bbox=[10, 10, 18, 18]
    )
    ev_ok = build_evidence(
        scan_id="s1", page_id="p1", page_url="https://portal.gov.in",
        idx=2, kind="element", text="Submit", device="mobile", bbox=[10, 50, 48, 48]
    )
    findings = check_touch_targets([ev_small, ev_ok])
    assert len(findings) == 1
    assert findings[0].issue_type == "SMALL_TOUCH_TARGET"
    assert findings[0].wcag_sc == "2.5.8"


def test_check_mobile_speed():
    findings_slow = check_mobile_speed(4.5, "ev_p1_1")
    assert len(findings_slow) == 1
    assert findings_slow[0].issue_type == "SLOW_ON_MOBILE"

    findings_fast = check_mobile_speed(2.1, "ev_p1_1")
    assert len(findings_fast) == 0
