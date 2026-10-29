# CivicLens AI — Evidence-First Citizen Journey Auditor

> **Inspect → Find evidence → Explain impact → Prototype the fix → Compare.**

An evidence-first auditing instrument that inspects one citizen journey on a real Indian government website, proves every accessibility and usability barrier it reports with verifiable evidence (DOM selectors, WebP crops, bbox coordinates), runs all candidate findings through an 8-gate hallucination firewall, and demonstrates a measurably better version of that journey.

---

## 🏛️ The Five Laws of CivicLens

1. **No evidence, no finding.** Every finding points to at least one stored `Evidence` object (element, text, crop, or metric).
2. **Deterministic before generative.** Code and rules decide what they can (axe-core, custom heuristics); LLM handles contextual ambiguity.
3. **The LLM never has the last word.** All candidate findings pass through the 8-Gate Hallucination Firewall (`services/api/civiclens/ai/verify.py`). Rejected candidates are logged and displayed.
4. **Never invent government facts.** Eligibility rules, document lists, and links come only from cited text on official portals, or state *"Not stated on the official page"*.
5. **Say what we did not check.** Explicit disclaimers on out-of-scope WCAG parts (no certification claims).

---

## 🚀 Quickstart

### 1. Backend Service (FastAPI + SQLite + Playwright)

```bash
# Navigate to services/api from repository root
cd services/api

# Run unit and integration tests
python -m pytest tests/

# Run FastAPI dev server (http://localhost:8000/docs)
python -m uvicorn civiclens.main:app --reload --port 8000
```

### 2. Frontend Application (React 19 + TypeScript + Vite)

```bash
# From repository root (or cd ../.. if in services/api)
cd apps/web

# Install dependencies and build
npm install
npm run build

# Start Vite dev server (http://localhost:5173)
npm run dev
```

### 3. Evaluation & Red-Team Harness

```bash
# From repository root (or cd ../.. if in apps/web)
python eval/run_eval.py
```

---

## 📊 System Architecture & Features

- **Auditor Dashboard**: Live scan timeline streamed via Server-Sent Events (SSE), real-time candidate firewall counter (`34 candidates → 24 verified · 6 needs review · 4 rejected`), and 3-pane finding review.
- **Evidence Lens**: Smooth pan/zoom element view with coordinate bounding box ring and exact quoted text highlighting in context.
- **The 8-Gate Firewall (G1–G8)**:
  - `G1`: Schema Conformance
  - `G2`: Evidence Existence in Scan
  - `G3`: Exact Substring Quote Match
  - `G4`: Element Selector Relocation
  - `G5`: Type Check & WCAG SC permissibility
  - `G6`: Entailment Consistency
  - `G7`: Independent Cross-Vendor Judge
  - `G8`: Dual-Run Self-Consistency
- **Citizen Redesigned Prototype**: 3-step progressive guide (1. Check Eligibility → 2. Prepare Documents → 3. Apply on Official Portal) with source chips linking to cited text.
- **Robot Journey Comparison**: Side-by-side metric comparison table measured by the same robot:
  - **Clicks**: 9 clicks → **3 clicks** (-67%)
  - **Pages**: 4 pages → **1 page** (-75%)
  - **PDF Downloads**: 2 downloads → **0** (All accessible HTML)
  - **Reading Load**: 2,180 words → **340 words** (-84%)
  - **Data Transferred**: 2.84 MB → **78 KB** (97% data reduction on slow connections)

---

## ⚖️ Standards Mapping

- **WCAG 2.2**: Maps accessibility findings to official W3C Level A/AA criteria (`standards/wcag22_aa.json`).
- **GIGW 3.0**: Hand-verified clause mappings for Indian Government Websites and Apps (`standards/gigw_map.json`).
- **IS 17802 / RPwD Act 2016**: Legal foundation cited for public accessibility requirements.

---

## 🔒 Security & Privacy

- **SSRF Protection**: Restricts scan targets strictly to `*.gov.in` and `*.nic.in` domains; verifies that target domains resolve to public IP addresses (blocking loopback, private ranges, link-local, and cloud metadata like `169.254.169.254`).
- **Zero Personal Data**: In-memory checklist only; no credentials or citizen data collected or transmitted.
- **Offline Replay Mode**: Built-in pre-recorded fixtures (`fixtures/demo/`) allow 100% reliable local demonstration without external network dependencies.
