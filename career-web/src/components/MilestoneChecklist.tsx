"use client";

/** Interactive milestone checklist — toggling PATCHes the API and the parent
 * refreshes the whole dashboard (the continuous-update loop, visible). */

import { Dashboard } from "@/lib/api";
import { useState } from "react";

const CATEGORY_LABELS: Record<string, string> = {
  profile: "Profile & presence",
  coding: "Coding practice",
  experience: "Real-world experience",
  interview: "Interview funnel",
};

export default function MilestoneChecklist({
  dash,
  onToggle,
}: {
  dash: Dashboard;
  onToggle: (id: string, done: boolean) => Promise<void>;
}) {
  const [pending, setPending] = useState<string | null>(null);
  const byCat = new Map<string, typeof dash.milestones.statuses>();
  for (const s of dash.milestones.statuses) {
    if (!byCat.has(s.category)) byCat.set(s.category, []);
    byCat.get(s.category)!.push(s);
  }

  async function toggle(id: string, done: boolean) {
    setPending(id);
    try {
      await onToggle(id, done);
    } finally {
      setPending(null);
    }
  }

  return (
    <section className="rounded-2xl border border-hairline bg-surface p-6">
      <div className="flex items-baseline justify-between gap-2">
        <h3 className="font-semibold">Milestones</h3>
        <span className="text-xs text-ink2">
          {dash.milestones.completion_pct}% overall
        </span>
      </div>

      {/* completion meter — same-ramp track */}
      <div className="mt-3 h-2 w-full rounded-full bg-accent-track">
        <div
          className="h-2 rounded-full bg-accent"
          style={{ width: `${dash.milestones.completion_pct}%` }}
        />
      </div>

      <div className="mt-5 space-y-5">
        {[...byCat.entries()].map(([cat, items]) => (
          <div key={cat}>
            <p className="text-xs font-medium text-muted uppercase tracking-wide">
              {CATEGORY_LABELS[cat] ?? cat}
            </p>
            <ul className="mt-2 space-y-1">
              {items.map((m) => (
                <li key={m.id}>
                  <button
                    type="button"
                    disabled={pending === m.id}
                    onClick={() => toggle(m.id, !m.completed)}
                    className={`flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-left text-sm transition-colors hover:bg-plane ${
                      pending === m.id ? "opacity-60" : ""
                    }`}
                  >
                    <span
                      className={`grid h-5 w-5 shrink-0 place-items-center rounded-md border text-[11px] ${
                        m.completed
                          ? "border-accent bg-accent text-white"
                          : "border-baseline"
                      }`}
                    >
                      {m.completed ? "✓" : ""}
                    </span>
                    <span
                      className={
                        m.completed
                          ? "text-muted line-through decoration-baseline"
                          : m.due_now
                            ? ""
                            : "text-muted"
                      }
                    >
                      {m.name}
                    </span>
                    {!m.due_now && !m.completed && (
                      <span className="ml-auto text-[10px] text-muted whitespace-nowrap">
                        sem {m.relevant_from_semester}+
                      </span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
