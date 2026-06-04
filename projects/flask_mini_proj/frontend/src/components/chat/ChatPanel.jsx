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
  const containerRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-glass-border glass-panel-strong">
      {/* Messages — dominant vertical space */}
      <div
        ref={containerRef}
        className="scrollbar-calm min-h-[min(58vh,520px)] flex-1 overflow-y-auto px-4 py-16 md:min-h-[min(62vh,580px)] md:px-6 md:py-20"
      >
        <div className="flex min-h-full flex-col gap-4">
          {messages.length === 0 && !loading && (
            <EmptyState
              icon={MessageSquare}
              title={t("chatEmpty")}
              className="my-auto border-0 bg-transparent"
            />
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
            <div className="self-start rounded-2xl rounded-bl-md border border-glass-border bg-glass-strong px-4 py-3">
              <LoadingDots />
              <span className="sr-only">{t("loading")}</span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {error && (
        <div className="shrink-0 px-4 pb-2">
          <ErrorAlert message={error} />
        </div>
      )}

      <ChatInput
        value={input}
        onChange={onInputChange}
        onSend={onSend}
        onClear={onClear}
        loading={loading}
      />
    </div>
  );
}
