"use client";

/** Hero readiness figure + projection meter.
 * Dataviz: one hero figure per view (>=48px, system sans, proportional
 * figures); meter fill = accent, unfilled track = lighter step of the SAME
 * ramp; text wears ink tokens, never the series color. */

import { useEffect, useRef, useState } from "react";
import { Dashboard } from "@/lib/api";

/** Count-up that eases toward the target whenever it changes. */
function useCountUp(target: number, ms = 700) {
  const [value, setValue] = useState(target);
  const fromRef = useRef(target);
  useEffect(() => {
    const from = fromRef.current;
    if (from === target) return;
    let raf: number;
    const t0 = performance.now();
    const tick = (t: number) => {
      const p = Math.min(1, (t - t0) / ms);
      const eased = 1 - Math.pow(1 - p, 3);
      setValue(Math.round((from + (target - from) * eased) * 10) / 10);
      if (p < 1) raf = requestAnimationFrame(tick);
      else fromRef.current = target;
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, ms]);
  return value;
}

export default function ReadinessHero({ dash }: { dash: Dashboard }) {
  const now = dash.readiness.readiness_pct;
  const projected = dash.readiness.projected_readiness_pct;
  const gain = Math.round((projected - now) * 10) / 10;
  const shown = useCountUp(now);
  const roleName = dash.roadmap.role
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <section className="rounded-2xl border border-hairline bg-surface p-8">
      <p className="text-sm text-ink2">
        Career readiness — {roleName}, semester{" "}
        {dash.profile.academic.current_semester}
      </p>

      <div className="mt-2 flex items-end gap-4 flex-wrap">
        <span className="text-6xl font-semibold leading-none tracking-tight">
          {shown}%
        </span>
        {gain > 0 && (
          <span className="mb-1 text-sm font-medium text-goodtext">
            ↑ +{gain} pts after next steps
          </span>
        )}
      </div>

      {/* Meter: current fill + projected extension on a same-ramp track */}
      <div className="mt-6">
        <div
          className="relative h-3 w-full rounded-full bg-accent-track overflow-hidden"
          role="meter"
          aria-valuenow={now}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Readiness ${now} percent, projected ${projected} percent`}
        >
          {/* projected segment (soft step of same ramp) */}
          <div
            className="absolute inset-y-0 left-0 rounded-full bg-accent-soft transition-[width] duration-700 ease-out anim-meter"
            style={{ width: `${Math.min(projected, 100)}%` }}
          />
          {/* current segment */}
          <div
            className="absolute inset-y-0 left-0 rounded-full bg-accent transition-[width] duration-700 ease-out anim-meter"
            style={{ width: `${Math.min(now, 100)}%` }}
          />
        </div>
        <div className="mt-2 flex justify-between text-xs text-muted">
          <span>
            <span className="inline-block h-2 w-2 rounded-full bg-accent mr-1.5 align-middle" />
            now {now}%
          </span>
          <span>
            <span className="inline-block h-2 w-2 rounded-full bg-accent-soft mr-1.5 align-middle border border-hairline" />
            projected {projected}%
          </span>
        </div>
      </div>
    </section>
  );
}
