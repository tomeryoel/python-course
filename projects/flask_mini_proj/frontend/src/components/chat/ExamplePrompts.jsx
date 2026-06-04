import { cn } from "../../lib/cn";
import { useLocale } from "../../context/LocaleContext";

export default function ExamplePrompts({ scenarios, generalQuestions, onSelect, disabled }) {
  const { t } = useLocale();

  return (
    <section className="mt-5 space-y-4" aria-label="שאלות לדוגמה">
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
    </section>
  );
}

function PromptGroup({ label, items, onSelect, disabled }) {
  return (
    <div>
      <p className="mb-2 text-xs font-medium text-slate-500">{label}</p>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <button
            key={item.key}
            type="button"
            disabled={disabled}
            title={item.text}
            onClick={() => onSelect(item.text)}
            className={cn(
              "rounded-lg border border-glass-border bg-black/20 px-3 py-1.5 text-xs text-slate-300",
              "transition-all duration-200 hover:border-accent/40 hover:bg-accent/10 hover:text-white",
              "focus-ring disabled:opacity-50"
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}
