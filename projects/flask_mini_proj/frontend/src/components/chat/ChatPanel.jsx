import { useEffect, useRef } from "react";
import { MessageSquare } from "lucide-react";
import { useLocale } from "../../context/LocaleContext";
import EmptyState from "../ui/EmptyState";
import ErrorAlert from "../ui/ErrorAlert";
import LoadingDots from "../ui/LoadingDots";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

export default function ChatPanel({
  messages,
  loading,
  error,
  input,
  onInputChange,
  onSend,
  onClear,
}) {
  const { t } = useLocale();
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <section className="chat-panel-root" aria-label="חלון שיחה">
      {/* 1. Messages — dominant scrollable region */}
      <div className="chat-messages-region px-4 py-5 md:px-6 md:py-6">
        <div className="flex flex-col gap-4">
          {messages.length === 0 && !loading && (
            <div className="flex flex-1 items-center justify-center py-8">
              <EmptyState
                icon={MessageSquare}
                title={t("chatEmpty")}
                description="העוזר משתמש במסמכים שהועלו ובמשימות הפתוחות שלך."
                className="max-w-sm border-white/10 bg-white/[0.02]"
              />
            </div>
          )}

          {messages.map((msg, i) => (
            <MessageBubble
              key={`${msg.role}-${i}`}
              role={msg.role}
              text={msg.text}
              sources={msg.sources}
            />
          ))}

          {loading && (
            <div className="flex items-center gap-3 self-start rounded-2xl rounded-bl-md border border-white/10 bg-white/[0.06] px-4 py-3 shadow-inner-soft">
              <LoadingDots />
              <span className="text-sm text-slate-400">{t("loading")}</span>
            </div>
          )}
          <div ref={bottomRef} className="h-px shrink-0" />
        </div>
      </div>

      {/* 2. Error (between messages and input) */}
      {error && (
        <div className="shrink-0 border-t border-white/8 px-4 py-3">
          <ErrorAlert message={error} />
        </div>
      )}

      {/* 3. Input row — directly under messages */}
      <ChatInput
        value={input}
        onChange={onInputChange}
        onSend={onSend}
        onClear={onClear}
        loading={loading}
      />
    </section>
  );
}
