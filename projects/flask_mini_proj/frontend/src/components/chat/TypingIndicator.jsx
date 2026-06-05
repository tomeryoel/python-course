import { Sparkles } from "lucide-react";

/** Soft "assistant is typing" bubble with animated dots. */
export default function TypingIndicator({ label }) {
  return (
    <div className="flex w-full justify-start animate-fade-in">
      <div className="flex items-center gap-3 rounded-2xl rounded-bl-md border border-white/10 bg-gradient-to-b from-white/[0.1] to-white/[0.04] px-4 py-3 shadow-inner-soft">
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-accent/15 text-accent-light">
          <Sparkles className="h-3.5 w-3.5" />
        </span>
        <span className="inline-flex gap-1.5" aria-hidden>
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="h-2 w-2 rounded-full bg-accent-light animate-pulse-soft"
              style={{ animationDelay: `${i * 0.18}s` }}
            />
          ))}
        </span>
        <span className="text-sm text-slate-400">{label}</span>
      </div>
    </div>
  );
}
