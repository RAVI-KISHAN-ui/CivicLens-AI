"""Grounded fact extractor for the citizen redesigned journey.
Reference: Section 8.6 of AGENTS.md.
"""

from __future__ import annotations
import uuid
from civiclens.models import CitedFact, Evidence


def extract_scheme_facts(
    evidence_items: list[Evidence],
    goal_questions: list[dict[str, str]]
) -> list[CitedFact]:
    """Extracts cited facts for each goal question directly grounded in captured evidence."""
    facts: list[CitedFact] = []

    for q in goal_questions:
        q_id = q.get("id", "")
        matched_ev: Evidence | None = None

        if q_id == "eligibility":
            for ev in evidence_items:
                if any(k in ev.text.lower() for k in ("eligible", "eligibility", "criteria", "who can apply")):
                    matched_ev = ev
                    break

            if matched_ev:
                facts.append(CitedFact(
                    id=f"fact_elig_{uuid.uuid4().hex[:6]}",
                    field="eligibility",
                    value=matched_ev.text,
                    source_url=matched_ev.page_url,
                    evidence_ids=[matched_ev.id],
                    cited_text=matched_ev.text,
                    human_checked=False
                ))
            else:
                facts.append(CitedFact(
                    id=f"fact_elig_{uuid.uuid4().hex[:6]}",
                    field="eligibility",
                    value="Not stated on the official page",
                    source_url="",
                    evidence_ids=[],
                    cited_text="",
                    human_checked=False
                ))

        elif q_id == "documents":
            doc_evs = [ev for ev in evidence_items if "document" in ev.text.lower() or "certificate" in ev.text.lower()]
            if doc_evs:
                for doc_ev in doc_evs[:5]:
                    facts.append(CitedFact(
                        id=f"fact_doc_{uuid.uuid4().hex[:6]}",
                        field="document",
                        value=doc_ev.text,
                        source_url=doc_ev.page_url,
                        evidence_ids=[doc_ev.id],
                        cited_text=doc_ev.text,
                        human_checked=False
                    ))
            else:
                facts.append(CitedFact(
                    id=f"fact_doc_{uuid.uuid4().hex[:6]}",
                    field="document",
                    value="Not stated on the official page",
                    source_url="",
                    evidence_ids=[],
                    cited_text="",
                    human_checked=False
                ))

        elif q_id == "apply_link":
            matched_ev = next((ev for ev in evidence_items if ev.kind == "link" and "apply" in (ev.accessible_name or ev.text).lower() and ev.href), None)
            if matched_ev and matched_ev.href:
                facts.append(CitedFact(
                    id=f"fact_apply_{uuid.uuid4().hex[:6]}",
                    field="apply_link",
                    value=matched_ev.href,
                    source_url=matched_ev.page_url,
                    evidence_ids=[matched_ev.id],
                    cited_text=matched_ev.accessible_name or matched_ev.text,
                    human_checked=False
                ))
            else:
                facts.append(CitedFact(
                    id=f"fact_apply_{uuid.uuid4().hex[:6]}",
                    field="apply_link",
                    value="Not stated on the official page",
                    source_url="",
                    evidence_ids=[],
                    cited_text="",
                    human_checked=False
                ))

    return facts
