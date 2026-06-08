"""
Weekly Wellness Snapshot — Bedrock Agent Action Group tool (Lambda).

Generates a supportive weekly summary from completed/open tasks and recent topics.
Rule-based (no LLM) for reliability in student demos.

Supports:
  * Direct Lambda console test events
  * Bedrock Agent Action Group invocation format
"""

from __future__ import annotations

import json
from typing import Any


DISCLAIMER_HE = "סיכום זה מבוסס על משימות שהוזנו במערכת בלבד — אינו אבחון רפואי."
DISCLAIMER_EN = "This summary is based on tasks entered in the app only — not a medical diagnosis."


def _unwrap_event(event: dict) -> dict:
    """Accept direct test events or Bedrock Agent Action Group payloads."""
    if not isinstance(event, dict):
        return {}

    # Bedrock Agent OpenAPI Action Group requestBody format
    if "requestBody" in event:
        content = event.get("requestBody", {}).get("content", {})
        for block in content.values():
            props = block.get("properties")
            if isinstance(props, list):
                out = {}
                for p in props:
                    if isinstance(p, dict) and "name" in p:
                        out[p["name"]] = p.get("value")
                if out:
                    return out

            body = block.get("body", "")
            if isinstance(body, str) and body.strip():
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    return {}

            if isinstance(body, dict):
                return body

    # API Gateway / Flask direct body format
    if "body" in event and isinstance(event["body"], str):
        try:
            return json.loads(event["body"])
        except json.JSONDecodeError:
            pass

    # Direct Lambda test event
    return event

def _as_list(value: Any) -> list[str]:
    """Normalize Bedrock/Lambda input into a list of strings."""
    if value is None or value == "":
        return []

    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]

    if isinstance(value, str):
        # Try JSON array first
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass

        # Fallback: comma-separated or single item
        if "," in value:
            return [item.strip() for item in value.split(",") if item.strip()]

        return [value.strip()] if value.strip() else []

    return [str(value)]

def _build_snapshot(data: dict) -> dict[str, Any]:
    lang = (data.get("language") or data.get("preferred_language") or "he").lower()
    completed = _as_list(data.get("completed_tasks"))
    open_tasks = _as_list(data.get("open_tasks"))
    topics = _as_list(data.get("recent_topics"))
    recent_context = str(data.get("recent_context_summary") or "").strip()

    has_real_task_data = bool(completed or open_tasks or topics or recent_context)

    if lang.startswith("en"):
        if has_real_task_data:
            topics_str = ", ".join(topics[:5]) if topics else "recent app context"
            context_sentence = (
                f" Recent context: {recent_context}"
                if recent_context and not topics
                else ""
            )
            return {
                "week_summary": (
                    f"This week the focus was on: {topics_str}. "
                    f"{len(completed)} tasks completed, {len(open_tasks)} still open."
                    f"{context_sentence}"
                ),
                "completed_tasks": len(completed),
                "open_tasks": len(open_tasks),
                "encouragement": "Steady progress is built one small step at a time.",
                "next_focus": "Focus on one practical task and one short grounding routine.",
                "disclaimer": DISCLAIMER_EN,
            }

        return {
            "week_summary": (
                "I do not have saved weekly task data available in the current Agent test context. "
                "In the full application, this summary should be generated from app-level memory and saved tasks."
            ),
            "completed_tasks": 0,
            "open_tasks": 0,
            "encouragement": "You can still choose one small stabilizing action for the next step.",
            "next_focus": "Use the app context or saved tasks to generate a more specific weekly snapshot.",
            "disclaimer": DISCLAIMER_EN,
        }

    if has_real_task_data:
        topics_he = "، ".join(topics[:5]) if topics else "הקשר מהשיחות האחרונות"
        context_sentence = (
            f" מתוך ההקשר האחרון במערכת: {recent_context}"
            if recent_context and not topics
            else ""
        )
        return {
            "week_summary": (
                f"השבוע ההתמקדות הייתה ב: {topics_he}. "
                f"הושלמו {len(completed)} משימות, {len(open_tasks)} עדיין פתוחות."
                f"{context_sentence}"
            ),
            "completed_tasks": len(completed),
            "open_tasks": len(open_tasks),
            "encouragement": "נראה שיש מקום להמשיך בצעדים קטנים וברורים, בלי להעמיס.",
            "next_focus": "להתמקד במשימה אחת פשוטה ולהמשיך לתרגל קרקוע קצר בזמן הצפה.",
            "disclaimer": DISCLAIMER_HE,
        }

    return {
        "week_summary": (
            "לא נמצאו כרגע משימות שמורות או הקשר שבועי זמין מתוך סביבת הבדיקה של ה-Agent. "
            "באפליקציה המלאה, הסיכום השבועי צריך להיבנות מתוך הזיכרון האפליקטיבי והשיחות שנשמרו."
        ),
        "completed_tasks": 0,
        "open_tasks": 0,
        "encouragement": "אפשר להתחיל מצעד קטן אחד ולבנות ממנו המשך ברור.",
        "next_focus": "לחבר את הסיכום השבועי לזיכרון האפליקטיבי של Flask/SQLite כדי לקבל סיכום אישי יותר.",
        "disclaimer": DISCLAIMER_HE,
    }


def _agent_response(event: dict, body: dict, status_code: int = 200) -> dict:
    """
    Bedrock Agent response format for Action Groups created with OpenAPI/API schema.
    """
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup", "weekly"),
            "apiPath": event.get("apiPath", "/weekly"),
            "httpMethod": event.get("httpMethod", "POST"),
            "httpStatusCode": status_code,
            "responseBody": {
                "application/json": {
                    "body": json.dumps(body, ensure_ascii=False)
                }
            },
        },
    }


def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event, ensure_ascii=False))

        safe_event = event if isinstance(event, dict) else {}
        data = _unwrap_event(safe_event)
        print("Extracted data:", json.dumps(data, ensure_ascii=False))

        result = _build_snapshot(data)
        print("Result:", json.dumps(result, ensure_ascii=False))

        # Bedrock Agent Action Group invocation
        if isinstance(event, dict) and ("actionGroup" in event or "apiPath" in event):
            return _agent_response(event, result, 200)

        # Direct Lambda console test
        return {
            "statusCode": 200,
            "body": json.dumps(result, ensure_ascii=False),
        }

    except Exception as exc:
        print("Unhandled error:", str(exc))

        fallback = {
            "week_summary": "הייתה תקלה ביצירת הסיכום השבועי, אך ניתן להמשיך עם תשובה קצרה ובטוחה.",
            "completed_tasks": 0,
            "open_tasks": 0,
            "encouragement": "אפשר להמשיך בצעד קטן אחד בכל פעם.",
            "next_focus": "להתמקד במשימה אחת פשוטה ולא להעמיס.",
            "disclaimer": DISCLAIMER_HE,
            "error": str(exc),
        }

        if isinstance(event, dict) and ("actionGroup" in event or "apiPath" in event):
            return _agent_response(event, fallback, 200)

        return {
            "statusCode": 200,
            "body": json.dumps(fallback, ensure_ascii=False),
        }
