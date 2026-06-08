"""
Stress Check-in Classifier — Bedrock Agent Action Group tool (Lambda).

Classifies user distress / cognitive overload and returns safe routing guidance
for the Bedrock Agent. Rule-based only — no LLM, no diagnosis, no medical advice.

Supports direct Lambda console tests and Bedrock Agent Action Group events.
"""

from __future__ import annotations

import json
from typing import Any

DISCLAIMER_HE = (
    "כלי זה אינו אבחון, אינו טיפול, אינו ייעוץ פסיכיאטרי ואינו שירות חירום. "
    "הוא עוזר ל-Agent לבחור מסלול תגובה בטוח בלבד."
)
DISCLAIMER_EN = (
    "This tool is not a diagnosis, therapy, psychiatric advice, or emergency service. "
    "It only helps the Agent choose a safe response route."
)

# --- Keyword lists (Hebrew + English) ---

MEDIUM_KEYWORDS_HE = [
    "סטרס", "לחץ", "חרדה", "מוצף", "הצפה", "מבולבל", "בלבול",
    "לא זוכר", "לא מצליח", "עומס", "עומס קוגניטיבי", "קשה לי",
    "לא יודע מה לעשות", "איבדתי כיוון", "מתפרק", "נסער", "בהלה", "פאניקה",
]
MEDIUM_KEYWORDS_EN = [
    "stressed", "stress", "anxious", "anxiety", "overwhelmed", "overloaded",
    "confused", "panic", "panicking", "cannot think", "can't think",
    "don't know what to do", "dont know what to do", "can't remember",
    "cant remember", "dysregulated", "losing control",
]
HIGH_INTENSITY_HE = ["ממש מוצף", "ממש בסטרס", "לא מצליח לחשוב", "מאבד שליטה", "בהלה"]
HIGH_INTENSITY_EN = [
    "really overwhelmed", "very stressed", "can't think", "cannot think",
    "losing control", "panic attack",
]
CRISIS_KEYWORDS_HE = [
    "לפגוע בעצמי", "אובדני", "התאבדות", "להתאבד", "לא רוצה לחיות",
    "מסוכן לי", "בסכנה", "סכנה מיידית", "לפגוע במישהו",
    "לא בטוח", "לא יכול להישאר בטוח", "עלול לפגוע",
]
SOFTENERS_HE = ["קצת", "במידה", "לא כל כך", "יחסית"]
SOFTENERS_EN = ["a little", "slightly", "somewhat", "a bit"]
CRISIS_KEYWORDS_EN = [
    "self harm", "hurt myself", "kill myself", "suicide", "suicidal",
    "don't want to live", "dont want to live", "immediate danger",
    "danger right now", "hurt someone", "harm someone", "not safe",
    "can't stay safe", "cant stay safe", "might hurt myself",
]


def _unwrap_event(event: dict) -> dict:
    """Extract parameters from varied Bedrock Agent / direct test event shapes."""
    if not isinstance(event, dict):
        return {}

    if "parameters" in event and isinstance(event["parameters"], list):
        out: dict[str, Any] = {}
        for p in event["parameters"]:
            if isinstance(p, dict) and "name" in p:
                out[p["name"]] = p.get("value")
        if out:
            return out

    if "requestBody" in event:
        content = event.get("requestBody", {}).get("content", {})
        for block in content.values():
            body = block.get("body", "")
            props = block.get("properties")
            if isinstance(props, list):
                out = {}
                for p in props:
                    if isinstance(p, dict) and "name" in p:
                        out[p["name"]] = p.get("value")
                if out:
                    return out
            if isinstance(body, str) and body.strip():
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    pass

    if "body" in event and isinstance(event["body"], str):
        try:
            return json.loads(event["body"])
        except json.JSONDecodeError:
            pass

    return event


def _norm_text(text: str) -> str:
    return (text or "").strip().lower()


def _contains_any(text: str, keywords: list[str]) -> bool:
    t = _norm_text(text)
    return any(k.lower() in t for k in keywords)


def _count_keyword_hits(text: str, keywords: list[str]) -> int:
    t = _norm_text(text)
    return sum(1 for k in keywords if k.lower() in t)


def _to_int(val: Any, default: int | None = None) -> int | None:
    if val is None or val == "":
        return default
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def _to_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ("true", "1", "yes")
    return bool(val)


