"""Sample student profiles used by the demo and tests."""

from __future__ import annotations

from app.models import (
    Academic,
    CareerGoals,
    Experience,
    LearningConstraints,
    SkillAssessment,
    StudentProfile,
    TargetRole,
)


def backend_sem3_student() -> StudentProfile:
    """A 3rd-semester student aiming Backend with solid basics but gaps in
    infra (Docker/Linux) and databases -- the brief's 42%->58% archetype."""
    return StudentProfile(
        academic=Academic(
            college_tier=2,
            university="Example Institute of Technology",
            branch="CSE",
            current_semester=3,
            graduation_year=2028,
            cgpa=7.8,
            backlogs=0,
        ),
        goals=CareerGoals(
            target_role=TargetRole.BACKEND,
            target_salary_lpa=12,
            preferred_companies=["Product", "Startup"],
            work_mode="hybrid",
        ),
        constraints=LearningConstraints(daily_study_hours=3.0),
        skills=SkillAssessment(
            levels={
                "programming": 4,
                "problem_solving": 3,
                "git": 3,
                "dsa": 3,
                "sql": 2,
                "apis": 2,
                "python": 3,
                "communication": 3,
                "english": 4,
            }
        ),
        experience=Experience(
            resume_quality=2,
            github_maturity=2,
            projects_completed=2,
        ),
    )
