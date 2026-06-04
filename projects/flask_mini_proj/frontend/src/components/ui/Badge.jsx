import { cn } from "../../lib/cn";

const categoryStyles = {
  medication: "bg-amber-500/15 text-amber-200 border-amber-400/25",
  grounding: "bg-teal-500/15 text-teal-200 border-teal-400/25",
  sleep: "bg-indigo-500/15 text-indigo-200 border-indigo-400/25",
  routine: "bg-accent/15 text-accent-light border-accent/25",
  cognitive_load: "bg-violet-500/15 text-violet-200 border-violet-400/25",
};

export default function Badge({ children, category, className }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        category ? categoryStyles[category] : "bg-white/10 text-slate-300 border-white/15",
        className
      )}
    >
      {children}
    </span>
  );
}