def _compute_score(data: dict, text: str) -> int:
    """Deterministic distress score — higher means more overload."""
    score = 0
    score += _count_keyword_hits(text, MEDIUM_KEYWORDS_HE) * 2
    score += _count_keyword_hits(text, MEDIUM_KEYWORDS_EN) * 2
    score += _count_keyword_hits(text, HIGH_INTENSITY_HE) * 3
    score += _count_keyword_hits(text, HIGH_INTENSITY_EN) * 3

    stress = _to_int(data.get("self_reported_stress_level"))
    confusion = _to_int(data.get("confusion_level"))
    if stress is not None:
        if stress >= 8:
            score += 4
        elif stress >= 4:
            score += 2
    if confusion is not None:
        if confusion >= 8:
            score += 4
        elif confusion >= 4:
            score += 2
    if _to_bool(data.get("wants_human_support")):
        score += 2
    if _contains_any(text, SOFTENERS_HE) or _contains_any(text, SOFTENERS_EN):
        score = max(0, score - 2)
    return score


def _confidence(classification: str, score: int, crisis_hit: bool) -> str:
    if crisis_hit or classification == "crisis":
        return "high"
    if classification == "high" and score >= 8:
        return "high"
    if classification in ("high", "medium") and score >= 4:
        return "medium"
    return "low"


def _classify(data: dict) -> dict[str, Any]:
    lang = (data.get("preferred_language") or "he").lower()
    if not lang.startswith("en"):
        lang = "he"

    text = str(data.get("user_message") or data.get("recent_context_summary") or "")

    # Crisis flags take priority
    if _to_bool(data.get("has_immediate_danger")) or _to_bool(data.get("mentions_self_harm")):
        classification = "crisis"
        score = 99
        crisis_hit = True
    elif _contains_any(text, CRISIS_KEYWORDS_HE) or _contains_any(text, CRISIS_KEYWORDS_EN):
        classification = "crisis"
        score = 99
        crisis_hit = True
    else:
        crisis_hit = False
        score = _compute_score(data, text)
        stress = _to_int(data.get("self_reported_stress_level"), 0) or 0
        confusion = _to_int(data.get("confusion_level"), 0) or 0

        if score >= 6 or stress >= 8 or confusion >= 8:
            classification = "high"
        elif score >= 3 or (4 <= stress <= 7) or (4 <= confusion <= 7):
            classification = "medium"
        else:
            classification = "low"

    conf = _confidence(classification, score, crisis_hit)
    return _build_result(classification, conf, lang, data, text)


