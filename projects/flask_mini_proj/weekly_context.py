"""
Weekly snapshot / task-board request detection and app-level context injection for /api/chat.

When the user asks about tasks, weekly summary, or the task board, Flask collects
tasks + SQLite chat memory and appends a hidden context block to the Agent prompt.
"""

from __future__ import annotations

import os
import re
from typing import Any

from json_utils import dumps_json_safe, json_safe

import chat_store
from tasks import TasksFileError, get_all_tasks, get_tasks_path

# --- Weekly / task context detection (deterministic, no LLM) ---

_WEEKLY_PHRASES_HE = [
    "סיכום שבועי",
    "מצב המשימות",
    "משימות השבוע",
    "מה עשיתי השבוע",
    "מה נשאר לי לעשות",
    "סכם לי את השבוע",
    "תכין לי סיכום שבועי",
    "סיכום של השבוע",
    "סיכום השבוע",
    "תסכם לי את המשימות",
]
_WEEKLY_PHRASES_EN = [
    "weekly snapshot",
    "weekly wellness",
    "weekly summary",
    "summarize my week",
    "weekly tasks",
    "week summary",
    "my week in review",
]

_TASK_CONTEXT_PHRASES_HE = [
    "לוח המשימות",
    "משימות שסימנתי",
    "סימנתי שם",
    "מה עשיתי",
    "מה השלמתי",
    "משימות שהושלמו",
    "משימות פתוחות",
    "אין לך גישה ללוח המשימות",
    "תבדוק את המשימות",
    "תסכם לי את המשימות",
    "גישה ללוח",
    "סימנתי כבר",
    "מה שעשיתי",
    "המשימות שלי",
    "המשימות שביצעתי",
]
_TASK_CONTEXT_PHRASES_EN = [
    "task board",
    "tasks i completed",
    "completed tasks",
    "open tasks",
    "what i did this week",
    "what is left to do",
    "summarize my tasks",
    "my tasks",
    "tasks i marked",
    "marked as done",
]

_WEEKLY_PATTERN = re.compile(
    "|".join(re.escape(p) for p in _WEEKLY_PHRASES_HE + _WEEKLY_PHRASES_EN),
    re.IGNORECASE,
)
_TASK_CONTEXT_PATTERN = re.compile(
    "|".join(re.escape(p) for p in _TASK_CONTEXT_PHRASES_HE + _TASK_CONTEXT_PHRASES_EN),
    re.IGNORECASE,
)

# --- Topic inference keywords ---

_TOPIC_KEYWORDS: dict[str, str] = {
    # Hebrew keyword -> topic label
    "סטרס": "stress",
    "שינה": "sleep",
    "עומס": "overload",
    "הצפה": "overload",
    "תרופות": "medication",
    "ציפרלקס": "medication",
    "פסיכיאטר": "psychiatrist",
    "פסיכולוג": "therapist",
    "מטפל": "therapist",
    "טיפול": "therapy",
    "משימות": "tasks",
    "זיכרון": "memory",
    "חרדה": "anxiety",
    "תרגול": "practice",
    "קרקוע": "grounding",
    "שגרה": "routine",
    # English
    "stress": "stress",
    "sleep": "sleep",
    "overload": "overload",
    "overwhelm": "overload",
    "medication": "medication",
    "psychiatrist": "psychiatrist",
    "therapist": "therapist",
    "therapy": "therapy",
    "tasks": "tasks",
    "memory": "memory",
    "anxiety": "anxiety",
    "grounding": "grounding",
    "routine": "routine",
}


def is_task_context_request(message: str) -> bool:
    """Return True if the user refers to the app task board or marked tasks."""
    text = (message or "").strip()
    if not text:
        return False
    return bool(_TASK_CONTEXT_PATTERN.search(text))


def is_weekly_snapshot_request(message: str) -> bool:
    """Return True if the user message is asking for a weekly wellness snapshot."""
    text = (message or "").strip()
    if not text:
        return False
    return bool(_WEEKLY_PATTERN.search(text))


def should_inject_app_context(message: str) -> bool:
    """Weekly summary OR task-board phrasing → inject app context for the Agent."""
    return is_weekly_snapshot_request(message) or is_task_context_request(message)


def infer_recent_topics(user_messages: list[str]) -> list[str]:
    """Infer unique topics from recent user messages via keyword matching."""
    combined = " ".join(user_messages).lower()
    found: list[str] = []
    seen: set[str] = set()
    for keyword, topic in _TOPIC_KEYWORDS.items():
        if keyword.lower() in combined and topic not in seen:
            seen.add(topic)
            found.append(topic)
    return found


