"use client";

/** Weekly plan (accordion) + opportunities list. */

import { Dashboard } from "@/lib/api";
import { useState } from "react";

export function WeeklyPlanList({ dash }: { dash: Dashboard }) {
  const [open, setOpen] = useState<number | null>(1);
  const plan = dash.weekly_plan;
  if (!plan.length)
    return (
      <section className="rounded-2xl border border-hairline bg-surface p-6">
        <h3 className="font-semibold">This semester, week by week</h3>
        <p className="mt-2 text-sm text-ink2">
          Nothing scheduled this semester — you&apos;re ahead of the route.
        </p>
      </section>
    );

  return (
    <section className="rounded-2xl border border-hairline bg-surface p-6">
      <h3 className="font-semibold">This semester, week by week</h3>
      <p className="mt-1 text-xs text-muted">
        Sized to your {dash.profile.constraints.daily_study_hours}h/day budget
      </p>
      <ol className="mt-4 space-y-2">
        {plan.map((w) => {
          const isOpen = open === w.week;
          return (
            <li
              key={w.week}
              className="rounded-xl border border-hairline overflow-hidden"
            >
              <button
                type="button"
                onClick={() => setOpen(isOpen ? null : w.week)}
                className="flex w-full items-center gap-3 px-4 py-3 text-left text-sm hover:bg-plane transition-colors"
              >
                <span className="text-xs font-semibold text-muted w-12 shrink-0">
                  W{w.week}
                </span>
                <span className="font-medium flex-1 min-w-0 truncate">
                  {w.focus_skill}
                </span>
                <span className="text-xs text-ink2 whitespace-nowrap">
                  ~{w.estimated_hours}h
                </span>
                <span className="text-muted text-xs">{isOpen ? "−" : "+"}</span>
              </button>
              {isOpen && (
                <div className="border-t border-hairline px-4 py-3 text-sm space-y-2 bg-plane/50">
                  <p className="text-ink2">{w.topics}</p>
                  <ul className="space-y-1 text-xs text-ink2">
                    <li>🏋️ {w.practice}</li>
                    <li>🚀 {w.project_or_milestone}</li>
                    <li>🔁 {w.revision}</li>
                    {w.interview_prep && <li>🎤 {w.interview_prep}</li>}
                  </ul>
                  {w.resources.length > 0 && (
                    <div className="pt-1">
                      <p className="text-xs font-medium text-muted uppercase tracking-wide">
                        Resources
                      </p>
                      <ul className="mt-1 space-y-1">
                        {w.resources.map((r) => (
                          <li key={r.url}>
                            <a
                              href={r.url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-xs text-accent hover:underline"
                            >
                              {r.title}
                            </a>
                            <span className="ml-1.5 text-[10px] text-muted">
                              {r.kind}
                              {!r.free && " · paid"}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ol>
    </section>
  );
}

const KIND_ICONS: Record<string, string> = {
  internship: "💼",
  open_source: "🌱",
  hackathon: "⚡",
  contest: "🏆",
  fellowship: "🎓",
  scholarship: "🎓",
  ambassador: "📣",
  research: "🔬",
};

export function OpportunityList({ dash }: { dash: Dashboard }) {
  const opps = dash.opportunities;
  if (!opps.length) return null;
  const eligible = opps.filter((o) => o.eligible);
  const nearMiss = opps.filter((o) => !o.eligible);

  return (
    <section className="rounded-2xl border border-hairline bg-surface p-6">
      <h3 className="font-semibold">Opportunities for you</h3>
      <p className="mt-1 text-xs text-muted">
        Filtered to your semester and role — nothing irrelevant
      </p>

      <ul className="mt-4 space-y-2">
        {eligible.map((m) => (
          <li key={m.opportunity.id}>
            <a
              href={m.opportunity.url}
              target="_blank"
              rel="noreferrer"
              className="flex items-start gap-3 rounded-xl border border-hairline p-4 hover:border-baseline transition-colors"
            >
              <span className="text-lg leading-none mt-0.5">
                {KIND_ICONS[m.opportunity.kind] ?? "✨"}
              </span>
              <span className="min-w-0 flex-1">
                <span className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-medium">
                    {m.opportunity.name}
                  </span>
                  <span className="rounded-full bg-good/10 px-2 py-0.5 text-[10px] font-semibold text-goodtext uppercase tracking-wide">
                    eligible
                  </span>
                </span>
                <span className="mt-0.5 block text-xs text-ink2">
                  {m.opportunity.description}
                </span>
              </span>
            </a>
          </li>
        ))}
      </ul>

      {nearMiss.length > 0 && (
        <>
          <p className="mt-5 text-xs font-medium text-muted uppercase tracking-wide">
            Almost — here&apos;s what&apos;s missing
          </p>
          <ul className="mt-2 space-y-2">
            {nearMiss.map((m) => (
              <li
                key={m.opportunity.id}
                className="rounded-xl border border-hairline p-4 opacity-80"
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg leading-none">
                    {KIND_ICONS[m.opportunity.kind] ?? "✨"}
                  </span>
                  <span className="text-sm font-medium">
                    {m.opportunity.name}
                  </span>
                </div>
                <ul className="mt-1.5 space-y-0.5">
                  {m.missing.map((miss) => (
                    <li key={miss} className="text-xs text-ink2">
                      → {miss}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
