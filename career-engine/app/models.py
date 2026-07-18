"""Domain models for the AI Career Roadmap engine.

These Pydantic models are the contract the whole engine speaks: the student
profile that comes in, the graph the engine reasons over, and the roadmap that
goes out. Keeping them here (with no engine logic) makes the API layer and the
engine layer share one source of truth.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Enumerations
# --------------------------------------------------------------------------- #
class TargetRole(str, Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"
    AI_ENGINEER = "ai_engineer"
    ML_ENGINEER = "ml_engineer"
    DATA_SCIENTIST = "data_scientist"
    DEVOPS = "devops"
    CYBERSECURITY = "cybersecurity"
    ANDROID = "android"
    IOS = "ios"
    QA = "qa"
    PRODUCT_MANAGER = "product_manager"
    FDE = "fde"  # Forward Deployed Engineer (customer-facing AI/product eng)


class LearningStyle(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    INTERACTIVE = "interactive"
    PROJECT = "project"


class Budget(str, Enum):
    FREE_ONLY = "free_only"
    PAID_OK = "paid_ok"


# --------------------------------------------------------------------------- #
# Student profile (matches the brief's profiling section)
# --------------------------------------------------------------------------- #
class Academic(BaseModel):
    college_tier: int = Field(ge=1, le=3, description="1 = top tier, 3 = lower tier")
    university: Optional[str] = None
    branch: Optional[str] = None
    current_semester: int = Field(ge=1, le=8)
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = Field(default=None, ge=0, le=10)
    backlogs: int = Field(default=0, ge=0)
    attendance_restricted: bool = False


class CareerGoals(BaseModel):
    target_role: TargetRole
    campus: bool = True
    off_campus: bool = True
    target_salary_lpa: Optional[int] = Field(default=None, ge=0)
    preferred_companies: list[str] = Field(default_factory=list)
    work_mode: Optional[str] = None  # remote / hybrid / office


class LearningConstraints(BaseModel):
    daily_study_hours: float = Field(default=2.0, ge=0, le=16)
    budget: Budget = Budget.FREE_ONLY
    learning_style: LearningStyle = LearningStyle.PROJECT


# Skill self-assessment: 1-5 for each named skill in the brief.
# Stored as a dict keyed by skill id so the engine can look up any skill
# uniformly; missing skills are treated as level 0 (unknown).
class SkillAssessment(BaseModel):
    levels: dict[str, int] = Field(
        default_factory=dict,
        description="skill_id -> self-rated proficiency 0..5 (0/absent = unknown)",
    )

    def level_of(self, skill_id: str) -> int:
        return int(self.levels.get(skill_id, 0))


class Experience(BaseModel):
    resume_quality: int = Field(default=0, ge=0, le=5)
    github_maturity: int = Field(default=0, ge=0, le=5)
    cp_level: int = Field(default=0, ge=0, le=5, description="competitive programming")
    internships: int = Field(default=0, ge=0)
    projects_completed: int = Field(default=0, ge=0)
    open_source_prs: int = Field(default=0, ge=0)
    hackathons: int = Field(default=0, ge=0)
    certifications: int = Field(default=0, ge=0)


class StudentProfile(BaseModel):
    academic: Academic
    goals: CareerGoals
    constraints: LearningConstraints = Field(default_factory=LearningConstraints)
    skills: SkillAssessment = Field(default_factory=SkillAssessment)
    experience: Experience = Field(default_factory=Experience)


# --------------------------------------------------------------------------- #
# Career graph
# --------------------------------------------------------------------------- #
class SkillNode(BaseModel):
    """A single learnable node in the career graph."""

    id: str
    name: str
    prerequisites: list[str] = Field(
        default_factory=list, description="skill ids that should come first"
    )
    effort_hours: int = Field(
        default=20, ge=1, description="approx hours to reach a working (level ~3) grasp"
    )
    difficulty: int = Field(default=2, ge=1, le=5)
    # Earliest semester this is appropriate to start. The engine never
    # recommends a node before this, enforcing "no advanced topics too early".
    min_semester: int = Field(default=1, ge=1, le=8)


class RoleRequirement(BaseModel):
    """How much a role needs a given skill."""

    skill_id: str
    target_level: int = Field(ge=1, le=5, description="proficiency the role expects")
    weight: float = Field(
        default=1.0, gt=0, description="relative importance for this role"
    )


class RoleGraph(BaseModel):
    role: TargetRole
    name: str
    requirements: list[RoleRequirement]


# --------------------------------------------------------------------------- #
# Engine outputs
# --------------------------------------------------------------------------- #
class SkillGap(BaseModel):
    skill_id: str
    name: str
    current_level: int
    target_level: int
    weight: float
    # Fraction of this requirement still unmet, 0..1.
    gap_fraction: float


class Recommendation(BaseModel):
    skill_id: str
    name: str
    reason: str
    current_level: int
    target_level: int
    effort_hours: int
    # Prereqs the student is still missing before this becomes learnable.
    blocked_by: list[str] = Field(default_factory=list)
    # Readiness points (percentage points) gained by closing this gap.
    readiness_gain: float


class ReadinessResult(BaseModel):
    role: TargetRole
    readiness_pct: float
    gaps: list[SkillGap]
    recommendations: list[Recommendation]
    projected_readiness_pct: float
    projected_from: list[str] = Field(
        default_factory=list, description="skill ids assumed completed in the projection"
    )


class RoadmapItem(BaseModel):
    skill_id: str
    name: str
    effort_hours: int
    prerequisites: list[str]
    rationale: str


class SemesterPlan(BaseModel):
    semester: int
    theme: str
    items: list[RoadmapItem]
    total_effort_hours: int


class Roadmap(BaseModel):
    role: TargetRole
    current_semester: int
    readiness_pct: float
    projected_readiness_pct: float
    semesters: list[SemesterPlan]
