"""Tests for source formatting and answer sanitization."""

import json
from datetime import datetime, timezone

from response_utils import dedupe_disclaimer_lines, sanitize_agent_answer
from source_utils import (
    extract_filename_from_uri,
    format_source_for_display,
    format_sources_for_api,
    is_opaque_source_label,
    strip_opaque_source_citations_from_answer,
)
from tasks import get_tasks_path
from weekly_context import (
    build_weekly_app_context,
    is_task_context_request,
    is_weekly_snapshot_request,
    should_inject_app_context,
)


def test_task_board_phrasing_triggers_task_context():
    msg = "אין לך גישה ללוח המשימות? סימנתי שם כבר את מה שעשיתי"
    assert is_task_context_request(msg)
    assert should_inject_app_context(msg)


def test_task_board_keywords():
    assert is_task_context_request("לוח המשימות")
    assert is_task_context_request("משימות שסימנתי")


def test_normal_rag_question_not_task_context():
    assert not should_inject_app_context("מה ההמלצות לשינה לפי המסמכים?")


def test_weekly_and_task_context_use_same_tasks_path(sample_tasks):
    assert build_weekly_app_context(None)["tasks_path"] == get_tasks_path()


def test_opaque_id_detection():
    assert is_opaque_source_label("zT52")
    assert is_opaque_source_label("egDM")
    assert not is_opaque_source_label("clinical_summary.pdf")


def test_extract_filename_from_s3_uri():
    uri = "s3://my-bucket/data/clinical_summary.pdf"
    assert extract_filename_from_uri(uri) == "clinical_summary.pdf"


def test_format_source_uses_filename_not_opaque_id():
    src = format_source_for_display({
        "uri": "s3://bucket/data/sleep_guidelines.pdf",
        "text_preview": "zT52",
    })
    assert src["display_name"] == "sleep_guidelines.pdf"


def test_format_sources_drops_opaque_ids():
    formatted = format_sources_for_api([
        {"text_preview": "zT52", "uri": ""},
        {"uri": "s3://b/data/doc.pdf", "text_preview": "chunk"},
    ])
    assert len(formatted) == 1
    assert formatted[0]["display_name"] == "doc.pdf"


def test_strip_opaque_source_line_from_answer():
    answer = (
        "תשובה לדוגמה.\n\n"
        "מסמכים שעליהם התבסס המידע: zT52, sQ4p, egDM"
    )
    cleaned = strip_opaque_source_citations_from_answer(answer)
    assert "zT52" not in cleaned
    assert "תשובה לדוגמה" in cleaned


def test_dedupe_disclaimer_lines():
    answer = (
        "טקסט.\n\n"
        "לפי המסמכים שהועלו בלבד, ולא כהנחיה רפואית חדשה…\n\n"
        "ולא כהנחיה רפואית חדשה."
    )
    once = dedupe_disclaimer_lines(answer, "he")
    assert once.count("לא כהנחיה רפואית") == 1


def test_two_identical_disclaimers_reduced_to_one():
    answer = (
        "מידע על התרופה.\n"
        "לפי המסמכים שהועלו בלבד, ולא כהנחיה רפואית חדשה…\n"
        "לפי המסמכים שהועלו בלבד, ולא כהנחיה רפואית חדשה…"
    )
    once = dedupe_disclaimer_lines(answer, "he")
    assert once.count("כהנחיה רפואית") == 1


def test_two_near_duplicate_disclaimers_reduced_to_one():
    answer = (
        "מידע על התרופה.\n"
        "**לפי המסמכים שהועלו בלבד, ולא כהנחיה רפואית חדשה.**\n"
        "לפי המסמכים שהועלו בלבד — ולא כהנחיה רפואית חדשה"
    )
    once = dedupe_disclaimer_lines(answer, "he")
    assert once.count("כהנחיה רפואית") == 1


def test_non_medication_answer_unchanged():
    answer = "תרגיל קרקוע 5-4-3-2-1 יכול לעזור כשמרגישים הצפה."
    assert dedupe_disclaimer_lines(answer, "he") == answer
    assert sanitize_agent_answer(answer, "מה זה קרקוע?", "he") == answer


def test_medication_answer_keeps_one_disclaimer():
    answer = "המינון של ציפרלקס לפי המסמך הוא 20 מ\"ג."
    cleaned = sanitize_agent_answer(answer, "מה המינון של ציפרלקס?", "he")
    assert cleaned.count("כהנחיה רפואית") == 1


def test_doctor_referral_near_duplicate_deduped():
    answer = (
        "מידע על תרופה.\n"
        "איני רופא, פנה לפסיכיאטר לפני שינוי.\n"
        "**איני רופא — פנה לפסיכיאטר לפני כל שינוי**"
    )
    once = dedupe_disclaimer_lines(answer, "he")
    assert once.lower().count("איני רופא") == 1


def test_sanitize_agent_answer_combined():
    answer = (
        "ציפרלקס 20mg.\n"
        "מסמכים שעליהם התבסס המידע: zT52\n"
        "לפי המסמכים בלבד ולא כהנחיה רפואית חדשה.\n"
        "ולא כהנחיה רפואית חדשה."
    )
    cleaned = sanitize_agent_answer(answer, "מה המינון של ציפרלקס?", "he")
    assert "zT52" not in cleaned
    assert cleaned.count("לא כהנחיה רפואית") == 1


def test_weekly_context_json_serializable(tmp_path, monkeypatch):
    db_path = tmp_path / "chat.db"
    monkeypatch.setenv("CHAT_DB_PATH", str(db_path))
    monkeypatch.setenv("TASKS_JSON_PATH", str(tmp_path / "t.json"))
    import chat_store

    chat_store.DB_PATH = str(db_path)
    chat_store.init_db()
    ctx = build_weekly_app_context(None)
    json.dumps(ctx)


def test_chat_task_context_injects_block(client, monkeypatch, sample_tasks):
    monkeypatch.setenv("BEDROCK_AGENT_ID", "TEST_AGENT")
    monkeypatch.setenv("BEDROCK_AGENT_ALIAS_ID", "TEST_ALIAS")
    captured: dict = {}

    def mock_agent(message, conversation_id=None, **kwargs):
        captured["message"] = message
        return {
            "status": "success",
            "answer": "סיכום משימות.",
            "sources": [],
            "tool_calls": [],
            "trace_summary": [],
            "agent_session_id": "s",
            "conversation_id": conversation_id,
        }

    monkeypatch.setattr("app.answer_with_agent", mock_agent)
    user_msg = "אין לך גישה ללוח המשימות? סימנתי שם כבר את מה שעשיתי"
    res = client.post("/api/chat", json={"message": user_msg})
    assert res.status_code == 200
    assert "[APP_CONTEXT_FOR_WEEKLY_SNAPSHOT]" in captured["message"]
