"""Tests for weekly snapshot detection and app-context injection."""

import chat_store
from weekly_context import (
    augment_message_for_weekly_snapshot,
    build_weekly_app_context,
    format_weekly_app_context_block,
    infer_recent_topics,
    is_task_context_request,
    is_weekly_snapshot_request,
    should_inject_app_context,
)


def test_task_context_detection_hebrew():
    assert is_task_context_request("אין לך גישה ללוח המשימות? סימנתי שם")
    assert should_inject_app_context("לוח המשימות")
    assert should_inject_app_context("משימות שסימנתי")


def test_weekly_request_detection_hebrew():
    assert is_weekly_snapshot_request("תכין לי סיכום שבועי קצר של מצב המשימות")
    assert is_weekly_snapshot_request("מה עשיתי השבוע?")


def test_weekly_request_detection_english():
    assert is_weekly_snapshot_request("Please give me a weekly summary of my tasks")
    assert is_weekly_snapshot_request("weekly wellness snapshot")


def test_non_weekly_message_not_detected():
    assert not should_inject_app_context("מה ההמלצות לשינה לפי המסמכים?")
    assert not should_inject_app_context("שלום")


def test_infer_recent_topics_from_messages():
    topics = infer_recent_topics([
        "אני בסטרס לגבי שינה והתרופות",
        "המטפלת המליצה על תרגול קרקוע",
    ])
    assert "stress" in topics
    assert "sleep" in topics
    assert "medication" in topics
    assert "grounding" in topics


def test_context_builder_empty_tasks_when_no_tasks_file(tmp_path, monkeypatch):
    monkeypatch.setenv("TASKS_JSON_PATH", str(tmp_path / "missing_tasks.json"))
    db_path = tmp_path / "chat.db"
    monkeypatch.setenv("CHAT_DB_PATH", str(db_path))
    chat_store.DB_PATH = str(db_path)
    chat_store.init_db()

    ctx = build_weekly_app_context(None, language="he")
    assert ctx["completed_tasks"] == []
    assert ctx["open_tasks"] == []
    assert "language" in ctx


def test_context_builder_infers_topics_from_messages(tmp_path, monkeypatch):
    db_path = tmp_path / "chat.db"
    monkeypatch.setenv("CHAT_DB_PATH", str(db_path))
    monkeypatch.setenv("TASKS_JSON_PATH", str(tmp_path / "no_tasks.json"))
    chat_store.DB_PATH = str(db_path)
    chat_store.init_db()

    conv = chat_store.create_conversation(title="test")
    chat_store.add_message(conv["conversation_id"], "user", "יש לי עומס וחרדה לגבי שינה")

    ctx = build_weekly_app_context(conv["conversation_id"], language="he")
    assert "sleep" in ctx["recent_topics"] or "anxiety" in ctx["recent_topics"]
    assert ctx["recent_context_summary"]


def test_context_builder_loads_tasks_from_json(tmp_path, monkeypatch, sample_tasks):
    db_path = tmp_path / "chat.db"
    monkeypatch.setenv("CHAT_DB_PATH", str(db_path))
    chat_store.DB_PATH = str(db_path)
    chat_store.init_db()

    from tasks import get_tasks_path

    ctx = build_weekly_app_context(None, language="he")
    assert ctx["open_tasks"]
    assert ctx["tasks_path"] == get_tasks_path()


def test_format_weekly_block_contains_marker():
    block = format_weekly_app_context_block({
        "completed_tasks": ["a"],
        "open_tasks": ["b"],
        "recent_topics": ["sleep"],
        "recent_context_summary": "summary",
        "language": "he",
    })
    assert "[APP_CONTEXT_FOR_WEEKLY_SNAPSHOT]" in block
    assert "[/APP_CONTEXT_FOR_WEEKLY_SNAPSHOT]" in block
    assert "completed_tasks" in block


def test_augment_appends_hidden_block():
    augmented = augment_message_for_weekly_snapshot("תכין סיכום שבועי", None, language="he")
    assert augmented.startswith("תכין סיכום שבועי")
    assert "[APP_CONTEXT_FOR_WEEKLY_SNAPSHOT]" in augmented


def test_chat_weekly_uses_augmented_prompt_not_stored(client, monkeypatch, sample_tasks):
    monkeypatch.setenv("BEDROCK_AGENT_ID", "TEST_AGENT")
    monkeypatch.setenv("BEDROCK_AGENT_ALIAS_ID", "TEST_ALIAS")

    captured: dict = {}

    def mock_agent(message, conversation_id=None, **kwargs):
        captured["message"] = message
        return {
            "status": "success",
            "answer": "סיכום שבועי לדוגמה.",
            "sources": [],
            "tool_calls": [],
            "trace_summary": [],
            "agent_session_id": "sess-1",
            "conversation_id": conversation_id,
        }

    monkeypatch.setattr("app.answer_with_agent", mock_agent)

    user_msg = "תכין לי סיכום שבועי קצר של מצב המשימות"
    res = client.post("/api/chat", json={"message": user_msg})
    assert res.status_code == 200

    assert "[APP_CONTEXT_FOR_WEEKLY_SNAPSHOT]" in captured["message"]
    assert user_msg in captured["message"]

    cid = res.get_json()["conversation_id"]
    conv = chat_store.get_conversation(cid)
    user_stored = [m for m in conv["messages"] if m["role"] == "user"][-1]["content"]
    assert user_stored == user_msg
    assert "[APP_CONTEXT_FOR_WEEKLY_SNAPSHOT]" not in user_stored
