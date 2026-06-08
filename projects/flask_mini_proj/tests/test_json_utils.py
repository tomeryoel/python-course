"""Tests for JSON-safe serialization helpers."""

import json
from datetime import date, datetime, timezone

import chat_store
from agent_engine import parse_agent_response
from json_utils import dumps_json_safe, json_safe
from weekly_context import build_weekly_app_context


def test_json_safe_converts_datetime_to_iso():
    dt = datetime(2026, 6, 7, 12, 30, tzinfo=timezone.utc)
    assert json_safe(dt) == "2026-06-07T12:30:00+00:00"


def test_json_safe_converts_date_to_iso():
    d = date(2026, 6, 7)
    assert json_safe(d) == "2026-06-07"


def test_json_safe_recursive_dict_and_list():
    dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
    data = {"items": [{"at": dt}], "count": 1}
    safe = json_safe(data)
    json.dumps(safe)
    assert safe["items"][0]["at"] == "2026-01-01T00:00:00+00:00"


def test_conversation_dict_with_datetime_serializable(tmp_path, monkeypatch):
    db_path = tmp_path / "chat.db"
    monkeypatch.setenv("CHAT_DB_PATH", str(db_path))
    chat_store.DB_PATH = str(db_path)
    chat_store.init_db()

    conv = chat_store.create_conversation(title="test")
    chat_store.add_message(conv["conversation_id"], "user", "שלום")

    loaded = chat_store.get_conversation(conv["conversation_id"])
    json.dumps(loaded)


def test_parse_agent_response_handles_datetime_in_trace():
    dt = datetime(2026, 6, 7, 15, 0, tzinfo=timezone.utc)
    response = {
        "completion": [
            {"chunk": {"bytes": "תשובה לדוגמה".encode("utf-8")}},
            {"trace": {"trace": {"orchestrationTrace": {"timestamp": dt}}}},
        ]
    }
    parsed = parse_agent_response(response)
    assert parsed["answer"] == "תשובה לדוגמה"
    json.dumps(parsed)


def test_weekly_context_builder_json_safe(tmp_path, monkeypatch):
    db_path = tmp_path / "chat.db"
    monkeypatch.setenv("CHAT_DB_PATH", str(db_path))
    monkeypatch.setenv("TASKS_JSON_PATH", str(tmp_path / "missing.json"))
    chat_store.DB_PATH = str(db_path)
    chat_store.init_db()

    ctx = build_weekly_app_context(None, language="he")
    json.dumps(ctx)


def test_chat_non_weekly_serializes_agent_result(client, monkeypatch):
    monkeypatch.setenv("BEDROCK_AGENT_ID", "TEST_AGENT")
    monkeypatch.setenv("BEDROCK_AGENT_ALIAS_ID", "TEST_ALIAS")

    def mock_agent(message, conversation_id=None, **kwargs):
        return {
            "status": "success",
            "answer": "תשובה",
            "sources": [],
            "tool_calls": [],
            "trace_summary": ['{"ts": "2026-06-07T12:00:00+00:00"}'],
            "agent_session_id": "sess-1",
            "conversation_id": conversation_id,
            "memory_summary": {"recent_turns": 0},
        }

    monkeypatch.setattr("app.answer_with_agent", mock_agent)
    res = client.post("/api/chat", json={"message": "מה ההמלצות לשינה?"})
    assert res.status_code == 200
    data = res.get_json()
    json.dumps(data)


def test_conversations_list_json_serializable(client):
    client.post("/api/conversations", json={"title": "בדיקה"})
    res = client.get("/api/conversations")
    assert res.status_code == 200
    json.dumps(res.get_json())
