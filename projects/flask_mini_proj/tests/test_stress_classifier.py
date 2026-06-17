"""Tests for stress check-in classifier Lambda logic."""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAMBDA_DIR = ROOT / "aws" / "lambda" / "stress_check_in_classifier"


def _load_classifier():
    path = LAMBDA_DIR / "lambda_function.py"
    spec = importlib.util.spec_from_file_location("stress_check_in_classifier_lambda", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _invoke(payload: dict) -> dict:
    mod = _load_classifier()
    resp = mod.lambda_handler(payload, None)
    return json.loads(resp["body"])


def test_low_classification():
    body = _invoke({"user_message": "מה המטפל כתב לגבי תרגול נשימות?", "preferred_language": "he"})
    assert body["classification"] == "low"
    assert body["recommended_route"] == "kb_answer"
    assert body["should_use_knowledge_base"] is True


def test_medium_classification():
    body = _invoke({
        "user_message": "אני קצת בלחץ ומבולבל",
        "self_reported_stress_level": 5,
        "preferred_language": "he",
    })
    assert body["classification"] == "medium"
    assert body["response_mode"] == "short"


def test_high_classification():
    body = _invoke({
        "user_message": "אני ממש מוצף ולא מצליח לחשוב",
        "self_reported_stress_level": 8,
        "confusion_level": 8,
        "preferred_language": "he",
    })
    assert body["classification"] == "high"
    assert body["should_start_with_grounding"] is True
    assert body["should_offer_trusted_contact_message"] is True


def test_crisis_classification():
    body = _invoke({"user_message": "אני עלול לפגוע בעצמי", "preferred_language": "he"})
    assert body["classification"] == "crisis"
    assert body["should_recommend_emergency_support"] is True
    assert body["should_recommend_professional_support"] is True
    assert body["response_mode"] == "crisis_safe"


def test_english_support():
    body = _invoke({
        "user_message": "I am overwhelmed and I don't know what to do",
        "self_reported_stress_level": 7,
        "preferred_language": "en",
    })
    assert body["classification"] in ("medium", "high")
    summary = body["user_facing_summary"]
    assert not any("\u0590" <= c <= "\u05ff" for c in summary)
    assert summary  # non-empty English text


def test_missing_optional_fields_safe_default():
    body = _invoke({})
    assert body["classification"] == "low"
    assert body["recommended_route"] == "kb_answer"
    assert body["safety_disclaimer"]
