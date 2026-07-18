"""Tests for the deterministic career engine."""

from __future__ import annotations

from app.engine import (
    analyze,
    compute_gaps,
    compute_readiness_pct,
    project_after,
    recommend,
)
from app.graph.roles import ROLES
from app.models import (
    Academic,
    CareerGoals,
    SkillAssessment,
    StudentProfile,
    TargetRole,
)
from app.samples import backend_sem3_student


def _profile(levels: dict[str, int], role=TargetRole.BACKEND, sem=3) -> StudentProfile:
    return StudentProfile(
        academic=Academic(college_tier=2, current_semester=sem),
        goals=CareerGoals(target_role=role),
        skills=SkillAssessment(levels=levels),
    )


def test_empty_profile_is_zero_readiness():
    p = _profile({})
    assert compute_readiness_pct(p, ROLES[TargetRole.BACKEND]) == 0.0


def test_full_profile_is_100_readiness():
    role = ROLES[TargetRole.BACKEND]
    # Meet every requirement exactly at target.
    levels = {r.skill_id: r.target_level for r in role.requirements}
    p = _profile(levels)
    assert compute_readiness_pct(p, role) == 100.0


def test_readiness_is_between_0_and_100():
    p = backend_sem3_student()
    r = compute_readiness_pct(p, ROLES[TargetRole.BACKEND])
    assert 0.0 < r < 100.0


def test_overshooting_target_does_not_exceed_100():
    role = ROLES[TargetRole.BACKEND]
    # Everyone maxed at 5, higher than most targets -> still exactly 100.
    levels = {r.skill_id: 5 for r in role.requirements}
    p = _profile(levels)
    assert compute_readiness_pct(p, role) == 100.0


def test_gaps_sorted_by_weighted_severity():
    p = backend_sem3_student()
    gaps = compute_gaps(p, ROLES[TargetRole.BACKEND])
    scores = [g.weight * g.gap_fraction for g in gaps]
    assert scores == sorted(scores, reverse=True)


def test_projection_increases_readiness():
    """The 42%->58% story: completing recommended skills raises readiness."""
    p = backend_sem3_student()
    result = analyze(p)
    assert result.projected_readiness_pct > result.readiness_pct
    # Projection is driven only by actionable (unblocked) recommendations.
    assert result.projected_from
    for sid in result.projected_from:
        # Actionable recs must have no missing prereqs.
        rec = next(r for r in result.recommendations if r.skill_id == sid)
        assert rec.blocked_by == []


def test_project_after_specific_skills():
    p = backend_sem3_student()
    role = ROLES[TargetRole.BACKEND]
    before = compute_readiness_pct(p, role)
    after = project_after(p, role, ["sql", "apis"])
    assert after > before


def test_blocked_skill_is_penalised_below_its_prereq():
    """System design (needs apis/redis/sql) must not outrank its prereqs."""
    # Student has nothing infra-related; system_design is deeply blocked.
    p = _profile({"programming": 4, "dsa": 4, "git": 3})
    recs = recommend(p, ROLES[TargetRole.BACKEND], top_n=12)
    ids = [r.skill_id for r in recs]
    assert "system_design" in ids
    assert "apis" in ids
    # A prerequisite of system_design should be recommended before it.
    assert ids.index("apis") < ids.index("system_design")


def test_recommendations_carry_readiness_gain():
    p = backend_sem3_student()
    result = analyze(p)
    assert all(r.readiness_gain >= 0 for r in result.recommendations)
    assert result.recommendations  # non-empty for an incomplete student
