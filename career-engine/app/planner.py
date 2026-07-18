"""Dynamic weekly planner.

Takes a semester's roadmap items and slices them into concrete weekly plans
sized by the student's daily study time. Each week carries learning topics,
estimated hours, practice, a project/milestone cue, revision, and (from a given
point) interview prep -- matching the brief's weekly-plan requirement.

Adaptivity: `generate_weekly_plan` accepts the set of already-completed skills,
so re-running after progress naturally produces a shorter, forward-looking plan
(the "adapt if the student falls behind or finishes early" requirement).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models import StudentProfile
from app.resources import Resource, resources_for
from app.roadmap import generate_roadmap

HOURS_PER_WEEK_DEFAULT = 14.0
# Interview prep starts appearing in the plan from this semester on.
INTERVIEW_PREP_FROM_SEMESTER = 6


class WeeklyPlan(BaseModel):
    week: int
    semester: int
    focus_skill_id: str
    focus_skill: str
    topics: str
    estimated_hours: float
    practice: str
    project_or_milestone: str
    revision: str
    interview_prep: str | None = None
    resources: list[Resource] = Field(default_factory=list)


def _weeks_for_item(effort_hours: int, hours_per_week: float) -> int:
    """How many weeks a skill needs at the student's pace (at least 1)."""
    return max(1, round(effort_hours / hours_per_week))


def generate_weekly_plan(
    profile: StudentProfile,
    completed_skill_ids: set[str] | None = None,
    max_weeks: int = 16,
) -> list[WeeklyPlan]:
    """Weekly plan for the student's *current* semester, honoring progress.

    Only the current semester is expanded into weeks (that's the actionable
    horizon); completed skills are skipped so the plan always looks forward.
    """
    completed = completed_skill_ids or set()
    hours_per_day = profile.constraints.daily_study_hours or 2.0
    hours_per_week = round(hours_per_day * 7, 1) or HOURS_PER_WEEK_DEFAULT

    roadmap = generate_roadmap(profile)
    current = next(
        (s for s in roadmap.semesters if s.semester == profile.academic.current_semester),
        None,
    )
    if current is None:
        return []

    plans: list[WeeklyPlan] = []
    week = 1
    for item in current.items:
        if item.skill_id in completed:
            continue
        span = _weeks_for_item(item.effort_hours, hours_per_week)
        per_week_hours = round(item.effort_hours / span, 1)
        res = resources_for(
            item.skill_id,
            budget=profile.constraints.budget,
            style=profile.constraints.learning_style,
        )
        for part in range(1, span + 1):
            if week > max_weeks:
                return plans
            multi = f" (part {part}/{span})" if span > 1 else ""
            interview = None
            if current.semester >= INTERVIEW_PREP_FROM_SEMESTER:
                interview = f"Solve 3-5 interview questions on {item.name}."
            plans.append(
                WeeklyPlan(
                    week=week,
                    semester=current.semester,
                    focus_skill_id=item.skill_id,
                    focus_skill=item.name,
                    topics=f"{item.name}{multi}: core concepts and hands-on.",
                    estimated_hours=per_week_hours,
                    practice=f"Daily practice on {item.name}; small exercises.",
                    project_or_milestone=(
                        f"Apply {item.name} in a mini-project this week."
                        if part == span
                        else "Keep building toward the project."
                    ),
                    revision="Revise last week's topics (~1h) + spaced repetition.",
                    interview_prep=interview,
                    resources=res if part == 1 else [],  # list resources once, up front
                )
            )
            week += 1

    return plans
