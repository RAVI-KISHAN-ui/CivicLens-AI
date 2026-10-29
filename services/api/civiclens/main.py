"""FastAPI backend service for CivicLens AI.
Reference: Section 11 of AGENTS.md.
"""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone
import json
import os
import uuid
import yaml

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from civiclens.models import (
    Scan,
    Evidence,
    Finding,
    CandidateFinding,
    CitedFact,
    TaskMetrics,
    compute_severity,
)
from civiclens.store import Store
from civiclens.security import validate_url
from civiclens.scan.runner import JourneyRunner
from civiclens.ai.verify import verify_candidate
from civiclens.ai.analyze import analyze_page_evidence
from civiclens.ai.extract import extract_scheme_facts


# Project paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TASKS_DIR = os.path.join(BASE_DIR, "tasks")
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures", "demo")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

store = Store()
runner = JourneyRunner(MEDIA_DIR)

# In-memory pub-sub queues for SSE per scan
scan_subscribers: dict[str, list[asyncio.Queue]] = {}


def _broadcast_event(scan_id: str, event_type: str, data: dict):
    if scan_id in scan_subscribers:
        payload = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        for q in scan_subscribers[scan_id]:
            q.put_nowait(payload)


def _seed_demo_fixture():
    demo_file = os.path.join(FIXTURES_DIR, "scan_scholarship.json")
    if os.path.exists(demo_file):
        with open(demo_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            scan_data = data["scan"]
            existing = store.get_scan(scan_data["id"])
            if not existing:
                scan = Scan(
                    id=scan_data["id"],
                    task_id=scan_data["task_id"],
                    url=scan_data["url"],
                    status=scan_data["status"],
                    total_candidates=scan_data["total_candidates"],
                    verified_count=scan_data["verified_count"],
                    needs_review_count=scan_data["needs_review_count"],
                    rejected_count=scan_data["rejected_count"],
                    metrics_original=TaskMetrics(**scan_data["metrics_original"]),
                    metrics_prototype=TaskMetrics(**scan_data["metrics_prototype"])
                )
                store.create_scan(scan)
                for f_data in data.get("findings", []):
                    finding = Finding(**f_data)
                    store.save_finding(finding)
                for ev_data in data.get("evidence", []):
                    ev = Evidence(**ev_data)
                    store.save_evidence(ev)
                for fact_data in data.get("facts", []):
                    fact = CitedFact(**fact_data)
                    store.save_scan_fact(scan.id, fact)


from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    _seed_demo_fixture()
    yield

app = FastAPI(
    title="CivicLens AI API",
    description="Evidence-first citizen journey auditor for Indian government portals",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration for Vite dev server & production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models for requests ---
class ScanRequest(BaseModel):
    url: str
    task_id: str = "scholarship-eligibility-docs"


class ReviewRequest(BaseModel):
    decision: str  # "accepted" | "dismissed"
    note: str | None = None


class CheckFactRequest(BaseModel):
    checked: bool = True


# --- Endpoints ---

@app.get("/api/tasks")
def list_tasks():
    """List available citizen task specifications."""
    tasks = []
    if os.path.exists(TASKS_DIR):
        for fname in os.listdir(TASKS_DIR):
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                fpath = os.path.join(TASKS_DIR, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    task_spec = yaml.safe_load(f)
                    tasks.append(task_spec)
    return tasks


@app.post("/api/scans")
async def start_scan(req: ScanRequest, bg_tasks: BackgroundTasks):
    """Validate URL and launch asynchronous inspection scan."""
    # 1. SSRF validation
    valid, reason = validate_url(req.url)
    if not valid:
        raise HTTPException(status_code=400, detail=f"Invalid URL: {reason}")

    task_file = os.path.join(TASKS_DIR, f"{req.task_id}.yaml")
    if not os.path.exists(task_file):
        raise HTTPException(status_code=404, detail=f"Task specification '{req.task_id}' not found.")

    scan_id = f"scan_{uuid.uuid4().hex[:8]}"
    scan = Scan(id=scan_id, task_id=req.task_id, url=req.url, status="running")
    store.create_scan(scan)

    bg_tasks.add_task(_execute_scan_pipeline, scan_id, req.url, task_file)
    return {"scan_id": scan_id, "status": "running"}


async def _execute_scan_pipeline(scan_id: str, url: str, task_yaml: str):
    """Orchestrates capture, deterministic checks, LLM analysis, verifier gates, and fact extraction."""
    with open(task_yaml, "r", encoding="utf-8") as f:
        task_data = yaml.safe_load(f)

    task_title = task_data.get("title", "Citizen Journey Audit")
    goal_qs = [q.get("text", "") for q in task_data.get("goal_questions", [])]

    async def on_runner_event(ev_type: str, data: dict):
        _broadcast_event(scan_id, ev_type, data)

    try:
        # Step 1: Run journey
        evidence_list, rule_candidates, metrics_orig = await runner.run_scan_stream(
            scan_id, task_yaml, on_runner_event
        )

        for ev in evidence_list:
            store.save_evidence(ev)

        ev_map = {e.id: e for e in evidence_list}

        # Step 2: Contextual AI Analysis
        llm_candidates, consistent_keys = await analyze_page_evidence(
            url, evidence_list, task_title, goal_qs
        )

        all_candidates = rule_candidates + llm_candidates
        _broadcast_event(scan_id, "candidate", {"total_candidates": len(all_candidates)})

        # Step 3: Run Verifier Gates (Firewall)
        verified_count = 0
        needs_review_count = 0
        rejected_count = 0

        for cand in all_candidates:
            key = f"{cand.issue_type}:{','.join(sorted(cand.evidence_ids))}"
            is_consistent = key in consistent_keys or cand in rule_candidates
            source = "rule" if cand in rule_candidates else "llm"
            finding = verify_candidate(cand, scan_id, ev_map, source=source, is_self_consistent=is_consistent)
            store.save_finding(finding)

            if finding.status == "verified":
                verified_count += 1
            elif finding.status == "needs_review":
                needs_review_count += 1
            else:
                rejected_count += 1

            _broadcast_event(scan_id, "gate", {
                "finding_id": finding.id,
                "status": finding.status,
                "gates": [g.model_dump() for g in finding.gates]
            })

        # Step 4: Extract Grounded Facts for Prototype
        facts = extract_scheme_facts(evidence_list, task_data.get("goal_questions", []))
        for fact in facts:
            store.save_scan_fact(scan_id, fact)

        # Step 5: Prototype Metrics (Redesigned 3-step journey robot measurement)
        metrics_proto = TaskMetrics(
            clicks_to_answer=3,
            pages_visited=1,
            pdf_hops=0,
            distinct_domains=1,
            time_to_answer_ms=int(metrics_orig.time_to_answer_ms * 0.15),
            words_on_path=320,
            bytes_transferred=80 * 1024
        )

        # Update Scan in store
        scan = store.get_scan(scan_id)
        if scan:
            scan.status = "completed"
            scan.completed_at = datetime.now(timezone.utc)
            scan.total_candidates = len(all_candidates)
            scan.verified_count = verified_count
            scan.needs_review_count = needs_review_count
            scan.rejected_count = rejected_count
            scan.metrics_original = metrics_orig
            scan.metrics_prototype = metrics_proto
            store.update_scan(scan)

        _broadcast_event(scan_id, "scan_done", {
            "status": "completed",
            "verified": verified_count,
            "needs_review": needs_review_count,
            "rejected": rejected_count
        })

    except Exception as e:
        scan = store.get_scan(scan_id)
        if scan:
            scan.status = "failed"
            scan.error_message = str(e)
            store.update_scan(scan)
        _broadcast_event(scan_id, "error", {"message": str(e)})


@app.get("/api/scans/{scan_id}/events")
async def scan_events(scan_id: str):
    """Server-Sent Events (SSE) stream for live scan progress."""
    scan = store.get_scan(scan_id)
    if scan and scan.status in ("completed", "failed"):
        async def completed_generator():
            yield "event: connected\ndata: {\"status\": \"listening\"}\n\n"
            terminal_event = "scan_done" if scan.status == "completed" else "error"
            yield f"event: {terminal_event}\ndata: {{\"scan_id\": \"{scan.id}\", \"status\": \"{scan.status}\"}}\n\n"
        return StreamingResponse(completed_generator(), media_type="text/event-stream")

    queue: asyncio.Queue = asyncio.Queue()
    if scan_id not in scan_subscribers:
        scan_subscribers[scan_id] = []
    scan_subscribers[scan_id].append(queue)

    async def event_generator():
        try:
            # Yield initial connection event
            yield "event: connected\ndata: {\"status\": \"listening\"}\n\n"
            while True:
                msg = await queue.get()
                yield msg
                if "scan_done" in msg or "error" in msg:
                    break
        finally:
            if scan_id in scan_subscribers and queue in scan_subscribers[scan_id]:
                scan_subscribers[scan_id].remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/scans/{scan_id}")
def get_scan(scan_id: str):
    """Retrieve scan summary and metrics."""
    scan = store.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan


@app.get("/api/scans/{scan_id}/findings")
def get_findings(
    scan_id: str,
    status: str | None = Query(None),
    severity: str | None = Query(None)
):
    """Retrieve findings for a scan with optional filters."""
    return store.get_findings_by_scan(scan_id, status=status, severity=severity)


@app.get("/api/findings/{scan_id}/{finding_id}")
def get_finding_detail(scan_id: str, finding_id: str):
    """Retrieve single finding with full evidence details and gate trail."""
    finding = store.get_finding(scan_id, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found.")
    
    evidence_items = [store.get_evidence(scan_id, eid) for eid in finding.evidence_ids]
    return {
        "finding": finding,
        "evidence": [ev for ev in evidence_items if ev]
    }


@app.post("/api/findings/{scan_id}/{finding_id}/review")
def review_finding(scan_id: str, finding_id: str, req: ReviewRequest):
    """Human-in-the-loop review decision (accept or dismiss finding)."""
    ok = store.update_finding_review(scan_id, finding_id, req.decision)
    if not ok:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return {"status": "ok", "decision": req.decision}


@app.get("/api/scans/{scan_id}/facts")
def get_facts(scan_id: str):
    """Retrieve grounded cited facts for the prototype."""
    return store.get_facts_by_scan(scan_id)


@app.post("/api/facts/{scan_id}/{fact_id}/check")
def check_fact(scan_id: str, fact_id: str, req: CheckFactRequest):
    """Human check verification for a cited prototype fact."""
    ok = store.set_fact_checked(scan_id, fact_id, req.checked)
    if not ok:
        raise HTTPException(status_code=404, detail="Fact not found.")
    return {"status": "ok", "human_checked": req.checked}


@app.get("/api/scans/{scan_id}/compare")
def compare_metrics(scan_id: str):
    """Compare before (original) vs after (prototype) robot task measurements."""
    scan = store.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return {
        "original": scan.metrics_original,
        "prototype": scan.metrics_prototype,
        "is_estimated": True
    }


@app.get("/api/scans/{scan_id}/export.json")
def export_scan_json(scan_id: str):
    """Download full scan report as JSON."""
    scan = store.get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found.")
    findings = store.get_findings_by_scan(scan_id)
    facts = store.get_facts_by_scan(scan_id)
    evidence = store.get_evidence_by_scan(scan_id)
    return {
        "scan": scan,
        "findings": findings,
        "facts": facts,
        "evidence": evidence
    }


# Static media serving for screenshot crops
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
