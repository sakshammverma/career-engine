"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { STUDENT_KEY } from "@/lib/api";
import ThemeToggle from "@/components/ThemeToggle";

const ROLES = [
  "Backend",
  "Frontend",
  "Full Stack",
  "AI Engineer",
  "ML Engineer",
  "Data Scientist",
  "DevOps",
  "Android",
  "iOS",
  "FDE",
];

/** Animated product mock: the readiness meter recalculating. */
function HeroMock() {
  const frames = [
    { pct: 38, step: "Learn Linux & Shell", delta: "+6.2" },
    { pct: 44, step: "Learn SQL & Databases", delta: "+5.6" },
    { pct: 50, step: "Learn APIs (REST/HTTP)", delta: "+6.2" },
    { pct: 56, step: "Learn Docker", delta: "+7.4" },
  ];
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((v) => (v + 1) % frames.length), 2200);
    return () => clearInterval(t);
  }, [frames.length]);
  const f = frames[i];

  return (
    <div className="mx-auto mt-14 w-full max-w-md rounded-2xl border border-hairline bg-surface p-6 text-left shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-xs text-ink2">Career readiness — Backend</p>
        <span className="rounded-full bg-good/10 px-2 py-0.5 text-[10px] font-semibold text-goodtext">
          {f.delta} pts
        </span>
      </div>
      <p className="mt-1 text-4xl font-semibold tracking-tight tabular-nums">
        {f.pct}%
      </p>
      <div className="mt-3 h-2.5 w-full rounded-full bg-accent-track overflow-hidden">
        <div
          className="h-full rounded-full bg-accent transition-[width] duration-1000 ease-out"
          style={{ width: `${f.pct}%` }}
        />
      </div>
      <div className="mt-4 flex items-center gap-2 text-xs text-ink2">
        <span className="grid h-5 w-5 place-items-center rounded-full bg-accent text-[10px] font-bold text-white">
          →
        </span>
        <span key={f.step} className="anim-fade-in">
          Next: {f.step}
        </span>
      </div>
    </div>
  );
}

export default function Landing() {
  const [hasStudent, setHasStudent] = useState(false);
  useEffect(() => {
    setHasStudent(Boolean(localStorage.getItem(STUDENT_KEY)));
  }, []);

  return (
    <main className="flex-1 flex flex-col">
      {/* Nav */}
      <header className="w-full border-b border-hairline">
        <div className="mx-auto max-w-5xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-accent" />
            <span className="font-semibold tracking-tight">CareerMap</span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href={hasStudent ? "/dashboard" : "/onboarding"}
              className="text-sm text-ink2 hover:text-ink transition-colors"
            >
              {hasStudent ? "Dashboard →" : "Get started →"}
            </Link>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        {/* soft radial wash behind the hero */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 h-[480px]"
          style={{
            background:
              "radial-gradient(600px 280px at 50% 0%, color-mix(in oklab, var(--accent) 14%, transparent), transparent 70%)",
          }}
        />
        <div className="relative mx-auto max-w-5xl px-6 pt-20 pb-16 text-center anim-fade-up">
          <p className="text-sm font-medium text-accent mb-4 tracking-wide uppercase">
            Google Maps for careers
          </p>
          <h1 className="text-4xl sm:text-6xl font-semibold tracking-tight leading-[1.05]">
            Stop following roadmaps.
            <br />
            <span className="text-ink2">Get one computed for you.</span>
          </h1>
          <p className="mt-6 text-lg text-ink2 max-w-2xl mx-auto leading-relaxed">
            CareerMap profiles where you are — semester, skills, constraints —
            and continuously recalculates the highest-ROI path to your target
            job. Learn something, and the whole route updates.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link
              href="/onboarding"
              className="rounded-lg bg-accent px-6 py-3 text-white font-medium hover:bg-accent-strong transition-all hover:shadow-lg hover:shadow-accent/25"
            >
              Build my roadmap
            </Link>
            {hasStudent && (
              <Link
                href="/dashboard"
                className="rounded-lg border border-hairline px-6 py-3 font-medium text-ink2 hover:text-ink transition-colors"
              >
                Open dashboard
              </Link>
            )}
          </div>

          <HeroMock />
          <p className="mt-3 text-xs text-muted">
            Live recalculation — this is the actual product loop
          </p>
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-5xl px-6 py-16 grid gap-4 sm:grid-cols-3 stagger">
        {[
          {
            n: "01",
            t: "Profile",
            d: "Your semester, self-rated skills, study time, and target role — 2 minutes.",
          },
          {
            n: "02",
            t: "Compute",
            d: "A career graph scores your readiness % and finds the highest-ROI next skills, prerequisites resolved.",
          },
          {
            n: "03",
            t: "Recalculate",
            d: "Mark progress and the roadmap, weekly plan, and opportunities recompute — like a GPS rerouting.",
          },
        ].map((s) => (
          <div
            key={s.n}
            className="card-lift rounded-xl border border-hairline bg-surface p-6"
          >
            <p className="text-xs font-medium text-accent">{s.n}</p>
            <h3 className="mt-2 font-semibold">{s.t}</h3>
            <p className="mt-2 text-sm text-ink2 leading-relaxed">{s.d}</p>
          </div>
        ))}
      </section>

      {/* Roles */}
      <section className="mx-auto max-w-5xl px-6 pb-16 text-center">
        <p className="text-sm text-muted mb-4">Ten career tracks, one engine</p>
        <div className="flex flex-wrap justify-center gap-2">
          {ROLES.map((r) => (
            <span
              key={r}
              className="rounded-full border border-hairline bg-surface px-3 py-1 text-sm text-ink2 hover:border-baseline hover:text-ink transition-colors"
            >
              {r}
            </span>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-hairline">
        <div className="mx-auto max-w-5xl px-6 py-6 flex items-center justify-between text-xs text-muted">
          <span>CareerMap — readiness computed, not guessed.</span>
          <a
            href="https://github.com/sakshammverma/career-engine"
            target="_blank"
            rel="noreferrer"
            className="hover:text-ink2 transition-colors"
          >
            GitHub ↗
          </a>
        </div>
      </footer>
    </main>
  );
}
