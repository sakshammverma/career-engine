# CareerMap — Google Maps for careers

Personalized, continuously recalculated career roadmaps for students. A
deterministic career-graph engine computes readiness %, highest-ROI next
steps, semester-aware roadmaps, weekly plans, milestones, and opportunity
matches; an AI mentor (Groq) explains and advises on top of that state.

```
career-engine/   FastAPI backend — the engine (Python, zero-infra SQLite)
career-web/      Next.js frontend (Tailwind, validated dataviz palette)
render.yaml      One-click Render blueprint for the backend
```

## Run locally

```bash
# Terminal 1 — API on :8000
cd career-engine
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2 — web on :3000
cd career-web
npm install
npm run dev
```

Optional: put a Groq key in `career-engine/.env` (`GROQ_API_KEY=gsk_...`,
free at https://console.groq.com/keys) to switch the mentor from offline
mode to live LLM answers.

## Deploy free

### 1. Backend → Render

1. Push this repo to GitHub.
2. On https://render.com → **New + → Blueprint** → select the repo.
   Render reads `render.yaml` and creates the `career-engine` service.
3. In the service's **Environment** tab, set `GROQ_API_KEY` to your key.
4. Note your URL, e.g. `https://career-engine.onrender.com`.

Free-tier notes: the service sleeps after ~15 min idle (first request
cold-starts in ~30–50 s), and the SQLite file is **ephemeral** — student
profiles reset on each deploy/restart. Fine for a demo; for durable data,
swap `app/store.py` to a free Postgres (Neon/Supabase).

### 2. Frontend → Vercel

1. On https://vercel.com → **Add New → Project** → import the repo.
2. Set **Root Directory** to `career-web`.
3. Add env var `NEXT_PUBLIC_API_URL = https://<your-service>.onrender.com`.
4. Deploy. Note your URL, e.g. `https://careermap.vercel.app`.

### 3. Connect them

Back in Render → Environment, update:

```
CORS_ORIGINS=http://localhost:3000,https://<your-app>.vercel.app
```

Save (the service redeploys) — done. Open the Vercel URL and build a roadmap.
