"""FastAPI surface for the career engine.

Stateless (compute-only) endpoints:
  GET  /health
  GET  /roles
  POST /readiness                       -- readiness + ROI recommendations
  POST /roadmap                         -- semester-aware roadmap
  POST /weekly-plan                     -- weekly plan for a given profile
  GET  /resources/{skill_id}            -- curated resources for a skill

Stateful (persisted) endpoints -- the "continuously updated" loop:
  POST /students                        -- create a student, returns id
  GET  /students/{id}/dashboard         -- recomputed readiness/roadmap/milestones/plan
  PATCH /students/{id}/skills/{skill}   -- update a skill level, recompute
  PATCH /students/{id}/milestones/{m}   -- toggle a milestone, recompute
  POST /students/{id}/advance-semester  -- move to next semester, recompute
  GET  /students/{id}/history           -- progress log
"""

from __future__ import annotations

import os

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.dashboard import Dashboard, build_dashboard
from app.engine import analyze
from app.graph.roles import ROLES
from app.mentor import Mentor, MentorReply
from app.milestones import MILESTONES
from app.models import (
    Budget,
    LearningStyle,
    ReadinessResult,
    Roadmap,
    RoleGraph,
    StudentProfile,
)
from app.planner import WeeklyPlan, generate_weekly_plan
from app.opportunities import OpportunityMatch, match_opportunities
from app.resources import Resource, resources_for
from app.roadmap import generate_roadmap
from app.store import ProfileStore, StudentNotFound

app = FastAPI(
    title="AI Career Roadmap Engine",
    version="0.2.0",
    summary="Deterministic career engine with persistence: readiness %, "
    "semester-aware roadmaps, milestones, and an adaptive weekly planner that "
    "recompute as the student makes progress.",
)

# Allow the Next.js frontend to call this API. In production set
# CORS_ORIGINS to a comma-separated list (e.g. your Vercel URL).
_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        o.strip()
        for o in os.environ.get("CORS_ORIGINS", _default_origins).split(",")
        if o.strip()
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default to a real DB file so students survive server restarts; tests and
# ephemeral runs can set CAREER_DB=":memory:".
store = ProfileStore(os.environ.get("CAREER_DB", "career.db"))
mentor = Mentor()


def _dashboard(student_id: str) -> Dashboard:
    try:
        profile = store.get_profile(student_id)
        milestones = store.get_completed_milestones(student_id)
    except StudentNotFound:
        raise HTTPException(status_code=404, detail="student not found")
    return build_dashboard(student_id, profile, milestones)


# --------------------------------------------------------------------------- #
# Stateless compute endpoints
# --------------------------------------------------------------------------- #
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/roles", response_model=list[RoleGraph])
def list_roles() -> list[RoleGraph]:
    return list(ROLES.values())


@app.post("/readiness", response_model=ReadinessResult)
def readiness(profile: StudentProfile, top_n: int = 5) -> ReadinessResult:
    return analyze(profile, top_n=top_n)


@app.post("/roadmap", response_model=Roadmap)
def roadmap(profile: StudentProfile) -> Roadmap:
    return generate_roadmap(profile)


@app.post("/weekly-plan", response_model=list[WeeklyPlan])
def weekly_plan(profile: StudentProfile) -> list[WeeklyPlan]:
    return generate_weekly_plan(profile)


@app.post("/opportunities", response_model=list[OpportunityMatch])
def opportunities(profile: StudentProfile) -> list[OpportunityMatch]:
    """Relevant opportunities for this profile: eligible first, then near-misses
    with exactly what's missing."""
    return match_opportunities(profile)


@app.get("/resources/{skill_id}", response_model=list[Resource])
def resources(
    skill_id: str,
    budget: Budget = Budget.FREE_ONLY,
    style: LearningStyle | None = None,
) -> list[Resource]:
    return resources_for(skill_id, budget=budget, style=style)


# --------------------------------------------------------------------------- #
# Stateful, persisted endpoints
# --------------------------------------------------------------------------- #
@app.post("/students", status_code=201)
def create_student(profile: StudentProfile) -> dict[str, str]:
    sid = store.create_student(profile)
    return {"student_id": sid}


@app.get("/students/{student_id}/dashboard", response_model=Dashboard)
def get_dashboard(student_id: str) -> Dashboard:
    return _dashboard(student_id)


@app.patch("/students/{student_id}/skills/{skill_id}", response_model=Dashboard)
def update_skill(
    student_id: str, skill_id: str, level: int = Body(..., embed=True, ge=0, le=5)
) -> Dashboard:
    try:
        store.set_skill_level(student_id, skill_id, level)
    except StudentNotFound:
        raise HTTPException(status_code=404, detail="student not found")
    return _dashboard(student_id)


@app.patch("/students/{student_id}/milestones/{milestone_id}", response_model=Dashboard)
def update_milestone(
    student_id: str, milestone_id: str, done: bool = Body(..., embed=True)
) -> Dashboard:
    if milestone_id not in MILESTONES:
        raise HTTPException(status_code=404, detail="unknown milestone")
    try:
        store.set_milestone(student_id, milestone_id, done)
    except StudentNotFound:
        raise HTTPException(status_code=404, detail="student not found")
    return _dashboard(student_id)


@app.post("/students/{student_id}/advance-semester", response_model=Dashboard)
def advance_semester(student_id: str) -> Dashboard:
    try:
        store.advance_semester(student_id)
    except StudentNotFound:
        raise HTTPException(status_code=404, detail="student not found")
    return _dashboard(student_id)


@app.get("/students/{student_id}/history")
def history(student_id: str) -> list[dict]:
    try:
        return store.progress_history(student_id)
    except StudentNotFound:
        raise HTTPException(status_code=404, detail="student not found")


@app.post("/students/{student_id}/mentor", response_model=MentorReply)
def ask_mentor(
    student_id: str, question: str = Body(..., embed=True, min_length=1)
) -> MentorReply:
    """Ask the AI mentor. Grounded in the student's freshly recomputed
    dashboard; falls back to a deterministic offline answer without an API key."""
    dash = _dashboard(student_id)
    return mentor.ask(dash, question)
