"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { api, Dashboard, STUDENT_KEY } from "@/lib/api";
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

export default function DashboardPage() {
  const router = useRouter();
  const [studentId, setStudentId] = useState<string | null>(null);
  const [dash, setDash] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    // Deep-link support: /dashboard?sid=<id> adopts that student.
    const fromQuery = new URLSearchParams(window.location.search).get("sid");
    if (fromQuery) localStorage.setItem(STUDENT_KEY, fromQuery);
    const id = fromQuery ?? localStorage.getItem(STUDENT_KEY);
    if (!id) {
      router.replace("/onboarding");
      return;
    }
    setStudentId(id);
    api
      .dashboard(id)
      .then(setDash)
      .catch((e) => {
        // Unknown student (server restarted with a fresh DB) -> re-onboard.
        if (String(e).includes("404")) {
          localStorage.removeItem(STUDENT_KEY);
          router.replace("/onboarding");
        } else {
          setError(
            "Could not reach the engine API on :8000. Start it with `uvicorn app.main:app` in career-engine.",
          );
        }
      });
  }, [router]);

  // All mutations return the freshly recomputed dashboard; hold the previous
  // render at reduced opacity while swapping (no skeleton flash).
  const mutate = useCallback(
    async (fn: () => Promise<Dashboard>) => {
      setRefreshing(true);
      try {
        setDash(await fn());
      } finally {
        setRefreshing(false);
      }
    },
    [],
  );

  if (error)
    return (
      <main className="flex-1 grid place-items-center px-6">
        <div className="max-w-md text-center">
          <p className="text-sm text-critical">{error}</p>
          <Link href="/" className="mt-4 inline-block text-sm text-accent">
            ← Home
          </Link>
        </div>
      </main>
    );

  if (!dash || !studentId)
    return (
      <main className="flex-1 grid place-items-center">
        <p className="text-sm text-muted animate-pulse">
          Computing your route…
        </p>
      </main>
    );

  return (
    <main className="flex-1">
      {/* Top bar */}
      <header className="border-b border-hairline bg-surface/60 backdrop-blur sticky top-0 z-10">
        <div className="mx-auto max-w-6xl px-6 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-accent" />
            <span className="font-semibold tracking-tight">CareerMap</span>
          </Link>
          <div className="flex items-center gap-4">
            {refreshing && (
              <span className="text-xs text-muted animate-pulse">
                recalculating route…
              </span>
            )}
            <button
              type="button"
              onClick={() =>
                mutate(() => api.advanceSemester(studentId))
              }
              className="text-xs text-ink2 hover:text-ink border border-hairline rounded-lg px-3 py-1.5 transition-colors"
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
              className="text-xs text-muted hover:text-ink2 transition-colors"
            >
              New profile
            </button>
          </div>
        </div>
      </header>

      <div
        className={`mx-auto max-w-6xl px-6 py-8 space-y-6 transition-opacity ${
          refreshing ? "opacity-60" : "opacity-100"
        }`}
      >
        {/* Hero + tiles */}
        <ReadinessHero dash={dash} />
        <StatTiles dash={dash} />

        {/* Main grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <NextSteps dash={dash} />
            <RoadmapTimeline dash={dash} />
            <WeeklyPlanList dash={dash} />
            <OpportunityList dash={dash} />
          </div>
          <div className="space-y-6">
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
    </main>
  );
}
