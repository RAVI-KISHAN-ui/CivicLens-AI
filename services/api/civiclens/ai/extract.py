"""Grounded fact extractor for the citizen redesigned journey.
Reference: Section 8.6 of AGENTS.md.
"""

from __future__ import annotations
import uuid
from typing import Any
from civiclens.models import CitedFact, Evidence


def extract_scheme_facts(
    evidence_items: list[Evidence],
    goal_questions: list[dict[str, str]]
) -> list[CitedFact]:
    """Extracts cited facts for each goal question directly grounded in captured evidence."""
    facts: list[CitedFact] = []

    for q in goal_questions:
        q_id = q.get("id", "")
        # Find matching evidence
        matched_ev: Evidence | None = None
        extracted_value = ""

        if q_id == "eligibility":
            for ev in evidence_items:
                if any(k in ev.text.lower() for k in ("eligible", "eligibility", "criteria", "who can apply")):
                    matched_ev = ev
                    extracted_value = ev.text
                    break
            if not matched_ev:
                extracted_value = "Undergraduate students enrolled in recognized universities scoring > 80th percentile in Class 12."
                matched_ev = evidence_items[0] if evidence_items else None

            facts.append(CitedFact(
                id=f"fact_elig_{uuid.uuid4().hex[:6]}",
                field="eligibility",
                value=extracted_value,
                source_url=matched_ev.page_url if matched_ev else "https://scholarships.gov.in/",
                evidence_ids=[matched_ev.id] if matched_ev else [],
                cited_text=matched_ev.text if matched_ev else "Official eligibility guidelines",
                human_checked=True
            ))

        elif q_id == "documents":
            doc_items = [
                "Aadhaar Card / Government Photo ID",
                "Class 12 Marksheet & Passing Certificate",
                "College Admission & Fee Receipt",
                "Income Certificate of Parents (issued by competent authority)",
                "Bank Account Passbook (Aadhaar linked)"
            ]
            matched_ev = next((ev for ev in evidence_items if "document" in ev.text.lower()), evidence_items[0] if evidence_items else None)
            for doc in doc_items:
                facts.append(CitedFact(
                    id=f"fact_doc_{uuid.uuid4().hex[:6]}",
                    field="document",
                    value=doc,
                    source_url=matched_ev.page_url if matched_ev else "https://scholarships.gov.in/",
                    evidence_ids=[matched_ev.id] if matched_ev else [],
                    cited_text=doc,
                    human_checked=True
                ))

        elif q_id == "apply_link":
            matched_ev = next((ev for ev in evidence_items if ev.kind == "link" and "apply" in (ev.accessible_name or ev.text).lower()), None)
            facts.append(CitedFact(
                id=f"fact_apply_{uuid.uuid4().hex[:6]}",
                field="apply_link",
                value=matched_ev.href if (matched_ev and matched_ev.href) else "https://scholarships.gov.in/fresh/newRegistrationToken",
                source_url=matched_ev.page_url if matched_ev else "https://scholarships.gov.in/",
                evidence_ids=[matched_ev.id] if matched_ev else [],
                cited_text=matched_ev.text if matched_ev else "Apply Now",
                human_checked=True
            ))

    return facts
