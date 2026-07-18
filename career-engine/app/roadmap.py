"""Semester-aware roadmap generation.

Takes the gaps the engine found and lays them out across semesters:
  * respects prerequisites (a skill never appears before its prereqs),
  * respects `min_semester` (no advanced topics too early),
  * respects the student's weekly study budget (a semester isn't overloaded).

The result is an ordered plan from the student's current semester to graduation.
"""

from __future__ import annotations

from app.engine import compute_gaps
from app.graph.roles import ROLES
from app.graph.skills import SKILLS
from app.models import (
    Roadmap,
    RoadmapItem,
    SemesterPlan,
    StudentProfile,
)

FINAL_SEMESTER = 8
WEEKS_PER_SEMESTER = 16

# Human-readable themes echoing the brief's semester progression.
SEMESTER_THEMES = {
    1: "Foundations: programming, Git, first projects",
    2: "Core CS: DSA, SQL, GitHub, resume",
    3: "Development stack & intermediate projects",
    4: "Internships, open source, hackathons",
    5: "Advanced projects & system design",
    6: "Interview prep, applications, mock interviews",
    7: "Applications, referrals, offers",
    8: "Offers & negotiation",
}


def _needed_skills_in_order(profile: StudentProfile) -> list[str]:
    """All gap skills plus their (missing) prerequisites, topologically sorted.

    We pull in prerequisites even if the role doesn't list them directly, so the
    plan is actually followable.
    """
    role = ROLES[profile.goals.target_role]
    gaps = {g.skill_id for g in compute_gaps(profile, role)}

    # Expand to include any prerequisite chain the student hasn't mastered.
    needed: set[str] = set()

    def pull(skill_id: str) -> None:
        if skill_id in needed:
            return
        # Skip skills the student already has a working grasp of.
        if profile.skills.level_of(skill_id) >= 3 and skill_id not in gaps:
            return
        needed.add(skill_id)
        for pre in SKILLS[skill_id].prerequisites:
            if profile.skills.level_of(pre) < 3:
                pull(pre)

    for sid in gaps:
        pull(sid)

    # Topological sort (Kahn) over the needed subset so prereqs come first.
    indeg = {s: 0 for s in needed}
    for s in needed:
        for pre in SKILLS[s].prerequisites:
            if pre in needed:
                indeg[s] += 1

    # Stable order: by difficulty then id, so ties are deterministic.
    ready = sorted(
        (s for s in needed if indeg[s] == 0),
        key=lambda s: (SKILLS[s].difficulty, s),
    )
    ordered: list[str] = []
    while ready:
        node = ready.pop(0)
        ordered.append(node)
        for s in needed:
            if node in SKILLS[s].prerequisites and indeg[s] > 0:
                indeg[s] -= 1
                if indeg[s] == 0:
                    ready.append(s)
        ready.sort(key=lambda s: (SKILLS[s].difficulty, s))

    return ordered


def generate_roadmap(profile: StudentProfile) -> Roadmap:
    """Build the full semester-by-semester roadmap for the student."""
    from app.engine import analyze  # local import avoids a cycle

    role = ROLES[profile.goals.target_role]
    ordered = _needed_skills_in_order(profile)

    # Weekly study budget -> hours available per semester.
    hours_per_semester = max(
        1, int(profile.constraints.daily_study_hours * 7 * WEEKS_PER_SEMESTER)
    )

    current_sem = profile.academic.current_semester
    semesters: dict[int, SemesterPlan] = {}
    # Track when each skill lands, so a prereq scheduled this pass blocks its
    # dependents from slipping earlier.
    scheduled_at: dict[str, int] = {}

    remaining = list(ordered)
    sem = current_sem
    while remaining and sem <= FINAL_SEMESTER:
        plan = SemesterPlan(
            semester=sem,
            theme=SEMESTER_THEMES.get(sem, "Continued growth"),
            items=[],
            total_effort_hours=0,
        )
        budget = hours_per_semester
        progressed = True
        # Multiple passes so that unblocking a prereq lets a dependent in too.
        while progressed:
            progressed = False
            for sid in list(remaining):
                node = SKILLS[sid]
                # Gate: not before its earliest appropriate semester.
                if sem < node.min_semester:
                    continue
                # Gate: all prereqs must already be scheduled (or pre-known).
                unmet = [
                    p
                    for p in node.prerequisites
                    if profile.skills.level_of(p) < 3 and p not in scheduled_at
                ]
                if unmet:
                    continue
                # Gate: fits remaining budget (but always allow at least one
                # item per semester so a heavy skill can't stall forever).
                if node.effort_hours > budget and plan.items:
                    continue

                rationale = _rationale(sid, role)
                plan.items.append(
                    RoadmapItem(
                        skill_id=sid,
                        name=node.name,
                        effort_hours=node.effort_hours,
                        prerequisites=node.prerequisites,
                        rationale=rationale,
                    )
                )
                plan.total_effort_hours += node.effort_hours
                budget -= node.effort_hours
                scheduled_at[sid] = sem
                remaining.remove(sid)
                progressed = True

        if plan.items:
            semesters[sem] = plan
        sem += 1

    result = analyze(profile)
    return Roadmap(
        role=role.role,
        current_semester=current_sem,
        readiness_pct=result.readiness_pct,
        projected_readiness_pct=result.projected_readiness_pct,
        semesters=[semesters[k] for k in sorted(semesters)],
    )


def _rationale(skill_id: str, role) -> str:
    """One-line why-this-now for a roadmap item."""
    req = next((r for r in role.requirements if r.skill_id == skill_id), None)
    if req is not None:
        return (
            f"Directly required for {role.name} (target level {req.target_level}, "
            f"weight {req.weight})."
        )
    return "Prerequisite that unlocks role-required skills."
