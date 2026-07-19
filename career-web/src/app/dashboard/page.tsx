"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, Dashboard, STUDENT_KEY, warmUp } from "@/lib/api";
import ReadinessHero from "@/components/ReadinessHero";
import StatTiles from "@/components/StatTiles";
import { NextSteps, SkillGapBars } from "@/components/GapsAndSteps";
import RoadmapTimeline from "@/components/RoadmapTimeline";
import MilestoneChecklist from "@/components/MilestoneChecklist";
import {
  WeeklyPlanList,
  OpportunityList,
} from "@/components/PlanAndOpportunities";
import MentorChat from "@/components/MentorChat";
import ProgressPanel from "@/components/ProgressPanel";
import ThemeToggle from "@/components/ThemeToggle";
import WakingOverlay from "@/components/WakingOverlay";
import Toast, { ToastData } from "@/components/Toast";

export default function DashboardPage() {
  const router = useRouter();
  const [studentId, setStudentId] = useState<string | null>(null);
  const [dash, setDash] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [waking, setWaking] = useState(false);
  const [wakeElapsed, setWakeElapsed] = useState(0);
  const [wakeFailed, setWakeFailed] = useState(false);
  const [toast, setToast] = useState<ToastData | null>(null);
  const toastSeq = useRef(0);

  const load = useCallback(async () => {
    const fromQuery = new URLSearchParams(window.location.search).get("sid");
    if (fromQuery) localStorage.setItem(STUDENT_KEY, fromQuery);
    const id = fromQuery ?? localStorage.getItem(STUDENT_KEY);
    if (!id) {
      router.replace("/onboarding");
      return;
    }
    setStudentId(id);
    setWakeFailed(false);

    // Wake the engine first (no-op when already warm), with visible progress.
    setWaking(true);
    const awake = await warmUp(setWakeElapsed);
    if (!awake) {
      setWaking(false);
      setWakeFailed(true);
      return;
    }
    try {
      setDash(await api.dashboard(id));
      setWaking(false);
    } catch (e) {
      setWaking(false);
      if (String(e).includes("404")) {
        // Server restarted with a fresh DB — profile is gone; re-onboard.
        localStorage.removeItem(STUDENT_KEY);
        router.replace("/onboarding");
      } else {
        setError("Something went wrong talking to the engine. Try a refresh.");
      }
    }
  }, [router]);

  useEffect(() => {
    load();
  }, [load]);

  // All mutations return the freshly recomputed dashboard. Show the readiness
  // delta as a toast — the "route recalculated" moment.
  const mutate = useCallback(
    async (fn: () => Promise<Dashboard>, silent = false) => {
      setRefreshing(true);
      try {
        const before = dash?.readiness.readiness_pct ?? 0;
        const next = await fn();
        setDash(next);
        if (!silent) {
          const delta =
            Math.round((next.readiness.readiness_pct - before) * 10) / 10;
          toastSeq.current += 1;
          if (delta !== 0) {
            setToast({
              id: toastSeq.current,
              kind: delta > 0 ? "up" : "down",
              title: `Readiness ${delta > 0 ? "+" : ""}${delta} pts → ${next.readiness.readiness_pct}%`,
              body: "Route recalculated",
            });
          } else {
            setToast({
              id: toastSeq.current,
              kind: "info",
              title: "Route recalculated",
            });
          }
        }
      } finally {
        setRefreshing(false);
      }
    },
    [dash],
  );

  if (wakeFailed || waking)
    return (
      <WakingOverlay
        elapsed={wakeElapsed}
        failed={wakeFailed}
        onRetry={load}
      />
    );

  if (error)
    return (
      <main className="flex-1 grid place-items-center px-6">
        <div className="max-w-md text-center">
          <p className="text-sm text-critical">{error}</p>
          <button
            type="button"
            onClick={load}
            className="mt-4 rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-strong transition-colors"
          >
            Retry
          </button>
        </div>
      </main>
    );

  if (!dash || !studentId)
    return (
      <main className="flex-1 grid place-items-center">
        <p className="text-sm text-muted anim-pulse">Computing your route…</p>
      </main>
    );

  return (
    <main className="flex-1">
      {/* Top bar */}
      <header className="border-b border-hairline bg-surface/70 backdrop-blur sticky top-0 z-10">
        <div className="mx-auto max-w-6xl px-6 py-3 flex items-center justify-between gap-3">
          <Link href="/" className="flex items-center gap-2 shrink-0">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-accent" />
            <span className="font-semibold tracking-tight">CareerMap</span>
          </Link>
          <div className="flex items-center gap-2 sm:gap-3">
            {refreshing && (
              <span className="hidden sm:inline text-xs text-muted anim-pulse">
                recalculating…
              </span>
            )}
            <button
              type="button"
              onClick={() => mutate(() => api.advanceSemester(studentId))}
              className="text-xs text-ink2 hover:text-ink border border-hairline rounded-lg px-3 py-1.5 transition-colors whitespace-nowrap"
              title="Move to the next semester and replan"
            >
              Advance semester →
            </button>
            <button
              type="button"
              onClick={() => {
                localStorage.removeItem(STUDENT_KEY);
                router.push("/onboarding");
              }}
              className="hidden sm:inline text-xs text-muted hover:text-ink2 transition-colors"
            >
              New profile
            </button>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <div
        className={`mx-auto max-w-6xl px-6 py-8 space-y-6 transition-opacity duration-200 ${
          refreshing ? "opacity-60" : "opacity-100"
        }`}
      >
        {/* Hero + tiles */}
        <div className="anim-fade-up">
          <ReadinessHero dash={dash} />
        </div>
        <StatTiles dash={dash} />

        {/* Main grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6 stagger">
            <NextSteps dash={dash} />
            <RoadmapTimeline dash={dash} />
            <WeeklyPlanList dash={dash} />
            <OpportunityList dash={dash} />
          </div>
          <div className="space-y-6 stagger">
            <ProgressPanel
              dash={dash}
              onSetSkill={(skill, level) =>
                mutate(() => api.setSkill(studentId, skill, level))
              }
            />
            <SkillGapBars dash={dash} />
            <MilestoneChecklist
              dash={dash}
              onToggle={(id, done) =>
                mutate(() => api.setMilestone(studentId, id, done))
              }
            />
            <MentorChat studentId={studentId} />
          </div>
        </div>
      </div>

      <Toast toast={toast} onDone={() => setToast(null)} />
    </main>
  );
}
