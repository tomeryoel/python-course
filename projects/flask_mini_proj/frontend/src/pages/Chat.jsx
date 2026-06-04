import { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { clearChat, sendChat } from "../api";
import ChatPanel from "../components/chat/ChatPanel";
import ExamplePrompts from "../components/chat/ExamplePrompts";
import PageHeader from "../components/layout/PageHeader";
import { useLocale } from "../context/LocaleContext";
import { GENERAL_QUESTIONS, SCENARIO_PROMPTS } from "../data/examples";
import { detectLocaleFromAnswer } from "../lib/i18n";
import { toUserMessage } from "../lib/errors";

export default function Chat() {
  const location = useLocation();
  const { setLocaleFromUserMessage, processAssistantAnswer, t } = useLocale();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const ask = useCallback(
    async (question) => {
      const q = (question || input).trim();
      if (!q) return;

      const userLocale = setLocaleFromUserMessage(q);
      setError("");
      setInput("");
      setMessages((m) => [...m, { role: "user", text: q }]);
      setLoading(true);

      try {
        const data = await sendChat(q);
        const answerLocale = detectLocaleFromAnswer(
          data.answer,
          typeof userLocale === "string" ? userLocale : undefined
        );
        const normalized = processAssistantAnswer(data.answer, answerLocale);

        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            text: normalized,
            sources: data.sources,
            status: data.status,
          },
        ]);
      } catch (e) {
        setError(toUserMessage(e, t));
      } finally {
        setLoading(false);
      }
    },
    [input, processAssistantAnswer, setLocaleFromUserMessage, t]
  );

  useEffect(() => {
    if (location.state?.question) {
      ask(location.state.question);
      window.history.replaceState({}, "");
    }
  }, [location.state?.question]);

  async function handleClear() {
    await clearChat();
    setMessages([]);
    setError("");
  }

  return (
    <div className="flex h-[calc(100vh-7rem)] min-h-0 flex-col lg:h-[calc(100vh-5rem)]">
      <PageHeader
        title="שיחה עם העוזר"
        subtitle="שאל על ההנחיות מהמסמכים — במצוקה, העוזר יתחיל במשפט מרגיע."
      />

      <div className="flex min-h-0 flex-1 flex-col">
        <ChatPanel
          messages={messages}
          loading={loading}
          error={error}
          input={input}
          onInputChange={setInput}
          onSend={() => ask()}
          onClear={handleClear}
        />

        <ExamplePrompts
          scenarios={SCENARIO_PROMPTS}
          generalQuestions={GENERAL_QUESTIONS}
          onSelect={ask}
          disabled={loading}
        />
      </div>
    </div>
  );
}
