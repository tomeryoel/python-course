"""
Clinical document uploads and registry — prepared for Bedrock KB ingestion.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
REGISTRY_PATH = os.path.join(BASE_DIR, "documents_registry.json")

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_BYTES = 15 * 1024 * 1024


class DocumentError(Exception):
    pass


def _ensure_dirs() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)


def _load_registry() -> list[dict[str, Any]]:
    if not os.path.isfile(REGISTRY_PATH):
        return []
    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as exc:
        raise DocumentError("רשימת המסמכים פגומה.") from exc


def _save_registry(docs: list[dict[str, Any]]) -> None:
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)


def list_documents() -> list[dict[str, Any]]:
    return _load_registry()


def _safe_filename(name: str) -> str:
    base = os.path.basename(name)
    base = re.sub(r"[^\w.\- א-ת]", "_", base, flags=re.UNICODE)
    return base[:180] or "document"


def register_document(
    *,
    original_name: str,
    stored_name: str,
    file_type: str,
    size_bytes: int,
    source_label: str = "העלאת משתמש",
) -> dict[str, Any]:
    entry = {
        "id": f"doc_{uuid.uuid4().hex[:12]}",
        "name": original_name,
        "stored_name": stored_name,
        "type": file_type,
        "size_bytes": size_bytes,
        "source": source_label,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_ingestion",
        "ingestion_note": (
            "ממתין לסנכרון ל-Knowledge Base — הפעל ingestion ב-AWS Bedrock."
        ),
    }
    docs = _load_registry()
    docs.insert(0, entry)
    _save_registry(docs)
    return entry


def save_upload(file_storage) -> dict[str, Any]:
    """Save uploaded file and register metadata."""
    if not file_storage or not file_storage.filename:
        raise DocumentError("לא התקבל קובץ.")

    original = file_storage.filename
    ext = os.path.splitext(original)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentError("סוג קובץ לא נתמך. PDF, DOCX או TXT בלבד.")

    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)
    if size > MAX_FILE_BYTES:
        raise DocumentError("הקובץ גדול מדי (מקסימום 15MB).")

    _ensure_dirs()
    safe = _safe_filename(original)
    stored_name = f"{uuid.uuid4().hex[:8]}_{safe}"
    path = os.path.join(UPLOAD_DIR, stored_name)
    file_storage.save(path)

    file_type = ext.lstrip(".").upper()
    return register_document(
        original_name=original,
        stored_name=stored_name,
        file_type=file_type,
        size_bytes=size,
    )


def mark_document_synced(doc_id: str) -> dict[str, Any] | None:
    """Future: call after Bedrock ingestion completes."""
    docs = _load_registry()
    for i, d in enumerate(docs):
        if d.get("id") == doc_id:
            docs[i]["status"] = "synced"
            docs[i]["ingestion_note"] = "מסונכרן ל-Knowledge Base"
            docs[i]["synced_at"] = datetime.now(timezone.utc).isoformat()
            _save_registry(docs)
            return docs[i]
    return None
