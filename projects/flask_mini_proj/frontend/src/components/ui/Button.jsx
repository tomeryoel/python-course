import { cn } from "../../lib/cn";

const variants = {
  primary:
    "bg-gradient-to-l from-accent to-accent-dim text-white shadow-lg shadow-accent/25 hover:shadow-glow hover:brightness-110",
  secondary:
    "border border-white/12 bg-white/[0.06] text-slate-200 hover:bg-white/10 hover:border-white/20",
  ghost: "text-slate-400 hover:bg-white/8 hover:text-white",
  grounding:
    "bg-gradient-to-l from-teal-700 to-teal-500 text-white shadow-lg shadow-teal-900/30 hover:brightness-110",
  danger: "border border-red-400/30 text-red-200 hover:bg-red-500/10",
};

const sizes = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2.5 text-sm",
  lg: "px-6 py-3 text-base",
};

export default function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}) {
  return (
    <button
      type="button"
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all duration-200",
        "disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none",
        "focus-ring",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
