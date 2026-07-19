"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, STUDENT_KEY, StudentProfile, warmUp } from "@/lib/api";
import ThemeToggle from "@/components/ThemeToggle";
import WakingOverlay from "@/components/WakingOverlay";

/* ------------------------------------------------------------------ */
/* Static option data                                                  */
/* ------------------------------------------------------------------ */
const ROLE_OPTIONS = [
  { id: "backend", label: "Backend", blurb: "APIs, databases, systems" },
  { id: "frontend", label: "Frontend", blurb: "React, UI engineering" },
  { id: "fullstack", label: "Full Stack", blurb: "End-to-end product" },
  { id: "ai_engineer", label: "AI Engineer", blurb: "LLMs, RAG, agents" },
  { id: "ml_engineer", label: "ML Engineer", blurb: "Models in production" },
  { id: "data_scientist", label: "Data Scientist", blurb: "Stats, insight, ML" },
  { id: "devops", label: "DevOps", blurb: "Infra, CI/CD, cloud" },
  { id: "android", label: "Android", blurb: "Kotlin apps" },
  { id: "ios", label: "iOS", blurb: "Swift apps" },
  { id: "fde", label: "FDE", blurb: "Forward-deployed AI eng" },
];

const SKILLS: { id: string; name: string }[] = [
  { id: "programming", name: "Programming" },
  { id: "dsa", name: "DSA" },
  { id: "python", name: "Python" },
  { id: "java", name: "Java" },
  { id: "cpp", name: "C++" },
  { id: "javascript", name: "JavaScript" },
  { id: "react", name: "React" },
  { id: "apis", name: "Backend / APIs" },
  { id: "sql", name: "SQL" },
  { id: "git", name: "Git" },
  { id: "linux", name: "Linux" },
  { id: "docker", name: "Docker" },
  { id: "cloud", name: "Cloud" },
  { id: "ml", name: "AI / ML" },
  { id: "communication", name: "Communication" },
  { id: "english", name: "English" },
];

const LEVEL_HINTS = ["None", "Basics", "Learning", "Working", "Strong", "Expert"];

const STEPS = ["Academics", "Goal", "Constraints", "Skills", "Experience"];

/* ------------------------------------------------------------------ */
/* Small controls                                                      */
/* ------------------------------------------------------------------ */
function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-ink2">{label}</span>
      <div className="mt-1.5">{children}</div>
    </label>
  );
}

const inputCls =
  "w-full rounded-lg border border-hairline bg-surface px-3 py-2 text-sm outline-none focus:border-accent transition-colors";

