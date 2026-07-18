"""Role graphs: what each target job actually requires, as weighted skill
targets. The engine measures a student against these.

Weights encode relative importance (DSA matters more than accessibility for a
backend role, etc.). Target levels are the 1-5 proficiency a fresher is
realistically expected to show for that role.
"""

from __future__ import annotations

from app.graph.skills import SKILLS
from app.models import RoleGraph, RoleRequirement, TargetRole


def _req(skill_id: str, level: int, weight: float = 1.0) -> RoleRequirement:
    return RoleRequirement(skill_id=skill_id, target_level=level, weight=weight)


_ROLES: list[RoleGraph] = [
    RoleGraph(
        role=TargetRole.BACKEND,
        name="Backend Engineer",
        requirements=[
            _req("programming", 4, 2.0),
            _req("dsa", 4, 2.0),
            _req("apis", 4, 2.0),
            _req("sql", 4, 1.8),
            _req("redis", 3, 1.0),
            _req("docker", 3, 1.2),
            _req("linux", 3, 1.0),
            _req("testing", 3, 1.0),
            _req("cicd", 3, 0.9),
            _req("cloud", 3, 1.0),
            _req("system_design", 3, 1.5),
            _req("git", 3, 0.8),
        ],
    ),
    RoleGraph(
        role=TargetRole.FRONTEND,
        name="Frontend Engineer",
        requirements=[
            _req("programming", 3, 1.2),
            _req("html_css", 4, 1.8),
            _req("javascript", 4, 2.0),
            _req("typescript", 3, 1.5),
            _req("react", 4, 2.0),
            _req("nextjs", 3, 1.3),
            _req("web_perf", 3, 1.0),
            _req("accessibility", 3, 0.8),
            _req("testing", 3, 1.0),
            _req("dsa", 3, 1.2),
            _req("git", 3, 0.8),
        ],
    ),
    RoleGraph(
        role=TargetRole.AI_ENGINEER,
        name="AI Engineer",
        requirements=[
            _req("python", 4, 2.0),
            _req("dsa", 3, 1.2),
            _req("ml", 4, 2.0),
            _req("dl", 4, 1.8),
            _req("pytorch", 3, 1.5),
            _req("transformers", 3, 1.6),
            _req("genai_apps", 4, 1.6),
            _req("rag", 3, 1.4),
            _req("mlops", 3, 1.2),
            _req("apis", 3, 1.0),
            _req("docker", 3, 0.9),
            _req("git", 3, 0.7),
        ],
    ),
    RoleGraph(
        role=TargetRole.FULLSTACK,
        name="Full Stack Engineer",
        requirements=[
            _req("programming", 4, 1.8),
            _req("dsa", 3, 1.5),
            _req("javascript", 4, 1.8),
            _req("html_css", 3, 1.2),
            _req("react", 4, 1.8),
            _req("typescript", 3, 1.2),
            _req("apis", 4, 1.8),
            _req("sql", 4, 1.5),
            _req("docker", 3, 1.0),
            _req("testing", 3, 1.0),
            _req("cicd", 3, 0.8),
            _req("cloud", 3, 0.9),
            _req("system_design", 3, 1.2),
            _req("git", 3, 0.8),
        ],
    ),
    RoleGraph(
        role=TargetRole.ML_ENGINEER,
        name="ML Engineer",
        requirements=[
            # ML Engineer = models in production: stronger engineering/MLOps
            # emphasis than AI Engineer, plus statistics rigor.
            _req("python", 4, 2.0),
            _req("statistics", 4, 1.6),
            _req("dsa", 4, 1.5),
            _req("pandas", 4, 1.2),
            _req("ml", 4, 2.0),
            _req("dl", 4, 1.6),
            _req("pytorch", 4, 1.5),
            _req("sql", 3, 1.0),
            _req("docker", 3, 1.2),
            _req("cloud", 3, 1.2),
            _req("mlops", 4, 1.8),
            _req("apis", 3, 1.0),
            _req("git", 3, 0.7),
        ],
    ),
    RoleGraph(
        role=TargetRole.DATA_SCIENTIST,
        name="Data Scientist",
        requirements=[
            _req("python", 4, 1.8),
            _req("statistics", 5, 2.0),
            _req("pandas", 4, 1.8),
            _req("data_viz", 4, 1.4),
            _req("sql", 4, 1.8),
            _req("ml", 4, 1.6),
            _req("dl", 3, 1.0),
            _req("communication", 4, 1.2),
            _req("git", 3, 0.6),
        ],
    ),
    RoleGraph(
        role=TargetRole.DEVOPS,
        name="DevOps Engineer",
        requirements=[
            _req("linux", 4, 2.0),
            _req("programming", 3, 1.2),
            _req("python", 3, 1.0),
            _req("git", 4, 1.2),
            _req("docker", 4, 2.0),
            _req("kubernetes", 4, 1.8),
            _req("cicd", 4, 1.8),
            _req("cloud", 4, 1.8),
            _req("terraform", 3, 1.4),
            _req("monitoring", 3, 1.4),
            _req("sql", 3, 0.8),
            _req("system_design", 3, 1.0),
        ],
    ),
    RoleGraph(
        role=TargetRole.ANDROID,
        name="Android Engineer",
        requirements=[
            _req("programming", 4, 1.6),
            _req("dsa", 3, 1.4),
            _req("kotlin", 4, 2.0),
            _req("android_sdk", 4, 2.0),
            _req("apis", 3, 1.2),
            _req("sql", 3, 1.0),
            _req("testing", 3, 1.0),
            _req("git", 3, 0.8),
        ],
    ),
    RoleGraph(
        role=TargetRole.IOS,
        name="iOS Engineer",
        requirements=[
            _req("programming", 4, 1.6),
            _req("dsa", 3, 1.4),
            _req("swift", 4, 2.0),
            _req("ios_sdk", 4, 2.0),
            _req("apis", 3, 1.2),
            _req("sql", 3, 1.0),
            _req("testing", 3, 1.0),
            _req("git", 3, 0.8),
        ],
    ),
    RoleGraph(
        role=TargetRole.FDE,
        name="Forward Deployed Engineer",
        requirements=[
            # FDE = ship working AI solutions inside customer environments:
            # breadth + speed + LLM-app skills + unusually high communication.
            _req("programming", 4, 1.8),
            _req("python", 4, 1.6),
            _req("apis", 4, 1.8),
            _req("sql", 4, 1.5),
            _req("genai_apps", 4, 2.0),
            _req("rag", 3, 1.4),
            _req("react", 3, 1.2),
            _req("docker", 3, 1.0),
            _req("cloud", 3, 1.0),
            _req("linux", 3, 0.9),
            _req("communication", 5, 2.0),
            _req("english", 4, 1.0),
            _req("git", 3, 0.7),
        ],
    ),
]

ROLES: dict[TargetRole, RoleGraph] = {r.role: r for r in _ROLES}


def _validate_roles() -> None:
    """Every role requirement must reference a real skill node."""
    for role in _ROLES:
        for req in role.requirements:
            if req.skill_id not in SKILLS:
                raise ValueError(
                    f"role '{role.role}' requires unknown skill '{req.skill_id}'"
                )


_validate_roles()
