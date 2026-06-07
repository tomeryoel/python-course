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
    if "requestBody" in event:
        content = event.get("requestBody", {}).get("content", {})
        for block in content.values():
            body = block.get("body", "")
            if isinstance(body, str):
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    return {}
    if "body" in event and isinstance(event["body"], str):
        try:
            return json.loads(event["body"])
        except json.JSONDecodeError:
            pass
    return event if isinstance(event, dict) else {}


def _build_snapshot(data: dict) -> dict[str, Any]:
    lang = (data.get("language") or "he").lower()
    completed = data.get("completed_tasks") or []
    open_tasks = data.get("open_tasks") or []
    topics = data.get("recent_topics") or []

    if lang.startswith("en"):
        topics_str = ", ".join(topics[:5]) if topics else "general wellness"
        return {
            "week_summary": (
                f"This week the focus was on: {topics_str}. "
                f"{len(completed)} tasks completed, {len(open_tasks)} still open."
            ),
            "completed_tasks": len(completed),
            "open_tasks": len(open_tasks),
            "encouragement": (
                "Steady progress on building routines — keep going one step at a time."
            ),
            "next_focus": (
                "Continue short grounding exercises during overwhelm and keep a stable evening routine."
            ),
            "disclaimer": DISCLAIMER_EN,
        }

    topics_he = "، ".join(topics[:5]) if topics else "בריאות כללית"
    return {
        "week_summary": (
            f"השבוע ההתמקדות הייתה ב: {topics_he}. "
            f"הושלמו {len(completed)} משימות, {len(open_tasks)} עדיין פתוחות."
        ),
        "completed_tasks": len(completed),
        "open_tasks": len(open_tasks),
        "encouragement": "נראה שיש התקדמות הדרגתית סביב יצירת שגרה יציבה יותר.",
        "next_focus": "להמשיך לתרגל קרקוע קצר בזמן הצפה ולשמור על שגרת ערב קבועה.",
        "disclaimer": DISCLAIMER_HE,
    }


def _agent_response(action_group: str, function: str, body: dict) -> dict:
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "function": function,
            "functionResponse": {
                "responseBody": {
                    "TEXT": {"body": json.dumps(body, ensure_ascii=False)},
                }
            },
        },
    }


def lambda_handler(event, context):
    data = _unwrap_event(event)
    result = _build_snapshot(data)

    # Bedrock Agent Action Group wrapper
    if "actionGroup" in event or "agent" in event:
        ag = event.get("actionGroup", "WeeklyWellnessSnapshot")
        fn = event.get("function", "weekly_wellness_snapshot")
        return _agent_response(ag, fn, result)

    return {
        "statusCode": 200,
        "body": json.dumps(result, ensure_ascii=False),
    }