function Segmented<T extends string | number>({
  value,
  options,
  onChange,
}: {
  value: T;
  options: { v: T; label: string }[];
  onChange: (v: T) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => (
        <button
          key={String(o.v)}
          type="button"
          onClick={() => onChange(o.v)}
          className={`rounded-lg border px-3 py-1.5 text-sm transition-colors ${
            value === o.v
              ? "border-accent bg-accent text-white"
              : "border-hairline bg-surface text-ink2 hover:text-ink"
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Page                                                                */
/* ------------------------------------------------------------------ */
export default function Onboarding() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [waking, setWaking] = useState(false);
  const [wakeElapsed, setWakeElapsed] = useState(0);
  const [wakeFailed, setWakeFailed] = useState(false);

  // form state
  const [semester, setSemester] = useState(3);
  const [tier, setTier] = useState(2);
  const [university, setUniversity] = useState("");
  const [branch, setBranch] = useState("");
  const [cgpa, setCgpa] = useState("");
  const [role, setRole] = useState("backend");
  const [salary, setSalary] = useState<number>(8);
  const [workMode, setWorkMode] = useState("hybrid");
  const [hours, setHours] = useState(3);
  const [budget, setBudget] = useState<"free_only" | "paid_ok">("free_only");
  const [style, setStyle] = useState<
    "video" | "text" | "interactive" | "project"
  >("project");
  const [levels, setLevels] = useState<Record<string, number>>(
    Object.fromEntries(SKILLS.map((s) => [s.id, 0])),
  );
  const [exp, setExp] = useState({
    projects_completed: 0,
    internships: 0,
    open_source_prs: 0,
    hackathons: 0,
    cp_level: 0,
    resume_quality: 0,
    github_maturity: 0,
    certifications: 0,
  });

  // Quick demo fill — lets a visitor feel the product in one click.
  function fillSample() {
    setSemester(3);
    setTier(2);
    setUniversity("AKTU");
    setBranch("CSE");
    setCgpa("7.8");
    setRole("backend");
    setSalary(10);
    setWorkMode("hybrid");
    setHours(3);
    setBudget("free_only");
    setStyle("project");
    setLevels((prev) => ({
      ...prev,
      programming: 4,
      dsa: 3,
      python: 3,
      sql: 2,
      git: 3,
      communication: 3,
      english: 4,
    }));
    setExp((p) => ({ ...p, projects_completed: 2, resume_quality: 2 }));
    setStep(STEPS.length - 1);
  }

  async function submit() {
    setBusy(true);
    setError(null);
    setWakeFailed(false);
    const profile: StudentProfile = {
      academic: {
        college_tier: tier,
        university: university || null,
        branch: branch || null,
        current_semester: semester,
        graduation_year: null,
        cgpa: cgpa ? Number(cgpa) : null,
        backlogs: 0,
        attendance_restricted: false,
      },
      goals: {
        target_role: role,
        campus: true,
        off_campus: true,
        target_salary_lpa: salary,
        preferred_companies: [],
        work_mode: workMode,
      },
      constraints: {
        daily_study_hours: hours,
        budget,
        learning_style: style,
      },
      skills: {
        levels: Object.fromEntries(
          Object.entries(levels).filter(([, v]) => v > 0),
        ),
      },
      experience: exp,
    };
    try {
      // Wake the free-tier engine first (no-op when already warm).
      setWaking(true);
      const awake = await warmUp(setWakeElapsed);
      if (!awake) {
        setWaking(false);
        setWakeFailed(true);
        setBusy(false);
        return;
      }
      const { student_id } = await api.createStudent(profile);
      localStorage.setItem(STUDENT_KEY, student_id);
      router.push("/dashboard");
    } catch (e) {
      setWaking(false);
      setError(`Something went wrong creating your profile. (${String(e)})`);
      setBusy(false);
    }
  }

  const canNext =
    step !== 1 || Boolean(role); /* role always set; guard kept for clarity */

  if (waking || wakeFailed)
    return (
      <WakingOverlay
        elapsed={wakeElapsed}
        failed={wakeFailed}
        onRetry={() => {
          setWakeFailed(false);
          submit();
        }}
      />
    );

  return (
    <main className="flex-1 mx-auto w-full max-w-2xl px-6 py-8">
      {/* Mini header */}
      <div className="mb-8 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-accent" />
          <span className="font-semibold tracking-tight">CareerMap</span>
        </Link>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={fillSample}
            className="text-xs text-muted hover:text-ink2 transition-colors"
            title="Fill a realistic sample profile to try the product fast"
          >
            Try with sample data
          </button>
          <ThemeToggle />
        </div>
      </div>

      {/* Stepper */}
      <ol className="flex items-center gap-1 mb-10">
        {STEPS.map((s, i) => (
          <li key={s} className="flex items-center gap-1 flex-1 last:flex-none">
            <button
              type="button"
              onClick={() => i < step && setStep(i)}
              className={`flex items-center gap-2 text-xs font-medium whitespace-nowrap ${
                i === step
                  ? "text-ink"
                  : i < step
                    ? "text-accent cursor-pointer"
                    : "text-muted"
              }`}
            >
              <span
                className={`grid h-6 w-6 place-items-center rounded-full border text-[11px] ${
                  i === step
                    ? "border-accent bg-accent text-white"
                    : i < step
                      ? "border-accent text-accent"
                      : "border-hairline"
                }`}
              >
                {i < step ? "✓" : i + 1}
              </span>
              <span className="hidden sm:inline">{s}</span>
            </button>
            {i < STEPS.length - 1 && (
              <span className="h-px flex-1 bg-grid mx-2 hidden sm:block" />
            )}
          </li>
        ))}
      </ol>

      <div
        key={step}
        className="anim-fade-up rounded-2xl border border-hairline bg-surface p-8"
      >
        {/* STEP 0 — Academics */}
        {step === 0 && (
          <div className="space-y-5">
            <h2 className="text-xl font-semibold">Where are you right now?</h2>
            <Field label="Current semester">
              <Segmented
                value={semester}
                onChange={setSemester}
                options={Array.from({ length: 8 }, (_, i) => ({
                  v: i + 1,
                  label: `${i + 1}`,
                }))}
              />
            </Field>
            <Field label="College tier">
              <Segmented
                value={tier}
                onChange={setTier}
                options={[
                  { v: 1, label: "Tier 1 (IIT/NIT/top)" },
                  { v: 2, label: "Tier 2" },
                  { v: 3, label: "Tier 3" },
                ]}
              />
            </Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="University (optional)">
                <input
                  className={inputCls}
                  value={university}
                  onChange={(e) => setUniversity(e.target.value)}
                  placeholder="e.g. AKTU"
                />
              </Field>
              <Field label="Branch (optional)">
                <input
                  className={inputCls}
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  placeholder="e.g. CSE"
                />
              </Field>
            </div>
            <Field label="CGPA (optional)">
              <input
                className={inputCls}
                value={cgpa}
                onChange={(e) => setCgpa(e.target.value)}
                placeholder="e.g. 7.8"
                inputMode="decimal"
              />
            </Field>
          </div>
        )}

        {/* STEP 1 — Goal */}
        {step === 1 && (
          <div className="space-y-5">
            <h2 className="text-xl font-semibold">Where do you want to go?</h2>
            <div className="grid grid-cols-2 gap-3">
              {ROLE_OPTIONS.map((r) => (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => setRole(r.id)}
                  className={`rounded-xl border p-4 text-left transition-colors ${
                    role === r.id
                      ? "border-accent bg-accent/5"
                      : "border-hairline hover:border-baseline"
                  }`}
                >
                  <span className="flex items-center justify-between">
                    <span className="font-medium text-sm">{r.label}</span>
                    {role === r.id && (
                      <span className="text-accent text-sm">●</span>
                    )}
                  </span>
                  <span className="mt-1 block text-xs text-muted">
                    {r.blurb}
                  </span>
                </button>
              ))}
            </div>
            <Field label="Target salary (LPA)">
              <Segmented
                value={salary}
                onChange={setSalary}
                options={[
                  { v: 5, label: "4–6" },
                  { v: 10, label: "8–12" },
                  { v: 18, label: "15+" },
                  { v: 25, label: "25+" },
                ]}
              />
            </Field>
            <Field label="Preferred work mode">
              <Segmented
                value={workMode}
                onChange={setWorkMode}
                options={[
                  { v: "remote", label: "Remote" },
                  { v: "hybrid", label: "Hybrid" },
                  { v: "office", label: "Office" },
                ]}
              />
            </Field>
          </div>
        )}

        {/* STEP 2 — Constraints */}
        {step === 2 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">How do you learn?</h2>
            <Field label={`Daily study time — ${hours}h/day`}>
              <input
                type="range"
                min={1}
                max={10}
                step={0.5}
                value={hours}
                onChange={(e) => setHours(Number(e.target.value))}
                className="w-full accent-[var(--accent)]"
              />
              <div className="flex justify-between text-xs text-muted mt-1">
                <span>1h</span>
                <span>10h</span>
              </div>
            </Field>
            <Field label="Budget">
              <Segmented
                value={budget}
                onChange={setBudget}
                options={[
                  { v: "free_only", label: "Free resources only" },
                  { v: "paid_ok", label: "Paid courses OK" },
                ]}
              />
            </Field>
            <Field label="Learning style">
              <Segmented
                value={style}
                onChange={setStyle}
                options={[
                  { v: "video", label: "Video" },
                  { v: "text", label: "Text" },
                  { v: "interactive", label: "Interactive" },
                  { v: "project", label: "Project-based" },
                ]}
              />
            </Field>
          </div>
        )}

        {/* STEP 3 — Skills */}
        {step === 3 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Rate your skills</h2>
            <p className="text-sm text-ink2 -mt-2">
              0 = never touched it · 5 = expert. Be honest — the roadmap is
              only as good as this.
            </p>
            <div className="space-y-3">
              {SKILLS.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between gap-4"
                >
                  <span className="text-sm w-36 shrink-0">{s.name}</span>
                  <div className="flex gap-1.5 flex-1 justify-end">
                    {[0, 1, 2, 3, 4, 5].map((v) => (
                      <button
                        key={v}
                        type="button"
                        title={LEVEL_HINTS[v]}
                        onClick={() =>
                          setLevels((prev) => ({ ...prev, [s.id]: v }))
                        }
                        className={`h-8 w-8 rounded-md border text-xs transition-colors ${
                          levels[s.id] === v
                            ? "border-accent bg-accent text-white"
                            : "border-hairline text-ink2 hover:border-baseline"
                        }`}
                      >
                        {v}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* STEP 4 — Experience */}
        {step === 4 && (
          <div className="space-y-5">
            <h2 className="text-xl font-semibold">Experience so far</h2>
            <div className="grid grid-cols-2 gap-4">
              {(
                [
                  ["projects_completed", "Projects completed"],
                  ["internships", "Internships"],
                  ["open_source_prs", "Open-source PRs"],
                  ["hackathons", "Hackathons"],
                ] as const
              ).map(([k, label]) => (
                <Field key={k} label={label}>
                  <input
                    type="number"
                    min={0}
                    className={inputCls}
                    value={exp[k]}
                    onChange={(e) =>
                      setExp((p) => ({
                        ...p,
                        [k]: Math.max(0, Number(e.target.value)),
                      }))
                    }
                  />
                </Field>
              ))}
            </div>
            <Field label={`Competitive programming level — ${exp.cp_level}/5`}>
              <input
                type="range"
                min={0}
                max={5}
                value={exp.cp_level}
                onChange={(e) =>
                  setExp((p) => ({ ...p, cp_level: Number(e.target.value) }))
                }
                className="w-full accent-[var(--accent)]"
              />
            </Field>
            <Field label={`Resume quality — ${exp.resume_quality}/5`}>
              <input
                type="range"
                min={0}
                max={5}
                value={exp.resume_quality}
                onChange={(e) =>
                  setExp((p) => ({
                    ...p,
                    resume_quality: Number(e.target.value),
                  }))
                }
                className="w-full accent-[var(--accent)]"
              />
            </Field>
            {error && (
              <p className="text-sm text-critical border border-hairline rounded-lg p-3">
                {error}
              </p>
            )}
          </div>
        )}

        {/* Nav buttons */}
        <div className="mt-8 flex justify-between">
          <button
            type="button"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className="rounded-lg px-4 py-2 text-sm text-ink2 hover:text-ink disabled:opacity-0 transition-colors"
          >
            ← Back
          </button>
          {step < STEPS.length - 1 ? (
            <button
              type="button"
              disabled={!canNext}
              onClick={() => setStep((s) => s + 1)}
              className="rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-strong transition-colors"
            >
              Continue →
            </button>
          ) : (
            <button
              type="button"
              onClick={submit}
              disabled={busy}
              className="rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-strong disabled:opacity-60 transition-colors"
            >
              {busy ? "Computing your route…" : "Compute my roadmap"}
            </button>
          )}
        </div>
      </div>
    </main>
  );
}
