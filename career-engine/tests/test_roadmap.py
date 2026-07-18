"""Tests for semester-aware roadmap generation."""

from __future__ import annotations

from app.graph.skills import SKILLS
from app.models import (
    Academic,
    CareerGoals,
    SkillAssessment,
    StudentProfile,
    TargetRole,
)
from app.roadmap import generate_roadmap
from app.samples import backend_sem3_student


def test_roadmap_starts_at_current_semester():
    p = backend_sem3_student()  # semester 3
    rm = generate_roadmap(p)
    assert rm.current_semester == 3
    assert all(s.semester >= 3 for s in rm.semesters)


def test_no_advanced_topic_before_min_semester():
    """Nothing is scheduled earlier than its min_semester gate."""
    p = backend_sem3_student()
    rm = generate_roadmap(p)
    for sem in rm.semesters:
        for item in sem.items:
            assert sem.semester >= SKILLS[item.skill_id].min_semester


def test_prerequisites_scheduled_before_dependents():
    p = backend_sem3_student()
    rm = generate_roadmap(p)
    placed: dict[str, int] = {}
    for sem in rm.semesters:
        for item in sem.items:
            placed[item.skill_id] = sem.semester
    for sid, when in placed.items():
        for pre in SKILLS[sid].prerequisites:
            if pre in placed:  # if we scheduled the prereq, it must come first
                assert placed[pre] <= when


def test_system_design_lands_in_a_late_semester():
    """A student who needs system design shouldn't see it before semester 5."""
    p = StudentProfile(
        academic=Academic(college_tier=2, current_semester=3),
        goals=CareerGoals(target_role=TargetRole.BACKEND),
        skills=SkillAssessment(
            levels={"programming": 4, "problem_solving": 4, "dsa": 4, "git": 3}
        ),
    )
    rm = generate_roadmap(p)
    for sem in rm.semesters:
        for item in sem.items:
            if item.skill_id == "system_design":
                assert sem.semester >= 5


def test_roadmap_nonempty_for_incomplete_student():
    p = backend_sem3_student()
    rm = generate_roadmap(p)
    assert rm.semesters
    assert any(sem.items for sem in rm.semesters)


def test_ai_engineer_roadmap_generates():
    p = StudentProfile(
        academic=Academic(college_tier=1, current_semester=4),
        goals=CareerGoals(target_role=TargetRole.AI_ENGINEER),
        skills=SkillAssessment(levels={"programming": 4, "python": 4, "dsa": 3}),
    )
    rm = generate_roadmap(p)
    assert rm.role == TargetRole.AI_ENGINEER
    assert rm.semesters
