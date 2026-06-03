import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { clearChat, sendChat } from "../api";
import { GENERAL_QUESTIONS, SCENARIO_PROMPTS } from "../data/examples";

export default function Chat() {
  const location = useLocation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    if (location.state?.question) {
      ask(location.state.question);
      window.history.replaceState({}, "");
    }
  }, [location.state]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function ask(question) {
    const q = (question || input).trim();
    if (!q) return;
    setError("");
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const data = await sendChat(q);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: data.answer,
          sources: data.sources,
          status: data.status,
        },
      ]);
    } catch (e) {
      setError(
        e.message?.includes("fetch")
          ? "לא ניתן להתחבר לשרת. ודא ש-Flask רץ על פורט 5000."
          : e.message || "שגיאה בשליחה"
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleClear() {
    await clearChat();
    setMessages([]);
    setError("");
  }

  return (
    <>
      <h1 className="page-title">שיחה עם העוזר</h1>
      <p className="page-sub">
        שאל על ההנחיות מהמסמכים — במצוקה, העוזר יתחיל במשפט מרגיע.
      </p>

      <div className="glass-card chat-window">
        <div className="messages">
          {messages.length === 0 && (
            <p style={{ color: "var(--gray)", textAlign: "center" }}>
              בחר שאלה לדוגמה או כתוב מה אתה מרגיש עכשיו.
            </p>
          )}
          {messages.map((msg, i) => (
            <div key={i}>
              <div className={`bubble ${msg.role}`}>{msg.text}</div>
              {msg.sources?.length > 0 && (
                <div className="sources">
                  <details>
                    <summary>מקורות ({msg.sources.length})</summary>
                    <ul>
                      {msg.sources.map((s, j) => (
                        <li key={j}>
                          {s.text_preview || s.uri || `מקור ${s.index}`}
                        </li>
                      ))}
                    </ul>
                  </details>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="bubble assistant">
              <div className="loading-dots">
                <span />
                <span />
                <span />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {error && <div className="error-box">{error}</div>}

        <div className="example-btns">
          <strong style={{ width: "100%", fontSize: "0.8rem", color: "var(--gray)" }}>
            תרחישי בדיקה:
          </strong>
          {SCENARIO_PROMPTS.map((s) => (
            <button key={s.label} type="button" onClick={() => ask(s.text)} title={s.label}>
              {s.label}
            </button>
          ))}
        </div>
        <div className="example-btns">
          <strong style={{ width: "100%", fontSize: "0.8rem", color: "var(--gray)" }}>
            שאלות כלליות:
          </strong>
          {GENERAL_QUESTIONS.map((q) => (
            <button key={q} type="button" onClick={() => ask(q)}>
              {q.length > 42 ? q.slice(0, 42) + "…" : q}
            </button>
          ))}
        </div>

        <div className="chat-input-row">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="כתוב כאן… למשל: אני בסטרס עכשיו"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                ask();
              }
            }}
          />
          <button className="btn btn-primary" onClick={() => ask()} disabled={loading}>
            שלח
          </button>
          <button className="btn btn-ghost" onClick={handleClear} type="button">
            נקה
          </button>
        </div>
      </div>
    </>
  );
}
