# CivicLens AI — Project Vision & Architecture

> **Inspect → Find evidence → Explain impact → Prototype the fix → Compare.**

CivicLens AI is an evidence-first auditing instrument for Indian government citizen journeys. It audits real public portals, captures deterministic and contextual accessibility/usability barriers with concrete evidence (DOM selectors, WebP crops, bbox coordinates), runs candidates through an 8-gate hallucination firewall, prototypes a clean citizen-facing 3-step guide with cited facts, and compares the journeys using the exact same robotic test harness.

## Core Pillars
1. **No evidence, no finding**: Every finding must trace to a stored Evidence item.
2. **Deterministic before generative**: axe-core and custom heuristics run before LLM.
3. **The LLM never has the last word**: 8 verifier gates (G1–G8) validate all AI findings.
4. **Never invent government facts**: Prototype facts come with exact citations or "Not stated on the official page".
5. **Say what we did not check**: Explicit disclaimers on out-of-scope WCAG parts.

## Tech Stack
- **Backend**: FastAPI, Pydantic v2, Python 3.12+, SQLite, Playwright (Chromium), axe-playwright-python.
- **Frontend**: Vite, React 19, TypeScript, Tailwind CSS v4, Lucide icons, IBM Plex fonts.
- **AI/Verification**: Structured outputs, 8-gate firewall, citations extraction.
