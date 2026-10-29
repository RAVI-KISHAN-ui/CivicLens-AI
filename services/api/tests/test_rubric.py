"""Unit tests for the severity rubric.
Reference: Section 6 of AGENTS.md.
"""

from civiclens.models import compute_severity


def test_rubric_off_task_path():
    # Anything off task path is minor
    assert compute_severity("BROKEN_LINK", on_task_path=False) == "minor"
    assert compute_severity("MISSING_ACCESSIBLE_NAME", on_task_path=False) == "minor"
    assert compute_severity("VAGUE_LINK_TEXT", on_task_path=False) == "minor"


def test_rubric_blockers():
    # Broken link on task path is blocker
    assert compute_severity("BROKEN_LINK", on_task_path=True) == "blocker"
    # Key info only in PDF on task path is blocker
    assert compute_severity("KEY_INFO_ONLY_IN_PDF", on_task_path=True) == "blocker"
    # Missing accessible name on task path is blocker
    assert compute_severity("MISSING_ACCESSIBLE_NAME", on_task_path=True) == "blocker"


def test_rubric_majors():
    # Vague link text on task path is major
    assert compute_severity("VAGUE_LINK_TEXT", on_task_path=True) == "major"
    # Scattered info on task path is major
    assert compute_severity("INFO_SCATTERED_ACROSS_PAGES", on_task_path=True) == "major"
    # Slow on mobile on task path is major
    assert compute_severity("SLOW_ON_MOBILE", on_task_path=True) == "major"


def test_rubric_axe_impact_elevation():
    # axe critical / serious elevates to blocker
    assert compute_severity("OTHER_AXE_RULE", on_task_path=True, axe_impact="critical") == "blocker"
    assert compute_severity("OTHER_AXE_RULE", on_task_path=True, axe_impact="serious") == "blocker"
    assert compute_severity("OTHER_AXE_RULE", on_task_path=True, axe_impact="moderate") == "major"
