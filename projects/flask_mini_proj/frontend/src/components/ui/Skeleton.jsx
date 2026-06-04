import { cn } from "../../lib/cn";

export function Skeleton({ className }) {
  return (
    <div
      className={cn("animate-pulse rounded-xl bg-white/8", className)}
      aria-hidden
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="glass-panel space-y-3 p-5">
      <Skeleton className="h-5 w-1/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-4/5" />
    </div>
  );
}
