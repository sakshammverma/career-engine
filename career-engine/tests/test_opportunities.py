"""Tests for the opportunity engine."""

from __future__ import annotations

from app.models import (
    Academic,
    CareerGoals,
    Experience,
    SkillAssessment,
    StudentProfile,
    TargetRole,
)
from app.opportunities import OPPORTUNITIES, match_opportunities
from app.samples import backend_sem3_student


def _student(sem: int, role=TargetRole.BACKEND, levels=None, cp=0) -> StudentProfile:
    return StudentProfile(
        academic=Academic(college_tier=2, current_semester=sem),
        goals=CareerGoals(target_role=role),
        skills=SkillAssessment(levels=levels or {}),
        experience=Experience(cp_level=cp),
    )


def test_semester_window_filters_hard():
    """A semester-1 student sees nothing whose window starts later."""
    matches = match_opportunities(_student(sem=1))
    shown = {m.opportunity.id for m in matches}
    assert "gsoc" not in shown          # opens sem 3
    assert "google_step" not in shown   # opens sem 2


def test_step_excluded_for_seniors():
    """Google STEP is early-career only (max sem 4)."""
    matches = match_opportunities(_student(sem=6, levels={"programming": 4, "dsa": 4}))
    shown = {m.opportunity.id for m in matches}
    assert "google_step" not in shown


def test_role_specific_filtered():
    """Kaggle targets AI/ML/DS roles; a backend student never sees it."""
    be = match_opportunities(
        _student(sem=5, role=TargetRole.BACKEND, levels={"python": 4, "ml": 4}))
    assert "kaggle" not in {m.opportunity.id for m in be}

    ml = match_opportunities(
        _student(sem=5, role=TargetRole.ML_ENGINEER, levels={"python": 4, "ml": 4}))
    assert "kaggle" in {m.opportunity.id for m in ml}


def test_eligible_sorted_before_near_misses():
    matches = match_opportunities(backend_sem3_student())
    eligibles = [m.eligible for m in matches]
    # Once we hit the first ineligible, no eligible may follow.
    if False in eligibles:
        first_miss = eligibles.index(False)
        assert True not in eligibles[first_miss:]


def test_near_miss_lists_whats_missing():
    """A student below a skill floor sees the gap spelled out, not a rejection."""
    m = match_opportunities(_student(sem=4, levels={"programming": 4, "git": 3, "dsa": 1}))
    icpc = next(x for x in m if x.opportunity.id == "icpc")
    assert not icpc.eligible
    assert icpc.missing  # names the DSA/CP gaps


def test_cp_floor_enforced():
    no_cp = match_opportunities(_student(sem=4, levels={"dsa": 5}, cp=0))
    icpc = next(x for x in no_cp if x.opportunity.id == "icpc")
    assert not icpc.eligible

    with_cp = match_opportunities(_student(sem=4, levels={"dsa": 5}, cp=3))
    icpc = next(x for x in with_cp if x.opportunity.id == "icpc")
    assert icpc.eligible


def test_fit_scores_bounded():
    for m in match_opportunities(backend_sem3_student()):
        assert 0.0 <= m.fit_score <= 1.0


def test_catalog_ids_unique():
    assert len(OPPORTUNITIES) == len(set(OPPORTUNITIES))