def _collect_user_messages(conversation_id: str | None) -> list[str]:
    """Gather recent user messages from current and other conversations."""
    messages: list[str] = []

    if conversation_id:
        conv = chat_store.get_conversation(conversation_id)
        if conv:
            for m in conv.get("messages", []):
                if m.get("role") == "user" and m.get("content"):
                    messages.append(m["content"])

    if len(messages) < 3:
        for c in chat_store.list_conversations(limit=8):
            cid = c.get("conversation_id")
            if cid == conversation_id:
                continue
            q = (c.get("last_user_question") or "").strip()
            if q and q not in messages:
                messages.append(q)

    return messages


def _build_recent_context_summary(user_messages: list[str], language: str) -> str:
    recent = [m.strip() for m in user_messages if m.strip()][-3:]
    if not recent:
        if language.startswith("en"):
            return "No saved conversation history in the app."
        return "אין היסטוריית שיחה שמורה באפליקציה."

    combined = " | ".join(recent)
    if len(combined) > 320:
        combined = combined[:317] + "..."
    return combined


def build_weekly_app_context(
    conversation_id: str | None,
    language: str = "he",
) -> dict[str, Any]:
    """
    Collect app-level context for weekly snapshot / task-board requests.

    Tasks come from tasks.json via get_all_tasks() — same path as /api/tasks.
    """
    lang = "en" if language.lower().startswith("en") else "he"
    user_messages = _collect_user_messages(conversation_id)

    tasks_path = get_tasks_path()
    tasks_file_exists = os.path.isfile(tasks_path)

    completed_tasks: list[str] = []
    open_tasks: list[str] = []
    task_topics: list[str] = []

    try:
        tasks = get_all_tasks()
        completed_tasks = [
            str(t.get("title", "")).strip()
            for t in tasks
            if t.get("status") == "done" and t.get("title")
        ][:20]
        open_tasks = [
            str(t.get("title", "")).strip()
            for t in tasks
            if t.get("status") == "open" and t.get("title")
        ][:20]
        task_topics = list({
            str(t.get("category", "")).strip()
            for t in tasks
            if t.get("category")
        })[:8]
    except (TasksFileError, OSError):
        pass

    recent_topics = infer_recent_topics(user_messages)
    for t in task_topics:
        if t and t not in recent_topics:
            recent_topics.append(t)

    return json_safe({
        "completed_tasks": completed_tasks,
        "open_tasks": open_tasks,
        "recent_topics": recent_topics[:10],
        "recent_context_summary": _build_recent_context_summary(user_messages, lang),
        "language": lang,
        "tasks_path": tasks_path,
        "tasks_file_exists": tasks_file_exists,
        "completed_tasks_count": len(completed_tasks),
        "open_tasks_count": len(open_tasks),
    })


def format_weekly_app_context_block(context: dict[str, Any]) -> str:
    """Hidden block appended to the Agent prompt (not shown in UI chat history)."""
    agent_ctx = {
        k: v for k, v in context.items()
        if k not in (
            "tasks_path",
            "tasks_file_exists",
            "completed_tasks_count",
            "open_tasks_count",
        )
    }
    return (
        "\n\n[APP_CONTEXT_FOR_WEEKLY_SNAPSHOT]\n"
        "The Flask app provides this task/chat context. Use it — do not ask the user "
        "to manually list completed or open tasks when this block is present.\n"
        f"completed_tasks: {dumps_json_safe(agent_ctx.get('completed_tasks', []), ensure_ascii=False)}\n"
        f"open_tasks: {dumps_json_safe(agent_ctx.get('open_tasks', []), ensure_ascii=False)}\n"
        f"recent_topics: {dumps_json_safe(agent_ctx.get('recent_topics', []), ensure_ascii=False)}\n"
        f"recent_context_summary: {agent_ctx.get('recent_context_summary', '')}\n"
        f"language: {agent_ctx.get('language', 'he')}\n"
        "[/APP_CONTEXT_FOR_WEEKLY_SNAPSHOT]"
    )


def augment_message_for_weekly_snapshot(
    message: str,
    conversation_id: str | None,
    language: str = "he",
) -> str:
    """Append hidden weekly app context to the user message for invoke_agent."""
    ctx = build_weekly_app_context(conversation_id, language=language)
    return message + format_weekly_app_context_block(ctx)
