import { Shield } from "lucide-react";
import { useLocale } from "../../context/LocaleContext";

export default function DisclaimerBar() {
  const { uiDisclaimer } = useLocale();

  return (
    <div
      className="mb-4 flex items-start gap-2 rounded-lg border border-glass-border bg-glass/60 px-3 py-2 text-[0.7rem] leading-snug text-slate-400 backdrop-blur-md md:mb-5"
      role="note"
    >
      <Shield className="mt-0.5 h-3.5 w-3.5 shrink-0 text-accent/70" aria-hidden />
      <p>{uiDisclaimer}</p>
    </div>
  );
}
