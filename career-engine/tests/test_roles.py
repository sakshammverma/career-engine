"""Tests for the widened role graph set (incl. ML Engineer and FDE)."""

from __future__ import annotations

from app.engine import analyze
from app.graph.roles import ROLES
from app.graph.skills import SKILLS
from app.models import (
    Academic,
    CareerGoals,
    SkillAssessment,
    StudentProfile,
    TargetRole,
)
from app.roadmap import generate_roadmap

EXPECTED_ROLES = {
    TargetRole.BACKEND,
    TargetRole.FRONTEND,
    TargetRole.FULLSTACK,
    TargetRole.AI_ENGINEER,
    TargetRole.ML_ENGINEER,
    TargetRole.DATA_SCIENTIST,
    TargetRole.DEVOPS,
    TargetRole.ANDROID,
    TargetRole.IOS,
    TargetRole.FDE,
}


def _fresh_student(role: TargetRole, sem: int = 1) -> StudentProfile:
    return StudentProfile(
        academic=Academic(college_tier=2, current_semester=sem),
        goals=CareerGoals(target_role=role),
        skills=SkillAssessment(levels={}),
    )


def test_all_expected_roles_present():
    assert set(ROLES.keys()) == EXPECTED_ROLES


def test_every_role_requirement_references_real_skill():
    for role in ROLES.values():
        for req in role.requirements:
            assert req.skill_id in SKILLS, (role.role, req.skill_id)


def test_every_role_generates_roadmap_for_fresh_student():
    """A blank semester-1 student must get a valid, non-empty plan for any role."""
    for role in ROLES:
        p = _fresh_student(role)
        rm = generate_roadmap(p)
        assert rm.semesters, role
        result = analyze(p)
        assert result.readiness_pct == 0.0
        assert result.recommendations, role


def test_roadmaps_respect_min_semester_for_all_roles():
    for role in ROLES:
        rm = generate_roadmap(_fresh_student(role))
        for sem in rm.semesters:
            for item in sem.items:
                assert sem.semester >= SKILLS[item.skill_id].min_semester, (
                    role, item.skill_id)


def test_fde_emphasizes_communication_and_genai():
    """FDE's defining traits must show up in its gaps for a code-only student."""
    p = _fresh_student(TargetRole.FDE, sem=5)
    p.skills.levels = {
        "programming": 4, "python": 4, "apis": 4, "sql": 4,
        "git": 3, "linux": 3, "docker": 3,
    }
    result = analyze(p, top_n=10)
    gap_ids = {g.skill_id for g in result.gaps}
    assert "communication" in gap_ids
    assert "genai_apps" in gap_ids


def test_ml_engineer_distinct_from_ai_engineer():
    """ML Engineer weighs MLOps/statistics; AI Engineer weighs transformers/RAG."""
    ml = {r.skill_id for r in ROLES[TargetRole.ML_ENGINEER].requirements}
    ai = {r.skill_id for r in ROLES[TargetRole.AI_ENGINEER].requirements}
    assert "statistics" in ml
    assert "transformers" in ai
    assert ml != ai


def test_data_scientist_stats_heavy():
    ds = ROLES[TargetRole.DATA_SCIENTIST]
    stats = next(r for r in ds.requirements if r.skill_id == "statistics")
    assert stats.target_level == 5
    assert stats.weight >= max(r.weight for r in ds.requirements) - 0.01
