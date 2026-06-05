import { Send, Trash2 } from "lucide-react";
import { cn } from "../../lib/cn";
import { useLocale } from "../../context/LocaleContext";
import Button from "../ui/Button";

export default function ChatInput({ value, onChange, onSend, onClear, loading }) {
  const { t } = useLocale();

  return (
    <div className="shrink-0 border-t border-white/10 bg-navy-deep/50 px-4 py-4 md:px-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={t("chatPlaceholder")}
          rows={2}
          className={cn(
            "min-h-[56px] max-h-36 flex-1 resize-none rounded-xl border border-white/12",
            "bg-black/30 px-4 py-3 text-sm leading-relaxed text-white shadow-inner-soft",
            "placeholder:text-slate-500 transition focus:border-accent/40 focus:bg-black/40 focus-ring"
          )}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          aria-label={t("chatPlaceholder")}
        />
        <div className="flex shrink-0 gap-2 sm:flex-col-reverse sm:gap-2">
          <Button
            onClick={onSend}
            disabled={loading}
            size="md"
            className="min-w-[5rem] gap-1.5"
          >
            <Send className="h-4 w-4" />
            {t("send")}
          </Button>
          <Button variant="ghost" onClick={onClear} size="md" className="gap-1.5">
            <Trash2 className="h-4 w-4" />
            {t("clear")}
          </Button>
        </div>
      </div>
    </div>
  );
}
