"""
Centralized API response formatting, locale detection, and disclaimers.
"""

from __future__ import annotations

import re
from typing import Any

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
    ENGLISH_DISCLAIMER_MED,
    "Based only on the uploaded documents",
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


def apply_medication_disclaimer(answer: str, question: str, locale: str | None = None) -> str:
    loc = locale or detect_locale(question)
    if not (MEDICATION_KEYWORDS.search(question) or MEDICATION_KEYWORDS.search(answer)):
        return answer
    disclaimer = medication_disclaimer(loc)
    if disclaimer in answer:
        return answer
    return f"{answer.rstrip()}\n\n{disclaimer}"


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
