import { cn } from "../../lib/cn";

export default function PageHeader({ title, subtitle, action, compact = false }) {
  return (
    <header className={cn("shrink-0", compact ? "mb-3" : "mb-6 md:mb-8")}>
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1
            className={cn(
              "font-semibold tracking-tight text-white",
              compact ? "text-xl md:text-2xl" : "text-2xl md:text-3xl"
            )}
          >
            {title}
          </h1>
          {subtitle && (
            <p
              className={cn(
                "mt-1 max-w-2xl leading-relaxed text-slate-400",
                compact ? "text-xs md:text-sm" : "text-sm md:text-base"
              )}
            >
              {subtitle}
            </p>
          )}
        </div>
        {action}
      </div>
    </header>
  );
}
