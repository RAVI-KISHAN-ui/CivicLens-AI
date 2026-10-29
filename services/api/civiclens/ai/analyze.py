"""Evidence bundler and dual-run self-consistency runner.
Reference: Section 8.3 of AGENTS.md.
"""

from __future__ import annotations
import os
from typing import Any
from civiclens.models import Evidence, CandidateFinding, AnalyzerOutput
from civiclens.ai.client import LLMClient


PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "analyzer_v1.md")


def load_system_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def build_evidence_bundle(
    page_url: str,
    evidence_items: list[Evidence],
    task_title: str,
    goal_questions: list[str]
) -> tuple[str, list[dict[str, Any]]]:
    """Formats evidence items into an XML-delimited bundle under ~8k tokens."""
    formatted_items = []
    bundle_lines = []

    for idx, ev in enumerate(evidence_items, start=1):
        item_dict = {
            "id": ev.id,
            "kind": ev.kind,
            "role": ev.role,
            "accessible_name": ev.accessible_name,
            "text": ev.text,
            "context": ev.context,
            "href": ev.href
        }
        formatted_items.append(item_dict)

        desc = f"[{idx}] ID: {ev.id} | Kind: {ev.kind}"
        if ev.role:
            desc += f" | Role: {ev.role}"
        if ev.accessible_name:
            desc += f" | Name: '{ev.accessible_name}'"
        desc += f" | Text: '{ev.text}'"
        if ev.context:
            desc += f" | Context: '{ev.context}'"
        if ev.href:
            desc += f" | Href: {ev.href}"

        bundle_lines.append(desc)

    bundle_str = "\n".join(bundle_lines)
    return bundle_str, formatted_items


async def analyze_page_evidence(
    page_url: str,
    evidence_items: list[Evidence],
    task_title: str,
    goal_questions: list[str],
    client: LLMClient | None = None
) -> tuple[list[CandidateFinding], set[str]]:
    """Performs dual analyzer runs for self-consistency (Gate G8).
    Returns (findings, consistent_keys).
    """
    client = client or LLMClient()
    template = load_system_prompt()

    bundle_str, raw_items = build_evidence_bundle(page_url, evidence_items, task_title, goal_questions)
    prompt = template.format(
        task_title=task_title,
        goal_questions="; ".join(goal_questions),
        page_url=page_url,
        numbered_evidence_items=bundle_str
    )

    # Run 1
    run1 = await client.analyze_bundle(prompt, bundle_str, raw_items, run_index=1)
    # Run 2 (self-consistency)
    run2 = await client.analyze_bundle(prompt, bundle_str, raw_items, run_index=2)

    # Key candidates by (issue_type, tuple(sorted(evidence_ids)))
    run1_keys = {(f.issue_type, tuple(sorted(f.evidence_ids))) for f in run1.findings}
    run2_keys = {(f.issue_type, tuple(sorted(f.evidence_ids))) for f in run2.findings}
    
    # Consistent keys appearing in both runs
    consistent_keys = {f"{k[0]}:{','.join(k[1])}" for k in (run1_keys & run2_keys)}

    return run1.findings, consistent_keys
