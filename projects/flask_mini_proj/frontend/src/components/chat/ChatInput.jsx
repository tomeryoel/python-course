import Button from "../ui/Button";
import { useLocale } from "../../context/LocaleContext";

export default function ChatInput({ value, onChange, onSend, onClear, loading }) {
  const { t } = useLocale();

  return (
    <div className="shrink-0 border-t border-glass-border bg-navy/40 p-3 md:p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={t("chatPlaceholder")}
          rows={2}
          className="min-h-[52px] max-h-32 flex-1 resize-y rounded-xl border border-glass-border bg-black/25 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus-ring"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          aria-label={t("chatPlaceholder")}
        />
        <div className="flex shrink-0 gap-2">
          <Button onClick={onSend} disabled={loading} size="md" className="min-w-[4.5rem]">
            {t("send")}
          </Button>
          <Button variant="ghost" onClick={onClear} size="md">
            {t("clear")}
          </Button>
        </div>
      </div>
    </div>
  );
}
