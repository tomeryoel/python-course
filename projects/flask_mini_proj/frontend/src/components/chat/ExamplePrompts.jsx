import { Sparkles } from "lucide-react";
import { cn } from "../../lib/cn";
import { useLocale } from "../../context/LocaleContext";

/** Below chat panel — clearly separated, no overlap */
export default function ExamplePrompts({
  scenarios,
  generalQuestions,
  onSelect,
  disabled,
}) {
  const { t } = useLocale();

  return (
    <section
      className="shrink-0 rounded-2xl border border-white/8 bg-white/[0.02] p-4 shadow-card backdrop-blur-md md:p-5"
      aria-label="שאלות לדוגמה"
    >
      <div className="mb-4 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-slate-500">
        <Sparkles className="h-3.5 w-3.5 text-accent/70" />
        <span>הצעות מהירות</span>
      </div>

      <div className="space-y-5">
        <PromptGroup
          label={t("scenarios")}
          items={scenarios.map((s) => ({ key: s.label, label: s.label, text: s.text }))}
          onSelect={onSelect}
          disabled={disabled}
        />
        <PromptGroup
          label={t("generalQuestions")}
          items={generalQuestions.map((q) => ({
            key: q,
            label: q.length > 48 ? `${q.slice(0, 48)}…` : q,
            text: q,
          }))}
          onSelect={onSelect}
          disabled={disabled}
        />
      </div>
    </section>
  );
}

function PromptGroup({ label, items, onSelect, disabled }) {
  return (
    <div>
      <p className="mb-2.5 text-xs font-medium text-slate-500">{label}</p>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <button
            key={item.key}
            type="button"
            disabled={disabled}
            title={item.text}
            onClick={() => onSelect(item.text)}
            className={cn(
              "rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-xs text-slate-300",
              "transition-all duration-200 hover:-translate-y-0.5 hover:border-accent/35",
              "hover:bg-accent/10 hover:text-white hover:shadow-glow",
              "focus-ring disabled:translate-y-0 disabled:opacity-50"
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
