import { cn } from "../../lib/cn";

const variants = {
  primary:
    "bg-gradient-to-l from-accent to-accent-muted text-white shadow-md hover:shadow-glow hover:brightness-110",
  secondary:
    "border border-glass-border bg-glass text-slate-200 hover:bg-white/10",
  ghost: "text-slate-300 hover:bg-white/8 hover:text-white",
  grounding:
    "bg-gradient-to-l from-teal-700 to-teal-500 text-white shadow-md hover:brightness-110",
  danger: "border border-red-400/30 text-red-200 hover:bg-red-500/10",
};

const sizes = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2 text-sm",
  lg: "px-5 py-2.5 text-base",
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
        "disabled:cursor-not-allowed disabled:opacity-50",
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
