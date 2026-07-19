"use client";

/** Full-screen friendly overlay while the free-tier engine cold-starts. */
export default function WakingOverlay({
  elapsed,
  failed,
  onRetry,
}: {
  elapsed: number;
  failed: boolean;
  onRetry: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-plane/90 backdrop-blur-sm anim-fade-in">
      <div className="mx-6 max-w-sm rounded-2xl border border-hairline bg-surface p-8 text-center shadow-xl">
        {failed ? (
          <>
            <p className="text-3xl">😴</p>
            <h3 className="mt-3 font-semibold">Engine didn&apos;t wake up</h3>
            <p className="mt-2 text-sm text-ink2 leading-relaxed">
              The free-tier server can be slow on the first request. Give it
              another try.
            </p>
            <button
              type="button"
              onClick={onRetry}
              className="mt-5 rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-strong transition-colors"
            >
              Retry
            </button>
          </>
        ) : (
          <>
            {/* route-drawing spinner */}
            <svg
              className="mx-auto"
              width="44"
              height="44"
              viewBox="0 0 44 44"
              fill="none"
            >
              <circle
                cx="22"
                cy="22"
                r="18"
                stroke="var(--accent-track)"
                strokeWidth="4"
              />
              <circle
                cx="22"
                cy="22"
                r="18"
                stroke="var(--accent)"
                strokeWidth="4"
                strokeLinecap="round"
                strokeDasharray="40 80"
                className="origin-center animate-spin [animation-duration:1.2s]"
              />
            </svg>
            <h3 className="mt-4 font-semibold">Waking the engine…</h3>
            <p className="mt-2 text-sm text-ink2 leading-relaxed">
              Free hosting naps when idle. This takes ~30–50 seconds the
              first time — after that it&apos;s instant.
            </p>
            <p className="mt-3 text-xs text-muted tabular-nums">
              {elapsed}s elapsed
            </p>
          </>
        )}
      </div>
    </div>
  );
}