def _build_result(
    classification: str,
    confidence: str,
    lang: str,
    data: dict,
    text: str,
) -> dict[str, Any]:
    he = lang == "he"

    if classification == "low":
        return {
            "classification": "low",
            "confidence": confidence,
            "recommended_route": "kb_answer",
            "response_mode": "normal",
            "should_use_knowledge_base": True,
            "should_start_with_grounding": False,
            "should_offer_trusted_contact_message": False,
            "should_recommend_professional_support": False,
            "should_recommend_emergency_support": False,
            "agent_instruction": (
                "Answer normally using the Knowledge Base. "
                "Keep the answer grounded in uploaded documents."
            ),
            "user_facing_summary": (
                "נראה שזו שאלה רגילה למסמכים. כדאי לענות לפי המידע שמופיע ב-Knowledge Base."
                if he
                else "This looks like a normal document question. Answer from the Knowledge Base."
            ),
            "safe_next_steps": [
                "חפש במסמכים שהועלו" if he else "Search uploaded documents",
                "ענה בקצרה ובבהירות" if he else "Answer briefly and clearly",
            ],
            "avoid": [
                "אבחון רפואי" if he else "Medical diagnosis",
                "המצאת הנחיות שלא במסמכים" if he else "Inventing instructions not in documents",
            ],
            "safety_disclaimer": DISCLAIMER_HE if he else DISCLAIMER_EN,
        }

    if classification == "medium":
        has_stress_kw = _contains_any(text, MEDIUM_KEYWORDS_HE + MEDIUM_KEYWORDS_EN)
        return {
            "classification": "medium",
            "confidence": confidence,
            "recommended_route": "kb_answer_short",
            "response_mode": "short",
            "should_use_knowledge_base": True,
            "should_start_with_grounding": has_stress_kw,
            "should_offer_trusted_contact_message": False,
            "should_recommend_professional_support": False,
            "should_recommend_emergency_support": False,
            "agent_instruction": (
                "Give a short, calm answer. Use the Knowledge Base. Avoid overwhelming detail."
            ),
            "user_facing_summary": (
                "נראה שיש כאן קצת עומס או בלבול. כדאי לענות בקצרה, ברוגע, ועל בסיס המסמכים בלבד."
                if he
                else "Some stress or confusion detected. Answer briefly, calmly, from documents only."
            ),
            "safe_next_steps": [
                "ענה בקצרה" if he else "Keep the answer short",
                "השתמש ב-Knowledge Base" if he else "Use the Knowledge Base",
                "הימנע מפירוט מיותר" if he else "Avoid unnecessary detail",
            ],
            "avoid": [
                "תשובות ארוכות" if he else "Long answers",
                "ייעוץ רפואי חדש" if he else "New medical advice",
            ],
            "safety_disclaimer": DISCLAIMER_HE if he else DISCLAIMER_EN,
        }

    if classification == "high":
        severe = _to_int(data.get("self_reported_stress_level"), 0) or 0
        return {
            "classification": "high",
            "confidence": confidence,
            "recommended_route": "grounding_then_kb",
            "response_mode": "very_short",
            "should_use_knowledge_base": True,
            "should_start_with_grounding": True,
            "should_offer_trusted_contact_message": True,
            "should_recommend_professional_support": severe >= 8,
            "should_recommend_emergency_support": False,
            "agent_instruction": (
                "Start with one brief grounding step, then retrieve only the most relevant "
                "Knowledge Base guidance. Keep it very short."
            ),
            "user_facing_summary": (
                "נראה שאתה כרגע בעומס גבוה. כדאי להתחיל בצעד קצר להרגעה "
                "ורק אחר כך לבדוק את ההנחיות הרלוונטיות מהמסמכים."
                if he
                else "High overload detected. Start with one brief grounding step, "
                "then only the most relevant document guidance."
            ),
            "safe_next_steps": [
                "צעד קרקוע קצר אחד" if he else "One brief grounding step",
                "הנחיה רלוונטית אחת מהמסמכים" if he else "One relevant document instruction",
                "הצע לפנות לאדם קרוב אם צריך" if he else "Suggest a trusted contact if needed",
            ],
            "avoid": [
                "הסברים ארוכים" if he else "Long explanations",
                "רשימות ארוכות של משימות" if he else "Long task lists",
            ],
            "safety_disclaimer": DISCLAIMER_HE if he else DISCLAIMER_EN,
        }

    # crisis
    return {
        "classification": "crisis",
        "confidence": confidence,
        "recommended_route": "crisis_support",
        "response_mode": "crisis_safe",
        "should_use_knowledge_base": False,
        "should_start_with_grounding": True,
        "should_offer_trusted_contact_message": True,
        "should_recommend_professional_support": True,
        "should_recommend_emergency_support": True,
        "agent_instruction": (
            "Do not treat this as a normal RAG question. Encourage immediate human help, "
            "trusted support, and local emergency services. Do not provide medical or emergency care. "
            "Keep the answer short, calm, and direct."
        ),
        "user_facing_summary": (
            "נראה שיש כאן סימן למצוקה חריפה או סכנה אפשרית. "
            "חשוב לפנות מיד לעזרה אנושית, אדם קרוב, גורם מקצועי או שירותי חירום מקומיים."
            if he
            else "Possible acute distress or danger detected. Contact immediate human help, "
            "a trusted person, a professional, or local emergency services."
        ),
        "safe_next_steps": [
            "פנה לשירותי חירום מקומיים אם יש סכנה מיידית" if he else "Contact local emergency services if in immediate danger",
            "פנה לאדם קרוב שאתה סומך עליו" if he else "Reach a trusted person",
            "פנה לגורם מקצועי" if he else "Contact a professional",
        ],
        "avoid": [
            "להתנהג כאילו האפליקציה מספקת טיפול חירום" if he else "Pretending the app provides emergency care",
            "אבחון או ייעוץ רפואי" if he else "Diagnosis or medical advice",
            "המשך שאילת RAG רגילה בלבד" if he else "Continuing as a normal RAG Q&A only",
        ],
        "safety_disclaimer": DISCLAIMER_HE if he else DISCLAIMER_EN,
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
    data = _unwrap_event(event if isinstance(event, dict) else {})
    result = _classify(data)

    if isinstance(event, dict) and ("actionGroup" in event or "agent" in event):
        ag = event.get("actionGroup", "StressCheckInClassifier")
        fn = event.get("function", "stress_check_in_classifier")
        return _agent_response(ag, fn, result)

    return {
        "statusCode": 200,
        "body": json.dumps(result, ensure_ascii=False),
    }
