"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { STUDENT_KEY } from "@/lib/api";

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
          <Link
            href={hasStudent ? "/dashboard" : "/onboarding"}
            className="text-sm text-ink2 hover:text-ink transition-colors"
          >
            {hasStudent ? "Dashboard →" : "Get started →"}
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-5xl px-6 pt-24 pb-16 text-center">
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
            className="rounded-lg bg-accent px-6 py-3 text-white font-medium hover:bg-accent-strong transition-colors"
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
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-5xl px-6 pb-20 grid gap-4 sm:grid-cols-3">
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
            className="rounded-xl border border-hairline bg-surface p-6"
          >
            <p className="text-xs font-medium text-muted">{s.n}</p>
            <h3 className="mt-2 font-semibold">{s.t}</h3>
            <p className="mt-2 text-sm text-ink2 leading-relaxed">{s.d}</p>
          </div>
        ))}
      </section>

      {/* Roles */}
      <section className="mx-auto max-w-5xl px-6 pb-24 text-center">
        <p className="text-sm text-muted mb-4">Ten career tracks, one engine</p>
        <div className="flex flex-wrap justify-center gap-2">
          {ROLES.map((r) => (
            <span
              key={r}
              className="rounded-full border border-hairline bg-surface px-3 py-1 text-sm text-ink2"
            >
              {r}
            </span>
          ))}
        </div>
      </section>
    </main>
  );
}
