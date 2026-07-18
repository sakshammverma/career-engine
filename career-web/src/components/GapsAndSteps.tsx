"use client";

/** Highest-ROI next steps + skill gap bars.
 * Gap bars: one series -> every bar wears slot-1 accent (never a value ramp on
 * nominal categories). Thin marks, 4px rounded data-end, value labeled at the
 * tip, target shown as an ink tick on a same-surface track. */

import { Dashboard } from "@/lib/api";

export function NextSteps({ dash }: { dash: Dashboard }) {
  const recs = dash.readiness.recommendations;
  if (!recs.length)
    return (
      <section className="rounded-2xl border border-hairline bg-surface p-6">
        <h3 className="font-semibold">Next steps</h3>
        <p className="mt-2 text-sm text-ink2">
          No gaps left — you meet every requirement for this role. 🎉
        </p>
      </section>
    );

  return (
    <section className="rounded-2xl border border-hairline bg-surface p-6">
      <h3 className="font-semibold">Highest-ROI next steps</h3>
      <p className="mt-1 text-xs text-muted">
        Ranked by readiness gained per hour of effort
      </p>
      <ol className="mt-4 space-y-3">
        {recs.map((r, i) => (
          <li
            key={r.skill_id}
            className="flex items-start gap-3 rounded-xl border border-hairline p-4"
          >
            <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-accent text-xs font-semibold text-white">
              {i + 1}
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline justify-between gap-2 flex-wrap">
                <span className="font-medium text-sm">{r.name}</span>
                <span className="text-xs text-ink2 whitespace-nowrap">
                  +{r.readiness_gain} pts · ~{r.effort_hours}h
                </span>
              </div>
              {r.blocked_by.length > 0 ? (
                <p className="mt-1 text-xs text-muted">
                  🔒 unlocks after {r.blocked_by.join(", ")}
                </p>
              ) : (
                <p className="mt-1 text-xs text-goodtext">● ready to start</p>
              )}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

export function SkillGapBars({ dash }: { dash: Dashboard }) {
  const gaps = dash.readiness.gaps.slice(0, 8);
  if (!gaps.length) return null;

  return (
    <section className="rounded-2xl border border-hairline bg-surface p-6">
      <h3 className="font-semibold">Skill gaps</h3>
      <p className="mt-1 text-xs text-muted">
        Your level vs what the role expects (| = target)
      </p>
      <div className="mt-4 space-y-3">
        {gaps.map((g) => {
          const cur = (g.current_level / 5) * 100;
          const tgt = (g.target_level / 5) * 100;
          return (
            <div key={g.skill_id} title={`${g.name}: ${g.current_level} of ${g.target_level} needed`}>
              <div className="flex items-baseline justify-between">
                <span className="text-sm">{g.name}</span>
                <span className="text-xs text-ink2">
                  {g.current_level} / {g.target_level}
                </span>
              </div>
              <div className="relative mt-1.5 h-2.5 w-full rounded-full bg-plane border border-hairline">
                {/* current level fill — slot-1 accent, rounded data end */}
                <div
                  className="absolute inset-y-0 left-0 rounded-full bg-accent"
                  style={{ width: `${cur}%` }}
                />
                {/* target tick — ink, not a color */}
                <div
                  className="absolute top-[-3px] bottom-[-3px] w-0.5 bg-ink rounded"
                  style={{ left: `calc(${tgt}% - 1px)` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
