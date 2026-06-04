import { cn } from "../../lib/cn";

export default function LoadingDots({ className }) {
  return (
    <span className={cn("inline-flex gap-1.5", className)} aria-label="טוען">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-2 w-2 rounded-full bg-accent-light animate-pulse-soft"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </span>
  );
}
