import { cn } from "../../lib/cn";

/** Calm, premium empty state with a soft glowing icon halo. */
export default function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/10",
        "bg-white/[0.02] px-6 py-12 text-center animate-fade-in",
        className
      )}
    >
      {Icon && (
        <div className="relative mb-5">
          <div className="absolute inset-0 rounded-2xl bg-accent/20 blur-xl" aria-hidden />
          <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-gradient-to-b from-accent/20 to-accent/5 text-accent-light">
            <Icon className="h-7 w-7" strokeWidth={1.5} />
          </div>
        </div>
      )}
      <h4 className="text-base font-medium text-slate-100">{title}</h4>
      {description && (
        <p className="mt-2 max-w-sm text-sm leading-relaxed text-slate-400">{description}</p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
