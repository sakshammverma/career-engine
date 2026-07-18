"use client";

/** Semester roadmap as a vertical route (the Google-Maps metaphor):
 * a timeline with stops. Current semester emphasized (accent), future stops
 * recessive — emphasis form, not eight hues. */

import { Dashboard } from "@/lib/api";

export default function RoadmapTimeline({ dash }: { dash: Dashboard }) {
  const current = dash.roadmap.current_semester;

  return (
    <section className="rounded-2xl border border-hairline bg-surface p-6">
      <h3 className="font-semibold">Your route</h3>
      <p className="mt-1 text-xs text-muted">
        Semester-by-semester — prerequisites first, nothing before it&apos;s
        appropriate
      </p>

      <div className="mt-5 relative">
        {/* the route line */}
        <div className="absolute left-[11px] top-2 bottom-2 w-0.5 bg-grid" />

        <ol className="space-y-6">
          {dash.roadmap.semesters.map((sem) => {
            const isNow = sem.semester === current;
            return (
              <li key={sem.semester} className="relative pl-9">
                {/* stop marker */}
                <span
                  className={`absolute left-0 top-0.5 grid h-6 w-6 place-items-center rounded-full border-2 text-[10px] font-semibold ${
                    isNow
                      ? "border-accent bg-accent text-white"
                      : "border-baseline bg-surface text-ink2"
                  }`}
                >
                  {sem.semester}
                </span>

                <div className="flex items-baseline justify-between gap-2 flex-wrap">
                  <p
                    className={`text-sm font-medium ${isNow ? "" : "text-ink2"}`}
                  >
                    {sem.theme}
                    {isNow && (
                      <span className="ml-2 rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent uppercase tracking-wide">
                        you are here
                      </span>
                    )}
                  </p>
                  <span className="text-xs text-muted">
                    ~{sem.total_effort_hours}h
                  </span>
                </div>

                <div className="mt-2 flex flex-wrap gap-1.5">
                  {sem.items.map((item) => (
                    <span
                      key={item.skill_id}
                      title={`${item.rationale} ~${item.effort_hours}h`}
                      className={`rounded-md border px-2 py-1 text-xs ${
                        isNow
                          ? "border-accent/40 bg-accent/5 text-ink"
                          : "border-hairline text-ink2"
                      }`}
                    >
                      {item.name}
                    </span>
                  ))}
                </div>
              </li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
