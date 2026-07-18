"""Milestone tracking: the brief's checklist of concrete career achievements.

Milestones are separate from skills. A skill ("Docker", level 0-5) measures
knowledge; a milestone ("first internship", done/not-done) measures a real-world
achievement. Both feed the sense of progress, but they're tracked differently.

Each milestone carries the earliest semester it's typically relevant, so the
completion view can highlight what's due now versus later.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class MilestoneCategory(str, Enum):
    PROFILE = "profile"
    CODING = "coding"
    EXPERIENCE = "experience"
    INTERVIEW = "interview"


class MilestoneDef(BaseModel):
    id: str
    name: str
    category: MilestoneCategory
    relevant_from_semester: int = Field(ge=1, le=8, default=1)


# The canonical checklist from the brief. Ordered by when a student typically
# reaches them.
_MILESTONES: list[MilestoneDef] = [
    # Profile / presence
    MilestoneDef(id="github_created", name="GitHub created",
                 category=MilestoneCategory.PROFILE, relevant_from_semester=1),
    MilestoneDef(id="resume_ready", name="Resume ready",
                 category=MilestoneCategory.PROFILE, relevant_from_semester=2),
    MilestoneDef(id="portfolio_built", name="Portfolio built",
                 category=MilestoneCategory.PROFILE, relevant_from_semester=3),
    MilestoneDef(id="first_project", name="First project shipped",
                 category=MilestoneCategory.PROFILE, relevant_from_semester=1),
    # Coding practice
    MilestoneDef(id="leetcode_100", name="100 LeetCode solved",
                 category=MilestoneCategory.CODING, relevant_from_semester=2),
    MilestoneDef(id="leetcode_200", name="200 LeetCode solved",
                 category=MilestoneCategory.CODING, relevant_from_semester=3),
    MilestoneDef(id="leetcode_500", name="500 LeetCode solved",
                 category=MilestoneCategory.CODING, relevant_from_semester=4),
    MilestoneDef(id="codeforces_pupil", name="Codeforces Pupil",
                 category=MilestoneCategory.CODING, relevant_from_semester=3),
    MilestoneDef(id="codeforces_specialist", name="Codeforces Specialist",
                 category=MilestoneCategory.CODING, relevant_from_semester=5),
    # Real-world experience
    MilestoneDef(id="oss_pr", name="Open-source PR merged",
                 category=MilestoneCategory.EXPERIENCE, relevant_from_semester=4),
    MilestoneDef(id="hackathon", name="Hackathon participated",
                 category=MilestoneCategory.EXPERIENCE, relevant_from_semester=3),
    MilestoneDef(id="internship", name="Internship secured",
                 category=MilestoneCategory.EXPERIENCE, relevant_from_semester=4),
    # Interview funnel
    MilestoneDef(id="mock_interview", name="Mock interview done",
                 category=MilestoneCategory.INTERVIEW, relevant_from_semester=5),
    MilestoneDef(id="applications_sent", name="Applications sent",
                 category=MilestoneCategory.INTERVIEW, relevant_from_semester=6),
    MilestoneDef(id="interview_call", name="Interview call received",
                 category=MilestoneCategory.INTERVIEW, relevant_from_semester=6),
]

MILESTONES: dict[str, MilestoneDef] = {m.id: m for m in _MILESTONES}


class MilestoneStatus(BaseModel):
    id: str
    name: str
    category: MilestoneCategory
    relevant_from_semester: int
    completed: bool
    # True when the student is at/past the semester where this becomes relevant.
    due_now: bool


class MilestoneProgress(BaseModel):
    completion_pct: float
    completed_count: int
    total_count: int
    # Relevant-now completion: how much of what's currently due is done.
    due_completion_pct: float
    statuses: list[MilestoneStatus]


def milestone_progress(
    completed_ids: set[str], current_semester: int
) -> MilestoneProgress:
    """Build the full milestone view for a student.

    `completed_ids` is the set of milestone ids the student has marked done.
    Unknown ids are ignored so stale data can't corrupt the percentage.
    """
    statuses: list[MilestoneStatus] = []
    completed = 0
    due_total = 0
    due_done = 0

    for m in _MILESTONES:
        is_done = m.id in completed_ids
        is_due = current_semester >= m.relevant_from_semester
        if is_done:
            completed += 1
        if is_due:
            due_total += 1
            if is_done:
                due_done += 1
        statuses.append(
            MilestoneStatus(
                id=m.id,
                name=m.name,
                category=m.category,
                relevant_from_semester=m.relevant_from_semester,
                completed=is_done,
                due_now=is_due,
            )
        )

    total = len(_MILESTONES)
    return MilestoneProgress(
        completion_pct=round(100.0 * completed / total, 1) if total else 0.0,
        completed_count=completed,
        total_count=total,
        due_completion_pct=round(100.0 * due_done / due_total, 1) if due_total else 0.0,
        statuses=statuses,
    )
