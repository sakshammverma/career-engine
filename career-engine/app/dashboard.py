"""The recomputed student view.

This is what "continuously updated" means in practice: one function that, given a
persisted student, re-derives readiness, roadmap, milestones and the weekly plan
from the current profile state. Call it after any progress change and the whole
picture is fresh -- no cached/stale roadmap.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.engine import analyze
from app.milestones import MilestoneProgress, milestone_progress
from app.models import ReadinessResult, Roadmap, StudentProfile
from app.opportunities import OpportunityMatch, match_opportunities
from app.planner import WeeklyPlan, generate_weekly_plan
from app.roadmap import generate_roadmap


class Dashboard(BaseModel):
    student_id: str
    profile: StudentProfile
    readiness: ReadinessResult
    roadmap: Roadmap
    milestones: MilestoneProgress
    weekly_plan: list[WeeklyPlan]
    opportunities: list[OpportunityMatch]


def build_dashboard(
    student_id: str,
    profile: StudentProfile,
    completed_milestones: set[str],
) -> Dashboard:
    """Recompute the full student view from current state."""
    sem = profile.academic.current_semester
    # Skills the student already has a working grasp of count as "completed"
    # for planning, so the weekly plan looks forward.
    completed_skills = {sid for sid, lv in profile.skills.levels.items() if lv >= 3}
    return Dashboard(
        student_id=student_id,
        profile=profile,
        readiness=analyze(profile),
        roadmap=generate_roadmap(profile),
        milestones=milestone_progress(completed_milestones, sem),
        weekly_plan=generate_weekly_plan(profile, completed_skill_ids=completed_skills),
        opportunities=match_opportunities(profile),
    )
