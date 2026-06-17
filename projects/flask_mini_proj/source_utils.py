"""
Format Bedrock Agent / Knowledge Base sources for user-facing display.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import unquote

# Short opaque chunk/source IDs (e.g. zT52, sQ4p, egDM)
_OPAQUE_ID = re.compile(r"^[A-Za-z0-9]{3,10}$")

# Lines in Agent answers that list opaque internal IDs
_ANSWER_SOURCE_LINE_PATTERNS = [
    re.compile(r"^\s*מסמכים שעליהם התבסס המידע\s*:.*$", re.M),
    re.compile(r"^\s*מקורות\s*:.*$", re.M),
    re.compile(r"^\s*Sources\s*:.*$", re.M | re.I),
    re.compile(r"^\s*Based on documents\s*:.*$", re.M | re.I),
]


def is_opaque_source_label(text: str) -> bool:
    """True if text looks like an internal chunk ID, not a document name."""
    t = (text or "").strip()
    if not t:
        return True
    if len(t) <= 10 and _OPAQUE_ID.match(t):
        return True
    if re.search(r"\.(pdf|docx|doc|txt|md|jpg|jpeg|png)\b", t, re.I):
        return False
    if re.search(r"[\u0590-\u05FF]", t) and len(t) > 12:
        return False
    if " " in t and len(t) > 15:
        return False
    if len(t) <= 8 and " " not in t and not re.search(r"[\u0590-\u05FF]", t):
        return True
    return False


def extract_filename_from_uri(uri: str) -> str:
    if not uri:
        return ""
    path = uri.split("?")[0].split("#")[0]
    name = path.rsplit("/", 1)[-1].strip()
    return unquote(name) if name else ""


def format_source_for_display(source: dict[str, Any]) -> dict[str, Any] | None:
    """
    Return a user-facing source dict with display_name, or None if not readable.
    """
    uri = str(source.get("uri") or "")
    preview = str(source.get("text_preview") or "").strip()
    filename = extract_filename_from_uri(uri)

    display_name = ""
    if filename and not is_opaque_source_label(filename):
        display_name = filename
    elif preview and not is_opaque_source_label(preview[:80]):
        display_name = preview[:80].split("\n")[0].strip()
        if len(display_name) > 60:
            display_name = display_name[:57] + "…"

    if not display_name or is_opaque_source_label(display_name):
        return None

    return {
        "display_name": display_name,
        "uri": uri or None,
        "text_preview": preview if preview and not is_opaque_source_label(preview[:40]) else "",
    }


def format_sources_for_api(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate and drop opaque sources; keep readable document names only."""
    seen: set[str] = set()
    formatted: list[dict[str, Any]] = []
    for src in sources or []:
        item = format_source_for_display(src if isinstance(src, dict) else {})
        if not item:
            continue
        key = item["display_name"].lower()
        if key in seen:
            continue
        seen.add(key)
        formatted.append(item)
    return formatted


def strip_opaque_source_citations_from_answer(answer: str) -> str:
    """Remove Agent answer lines that list opaque chunk/source IDs."""
    if not answer:
        return answer
    result = answer
    for pattern in _ANSWER_SOURCE_LINE_PATTERNS:
        result = pattern.sub("", result)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return result
