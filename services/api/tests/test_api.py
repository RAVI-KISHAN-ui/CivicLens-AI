"""Integration tests for the CivicLens FastAPI endpoints.
Reference: Section 11.2 of AGENTS.md.
"""

from fastapi.testclient import TestClient
from civiclens.main import app, _seed_demo_fixture

client = TestClient(app)


def setup_module():
    _seed_demo_fixture()


def test_list_tasks():
    response = client.get("/api/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) >= 1
    assert any(t.get("id") == "scholarship-eligibility-docs" for t in tasks)


def test_get_demo_scan():
    response = client.get("/api/scans/scan_demo_scholarship")
    assert response.status_code == 200
    scan = response.json()
    assert scan["id"] == "scan_demo_scholarship"
    assert scan["status"] == "completed"
    assert scan["verified_count"] > 0
    assert scan["rejected_count"] > 0


def test_get_findings_and_filter():
    response = client.get("/api/scans/scan_demo_scholarship/findings?status=verified")
    assert response.status_code == 200
    findings = response.json()
    assert len(findings) >= 1
    assert all(f["status"] == "verified" for f in findings)


def test_review_finding():
    finding_id = "f_vague_link_ev_p1_2"
    response = client.post(
        f"/api/findings/scan_demo_scholarship/{finding_id}/review",
        json={"decision": "accepted", "note": "Verified by reviewer"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "accepted"


def test_get_facts_and_check():
    response = client.get("/api/scans/scan_demo_scholarship/facts")
    assert response.status_code == 200
    facts = response.json()
    assert len(facts) >= 1

    fact_id = facts[0]["id"]
    check_res = client.post(
        f"/api/facts/scan_demo_scholarship/{fact_id}/check",
        json={"checked": True}
    )
    assert check_res.status_code == 200
    assert check_res.json()["human_checked"] is True


def test_compare_metrics():
    response = client.get("/api/scans/scan_demo_scholarship/compare")
    assert response.status_code == 200
    comp = response.json()
    assert "original" in comp
    assert "prototype" in comp
    # Prototype should have fewer clicks and pages than original
    assert comp["prototype"]["clicks_to_answer"] < comp["original"]["clicks_to_answer"]


def test_export_scan_json():
    response = client.get("/api/scans/scan_demo_scholarship/export.json")
    assert response.status_code == 200
    data = response.json()
    assert "scan" in data
    assert "findings" in data
    assert "facts" in data


def test_start_scan_ssrf_rejection():
    # Attempting to scan a private IP or non-whitelisted domain must fail with 400
    response = client.post(
        "/api/scans",
        json={"url": "http://169.254.169.254/latest/meta-data/", "task_id": "scholarship-eligibility-docs"}
    )
    assert response.status_code == 400
    assert "Invalid URL" in response.json()["detail"]
