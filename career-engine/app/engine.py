"""The career engine: deterministic, LLM-free reasoning over the career graph.

Given a StudentProfile it computes:
  * readiness %      -- weighted coverage of the target role's requirements
  * skill gaps       -- where the student falls short, and by how much
  * recommendations  -- highest-ROI next skills, with prerequisites resolved
  * projected %      -- readiness after completing the top recommendations

All pure functions; no I/O, no globals mutated. This is the piece that makes
the product "decide what THIS student should learn next" rather than showing a
static list.
"""

from __future__ import annotations

from app.graph.roles import ROLES
from app.graph.skills import SKILLS
from app.models import (
    Recommendation,
    ReadinessResult,
    RoleGraph,
    SkillGap,
    StudentProfile,
)

# A prerequisite counts as "satisfied" once the student self-rates at or above
# this level -- a working grasp, not mastery.
PREREQ_SATISFIED_LEVEL = 3


def _coverage(current: int, target: int) -> float:
    """Fraction of a single requirement met, clamped to [0, 1]."""
    if target <= 0:
        return 1.0
    return min(max(current, 0), target) / target


def compute_readiness_pct(profile: StudentProfile, role: RoleGraph) -> float:
    """Weighted coverage of the role's requirements, as a 0-100 percentage."""
    total_weight = sum(r.weight for r in role.requirements)
    if total_weight == 0:
        return 0.0
    earned = 0.0
    for req in role.requirements:
        current = profile.skills.level_of(req.skill_id)
        earned += req.weight * _coverage(current, req.target_level)
    return round(100.0 * earned / total_weight, 1)


def compute_gaps(profile: StudentProfile, role: RoleGraph) -> list[SkillGap]:
    """Every unmet (or partially met) requirement, largest gap first."""
    gaps: list[SkillGap] = []
    for req in role.requirements:
        current = profile.skills.level_of(req.skill_id)
        gap_fraction = 1.0 - _coverage(current, req.target_level)
        if gap_fraction <= 0:
            continue
        node = SKILLS[req.skill_id]
        gaps.append(
            SkillGap(
                skill_id=req.skill_id,
                name=node.name,
                current_level=current,
                target_level=req.target_level,
                weight=req.weight,
                gap_fraction=round(gap_fraction, 3),
            )
        )
    # Largest weighted gap first.
    gaps.sort(key=lambda g: g.weight * g.gap_fraction, reverse=True)
    return gaps


def _readiness_gain(gap: SkillGap, total_weight: float) -> float:
    """Percentage points gained by fully closing this gap."""
    return round(100.0 * (gap.weight * gap.gap_fraction) / total_weight, 2)


def _missing_prereqs(profile: StudentProfile, skill_id: str) -> list[str]:
    """Prerequisite skill ids the student hasn't reached a working grasp of."""
    node = SKILLS[skill_id]
    return [
        pre
        for pre in node.prerequisites
        if profile.skills.level_of(pre) < PREREQ_SATISFIED_LEVEL
    ]


def recommend(
    profile: StudentProfile, role: RoleGraph, top_n: int = 5
) -> list[Recommendation]:
    """Rank next skills by ROI = readiness gained per hour of effort.

    A skill that is still blocked by missing prerequisites is penalised (its
    prerequisites are the real next step), so foundational unblocking naturally
    rises to the top -- e.g. you can't be told to do System Design before APIs.
    """
    total_weight = sum(r.weight for r in role.requirements)
    gaps = compute_gaps(profile, role)

    scored: list[tuple[float, Recommendation]] = []
    for gap in gaps:
        node = SKILLS[gap.skill_id]
        gain = _readiness_gain(gap, total_weight)
        blocked_by = _missing_prereqs(profile, gap.skill_id)

        # ROI per hour; blocked skills are discounted so their prerequisites,
        # which are themselves gaps, outrank them.
        roi = gain / node.effort_hours
        if blocked_by:
            roi *= 0.35

        if blocked_by:
            reason = (
                f"High-value for the role, but finish {', '.join(blocked_by)} first."
            )
        else:
            reason = (
                f"Closes a {gap.current_level}->{gap.target_level} gap on a "
                f"weight-{gap.weight} requirement (+{gain} pts)."
            )

        scored.append(
            (
                roi,
                Recommendation(
                    skill_id=gap.skill_id,
                    name=node.name,
                    reason=reason,
                    current_level=gap.current_level,
                    target_level=gap.target_level,
                    effort_hours=node.effort_hours,
                    blocked_by=blocked_by,
                    readiness_gain=gain,
                ),
            )
        )

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [rec for _roi, rec in scored[:top_n]]


def project_after(
    profile: StudentProfile, role: RoleGraph, skill_ids: list[str]
) -> float:
    """Readiness % assuming the given skills are raised to their target level.

    This produces the brief's headline: 42% now, +Docker/Linux/PostgreSQL -> 58%.
    """
    targets = {r.skill_id: r.target_level for r in role.requirements}
    boosted = dict(profile.skills.levels)
    for sid in skill_ids:
        if sid in targets:
            boosted[sid] = max(boosted.get(sid, 0), targets[sid])
    boosted_profile = profile.model_copy(deep=True)
    boosted_profile.skills.levels = boosted
    return compute_readiness_pct(boosted_profile, role)


def analyze(profile: StudentProfile, top_n: int = 5) -> ReadinessResult:
    """Full readiness analysis for the student's target role."""
    role = ROLES[profile.goals.target_role]
    readiness = compute_readiness_pct(profile, role)
    gaps = compute_gaps(profile, role)
    recs = recommend(profile, role, top_n=top_n)

    # Project over the recommendations that are actionable now (not blocked),
    # since those are what the student would realistically complete next.
    actionable = [r.skill_id for r in recs if not r.blocked_by]
    projected = project_after(profile, role, actionable)

    return ReadinessResult(
        role=role.role,
        readiness_pct=readiness,
        gaps=gaps,
        recommendations=recs,
        projected_readiness_pct=projected,
        projected_from=actionable,
    )
