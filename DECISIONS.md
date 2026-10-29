# Architecture & Dependency Decisions (DECISIONS.md)

| Date | Area | Decision | Rationale |
|---|---|---|---|
| 2026-10-30 | Architecture | Single-process FastAPI + asyncio + SQLite | Zero queue infrastructure (no Redis/Celery); simple local demo reliability |
| 2026-10-30 | Browser | Playwright for Python with Chromium | Async API, robust CDP network/CPU throttling emulation, reliable DOM/screenshot capture |
| 2026-10-30 | A11y Engine | axe-core via axe-playwright-python | Ground truth for WCAG 2.2 Level A/AA deterministic accessibility violations |
| 2026-10-30 | Frontend | Vite + React 19 + TypeScript + Tailwind v4 | High performance, lightweight bundle (<170KB dashboard, <80KB prototype), rapid prototyping |
| 2026-10-30 | Data Contract | Pydantic v2 with `extra="forbid"` | Strict schema validation prevents hallucinated or malformed candidate findings |
| 2026-10-30 | Anti-Hallucination | 8-Gate Verifier (Firewall) with Citations API | Structured output citing exact evidence IDs; rejected candidates logged transparently |
| 2026-10-30 | Offline Demo | Replay mode from static demo fixtures | Guaranteed demo execution regardless of venue Wi-Fi or target portal downtime |
