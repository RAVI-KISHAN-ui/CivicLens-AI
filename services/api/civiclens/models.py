"""Data contracts and evidence model for CivicLens AI.
Reference: Section 6 of AGENTS.md.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    """Base model that forbids unasked attributes (additionalProperties: false)."""
    model_config = ConfigDict(extra="forbid")


EvidenceKind = Literal[
    "element", "text_block", "link", "form_field", "pdf_link",
    "axe_violation", "metric", "page"
]


class Evidence(Strict):
    """Captured proof of page state, element or metric."""
    id: str  # "ev_<page>_<n>", unique within a scan
    scan_id: str
    page_id: str
    page_url: str
    device: Literal["desktop", "mobile"]
    kind: EvidenceKind
    selector: str | None = None  # role+name locator preferred, CSS fallback
    role: str | None = None
    accessible_name: str | None = None
    text: str  # visible text, Unicode NFC, whitespace collapsed
    context: str = ""  # surrounding text, <= 300 chars
    href: str | None = None
    bbox: list[float] | None = None  # [x, y, w, h] in CSS px on full-page screenshot
    crop_path: str | None = None  # WebP crop with 24 px padding
    axe_rule_id: str | None = None
    wcag_tags: list[str] = Field(default_factory=list)  # ["wcag2aa", "wcag143"]
    dom_snapshot_hash: str = ""  # sha256 of serialized DOM at capture time
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


IssueType = Literal[
    "VAGUE_LINK_TEXT",
    "UNCLEAR_INSTRUCTION",
    "JARGON_OR_COMPLEX_LANGUAGE",
    "INFO_SCATTERED_ACROSS_PAGES",
    "KEY_INFO_ONLY_IN_PDF",
    "MISSING_ACCESSIBLE_NAME",
    "LOW_CONTRAST",
    "SMALL_TOUCH_TARGET",
    "NO_LANGUAGE_OPTION",
    "BROKEN_LINK",
    "SLOW_ON_MOBILE",
    "DEEP_NAVIGATION",
    "NEW_WINDOW_UNANNOUNCED",
    "OTHER_AXE_RULE",
]


class CandidateFinding(Strict):
    """The ONLY shape the LLM analyzer may emit."""
    issue_type: IssueType
    evidence_ids: list[str]  # must exist in the bundle it was given
    quoted_text: str  # exact substring of the cited evidence text
    wcag_sc: str | None = None  # e.g., "2.4.4"
    who_is_affected: str  # e.g. "screen-reader users", "first-time applicants"
    citizen_impact: str  # 1-2 sentences, about THIS task
    suggested_fix: str  # concrete, implementable
    severity_hint: Literal["blocker", "major", "minor"] = "major"


class AnalyzerOutput(Strict):
    """Structured output schema for LLM analysis."""
    findings: list[CandidateFinding] = Field(default_factory=list)
    insufficient_evidence: list[str] = Field(default_factory=list)


class GateResult(Strict):
    """Result of a single hallucination firewall verification gate."""
    gate: str  # G1..G8
    passed: bool
    hard: bool
    detail: str


class Finding(Strict):
    """A verified or unverified finding served by the API."""
    id: str
    scan_id: str
    source: Literal["axe", "rule", "llm"]
    issue_type: IssueType
    evidence_ids: list[str]
    quoted_text: str
    wcag_sc: str | None = None
    gigw_ref: str | None = None  # from hand-verified map only
    who_is_affected: str
    citizen_impact: str
    suggested_fix: str
    severity: Literal["blocker", "major", "minor"]
    on_task_path: bool = True
    status: Literal["verified", "needs_review", "rejected"]
    gates: list[GateResult] = Field(default_factory=list)
    review: Literal["unreviewed", "accepted", "dismissed"] = "unreviewed"


class CitedFact(Strict):
    """A factual claim extracted for the prototype journey."""
    id: str | None = None
    field: Literal["eligibility", "document", "apply_link", "deadline", "contact", "amount"]
    value: str
    source_url: str
    evidence_ids: list[str] = Field(default_factory=list)
    cited_text: str
    human_checked: bool = False


class TaskMetrics(Strict):
    """Robot measurements for comparison."""
    clicks_to_answer: int = 0
    pages_visited: int = 0
    pdf_hops: int = 0
    distinct_domains: int = 1
    time_to_answer_ms: int = 0
    words_on_path: int = 0
    bytes_transferred: int = 0


class Scan(Strict):
    """Top-level record of an inspection run."""
    id: str
    task_id: str
    url: str
    status: Literal["running", "completed", "failed"] = "running"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    total_candidates: int = 0
    verified_count: int = 0
    needs_review_count: int = 0
    rejected_count: int = 0
    metrics_original: TaskMetrics | None = None
    metrics_prototype: TaskMetrics | None = None
    error_message: str | None = None


def compute_severity(
    issue_type: IssueType,
    on_task_path: bool,
    axe_impact: str | None = None
) -> Literal["blocker", "major", "minor"]:
    """Compute severity using the exact deterministic rubric in §6 of AGENTS.md.
    
    Blocker:
      - On task path AND prevents completion (e.g. broken link to apply, missing accessible name on key control, key info only in PDF).
    Major:
      - On task path and adds clear friction (vague link, scattered info, low contrast on task text, slow mobile).
    Minor:
      - Off task path, or cosmetic friction.
    """
    if not on_task_path:
        return "minor"

    # Specific blocker issues when on task path
    if issue_type in ("BROKEN_LINK", "MISSING_ACCESSIBLE_NAME", "KEY_INFO_ONLY_IN_PDF"):
        return "blocker"

    # Specific major issues on task path
    if issue_type in (
        "VAGUE_LINK_TEXT", "INFO_SCATTERED_ACROSS_PAGES", "LOW_CONTRAST",
        "SLOW_ON_MOBILE", "SMALL_TOUCH_TARGET", "NEW_WINDOW_UNANNOUNCED",
        "UNCLEAR_INSTRUCTION", "JARGON_OR_COMPLEX_LANGUAGE", "DEEP_NAVIGATION"
    ):
        return "major"

    # Axe impact mapping
    if axe_impact in ("critical", "serious"):
        return "blocker"
    elif axe_impact == "moderate":
        return "major"

    return "minor"
