"""Resource recommendation engine.

Maps each skill node to curated learning resources, then filters them by the
student's budget (free-only vs paid-ok) and learning style. The brief asks for
"only high-quality resources", so this is a hand-curated set of well-known,
reputable sources rather than a scraped list.

Only skills with curated entries appear; a skill with no curated resources
simply returns an empty list (never a fabricated link).
"""

from __future__ import annotations

from pydantic import BaseModel

from app.models import Budget, LearningStyle


class Resource(BaseModel):
    title: str
    url: str
    kind: str  # docs | video | course | practice | project | interview | cheatsheet
    free: bool
    # Learning styles this resource suits, for style-aware filtering.
    styles: list[LearningStyle]


def _r(title, url, kind, free, styles) -> Resource:
    return Resource(title=title, url=url, kind=kind, free=free, styles=styles)


V = LearningStyle.VIDEO
T = LearningStyle.TEXT
I = LearningStyle.INTERACTIVE
P = LearningStyle.PROJECT

# Curated resources keyed by skill id. Kept deliberately small and reputable.
_RESOURCES: dict[str, list[Resource]] = {
    "programming": [
        _r("CS50x (Harvard)", "https://cs50.harvard.edu/x/", "course", True, [V, P]),
        _r("Python Official Tutorial", "https://docs.python.org/3/tutorial/",
           "docs", True, [T]),
    ],
    "dsa": [
        _r("NeetCode 150", "https://neetcode.io/practice", "practice", True, [I, V]),
        _r("CSES Problem Set", "https://cses.fi/problemset/", "practice", True, [I]),
        _r("Abdul Bari Algorithms", "https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O",
           "video", True, [V]),
    ],
    "sql": [
        _r("SQLBolt", "https://sqlbolt.com/", "practice", True, [I]),
        _r("PostgreSQL Tutorial", "https://www.postgresqltutorial.com/", "docs",
           True, [T]),
    ],
    "apis": [
        _r("MDN HTTP Guide", "https://developer.mozilla.org/en-US/docs/Web/HTTP",
           "docs", True, [T]),
        _r("FastAPI Docs", "https://fastapi.tiangolo.com/", "docs", True, [T, P]),
    ],
    "linux": [
        _r("Linux Journey", "https://linuxjourney.com/", "interactive", True, [I]),
        _r("MIT Missing Semester", "https://missing.csail.mit.edu/", "course",
           True, [V, T]),
    ],
    "docker": [
        _r("Docker Official Getting Started",
           "https://docs.docker.com/get-started/", "docs", True, [T, P]),
        _r("Docker for Beginners (freeCodeCamp)",
           "https://www.youtube.com/watch?v=fqMOX6JJhGo", "video", True, [V]),
    ],
    "git": [
        _r("Pro Git (book)", "https://git-scm.com/book/en/v2", "docs", True, [T]),
        _r("Learn Git Branching", "https://learngitbranching.js.org/", "interactive",
           True, [I]),
    ],
    "react": [
        _r("React Official Docs", "https://react.dev/learn", "docs", True, [T, I]),
        _r("Scrimba Learn React", "https://scrimba.com/learn/learnreact", "course",
           True, [I, V]),
    ],
    "html_css": [
        _r("MDN Web Docs", "https://developer.mozilla.org/en-US/docs/Learn",
           "docs", True, [T]),
        _r("freeCodeCamp Responsive Web Design",
           "https://www.freecodecamp.org/learn/2022/responsive-web-design/",
           "practice", True, [I, P]),
    ],
    "javascript": [
        _r("javascript.info", "https://javascript.info/", "docs", True, [T, I]),
    ],
    "ml": [
        _r("Andrew Ng ML Specialization",
           "https://www.coursera.org/specializations/machine-learning-introduction",
           "course", False, [V]),
        _r("fast.ai Practical DL", "https://course.fast.ai/", "course", True, [V, P]),
    ],
    "system_design": [
        _r("System Design Primer",
           "https://github.com/donnemartin/system-design-primer", "docs", True, [T]),
        _r("Grokking System Design (interview)",
           "https://www.designgurus.io/course/grokking-the-system-design-interview",
           "interview", False, [T, I]),
    ],
    "testing": [
        _r("Pytest Docs", "https://docs.pytest.org/", "docs", True, [T, P]),
    ],
}


class SkillResources(BaseModel):
    skill_id: str
    resources: list[Resource]


def resources_for(
    skill_id: str,
    budget: Budget = Budget.FREE_ONLY,
    style: LearningStyle | None = None,
) -> list[Resource]:
    """Curated resources for one skill, filtered by budget and (optionally) style.

    Budget FREE_ONLY drops paid resources entirely. Style filtering is a *soft*
    preference: matching-style resources come first, but we never return an empty
    list solely because of style when suitable free resources exist.
    """
    items = _RESOURCES.get(skill_id, [])
    if budget == Budget.FREE_ONLY:
        items = [r for r in items if r.free]
    if style is not None:
        preferred = [r for r in items if style in r.styles]
        rest = [r for r in items if style not in r.styles]
        items = preferred + rest
    return items
