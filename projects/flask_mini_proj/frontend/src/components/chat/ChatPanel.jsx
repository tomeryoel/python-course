import { useEffect, useRef } from "react";
import { MessageSquare } from "lucide-react";
import { useLocale } from "../../context/LocaleContext";
import EmptyState from "../ui/EmptyState";
import ErrorAlert from "../ui/ErrorAlert";
import TypingIndicator from "./TypingIndicator";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

/**
 * Chat panel layout (top → bottom, never overlapping):
 *   1. messages region  (scrolls internally, dominant height)
 *   2. error alert       (optional, between messages and input)
 *   3. input row         (pinned directly under messages)
 */
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

  const empty = messages.length === 0 && !loading;

  return (
    <section className="chat-panel-root" aria-label="חלון שיחה">
      <div className="chat-messages-region px-4 py-5 md:px-6 md:py-6">
        {empty ? (
          <div className="flex h-full items-center justify-center">
            <EmptyState
              icon={MessageSquare}
              title={t("chatEmpty")}
              description="העוזר משתמש במסמכים שהועלו ובמשימות הפתוחות שלך."
              className="max-w-sm border-white/10 bg-white/[0.02]"
            />
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {messages.map((msg, i) => (
              <MessageBubble
                key={`${msg.role}-${i}`}
                role={msg.role}
                text={msg.text}
                sources={msg.sources}
              />
            ))}
            {loading && <TypingIndicator label={t("loading")} />}
            <div ref={bottomRef} className="h-px" />
          </div>
        )}
      </div>

      {error && (
        <div className="shrink-0 border-t border-white/8 px-4 py-3">
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
    </section>
  );
}
