"use client";

/** AI mentor chat. Shows mode badge (AI vs offline) and a collapsible
 * "grounded on" context so answers are transparent. */

import { api, MentorReply } from "@/lib/api";
import { useRef, useState } from "react";

interface Turn {
  q: string;
  a?: MentorReply;
}

const SUGGESTIONS = [
  "What should I focus on this month?",
  "Am I on track for my target role?",
  "How do I prepare for internships?",
];

export default function MentorChat({ studentId }: { studentId: string }) {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [showCtx, setShowCtx] = useState<number | null>(null);
  const scroller = useRef<HTMLDivElement>(null);

  async function ask(q: string) {
    if (!q.trim() || busy) return;
    setBusy(true);
    setInput("");
    setTurns((t) => [...t, { q }]);
    queueMicrotask(() =>
      scroller.current?.scrollTo({ top: 1e6, behavior: "smooth" }),
    );
    try {
      const reply = await api.askMentor(studentId, q);
      setTurns((t) => {
        const copy = [...t];
        copy[copy.length - 1] = { q, a: reply };
        return copy;
      });
    } catch {
      setTurns((t) => {
        const copy = [...t];
        copy[copy.length - 1] = {
          q,
          a: {
            answer: "Could not reach the mentor. Is the API running?",
            mode: "offline",
            context: "",
          },
        };
        return copy;
      });
    } finally {
      setBusy(false);
      queueMicrotask(() =>
        scroller.current?.scrollTo({ top: 1e6, behavior: "smooth" }),
      );
    }
  }

  return (
    <section className="rounded-2xl border border-hairline bg-surface p-6 flex flex-col">
      <h3 className="font-semibold">AI mentor</h3>
      <p className="mt-1 text-xs text-muted">
        Grounded in your live dashboard — it knows your gaps, plan, and
        milestones
      </p>

      <div
        ref={scroller}
        className="thin-scroll mt-4 max-h-80 space-y-4 overflow-y-auto pr-1"
      >
        {turns.length === 0 && (
          <div className="space-y-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => ask(s)}
                className="block w-full rounded-lg border border-hairline px-3 py-2 text-left text-sm text-ink2 hover:text-ink hover:border-baseline transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {turns.map((t, i) => (
          <div key={i} className="space-y-2">
            <p className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-accent px-3.5 py-2 text-sm text-white">
              {t.q}
            </p>
            {t.a ? (
              <div className="w-fit max-w-[92%] rounded-2xl rounded-bl-md border border-hairline bg-plane px-3.5 py-2.5">
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {t.a.answer}
                </p>
                <div className="mt-2 flex items-center gap-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${
                      t.a.mode === "llm"
                        ? "bg-accent/10 text-accent"
                        : "bg-plane border border-hairline text-muted"
                    }`}
                  >
                    {t.a.mode === "llm" ? "AI" : "offline"}
                  </span>
                  {t.a.context && (
                    <button
                      type="button"
                      onClick={() => setShowCtx(showCtx === i ? null : i)}
                      className="text-[10px] text-muted hover:text-ink2"
                    >
                      {showCtx === i ? "hide grounding" : "grounded on…"}
                    </button>
                  )}
                </div>
                {showCtx === i && (
                  <pre className="thin-scroll mt-2 max-h-40 overflow-auto rounded-lg border border-hairline bg-surface p-2 text-[10px] leading-relaxed text-ink2">
                    {t.a.context}
                  </pre>
                )}
              </div>
            ) : (
              <p className="w-fit rounded-2xl rounded-bl-md border border-hairline bg-plane px-3.5 py-2.5 text-sm text-muted">
                thinking…
              </p>
            )}
          </div>
        ))}
      </div>

      <form
        className="mt-4 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about your path…"
          className="flex-1 rounded-lg border border-hairline bg-plane px-3 py-2 text-sm outline-none focus:border-accent transition-colors"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-strong disabled:opacity-50 transition-colors"
        >
          Ask
        </button>
      </form>
    </section>
  );
}
