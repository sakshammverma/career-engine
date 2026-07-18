"""AI Mentor: grounded career advice over the deterministic engine state.

Architecture rule: the engine is the source of truth. Every mentor answer is
grounded in a context block built from the student's freshly recomputed
dashboard (readiness, gaps, ROI steps, milestones, opportunities). The LLM
explains and advises on top of those numbers; it never invents them.

LLM provider: Groq (OpenAI-compatible chat completions), called with httpx --
no extra SDK. If GROQ_API_KEY is missing or still the placeholder, the mentor
degrades gracefully to *offline mode*: a deterministic answer assembled from
the same dashboard context, so the product works end-to-end without a key.
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from pydantic import BaseModel

from app.dashboard import Dashboard

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
PLACEHOLDER_KEYS = {"", "your_groq_api_key_here"}

SYSTEM_PROMPT = """You are a pragmatic career mentor for engineering students.
You are given the student's CURRENT, COMPUTED career state (readiness %, skill
gaps, highest-ROI next steps, milestones, opportunities). Treat those numbers
as ground truth -- never contradict or re-estimate them.

Rules:
- Be concrete and specific to THIS student's semester, role and gaps.
- When recommending what to do next, prefer the listed highest-ROI steps.
- Keep answers tight: a few short paragraphs or a list, no fluff.
- If asked something outside careers/learning, briefly redirect."""


def _load_env(path: str | None = None) -> None:
    """Minimal .env loader (KEY=VALUE lines); real env vars take precedence."""
    env_path = Path(path) if path else Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def build_context(dash: Dashboard) -> str:
    """Compact grounding block the LLM (and offline mode) reasons over."""
    p = dash.profile
    lines = [
        f"Role goal: {p.goals.target_role.value} | Semester: "
        f"{p.academic.current_semester} | Study time: "
        f"{p.constraints.daily_study_hours}h/day",
        f"Readiness: {dash.readiness.readiness_pct}% now -> "
        f"{dash.readiness.projected_readiness_pct}% after next steps",
        "Highest-ROI next steps:",
    ]
    for r in dash.readiness.recommendations:
        blocked = f" (blocked by {', '.join(r.blocked_by)})" if r.blocked_by else ""
        lines.append(
            f"  - {r.name}: +{r.readiness_gain} pts, ~{r.effort_hours}h{blocked}"
        )
    top_gaps = dash.readiness.gaps[:5]
    if top_gaps:
        lines.append("Biggest gaps: " + ", ".join(
            f"{g.name} ({g.current_level}/{g.target_level})" for g in top_gaps))
    lines.append(
        f"Milestones: {dash.milestones.completed_count}/"
        f"{dash.milestones.total_count} done "
        f"({dash.milestones.due_completion_pct}% of currently-due)"
    )
    eligible = [m.opportunity.name for m in dash.opportunities if m.eligible][:5]
    if eligible:
        lines.append("Eligible opportunities: " + ", ".join(eligible))
    if dash.weekly_plan:
        wk = dash.weekly_plan[0]
        lines.append(f"This week's focus: {wk.focus_skill} (~{wk.estimated_hours}h)")
    return "\n".join(lines)


class MentorReply(BaseModel):
    answer: str
    mode: str  # "llm" | "offline"
    model: str | None = None
    context: str  # what the answer was grounded on (transparency/debugging)


def _offline_answer(dash: Dashboard, question: str) -> str:
    """Deterministic fallback built from the same grounding data."""
    recs = dash.readiness.recommendations
    actionable = [r for r in recs if not r.blocked_by]
    parts = [
        f"(Offline mentor -- add a Groq API key in .env for full answers.)",
        f"You're at {dash.readiness.readiness_pct}% readiness for "
        f"{dash.profile.goals.target_role.value}.",
    ]
    if actionable:
        steps = "; ".join(
            f"{r.name} (+{r.readiness_gain} pts, ~{r.effort_hours}h)"
            for r in actionable[:3]
        )
        parts.append(f"Best next steps: {steps}.")
        parts.append(
            f"Completing them takes you to about "
            f"{dash.readiness.projected_readiness_pct}%."
        )
    if dash.weekly_plan:
        parts.append(f"This week, focus on {dash.weekly_plan[0].focus_skill}.")
    eligible = [m.opportunity.name for m in dash.opportunities if m.eligible][:3]
    if eligible:
        parts.append(f"Worth applying to now: {', '.join(eligible)}.")
    return " ".join(parts)


class Mentor:
    """Groq-backed mentor with automatic offline fallback."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        _load_env()
        self.api_key = api_key if api_key is not None else os.environ.get("GROQ_API_KEY", "")
        self.model = model or os.environ.get("GROQ_MODEL", DEFAULT_MODEL)

    @property
    def live(self) -> bool:
        return self.api_key not in PLACEHOLDER_KEYS

    def ask(self, dash: Dashboard, question: str) -> MentorReply:
        context = build_context(dash)
        if not self.live:
            return MentorReply(
                answer=_offline_answer(dash, question), mode="offline", context=context
            )
        try:
            resp = httpx.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"STUDENT STATE:\n{context}\n\n"
                            f"QUESTION: {question}",
                        },
                    ],
                    "temperature": 0.4,
                    "max_tokens": 700,
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            answer = resp.json()["choices"][0]["message"]["content"]
            return MentorReply(
                answer=answer, mode="llm", model=self.model, context=context
            )
        except (httpx.HTTPError, KeyError, IndexError):
            # Network/auth/shape problems -> never break the product.
            return MentorReply(
                answer=_offline_answer(dash, question), mode="offline", context=context
            )
