"""
Knowledge Base + S3 status helpers for the Documents page and /api/knowledge-base/status.

RAG source of truth: S3 documents → Bedrock Knowledge Base (S3 Vectors) → Bedrock Agent.
Flask never queries OpenSearch or performs vector retrieval directly.
"""

from __future__ import annotations

import os
from typing import Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from agent_engine import is_agent_configured


def _region() -> str:
    return os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))


def _kb_id() -> str:
    return (
        os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "")
        or os.getenv("KNOWLEDGE_BASE_ID", "")
    ).strip()


def _s3_bucket() -> str:
    return os.getenv("S3_BUCKET_NAME", "").strip()


def _s3_prefix() -> str:
    return os.getenv("S3_PREFIX", "data/").strip() or "data/"


def list_s3_documents(max_keys: int = 50) -> tuple[list[dict[str, Any]], str | None]:
    """List objects in the configured S3 bucket/prefix. Returns (files, error)."""
    bucket = _s3_bucket()
    if not bucket:
        return [], None
    prefix = _s3_prefix()
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    try:
        client = boto3.client("s3", region_name=_region())
        resp = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=max_keys)
    except (NoCredentialsError, ClientError) as exc:
        return [], str(exc)
    files = []
    for obj in resp.get("Contents", []) or []:
        key = obj.get("Key", "")
        if key.endswith("/"):
            continue
        name = key.split("/")[-1]
        ext = name.rsplit(".", 1)[-1].upper() if "." in name else "FILE"
        files.append({
            "name": name,
            "key": key,
            "type": ext,
            "size_bytes": obj.get("Size", 0),
            "modified": obj.get("LastModified").isoformat() if obj.get("LastModified") else "",
        })
    return files, None


def get_knowledge_base_status() -> dict[str, Any]:
    kb_id = _kb_id()
    bucket = _s3_bucket()
    prefix = _s3_prefix()
    agent_ok = is_agent_configured()

    s3_files, s3_error = list_s3_documents() if bucket else ([], None)

    return {
        "runtime_mode": "bedrock_agent_knowledge_base",
        "knowledge_base_configured": bool(kb_id),
        "knowledge_base_id": kb_id or None,
        "agent_configured": agent_ok,
        "s3_bucket_configured": bool(bucket),
        "s3_bucket_name": bucket or None,
        "s3_prefix": prefix,
        "s3_document_count": len(s3_files),
        "s3_error": s3_error,
        "vector_store": "s3_vectors",
        "note": (
            "RAG is handled by the Bedrock Agent connected to the Bedrock Knowledge Base "
            "(S3 Vectors). Documents are stored in S3 under the configured prefix. "
            "Flask does not query OpenSearch or perform vector retrieval."
        ),
        "legacy_local_faiss": {
            "enabled": os.getenv("ENABLE_LEGACY_FAISS", "false").lower() in ("1", "true", "yes"),
            "note": "Local FAISS is legacy/optional only — not used by /api/chat.",
        },
    }
