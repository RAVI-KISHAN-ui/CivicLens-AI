# Requirements — CivicLens AI

## Functional Requirements
- [x] **FR1: Task Specifications**: Define structured YAML tasks with goal questions and recorded navigation paths.
- [x] **FR2: Standards Mapping**: WCAG 2.2 Level A/AA criteria enumeration and hand-verified GIGW 3.0 mappings.
- [ ] **FR3: Core Evidence Model & Security**: Pydantic contracts with `extra="forbid"`, SSRF protection with IP and domain allowlist, SQLite storage.
- [ ] **FR4: Inspection Layer**: Playwright browser runner with Desktop and throttled Mobile (Slow-4G) profiles, full-page screenshots, element crops, axe checks, custom deterministic rules.
- [ ] **FR5: Anti-Hallucination AI & Verifier**: Structured LLM candidate analyzer, 8-gate verification firewall (G1–G8), citations-based fact extractor.
- [ ] **FR6: FastAPI Service & SSE**: Live scan execution streaming via Server-Sent Events, REST API for findings, reviews, facts, and before/after metrics.
- [ ] **FR7: Auditor Dashboard & Evidence Lens**: Real-time scan timeline, firewall counter (Verified / Needs Review / Rejected), 3-pane finding viewer with smooth zoom and quote highlight, model card.
- [ ] **FR8: Citizen Prototype & Comparison**: 3-step accessible citizen guide with cited facts and in-memory checklist, side-by-side journey comparison table.
- [ ] **FR9: Replay Mode & Offline Demo**: Built-in recorded fixtures for 100% offline demonstration reliability.
