"""
Centralized API response formatting, locale detection, and disclaimers.
"""

from __future__ import annotations

import re
from typing import Any

from source_utils import strip_opaque_source_citations_from_answer

LOCALE_HE = "he"
LOCALE_EN = "en"

HEBREW_DISCLAIMER_MED = "לפי המסמכים שהועלו בלבד, ולא כהנחיה רפואית חדשה…"
ENGLISH_DISCLAIMER_MED = (
    "Based only on the uploaded documents and not as new medical advice."
)

ENGLISH_REQUEST_PATTERNS = [
    re.compile(r"\banswer\s+in\s+english\b", re.I),
    re.compile(r"\brespond\s+in\s+english\b", re.I),
    re.compile(r"\breply\s+in\s+english\b", re.I),
    re.compile(r"\bin\s+english\s+please\b", re.I),
    re.compile(r"ענה\s+באנגלית", re.I),
    re.compile(r"תענה\s+באנגלית", re.I),
    re.compile(r"בבקשה\s+באנגלית", re.I),
    re.compile(r"באנגלית\s*(\?|\.|!)?\s*$", re.I),
]

MEDICATION_KEYWORDS = re.compile(
    r"ציפרלקס|cipralex|קלונקס|clonex|תרופ|מינון|כדור|medication|dosage",
    re.IGNORECASE,
)

DISCLAIMER_VARIANTS = [
    HEBREW_DISCLAIMER_MED,
    "לפי המסמכים בלבד ולא כהנחיה רפואית חדשה.",
    "ולא כהנחיה רפואית חדשה",
    "ולא כהנחיה רפואית חדשה.",
    ENGLISH_DISCLAIMER_MED,
    "Based only on the uploaded documents",
]

DISCLAIMER_LINE_PATTERNS = [
    re.compile(r"לא כהנחיה רפואית", re.I),
    re.compile(r"not as new medical advice", re.I),
    re.compile(r"Based only on the uploaded documents", re.I),
    re.compile(r"לפי המסמכים שהועלו", re.I),
    re.compile(r"לפי המסמכים בלבד", re.I),
]


def detect_locale(question: str) -> str:
    text = (question or "").strip()
    if not text:
        return LOCALE_HE
    if any(p.search(text) for p in ENGLISH_REQUEST_PATTERNS):
        return LOCALE_EN
    return LOCALE_HE


def detect_locale_from_answer(answer: str, fallback: str = LOCALE_HE) -> str:
    hebrew = len(re.findall(r"[\u0590-\u05FF]", answer))
    latin = len(re.findall(r"[a-zA-Z]", answer))
    if latin > hebrew * 1.5 and latin > 40:
        return LOCALE_EN
    return fallback


def medication_disclaimer(locale: str) -> str:
    return ENGLISH_DISCLAIMER_MED if locale == LOCALE_EN else HEBREW_DISCLAIMER_MED


def normalize_disclaimers(answer: str, locale: str) -> str:
    if not answer:
        return answer
    target = medication_disclaimer(locale)
    result = answer
    for variant in DISCLAIMER_VARIANTS:
        if variant in result:
            result = result.replace(variant, target)
    if (
        locale == LOCALE_EN
        and MEDICATION_KEYWORDS.search(answer)
        and target not in result
    ):
        result = f"{result.rstrip()}\n\n{target}"
    return result


def dedupe_disclaimer_lines(answer: str, locale: str) -> str:
    """Keep at most one medication disclaimer sentence in the answer."""
    if not answer:
        return answer
    target = medication_disclaimer(locale)
    lines = answer.split("\n")
    kept: list[str] = []
    disclaimer_seen = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            kept.append(line)
            continue
        is_disclaimer = any(p.search(stripped) for p in DISCLAIMER_LINE_PATTERNS)
        if is_disclaimer:
            if disclaimer_seen:
                continue
            disclaimer_seen = True
            kept.append(target)
        else:
            kept.append(line)
    return "\n".join(kept).strip()


def sanitize_agent_answer(answer: str, question: str, locale: str | None = None) -> str:
    """Clean Agent answer: strip opaque source lines, dedupe disclaimers, add one if needed."""
    loc = locale or detect_locale(question)
    if not answer:
        return answer
    result = strip_opaque_source_citations_from_answer(answer)
    result = normalize_disclaimers(result, loc)
    result = dedupe_disclaimer_lines(result, loc)
    if MEDICATION_KEYWORDS.search(question) or MEDICATION_KEYWORDS.search(result):
        if medication_disclaimer(loc) not in result:
            result = f"{result.rstrip()}\n\n{medication_disclaimer(loc)}"
        result = dedupe_disclaimer_lines(result, loc)
    return result


def apply_medication_disclaimer(answer: str, question: str, locale: str | None = None) -> str:
    """Backward-compatible wrapper — prefer sanitize_agent_answer in /api/chat."""
    return sanitize_agent_answer(answer, question, locale)


def format_chat_response(result: dict[str, Any], question: str) -> dict[str, Any]:
    """Enrich RAG result with locale and normalized disclaimers."""
    locale = detect_locale(question)
    answer = result.get("answer", "")
    if result.get("status") == "success" and answer:
        loc = detect_locale_from_answer(answer, locale)
        answer = normalize_disclaimers(answer, loc)
        answer = apply_medication_disclaimer(answer, question, loc)
        locale = loc
    return {
        **result,
        "answer": answer,
        "locale": locale,
    }


def api_error(message: str, status: str = "error", code: int = 400) -> tuple[dict, int]:
    return {"error": message, "status": status}, code


def api_success(**payload) -> dict:
    return {"status": "success", **payload}
