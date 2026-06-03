"""
tasks.json — load, save, CRUD, and LLM-based task extraction.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TASKS_PATH = os.path.join(BASE_DIR, "tasks.json")

VALID_CATEGORIES = {
    "medication",
    "grounding",
    "sleep",
    "routine",
    "cognitive_load",
}
VALID_STATUSES = {"open", "done", "skipped"}


class TasksError(Exception):
    """Base error for task operations."""


class TasksFileError(TasksError):
    """tasks.json missing or corrupted."""


def get_tasks_path() -> str:
    return os.getenv("TASKS_JSON_PATH", DEFAULT_TASKS_PATH)


def _ensure_file(path: str | None = None) -> str:
    p = path or get_tasks_path()
    if not os.path.isfile(p):
        initial: list = []
        save_tasks(initial, p)
    return p


def load_tasks(path: str | None = None) -> list[dict[str, Any]]:
    p = path or get_tasks_path()
    if not os.path.isfile(p):
        return []
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise TasksFileError("קובץ tasks.json פגום. נא לתקן או למחוק ולהתחיל מחדש.") from exc
    except OSError as exc:
        raise TasksFileError(f"לא ניתן לקרוא את tasks.json: {exc}") from exc
    if not isinstance(data, list):
        raise TasksFileError("tasks.json חייב להכיל מערך של משימות.")
    return data


def save_tasks(tasks: list[dict[str, Any]], path: str | None = None) -> None:
    p = path or get_tasks_path()
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def _next_id(tasks: list[dict[str, Any]]) -> str:
    nums = []
    for t in tasks:
        tid = str(t.get("id", ""))
        m = re.match(r"task_(\d+)", tid)
        if m:
            nums.append(int(m.group(1)))
    n = max(nums, default=0) + 1
    return f"task_{n:03d}"


def get_all_tasks() -> list[dict[str, Any]]:
    _ensure_file()
    return load_tasks()


def get_task_by_id(task_id: str) -> dict[str, Any] | None:
    for t in load_tasks():
        if t.get("id") == task_id:
            return t
    return None


def add_task(payload: dict[str, Any]) -> dict[str, Any]:
    tasks = load_tasks()
    task = {
        "id": payload.get("id") or _next_id(tasks),
        "title": (payload.get("title") or "").strip(),
        "description": (payload.get("description") or "").strip(),
        "category": payload.get("category", "routine"),
        "source": (payload.get("source") or "הוספה ידנית").strip(),
        "frequency": payload.get("frequency", "daily"),
        "time": payload.get("time", ""),
        "status": payload.get("status", "open"),
        "safety_note": payload.get("safety_note", ""),
    }
    if not task["title"]:
        raise TasksError("כותרת המשימה חובה.")
    if task["category"] not in VALID_CATEGORIES:
        task["category"] = "routine"
    if task["status"] not in VALID_STATUSES:
        task["status"] = "open"
    if task["category"] == "medication" and not task["safety_note"]:
        task["safety_note"] = "לפי המסמכים בלבד ולא כהנחיה רפואית חדשה."
    tasks.append(task)
    save_tasks(tasks)
    return task


def update_task(task_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    tasks = load_tasks()
    for i, t in enumerate(tasks):
        if t.get("id") != task_id:
            continue
        for key in (
            "title",
            "description",
            "category",
            "source",
            "frequency",
            "time",
            "status",
            "safety_note",
        ):
            if key in payload:
                tasks[i][key] = payload[key]
        if tasks[i].get("category") not in VALID_CATEGORIES:
            tasks[i]["category"] = "routine"
        if tasks[i].get("status") not in VALID_STATUSES:
            tasks[i]["status"] = "open"
        save_tasks(tasks)
        return tasks[i]
    raise TasksError(f"משימה {task_id} לא נמצאה.")


def delete_task(task_id: str) -> None:
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t.get("id") != task_id]
    if len(new_tasks) == len(tasks):
        raise TasksError(f"משימה {task_id} לא נמצאה.")
    save_tasks(new_tasks)


def extract_tasks_from_text(
    document_text: str,
    source_name: str = "סיכום קליני",
    *,
    llm_extract_fn=None,
) -> list[dict[str, Any]]:
    """
    Extract tasks from clinical text via Bedrock (or injected mock for tests).
    """
    text = (document_text or "").strip()
    if not text:
        raise TasksError("טקסט המסמך ריק.")
    if len(text) > 12000:
        text = text[:12000] + "…"

    if llm_extract_fn is None:
        llm_extract_fn = _llm_extract_tasks

    raw_tasks = llm_extract_fn(text, source_name)
    existing = load_tasks()
    added = []
    for item in raw_tasks:
        if not isinstance(item, dict):
            continue
        item.setdefault("source", source_name)
        item.setdefault("status", "open")
        if item.get("category") == "medication":
            item.setdefault(
                "safety_note",
                "לפי המסמכים בלבד ולא כהנחיה רפואית חדשה.",
            )
        task = add_task(item)
        added.append(task)
    return added


def _llm_extract_tasks(document_text: str, source_name: str) -> list[dict[str, Any]]:
    from rag_engine import get_engine

    engine = get_engine()
    prompt = f"""נתח את הסיכום הקליני הבא וחלץ משימות תפקותיות/practical בלבד.
החזר JSON בלבד — מערך של אובייקטים ללא טקסט נוסף.

כל אובייקט:
{{
  "title": "כותרת קצרה בעברית",
  "description": "תיאור מעשי",
  "category": "medication|grounding|sleep|routine|cognitive_load",
  "frequency": "daily|weekly|as_needed",
  "time": "HH:MM או ריק",
  "safety_note": "ריק או disclaimer לתרופות"
}}

מקור: {source_name}

סיכום:
{document_text}
"""
    system = (
        "אתה מחלץ משימות טיפוליות מסיכומים קליניים. "
        "החזר רק JSON תקין — מערך. אל תמציא תרופות שלא מופיעות בטקסט."
    )
    answer, _ = engine._converse(prompt, extra_system=system)
    return _parse_tasks_json(answer)


def _parse_tasks_json(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []
