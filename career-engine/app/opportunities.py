"""Opportunity engine: match real-world opportunities to the student's profile.

The brief: "Only show relevant opportunities." Each opportunity declares
eligibility (semester window, roles it serves, skill floors, CP floor) and the
matcher scores it against the profile. Output is ranked: eligible-now first
(best fit on top), then near-misses with exactly what's missing -- so the
student sees both what to apply to and what to unlock next.

Like resources.py this is hand-curated data over deterministic logic; a later
milestone can hydrate it from live sources without changing the matcher.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from app.graph.skills import SKILLS
from app.models import StudentProfile, TargetRole


class OpportunityKind(str, Enum):
    INTERNSHIP = "internship"
    OPEN_SOURCE = "open_source"
    HACKATHON = "hackathon"
    CONTEST = "contest"
    FELLOWSHIP = "fellowship"
    SCHOLARSHIP = "scholarship"
    AMBASSADOR = "ambassador"
    RESEARCH = "research"


class Opportunity(BaseModel):
    id: str
    name: str
    kind: OpportunityKind
    url: str
    description: str
    # Semester window in which this is worth pursuing.
    min_semester: int = Field(default=1, ge=1, le=8)
    max_semester: int = Field(default=8, ge=1, le=8)
    # Roles this serves. Empty list = relevant to every role.
    roles: list[TargetRole] = Field(default_factory=list)
    # Skill floors: skill_id -> minimum self-rated level required to be a
    # credible applicant. Every id must exist in the skill graph.
    required_skills: dict[str, int] = Field(default_factory=dict)
    # Minimum competitive-programming level (Experience.cp_level), if any.
    min_cp_level: int = Field(default=0, ge=0, le=5)


_R = TargetRole

_OPPORTUNITIES: list[Opportunity] = [
    Opportunity(
        id="gsoc", name="Google Summer of Code", kind=OpportunityKind.OPEN_SOURCE,
        url="https://summerofcode.withgoogle.com/",
        description="Paid open-source program with mentoring orgs.",
        min_semester=3, max_semester=7,
        required_skills={"programming": 3, "git": 3},
    ),
    Opportunity(
        id="mlh", name="MLH Hackathons", kind=OpportunityKind.HACKATHON,
        url="https://mlh.io/",
        description="Global student hackathon league; team up and ship.",
        min_semester=2, max_semester=8,
        required_skills={"programming": 2},
    ),
    Opportunity(
        id="outreachy", name="Outreachy", kind=OpportunityKind.OPEN_SOURCE,
        url="https://www.outreachy.org/",
        description="Paid OSS internships for underrepresented groups.",
        min_semester=3, max_semester=8,
        required_skills={"programming": 3, "git": 3},
    ),
    Opportunity(
        id="icpc", name="ICPC", kind=OpportunityKind.CONTEST,
        url="https://icpc.global/",
        description="The premier team programming contest.",
        min_semester=2, max_semester=6,
        required_skills={"dsa": 3}, min_cp_level=2,
    ),
    Opportunity(
        id="sih", name="Smart India Hackathon", kind=OpportunityKind.HACKATHON,
        url="https://sih.gov.in/",
        description="National-scale problem-statement hackathon.",
        min_semester=3, max_semester=8,
        required_skills={"programming": 3},
    ),
    Opportunity(
        id="google_step", name="Google STEP Internship",
        kind=OpportunityKind.INTERNSHIP,
        url="https://buildyourfuture.withgoogle.com/programs/step",
        description="Early-career internship for 1st/2nd-year students.",
        min_semester=2, max_semester=4,
        required_skills={"programming": 3, "dsa": 3},
    ),
    Opportunity(
        id="mitacs", name="MITACS Globalink", kind=OpportunityKind.RESEARCH,
        url="https://www.mitacs.ca/our-programs/globalink-research-internship-students/",
        description="Funded research internship in Canada (3rd-year focus).",
        min_semester=4, max_semester=6,
        required_skills={"programming": 3},
    ),
    Opportunity(
        id="gssoc", name="GirlScript Summer of Code",
        kind=OpportunityKind.OPEN_SOURCE,
        url="https://gssoc.girlscript.tech/",
        description="Beginner-friendly OSS program; good first-PR ground.",
        min_semester=2, max_semester=6,
        required_skills={"programming": 2, "git": 2},
    ),
    Opportunity(
        id="kaggle", name="Kaggle Competitions", kind=OpportunityKind.CONTEST,
        url="https://www.kaggle.com/competitions",
        description="ML competitions; portfolio-grade results possible.",
        min_semester=4, max_semester=8,
        roles=[_R.AI_ENGINEER, _R.ML_ENGINEER, _R.DATA_SCIENTIST],
        required_skills={"python": 3, "ml": 3},
    ),
    Opportunity(
        id="codeforces_rounds", name="Codeforces Rounds",
        kind=OpportunityKind.CONTEST,
        url="https://codeforces.com/",
        description="Regular rated contests; build a CP rating.",
        min_semester=2, max_semester=6,
        required_skills={"dsa": 2},
    ),
    Opportunity(
        id="github_campus_expert", name="GitHub Campus Expert",
        kind=OpportunityKind.AMBASSADOR,
        url="https://education.github.com/experts",
        description="Campus community-leadership program by GitHub.",
        min_semester=3, max_semester=7,
        required_skills={"git": 3, "communication": 3},
    ),
    Opportunity(
        id="grace_hopper", name="Grace Hopper Celebration Scholarship",
        kind=OpportunityKind.SCHOLARSHIP,
        url="https://ghc.anitab.org/",
        description="Scholarship to attend the largest women-in-tech conference.",
        min_semester=2, max_semester=8,
    ),
    Opportunity(
        id="lfx", name="LFX Mentorship", kind=OpportunityKind.OPEN_SOURCE,
        url="https://lfx.linuxfoundation.org/tools/mentorship/",
        description="Linux Foundation paid OSS mentorships (cloud-native heavy).",
        min_semester=4, max_semester=8,
        roles=[_R.BACKEND, _R.DEVOPS, _R.FULLSTACK, _R.FDE],
        required_skills={"programming": 3, "git": 3, "linux": 3},
    ),
]

OPPORTUNITIES: dict[str, Opportunity] = {o.id: o for o in _OPPORTUNITIES}


def _validate_catalog() -> None:
    """Fail fast if catalog references unknown skills or bad windows."""
    for o in _OPPORTUNITIES:
        for sid in o.required_skills:
            if sid not in SKILLS:
                raise ValueError(f"opportunity '{o.id}' requires unknown skill '{sid}'")
        if o.min_semester > o.max_semester:
            raise ValueError(f"opportunity '{o.id}' has an empty semester window")


_validate_catalog()


class OpportunityMatch(BaseModel):
    opportunity: Opportunity
    eligible: bool
    # 0..1: how well the student clears the requirements (1 = comfortably).
    fit_score: float
    reasons: list[str]
    missing: list[str] = Field(
        default_factory=list, description="what to fix to become eligible"
    )


def match_opportunities(profile: StudentProfile) -> list[OpportunityMatch]:
    """Rank the catalog for this student: eligible (best fit first), then
    near-misses with what's missing. Out-of-window or wrong-role items are
    dropped entirely -- 'only show relevant opportunities'."""
    sem = profile.academic.current_semester
    role = profile.goals.target_role
    matches: list[OpportunityMatch] = []

    for opp in _OPPORTUNITIES:
        # Hard filters: not in the semester window, or role-specific and not
        # the student's role -> not shown at all.
        if not (opp.min_semester <= sem <= opp.max_semester):
            continue
        if opp.roles and role not in opp.roles:
            continue

        reasons = [f"Open in your semester window ({opp.min_semester}-{opp.max_semester})."]
        if opp.roles:
            reasons.append(f"Targets your role ({role.value}).")

        missing: list[str] = []
        scores: list[float] = []
        for sid, floor in opp.required_skills.items():
            level = profile.skills.level_of(sid)
            scores.append(min(level / floor, 1.0))
            if level < floor:
                missing.append(f"{SKILLS[sid].name} needs level {floor} (you: {level})")
            else:
                reasons.append(f"{SKILLS[sid].name} requirement met ({level}/{floor}).")
        if opp.min_cp_level:
            cp = profile.experience.cp_level
            scores.append(min(cp / opp.min_cp_level, 1.0))
            if cp < opp.min_cp_level:
                missing.append(
                    f"CP level needs {opp.min_cp_level} (you: {cp})"
                )

        fit = round(sum(scores) / len(scores), 2) if scores else 1.0
        matches.append(
            OpportunityMatch(
                opportunity=opp,
                eligible=not missing,
                fit_score=fit,
                reasons=reasons,
                missing=missing,
            )
        )

    # Eligible first, best fit on top; near-misses ranked by how close they are.
    matches.sort(key=lambda m: (not m.eligible, -m.fit_score, m.opportunity.id))
    return matches
