import { Shield } from "lucide-react";
import { cn } from "../../lib/cn";
import { useLocale } from "../../context/LocaleContext";

export default function DisclaimerBar({ compact = false }) {
  const { uiDisclaimer } = useLocale();

  return (
    <div
      className={cn(
        "flex shrink-0 items-start gap-2 rounded-lg border border-white/8 bg-white/[0.03] text-slate-500 backdrop-blur-sm",
        compact
          ? "mb-2 px-2.5 py-1.5 text-[0.65rem] leading-snug"
          : "mb-4 px-3 py-2 text-[0.7rem] leading-snug md:mb-5"
      )}
      role="note"
    >
      <Shield
        className={cn("shrink-0 text-accent/50", compact ? "mt-px h-3 w-3" : "mt-0.5 h-3.5 w-3.5")}
        aria-hidden
      />
      <p className="opacity-90">{uiDisclaimer}</p>
    </div>
  );
}
