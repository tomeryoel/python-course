import { AlertCircle } from "lucide-react";
import { cn } from "../../lib/cn";

export default function ErrorAlert({ message, className }) {
  if (!message) return null;
  return (
    <div
      role="alert"
      className={cn(
        "flex items-start gap-3 rounded-xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-100",
        className
      )}
    >
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-300" />
      <p className="leading-relaxed">{message}</p>
    </div>
  );
}
