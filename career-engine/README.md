# AI Career Roadmap Engine

The deterministic core of a "Google Maps for careers" platform. It decides **what
a specific student should learn next** to maximize their chance of landing a
target job — not a static roadmap, but a computed one.

**Frontend:** the Next.js app lives in `../career-web` (`npm run dev` →
http://localhost:3000). It consumes this API (CORS for :3000 is enabled).

This first milestone is the **Career Engine**: pure Python, no LLM, no database,
fully tested. It's the hard part (readiness math + prerequisite reasoning +
semester-aware planning) proven in isolation so it can drop into the full
FastAPI + Postgres + RAG stack later without change.

## What it does

Given a student profile (academics, target role, self-rated skills 1–5,
constraints) it computes:

- **Career readiness %** — weighted coverage of the target role's requirements.
- **Skill gaps** — where the student falls short, ranked by weighted severity.
- **Highest-ROI next steps** — readiness gained per hour, with prerequisites
  resolved (blocked skills are deferred behind their prereqs).
- **Projected readiness** — the "42% → 58%" story: readiness after completing the
  recommended, actionable skills.
- **Semester-aware roadmap** — the needed skills laid out across semesters,
  respecting prerequisites, `min_semester` gating ("never advanced topics too
  early"), and the student's weekly study budget.

## Layout

```
app/
  models.py          # Pydantic domain models (profile, graph, outputs)
  graph/
    skills.py        # skill nodes: prerequisites, effort, difficulty, min_semester
    roles.py         # role graphs: weighted skill requirements (10 roles incl. ML Eng, FDE)
  engine.py          # readiness %, gaps, ROI recommendations, projection
  roadmap.py         # semester-aware roadmap generation
  milestones.py      # checklist milestones + completion tracking
  resources.py       # curated resources per skill (budget/style aware)
  planner.py         # dynamic weekly planner (adapts to progress)
  opportunities.py   # opportunity engine (GSoC, MLH, ICPC... matched to profile)
  mentor.py          # AI mentor (Groq) grounded in engine state; offline fallback
  store.py           # SQLite persistence (stdlib) + progress log
  dashboard.py       # recomputed student view (the "continuously updated" core)
  main.py            # FastAPI endpoints (stateless compute + stateful/persisted)
  samples.py         # example student profiles
tests/               # pytest suite (43 tests)
demo.py              # console demo — no server needed
```

## The continuous-update loop

The brief's core idea — "Google Maps for careers, continuously recalculating" —
is implemented as: persist a student, mutate progress, recompute everything.

```
POST   /students                          -> student_id
GET    /students/{id}/dashboard           -> readiness + roadmap + milestones + weekly plan
PATCH  /students/{id}/skills/{skill}      -> {"level": 4}  (recomputes)
PATCH  /students/{id}/milestones/{m}      -> {"done": true} (recomputes)
POST   /students/{id}/advance-semester    -> (recomputes)
GET    /students/{id}/history             -> progress log
```

As a student learns Linux -> SQL -> APIs, readiness climbs 38% -> 44% -> 50% ->
56% and the weekly plan's next focus advances automatically. `demo.py` prints
this loop at the end.

Persistence is stdlib `sqlite3` storing the profile as JSON — the same shape
that drops into a Postgres `JSONB` column later with no engine changes.

## Run

```bash
pip install -r requirements.txt

# 1) Console demo (prints readiness, ROI steps, roadmap)
python demo.py

# 2) Test suite
python -m pytest -q

# 3) API server
uvicorn app.main:app --reload
#   -> http://127.0.0.1:8000/docs  (interactive Swagger UI)
```

### Example API call

```bash
curl -X POST http://127.0.0.1:8000/readiness \
  -H "content-type: application/json" \
  -d @- <<'JSON'
{
  "academic": {"college_tier": 2, "current_semester": 3, "cgpa": 7.8},
  "goals": {"target_role": "backend"},
  "constraints": {"daily_study_hours": 3.0},
  "skills": {"levels": {"programming": 4, "dsa": 3, "sql": 2, "apis": 2}}
}
JSON
```

## How the scoring works

- Each role lists requirements as `(skill, target_level 1–5, weight)`.
- Readiness = `sum(weight * min(current, target)/target) / sum(weight)`, as a %.
- ROI of closing a gap = `readiness_points_gained / effort_hours`. Skills still
  blocked by unmet prerequisites are discounted so their prerequisites surface
  first.
- The roadmap topologically sorts the needed skills, gates each by its
  `min_semester`, and packs them into semesters within the student's study budget
  (always allowing at least one item per semester so a heavy skill can't stall).

## Roadmap (next milestones)

Done: ✅ persistence + recompute · ✅ milestone tracking · ✅ weekly planner ·
✅ resource engine · ✅ 10 roles (Backend, Frontend, Full Stack, AI Engineer,
ML Engineer, Data Scientist, DevOps, Android, iOS, FDE) · ✅ opportunity engine
(`POST /opportunities`, also on the dashboard) · ✅ AI mentor
(`POST /students/{id}/mentor`).

### AI mentor setup

The mentor uses Groq's OpenAI-compatible API. Put a real key in `.env`
(free at https://console.groq.com/keys):

```
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile   # optional
```

Without a key it runs in **offline mode**: deterministic answers assembled from
the same dashboard state (readiness, ROI steps, weekly focus, opportunities).
Either way, every answer is grounded in the engine's computed numbers — the LLM
explains; it never invents readiness figures.

Next:

1. Next.js + shadcn frontend consuming these endpoints.
2. Swap SQLite for Postgres (`JSONB` profile column) + pgvector — no engine
   changes needed; `store.py` is the only file that moves.
