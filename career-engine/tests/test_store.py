"""Tests for persistence + the recompute loop."""

from __future__ import annotations

from app.dashboard import build_dashboard
from app.samples import backend_sem3_student
from app.store import ProfileStore, StudentNotFound

import pytest


def _store() -> ProfileStore:
    return ProfileStore(":memory:")


def test_create_and_get_roundtrip():
    s = _store()
    sid = s.create_student(backend_sem3_student())
    p = s.get_profile(sid)
    assert p.goals.target_role.value == "backend"
    assert p.academic.current_semester == 3


def test_missing_student_raises():
    s = _store()
    with pytest.raises(StudentNotFound):
        s.get_profile("nope")


def test_skill_update_persists_and_clamps():
    s = _store()
    sid = s.create_student(backend_sem3_student())
    s.set_skill_level(sid, "sql", 99)  # clamps to 5
    assert s.get_profile(sid).skills.level_of("sql") == 5
    s.set_skill_level(sid, "sql", -3)  # clamps to 0
    assert s.get_profile(sid).skills.level_of("sql") == 0


def test_progress_raises_readiness_via_recompute():
    """The core continuous-update guarantee: improving a skill raises readiness."""
    s = _store()
    sid = s.create_student(backend_sem3_student())

    before = build_dashboard(sid, s.get_profile(sid),
                             s.get_completed_milestones(sid)).readiness.readiness_pct

    # Student learns Linux, SQL, APIs to working level.
    for skill in ("linux", "sql", "apis"):
        s.set_skill_level(sid, skill, 4)

    after = build_dashboard(sid, s.get_profile(sid),
                            s.get_completed_milestones(sid)).readiness.readiness_pct
    assert after > before


def test_milestone_toggle_persists():
    s = _store()
    sid = s.create_student(backend_sem3_student())
    s.set_milestone(sid, "github_created", True)
    assert "github_created" in s.get_completed_milestones(sid)
    s.set_milestone(sid, "github_created", False)
    assert "github_created" not in s.get_completed_milestones(sid)


def test_advance_semester_caps_at_8():
    s = _store()
    sid = s.create_student(backend_sem3_student())
    for _ in range(10):
        s.advance_semester(sid)
    assert s.get_profile(sid).academic.current_semester == 8


def test_history_records_events():
    s = _store()
    sid = s.create_student(backend_sem3_student())
    s.set_skill_level(sid, "sql", 4)
    s.set_milestone(sid, "resume_ready", True)
    hist = s.progress_history(sid)
    kinds = {h["kind"] for h in hist}
    assert "skill" in kinds and "milestone" in kinds
