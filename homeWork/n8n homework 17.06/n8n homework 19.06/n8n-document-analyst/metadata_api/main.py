from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from docx import Document
import uuid
import tempfile
import os


app = FastAPI(
    title="Cybersecurity Document Metadata API",
    description="Enriches Gemini document analysis results with business metadata for n8n.",
    version="1.0.0"
)


class GeminiResult(BaseModel):
    filename: Optional[str] = None
    file_type: Optional[str] = None
    summary: Optional[str] = None
    classification: str
    sentiment: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    entities: Dict[str, Any] = Field(default_factory=dict)
    action_items: List[str] = Field(default_factory=list)


class SensitivityRequest(BaseModel):
    text: Optional[str] = ""
    entities: Dict[str, Any] = Field(default_factory=dict)


CATEGORIES = [
    "phishing_alert",
    "malware_alert",
    "vulnerability_report",
    "suspicious_login",
    "incident_summary",
    "other"
]


DEPARTMENT_MAP = {
    "phishing_alert": "Security Operations",
    "malware_alert": "Incident Response",
    "vulnerability_report": "Vulnerability Management",
    "suspicious_login": "Identity and Access Management",
    "incident_summary": "Security Operations",
    "other": "General IT"
}


def detect_sensitivity(text: str, entities: Dict[str, Any]) -> str:
    combined_text = (text + " " + str(entities)).lower()

    confidential_keywords = [
        "password",
        "credential",
        "credentials",
        "token",
        "secret",
        "private key",
        "vpn",
        "admin",
        "finance",
        "mailbox",
        "cve",
        "source ip",
        "ip address",
        "affected user",
        "personal data",
        "data leak",
        "breach"
    ]

    internal_keywords = [
        "server",
        "organization",
        "department",
        "employee",
        "scan",
        "siem",
        "alert",
        "firewall",
        "endpoint"
    ]

    if any(keyword in combined_text for keyword in confidential_keywords):
        return "confidential"

    if any(keyword in combined_text for keyword in internal_keywords):
        return "internal"

    return "public"


def calculate_adjusted_confidence(confidence_score: float, entities: Dict[str, Any]) -> float:
    entity_count = 0

    for value in entities.values():
        if isinstance(value, list):
            entity_count += len(value)
        elif value:
            entity_count += 1

    if entity_count >= 4:
        adjusted = confidence_score + 0.05
    elif entity_count == 0:
        adjusted = confidence_score - 0.10
    else:
        adjusted = confidence_score

    return round(max(0.0, min(1.0, adjusted)), 2)


def generate_routing_tag(classification: str, sensitivity: str, adjusted_confidence: float) -> str:
    if sensitivity == "confidential":
        return "escalate"

    if adjusted_confidence < 0.7:
        return "needs-review"

    if classification in ["phishing_alert", "malware_alert", "suspicious_login"]:
        return "security-review"

    return "auto-approved"


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "metadata-api"
    }


@app.get("/categories")
def get_categories():
    return {
        "categories": CATEGORIES
    }


@app.post("/sensitivity")
def classify_sensitivity(data: SensitivityRequest):
    sensitivity = detect_sensitivity(
        text=data.text or "",
        entities=data.entities
    )

    return {
        "sensitivity": sensitivity
    }


@app.post("/enrich")
def enrich(data: GeminiResult):
    sensitivity = detect_sensitivity(
        text=(data.summary or "") + " " + data.classification,
        entities=data.entities
    )

    adjusted_confidence = calculate_adjusted_confidence(
        confidence_score=data.confidence_score,
        entities=data.entities
    )

    department = DEPARTMENT_MAP.get(data.classification, "General IT")

    routing_tag = generate_routing_tag(
        classification=data.classification,
        sensitivity=sensitivity,
        adjusted_confidence=adjusted_confidence
    )

    return {
        "document_id": str(uuid.uuid4()),
        "filename": data.filename,
        "file_type": data.file_type,
        "department": department,
        "sensitivity": sensitivity,
        "routing_tag": routing_tag,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "adjusted_confidence_score": adjusted_confidence
    }


@app.post("/extract-docx")
async def extract_docx(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".docx"):
        return {
            "status": "error",
            "error": "Only .docx files are supported"
        }

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        document = Document(temp_path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        extracted_text = "\n".join(paragraphs)

        return {
            "status": "success",
            "text": extracted_text,
            "filename": file.filename,
            "file_type": "docx",
            "char_count": len(extracted_text)
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
