"use client";

import { useEffect } from "react";

export interface ToastData {
  id: number;
  title: string;
  body?: string;
  kind: "up" | "down" | "info";
}

/** Bottom-center toast — used for the "route recalculated" moment. */
export default function Toast({
  toast,
  onDone,
}: {
  toast: ToastData | null;
  onDone: () => void;
}) {
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(onDone, 3400);
    return () => clearTimeout(t);
  }, [toast, onDone]);

  if (!toast) return null;

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-6 z-50 flex justify-center px-4">
      <div
        key={toast.id}
        className="anim-toast pointer-events-auto flex items-center gap-3 rounded-xl border border-hairline bg-surface px-4 py-3 shadow-lg"
        role="status"
      >
        <span
          className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-sm ${
            toast.kind === "up"
              ? "bg-good/10 text-goodtext"
              : toast.kind === "down"
                ? "bg-critical/10 text-critical"
                : "bg-accent/10 text-accent"
          }`}
        >
          {toast.kind === "up" ? "↑" : toast.kind === "down" ? "↓" : "⟳"}
        </span>
        <div>
          <p className="text-sm font-semibold leading-tight">{toast.title}</p>
          {toast.body && (
            <p className="text-xs text-ink2 leading-tight mt-0.5">
              {toast.body}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
