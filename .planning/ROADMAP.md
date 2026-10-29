# Roadmap — CivicLens AI (Phased Execution)

- [x] **Phase 1: Project Scaffolding & Standards**
  - Setup root `AGENTS.md`, `CLAUDE.md`, `DECISIONS.md`, `.gitignore`, `.env.example`.
  - Standards mapping (`wcag22_aa.json`, `issue_sc_map.json`, `gigw_map.json`).
  - Task specification (`scholarship-eligibility-docs.yaml`).
  - Commit, push to GitHub, pull.

- [x] **Phase 2: Backend Core Models, Store & Security**
  - Setup `services/api/` package with `pyproject.toml`.
  - Pydantic models in `services/api/civiclens/models.py`.
  - SSRF protection & domain allowlisting in `security.py`.
  - SQLite evidence/finding storage in `store.py`.
  - Unit tests for security and models.
  - Commit, push to GitHub, pull.

- [x] **Phase 3: Inspection Layer & Deterministic Checks**
  - Playwright browser runner with Desktop and Throttled Mobile CDP emulation.
  - Screenshot capture and WebP element cropping.
  - Deterministic rules (vague link lexicon, PDF-only, navigation depth, touch targets, contrast).
  - Task metrics calculation.
  - Commit, push to GitHub, pull.

- [x] **Phase 4: AI Layer, Anti-Hallucination Verifier & Citations**
  - Analyzer prompts with strict JSON schema.
  - LLM client with multi-provider / mock / caching support.
  - 8-Gate Verifier (G1–G8) hallucination firewall.
  - Grounded scheme facts extractor with citations.
  - Unit tests for verifier gates and quote matching.
  - Commit, push to GitHub, pull.

- [x] **Phase 5: FastAPI Application, Endpoints & SSE Streaming**
  - FastAPI app with CORS and static media serving.
  - SSE endpoint for live scan streaming.
  - REST endpoints for scans, findings, human review, facts, comparison, export.
  - Demo fixture scan for offline replay mode.
  - Integration tests.
  - Commit, push to GitHub, pull.

- [ ] **Phase 6: Frontend App — Dashboard & Evidence Lens**
  - Vite + React 19 + TypeScript + Tailwind CSS v4 setup.
  - Civic instrument design tokens & dual English/Hindi i18n support.
  - Auditor Dashboard with live SSE scan timeline.
  - 3-pane finding detail with Evidence Lens and gate inspection.
  - Model card view.
  - Commit, push to GitHub, pull.

- [ ] **Phase 7: Citizen Prototype & Comparison View**
  - 3-step citizen redesigned guide with official source chips.
  - In-memory accessible documents checklist.
  - Official apply button with domain verification.
  - Side-by-side journey comparison view.
  - Offline replay mode support.
  - Commit, push to GitHub, pull.

- [ ] **Phase 8: Evaluation Harness & Final Verification**
  - Evaluation script (`eval/run_eval.py`) with golden and red-team sets.
  - End-to-end verification and performance budget check.
  - Final documentation, commit, push to GitHub, pull.
