"""The skill graph: every learnable node with prerequisites, effort, difficulty
and the earliest semester it should be introduced.

`min_semester` is what enforces the brief's rule "never recommend advanced
topics too early" -- system design and advanced ML are gated to later semesters
even if a role technically needs them.
"""

from __future__ import annotations

from app.models import SkillNode

# Ordered roughly foundational -> advanced. Every id referenced as a
# prerequisite or by a role must exist here (validated at import time below).
_SKILLS: list[SkillNode] = [
    # --- Foundations -------------------------------------------------------
    SkillNode(id="programming", name="Programming Fundamentals", prerequisites=[],
              effort_hours=60, difficulty=2, min_semester=1),
    SkillNode(id="problem_solving", name="Problem Solving", prerequisites=["programming"],
              effort_hours=40, difficulty=2, min_semester=1),
    SkillNode(id="git", name="Git & Version Control", prerequisites=["programming"],
              effort_hours=15, difficulty=1, min_semester=1),
    SkillNode(id="linux", name="Linux & Shell", prerequisites=["programming"],
              effort_hours=25, difficulty=2, min_semester=2),

    # --- Languages ---------------------------------------------------------
    SkillNode(id="python", name="Python", prerequisites=["programming"],
              effort_hours=40, difficulty=2, min_semester=1),
    SkillNode(id="java", name="Java", prerequisites=["programming"],
              effort_hours=50, difficulty=3, min_semester=2),
    SkillNode(id="cpp", name="C++", prerequisites=["programming"],
              effort_hours=50, difficulty=3, min_semester=1),
    SkillNode(id="javascript", name="JavaScript", prerequisites=["programming"],
              effort_hours=40, difficulty=2, min_semester=2),
    SkillNode(id="typescript", name="TypeScript", prerequisites=["javascript"],
              effort_hours=25, difficulty=2, min_semester=3),

    # --- CS core -----------------------------------------------------------
    SkillNode(id="dsa", name="Data Structures & Algorithms",
              prerequisites=["problem_solving"], effort_hours=120, difficulty=4,
              min_semester=2),
    SkillNode(id="sql", name="SQL & Databases", prerequisites=["programming"],
              effort_hours=30, difficulty=2, min_semester=2),
    SkillNode(id="cp", name="Competitive Programming", prerequisites=["dsa"],
              effort_hours=100, difficulty=5, min_semester=3),

    # --- Web / Frontend ----------------------------------------------------
    SkillNode(id="html_css", name="HTML & CSS", prerequisites=["programming"],
              effort_hours=30, difficulty=1, min_semester=2),
    SkillNode(id="react", name="React", prerequisites=["javascript", "html_css"],
              effort_hours=50, difficulty=3, min_semester=3),
    SkillNode(id="nextjs", name="Next.js", prerequisites=["react", "typescript"],
              effort_hours=40, difficulty=3, min_semester=4),
    SkillNode(id="web_perf", name="Web Performance", prerequisites=["react"],
              effort_hours=25, difficulty=3, min_semester=5),
    SkillNode(id="accessibility", name="Accessibility", prerequisites=["html_css"],
              effort_hours=15, difficulty=2, min_semester=4),

    # --- Backend -----------------------------------------------------------
    SkillNode(id="apis", name="APIs (REST/HTTP)", prerequisites=["programming", "sql"],
              effort_hours=35, difficulty=3, min_semester=3),
    SkillNode(id="redis", name="Redis & Caching", prerequisites=["apis"],
              effort_hours=20, difficulty=3, min_semester=4),
    SkillNode(id="docker", name="Docker", prerequisites=["linux"],
              effort_hours=25, difficulty=3, min_semester=4),
    SkillNode(id="testing", name="Testing", prerequisites=["programming"],
              effort_hours=25, difficulty=2, min_semester=3),
    SkillNode(id="cicd", name="CI/CD", prerequisites=["git", "testing"],
              effort_hours=20, difficulty=3, min_semester=4),
    SkillNode(id="cloud", name="Cloud (AWS/GCP)", prerequisites=["linux", "apis"],
              effort_hours=40, difficulty=4, min_semester=5),
    SkillNode(id="system_design", name="System Design",
              prerequisites=["apis", "redis", "sql"], effort_hours=60, difficulty=5,
              min_semester=5),

    # --- AI / ML -----------------------------------------------------------
    SkillNode(id="statistics", name="Statistics & Probability",
              prerequisites=["programming"], effort_hours=40, difficulty=3,
              min_semester=2),
    SkillNode(id="pandas", name="Pandas & Data Wrangling", prerequisites=["python"],
              effort_hours=30, difficulty=2, min_semester=3),
    SkillNode(id="data_viz", name="Data Visualization", prerequisites=["pandas"],
              effort_hours=20, difficulty=2, min_semester=3),
    SkillNode(id="ml", name="Machine Learning", prerequisites=["python", "dsa"],
              effort_hours=80, difficulty=4, min_semester=4),
    SkillNode(id="dl", name="Deep Learning", prerequisites=["ml"],
              effort_hours=80, difficulty=5, min_semester=5),
    SkillNode(id="pytorch", name="PyTorch", prerequisites=["dl"],
              effort_hours=40, difficulty=4, min_semester=5),
    SkillNode(id="transformers", name="Transformers", prerequisites=["pytorch"],
              effort_hours=50, difficulty=5, min_semester=6),
    # App-level skill: builds on LLM-API experience, not on model training.
    SkillNode(id="rag", name="RAG & Vector DBs", prerequisites=["genai_apps"],
              effort_hours=40, difficulty=4, min_semester=5),
    SkillNode(id="mlops", name="MLOps", prerequisites=["ml", "docker", "cloud"],
              effort_hours=50, difficulty=5, min_semester=6),
    # Building on top of LLM APIs (prompting, tool use, agents) -- much lower
    # barrier than training models, hence earlier min_semester than DL.
    SkillNode(id="genai_apps", name="GenAI Apps (LLM APIs, Prompting, Agents)",
              prerequisites=["python", "apis"], effort_hours=35, difficulty=3,
              min_semester=4),

    # --- DevOps / Infra ----------------------------------------------------
    SkillNode(id="kubernetes", name="Kubernetes", prerequisites=["docker"],
              effort_hours=45, difficulty=4, min_semester=5),
    SkillNode(id="terraform", name="Terraform & IaC", prerequisites=["cloud"],
              effort_hours=30, difficulty=4, min_semester=5),
    SkillNode(id="monitoring", name="Monitoring & Observability",
              prerequisites=["linux", "docker"], effort_hours=25, difficulty=3,
              min_semester=5),

    # --- Mobile ------------------------------------------------------------
    SkillNode(id="kotlin", name="Kotlin", prerequisites=["programming"],
              effort_hours=40, difficulty=3, min_semester=2),
    SkillNode(id="android_sdk", name="Android Development", prerequisites=["kotlin"],
              effort_hours=60, difficulty=3, min_semester=3),
    SkillNode(id="swift", name="Swift", prerequisites=["programming"],
              effort_hours=40, difficulty=3, min_semester=2),
    SkillNode(id="ios_sdk", name="iOS Development", prerequisites=["swift"],
              effort_hours=60, difficulty=3, min_semester=3),

    # --- Cross-cutting -----------------------------------------------------
    SkillNode(id="communication", name="Communication", prerequisites=[],
              effort_hours=20, difficulty=2, min_semester=1),
    SkillNode(id="english", name="English", prerequisites=[],
              effort_hours=20, difficulty=1, min_semester=1),
]

# Index by id for O(1) lookup.
SKILLS: dict[str, SkillNode] = {s.id: s for s in _SKILLS}


def _validate_graph() -> None:
    """Fail fast at import if any prerequisite points at a missing skill."""
    for skill in _SKILLS:
        for pre in skill.prerequisites:
            if pre not in SKILLS:
                raise ValueError(
                    f"skill '{skill.id}' has unknown prerequisite '{pre}'"
                )


_validate_graph()
