"use client";

/** "I learned something" panel — bump a skill level and watch the whole
 * dashboard recompute. This is the rerouting moment made tangible. */

import { Dashboard } from "@/lib/api";
import { useState } from "react";

const SKILL_LABELS: Record<string, string> = {};

export default function ProgressPanel({
  dash,
  onSetSkill,
}: {
  dash: Dashboard;
  onSetSkill: (skill: string, level: number) => Promise<void>;
}) {
  const [pendingSkill, setPendingSkill] = useState<string | null>(null);

  // Offer the skills most worth updating: current gaps first.
  const gapSkills = dash.readiness.gaps.map((g) => ({
    id: g.skill_id,
    name: g.name,
    level: g.current_level,
  }));

  async function bump(skill: string, level: number) {
    setPendingSkill(skill);
    try {
      await onSetSkill(skill, level);
    } finally {
      setPendingSkill(null);
    }
  }

  return (
    <section className="rounded-2xl border border-hairline bg-surface p-6">
      <h3 className="font-semibold">Log progress</h3>
      <p className="mt-1 text-xs text-muted">
        Learned something? Update your level — the route recalculates
        instantly.
      </p>
      <ul className="mt-4 space-y-2.5">
        {gapSkills.slice(0, 6).map((s) => (
          <li
            key={s.id}
            className={`flex items-center justify-between gap-3 ${
              pendingSkill === s.id ? "opacity-60" : ""
            }`}
          >
            <span className="text-sm min-w-0 truncate">
              {SKILL_LABELS[s.id] ?? s.name}
            </span>
            <div className="flex gap-1">
              {[0, 1, 2, 3, 4, 5].map((v) => (
                <button
                  key={v}
                  type="button"
                  disabled={pendingSkill !== null}
                  onClick={() => bump(s.id, v)}
                  className={`h-7 w-7 rounded-md border text-[11px] transition-colors ${
                    s.level === v
                      ? "border-accent bg-accent text-white"
                      : "border-hairline text-ink2 hover:border-baseline"
                  }`}
                >
                  {v}
                </button>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
