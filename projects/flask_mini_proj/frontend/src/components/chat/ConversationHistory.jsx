import { cn } from "../../lib/cn";

/** Sidebar list of previous conversations for chat memory demo. */
export default function ConversationHistory({
  conversations,
  activeId,
  onSelect,
  onNewChat,
  loading,
}) {
  return (
    <aside className="flex w-full flex-col rounded-2xl border border-white/8 bg-black/20 lg:w-56 lg:shrink-0">
      <div className="flex items-center justify-between border-b border-white/8 px-3 py-3">
        <h3 className="text-sm font-semibold text-slate-200">שיחות קודמות</h3>
        <button
          type="button"
          onClick={onNewChat}
          className="rounded-lg bg-accent/20 px-2 py-1 text-xs text-accent-light transition hover:bg-accent/30 focus-ring"
        >
          + חדש
        </button>
      </div>
      <ul className="max-h-48 overflow-y-auto scrollbar-calm lg:max-h-[420px]">
        {loading && (
          <li className="px-3 py-4 text-xs text-slate-500">טוען…</li>
        )}
        {!loading && conversations.length === 0 && (
          <li className="px-3 py-4 text-xs text-slate-500">אין שיחות עדיין</li>
        )}
        {conversations.map((c) => (
          <li key={c.conversation_id}>
            <button
              type="button"
              onClick={() => onSelect(c.conversation_id)}
              className={cn(
                "w-full border-b border-white/5 px-3 py-2.5 text-right text-xs transition hover:bg-white/5 focus-ring",
                activeId === c.conversation_id && "bg-accent/10 text-accent-light"
              )}
            >
              <p className="truncate font-medium">
                {c.title || c.last_user_question || "שיחה"}
              </p>
              {c.last_user_question && (
                <p className="mt-0.5 truncate text-slate-500">{c.last_user_question}</p>
              )}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
