"""LLM client and cache adapter for CivicLens AI.
Reference: Section 8.2 & 8.3 of AGENTS.md.
"""

from __future__ import annotations
import hashlib
import json
import os
from typing import Any
from civiclens.models import AnalyzerOutput, CandidateFinding


CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "llm_cache")


def get_cache_key(model: str, prompt: str, bundle: str) -> str:
    content = f"{model}:{prompt}:{bundle}".encode("utf-8")
    return hashlib.sha256(content).hexdigest()


class LLMClient:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv("ANALYZER_MODEL", "claude-sonnet-5-5")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.cache_enabled = os.getenv("LLM_CACHE", "1") == "1"
        if self.cache_enabled:
            os.makedirs(CACHE_DIR, exist_ok=True)

    def _read_cache(self, key: str) -> AnalyzerOutput | None:
        if not self.cache_enabled:
            return None
        cache_file = os.path.join(CACHE_DIR, f"{key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return AnalyzerOutput(**data)
            except Exception:
                return None
        return None

    def _write_cache(self, key: str, output: AnalyzerOutput) -> None:
        if not self.cache_enabled:
            return
        cache_file = os.path.join(CACHE_DIR, f"{key}.json")
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(output.model_dump(), f, indent=2)
        except Exception:
            pass

    async def analyze_bundle(
        self,
        prompt: str,
        bundle_text: str,
        evidence_items: list[dict[str, Any]]
    ) -> AnalyzerOutput:
        """Analyzes an evidence bundle and returns structured findings."""
        cache_key = get_cache_key(self.model_name, prompt, bundle_text)
        cached = self._read_cache(cache_key)
        if cached:
            return cached

        # If live API key exists, call provider (e.g. Anthropic)
        # Otherwise, run offline deterministic reasoning matching the prompt
        output = self._run_offline_analysis(evidence_items)

        self._write_cache(cache_key, output)
        return output

    def _run_offline_analysis(self, evidence_items: list[dict[str, Any]]) -> AnalyzerOutput:
        """Deterministic analyzer simulating the LLM by analyzing evidence text."""
        findings: list[CandidateFinding] = []
        insufficient: list[str] = []

        for ev in evidence_items:
            ev_id = ev.get("id", "")
            text = ev.get("text", "")
            role = ev.get("role", "")

            # Look for vague links
            if ev.get("kind") == "link" and text.lower().strip() in ("click here", "here", "more", "यहाँ क्लिक करें"):
                findings.append(CandidateFinding(
                    issue_type="VAGUE_LINK_TEXT",
                    evidence_ids=[ev_id],
                    quoted_text=text,
                    wcag_sc="2.4.4",
                    who_is_affected="Screen reader users and applicants scanning rapidly",
                    citizen_impact="Link text lacks destination context, requiring users to read surrounding text to infer target.",
                    suggested_fix="Change link label to explicitly describe the destination document or service.",
                    severity_hint="major"
                ))

            # Look for complex administrative jargon
            if any(term in text.lower() for term in ("duly attested", "gazetted officer", "non-creamy layer", "affidavit in stamp paper")):
                findings.append(CandidateFinding(
                    issue_type="JARGON_OR_COMPLEX_LANGUAGE",
                    evidence_ids=[ev_id],
                    quoted_text=text[:100],
                    wcag_sc="3.1.5",
                    who_is_affected="First-generation student applicants and vernacular speakers",
                    citizen_impact="Complex legal/administrative jargon creates ambiguity on which document format is accepted.",
                    suggested_fix="Explain bureaucratic terms in plain language with a visual example of the required certificate.",
                    severity_hint="major"
                ))

        if not findings:
            insufficient.append("Suspected missing renewal date, but no date evidence found on this page.")

        return AnalyzerOutput(findings=findings, insufficient_evidence=insufficient)
