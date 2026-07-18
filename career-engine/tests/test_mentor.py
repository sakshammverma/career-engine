"""Tests for the AI mentor layer (no real network calls)."""

from __future__ import annotations

import httpx
import pytest

from app.dashboard import build_dashboard
from app.mentor import Mentor, build_context
from app.samples import backend_sem3_student
from app.store import ProfileStore

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _dash():
    store = ProfileStore(":memory:")
    sid = store.create_student(backend_sem3_student())
    return build_dashboard(sid, store.get_profile(sid),
                           store.get_completed_milestones(sid))


# ----- grounding context --------------------------------------------------
def test_context_contains_engine_truths():
    dash = _dash()
    ctx = build_context(dash)
    assert f"{dash.readiness.readiness_pct}%" in ctx
    assert "Highest-ROI next steps:" in ctx
    # Every recommendation name is present in the grounding block.
    for rec in dash.readiness.recommendations:
        assert rec.name in ctx


# ----- offline mode -------------------------------------------------------
def test_placeholder_key_means_offline():
    m = Mentor(api_key="your_groq_api_key_here")
    assert not m.live
    reply = m.ask(_dash(), "what should I do next?")
    assert reply.mode == "offline"
    # Offline answer is still grounded: names a real next step.
    assert any(r.name in reply.answer
               for r in _dash().readiness.recommendations if not r.blocked_by)


def test_empty_key_means_offline():
    assert not Mentor(api_key="").live


# ----- live mode (mocked transport) --------------------------------------
def test_live_mode_calls_groq_and_returns_answer(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json
        request = httpx.Request("POST", url)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Focus on SQL this week."}}]},
            request=request,
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    m = Mentor(api_key="gsk_test_123", model="llama-3.3-70b-versatile")
    assert m.live
    reply = m.ask(_dash(), "what next?")
    assert reply.mode == "llm"
    assert reply.answer == "Focus on SQL this week."
    # The prompt sent to Groq embeds the deterministic state.
    sent = captured["json"]["messages"][1]["content"]
    assert "STUDENT STATE:" in sent and "Readiness:" in sent


def test_live_mode_falls_back_on_http_error(monkeypatch):
    def failing_post(*args, **kwargs):
        raise httpx.ConnectError("no network")

    monkeypatch.setattr(httpx, "post", failing_post)
    m = Mentor(api_key="gsk_test_123")
    reply = m.ask(_dash(), "help")
    assert reply.mode == "offline"
    assert reply.answer  # still useful


# ----- endpoint -----------------------------------------------------------
def test_mentor_endpoint_offline():
    r = client.post("/students", json=backend_sem3_student().model_dump())
    sid = r.json()["student_id"]
    r = client.post(f"/students/{sid}/mentor", json={"question": "what next?"})
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] in ("offline", "llm")
    assert body["answer"]
    assert "Readiness:" in body["context"]


def test_mentor_endpoint_404_unknown_student():
    r = client.post("/students/nope/mentor", json={"question": "hi"})
    assert r.status_code == 404


def test_mentor_endpoint_rejects_empty_question():
    r = client.post("/students", json=backend_sem3_student().model_dump())
    sid = r.json()["student_id"]
    r = client.post(f"/students/{sid}/mentor", json={"question": ""})
    assert r.status_code == 422
