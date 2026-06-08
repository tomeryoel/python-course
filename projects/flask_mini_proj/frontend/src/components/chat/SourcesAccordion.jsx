import { ChevronDown } from "lucide-react";
import { useLocale } from "../../context/LocaleContext";

export default function SourcesAccordion({ sources }) {
  const { t } = useLocale();

  return (
    <details className="group mt-2 text-xs text-slate-400">
      <summary className="flex cursor-pointer list-none items-center gap-1 rounded-lg py-1 hover:text-accent-light focus-ring">
        <ChevronDown className="h-3.5 w-3.5 transition-transform group-open:rotate-180" />
        {t("sources")} ({sources.length})
      </summary>
      <ul className="mt-2 space-y-1.5 rounded-lg border border-glass-border bg-black/20 p-3">
        {sources.map((s, j) => (
          <li key={j} className="leading-relaxed text-slate-400">
            {s.display_name || s.text_preview || s.uri || `מקור ${j + 1}`}
          </li>
        ))}
      </ul>
    </details>
  );
}
