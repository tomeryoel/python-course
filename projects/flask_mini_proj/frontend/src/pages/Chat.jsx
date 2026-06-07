import { useCallback, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import {
  clearChat,
  createConversation,
  fetchConversation,
  fetchConversations,
  sendChat,
} from "../api";
import ChatPanel from "../components/chat/ChatPanel";
import ConversationHistory from "../components/chat/ConversationHistory";
import ExamplePrompts from "../components/chat/ExamplePrompts";
import PageHeader from "../components/layout/PageHeader";
import { useLocale } from "../context/LocaleContext";
import { GENERAL_QUESTIONS, SCENARIO_PROMPTS } from "../data/examples";
import { detectLocaleFromAnswer, LOCALES } from "../lib/i18n";
import { toUserMessage } from "../lib/errors";

function mapMessages(conv) {
  return (conv?.messages || []).map((m) => ({
    role: m.role,
    text: m.content,
    sources: m.sources,
  }));
}

export default function Chat() {
  const location = useLocation();
  const { setLocaleFromUserMessage, processAssistantAnswer, setLocale, t } = useLocale();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const refreshConversations = useCallback(async () => {
    try {
      const list = await fetchConversations();
      setConversations(list);
    } catch {
      setConversations([]);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshConversations();
  }, [refreshConversations]);

  const loadConversation = useCallback(async (id) => {
    if (!id) return;
    try {
      const conv = await fetchConversation(id);
      setConversationId(id);
      setMessages(mapMessages(conv));
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }, []);

  const startNewChat = useCallback(async () => {
    try {
      const conv = await createConversation();
      setConversationId(conv.conversation_id);
      setMessages([]);
      setError("");
      await refreshConversations();
    } catch (e) {
      setError(e.message);
    }
  }, [refreshConversations]);

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
        const data = await sendChat(q, conversationId);
        if (data.conversation_id && data.conversation_id !== conversationId) {
          setConversationId(data.conversation_id);
        }
        const answerLocale =
          data.locale || detectLocaleFromAnswer(data.answer, userLocale);
        setLocale(answerLocale === LOCALES.en ? LOCALES.en : LOCALES.he);
        const normalized = processAssistantAnswer(data.answer, answerLocale);

        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            text: normalized,
            sources: data.sources,
            toolCalls: data.tool_calls,
            status: data.status,
          },
        ]);
        await refreshConversations();
      } catch (e) {
        setError(toUserMessage(e, t));
      } finally {
        setLoading(false);
      }
    },
    [
      input,
      conversationId,
      processAssistantAnswer,
      setLocale,
      setLocaleFromUserMessage,
      refreshConversations,
      t,
    ]
  );

  useEffect(() => {
    if (location.state?.question) {
      ask(location.state.question);
      window.history.replaceState({}, "");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state?.question]);

  async function handleClear() {
    if (conversationId) await clearChat(conversationId);
    await startNewChat();
  }

  return (
    <div className="chat-page">
      <PageHeader
        compact
        title="שיחה עם העוזר"
        subtitle="Bedrock Agent + Knowledge Base — שאל על ההנחיות מהמסמכים ב-S3."
      />

      <div className="flex flex-col gap-4 lg:flex-row lg:items-start">
        <ConversationHistory
          conversations={conversations}
          activeId={conversationId}
          onSelect={loadConversation}
          onNewChat={startNewChat}
          loading={historyLoading}
        />

        <div className="min-w-0 flex-1">
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
    </div>
  );
}
