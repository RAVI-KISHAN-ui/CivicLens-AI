"""Unit test for journey runner execution."""

import os
import pytest
from civiclens.scan.runner import JourneyRunner


@pytest.mark.asyncio
async def test_journey_runner_execution():
    runner = JourneyRunner()
    # Locate repo root tasks directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    task_file = os.path.join(base_dir, "tasks", "scholarship-eligibility-docs.yaml")
    
    events_received = []

    async def on_event(ev_type: str, data: dict):
        events_received.append((ev_type, data))

    evidence, candidates, metrics = await runner.run_scan_stream("test_scan_101", task_file, on_event)

    assert len(evidence) > 0
    assert len(candidates) > 0
    assert metrics.pages_visited >= 1
    assert any(e[0] == "page_started" for e in events_received)
    assert any(e[0] == "page_captured" for e in events_received)
