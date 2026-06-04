import { cn } from "../../lib/cn";

export default function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-2xl border border-dashed border-glass-border",
        "bg-glass/50 px-6 py-12 text-center animate-fade-in",
        className
      )}
    >
      {Icon && (
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-accent/10 text-accent-light">
          <Icon className="h-7 w-7" strokeWidth={1.5} />
        </div>
      )}
      <h4 className="text-base font-medium text-slate-200">{title}</h4>
      {description && (
        <p className="mt-2 max-w-sm text-sm leading-relaxed text-slate-400">{description}</p>
      )}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
