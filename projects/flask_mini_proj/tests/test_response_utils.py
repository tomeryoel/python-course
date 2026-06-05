from response_utils import (
    LOCALE_EN,
    LOCALE_HE,
    apply_medication_disclaimer,
    detect_locale,
    format_chat_response,
    normalize_disclaimers,
)


def test_detect_locale_english_request():
    assert detect_locale("Please answer in English") == LOCALE_EN


def test_detect_locale_hebrew_default():
    assert detect_locale("מה השעה לציפרלקס?") == LOCALE_HE


def test_normalize_disclaimer_to_english():
    heb = "לפי המסמכים שהועלו בלבד, ולא כהנחיה רפואית חדשה…"
    out = normalize_disclaimers(f"Answer. {heb}", LOCALE_EN)
    assert "Based only on the uploaded documents" in out
    assert heb not in out


def test_format_chat_response_adds_locale():
    result = format_chat_response(
        {"answer": "test", "status": "success", "sources": []},
        "answer in english please",
    )
    assert "locale" in result
