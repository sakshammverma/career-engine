"""Tests for the FastAPI endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.samples import backend_sem3_student

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_roles_endpoint():
    r = client.get("/roles")
    assert r.status_code == 200
    roles = r.json()
    assert any(role["role"] == "backend" for role in roles)


def test_readiness_endpoint():
    r = client.post("/readiness", json=backend_sem3_student().model_dump())
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "backend"
    assert 0 < body["readiness_pct"] < 100
    assert body["projected_readiness_pct"] >= body["readiness_pct"]
    assert body["recommendations"]


def test_roadmap_endpoint():
    r = client.post("/roadmap", json=backend_sem3_student().model_dump())
    assert r.status_code == 200
    body = r.json()
    assert body["current_semester"] == 3
    assert body["semesters"]


def test_validation_rejects_bad_semester():
    bad = backend_sem3_student().model_dump()
    bad["academic"]["current_semester"] = 99
    r = client.post("/readiness", json=bad)
    assert r.status_code == 422


# ----- stateful endpoints -------------------------------------------------
def _new_student() -> str:
    r = client.post("/students", json=backend_sem3_student().model_dump())
    assert r.status_code == 201
    return r.json()["student_id"]


def test_student_lifecycle_and_recompute():
    sid = _new_student()

    r = client.get(f"/students/{sid}/dashboard")
    assert r.status_code == 200
    before = r.json()["readiness"]["readiness_pct"]

    # Improve a skill -> dashboard recomputes with higher readiness.
    r = client.patch(f"/students/{sid}/skills/sql", json={"level": 4})
    assert r.status_code == 200
    after = r.json()["readiness"]["readiness_pct"]
    assert after > before


def test_milestone_endpoint_updates_progress():
    sid = _new_student()
    r = client.patch(f"/students/{sid}/milestones/github_created", json={"done": True})
    assert r.status_code == 200
    ms = r.json()["milestones"]
    assert ms["completed_count"] >= 1


def test_unknown_milestone_rejected():
    sid = _new_student()
    r = client.patch(f"/students/{sid}/milestones/bogus", json={"done": True})
    assert r.status_code == 404


def test_advance_semester_endpoint():
    sid = _new_student()
    r = client.post(f"/students/{sid}/advance-semester")
    assert r.status_code == 200
    assert r.json()["profile"]["academic"]["current_semester"] == 4


def test_dashboard_404_for_unknown_student():
    r = client.get("/students/does-not-exist/dashboard")
    assert r.status_code == 404


def test_resources_endpoint():
    r = client.get("/resources/dsa", params={"budget": "free_only"})
    assert r.status_code == 200
    assert all(item["free"] for item in r.json())
