"use client";

/** KPI row of stat tiles (dataviz stat-tile contract: label, value, optional
 * caption; proportional figures; no chart chrome). */

import { Dashboard } from "@/lib/api";

export default function StatTiles({ dash }: { dash: Dashboard }) {
  const dueDone = dash.milestones.due_completion_pct;
  const eligible = dash.opportunities.filter((o) => o.eligible).length;
  const weeks = dash.weekly_plan.length;
  const hours = dash.profile.constraints.daily_study_hours;

  const tiles = [
    {
      label: "Milestones done",
      value: `${dash.milestones.completed_count}/${dash.milestones.total_count}`,
      caption: `${dueDone}% of what's due now`,
    },
    {
      label: "Opportunities open",
      value: String(eligible),
      caption: "eligible today",
    },
    {
      label: "Plan horizon",
      value: `${weeks} wk`,
      caption: "this semester",
    },
    {
      label: "Study budget",
      value: `${Math.round(hours * 7)}h`,
      caption: `per week (${hours}h/day)`,
    },
  ];

  return (
    <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {tiles.map((t) => (
        <div
          key={t.label}
          className="rounded-xl border border-hairline bg-surface p-5"
        >
          <p className="text-xs text-ink2">{t.label}</p>
          <p className="mt-1 text-2xl font-semibold tracking-tight">
            {t.value}
          </p>
          <p className="mt-0.5 text-xs text-muted">{t.caption}</p>
        </div>
      ))}
    </section>
  );
}
