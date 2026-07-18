"""Tests for milestones, resources, and the weekly planner."""

from __future__ import annotations

from app.milestones import milestone_progress
from app.models import Budget, LearningStyle
from app.planner import generate_weekly_plan
from app.resources import resources_for
from app.samples import backend_sem3_student


# ----- milestones ---------------------------------------------------------
def test_milestone_completion_pct():
    prog = milestone_progress({"github_created", "resume_ready"}, current_semester=3)
    assert prog.completed_count == 2
    assert 0 < prog.completion_pct < 100


def test_milestone_due_now_reflects_semester():
    # At semester 1, late-stage milestones are not yet "due".
    prog = milestone_progress(set(), current_semester=1)
    due = {s.id for s in prog.statuses if s.due_now}
    assert "github_created" in due          # relevant from sem 1
    assert "internship" not in due          # relevant from sem 4


def test_unknown_milestone_ids_ignored():
    prog = milestone_progress({"not_a_real_milestone"}, current_semester=3)
    assert prog.completed_count == 0


# ----- resources ----------------------------------------------------------
def test_free_only_filters_paid():
    all_ml = resources_for("ml", budget=Budget.PAID_OK)
    free_ml = resources_for("ml", budget=Budget.FREE_ONLY)
    assert len(free_ml) <= len(all_ml)
    assert all(r.free for r in free_ml)


def test_style_preference_orders_first():
    res = resources_for("dsa", budget=Budget.FREE_ONLY, style=LearningStyle.VIDEO)
    assert res  # dsa has curated resources
    # First result should suit the requested style.
    assert LearningStyle.VIDEO in res[0].styles


def test_unknown_skill_returns_empty():
    assert resources_for("nonexistent_skill") == []


# ----- weekly planner -----------------------------------------------------
def test_weekly_plan_nonempty_and_sequential():
    plans = generate_weekly_plan(backend_sem3_student())
    assert plans
    weeks = [p.week for p in plans]
    assert weeks == list(range(1, len(weeks) + 1))


def test_weekly_plan_hours_track_study_time():
    p = backend_sem3_student()  # 3h/day -> 21h/week
    plans = generate_weekly_plan(p)
    # No single week should wildly exceed the weekly budget.
    assert all(plan.estimated_hours <= 21 * 1.5 for plan in plans)


def test_weekly_plan_skips_completed_skills():
    p = backend_sem3_student()
    full = generate_weekly_plan(p, completed_skill_ids=set())
    # Mark the first focus skill as completed -> it drops out.
    first_skill = full[0].focus_skill_id
    fewer = generate_weekly_plan(p, completed_skill_ids={first_skill})
    assert all(plan.focus_skill_id != first_skill for plan in fewer)


def test_interview_prep_appears_late_only():
    p = backend_sem3_student()
    p.academic.current_semester = 6
    plans = generate_weekly_plan(p)
    # At semester 6+, interview prep should be present on at least one week.
    assert any(plan.interview_prep for plan in plans)
