import { cn } from "../../lib/cn";

export function Card({ className, children, ...props }) {
  return (
    <div className={cn("glass-panel p-5 md:p-6", className)} {...props}>
      {children}
    </div>
  );
}

export function CardHeader({ className, title, subtitle, action }) {
  return (
    <div className={cn("mb-4 flex flex-wrap items-start justify-between gap-3", className)}>
      <div>
        {title && <h3 className="text-lg font-semibold text-white">{title}</h3>}
        {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
