"""
Optional direct Lambda tool invocations for demo/testing.

The main architecture uses Bedrock Agent Action Groups. These endpoints let the
UI demonstrate tool behavior without requiring a full Agent trace in dev.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger("ptsd.tools")

E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")


def _region() -> str:
    return os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))


def _lambda_client():
    return boto3.client("lambda", region_name=_region())


def invoke_weekly_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    name = os.getenv("WEEKLY_SNAPSHOT_LAMBDA_NAME", "ptsd-weekly-wellness-snapshot")
    return _invoke_lambda(name, payload)


def invoke_stress_check_in(payload: dict[str, Any]) -> dict[str, Any]:
    name = os.getenv("STRESS_CHECK_IN_LAMBDA_NAME", "ptsd-stress-check-in-classifier")
    return _invoke_lambda(name, payload)


def invoke_emergency_call(payload: dict[str, Any]) -> dict[str, Any]:
    if not payload.get("confirmed"):
        return {
            "status": "confirmation_required",
            "message": "Emergency contact call requires explicit user confirmation.",
        }
    phone = (payload.get("emergency_contact_phone") or "").strip()
    if not phone:
        phone = os.getenv("EMERGENCY_CONTACT_PHONE", "").strip()
    if not E164_PATTERN.match(phone):
        return {
            "status": "failed",
            "error": "Missing or invalid emergency_contact_phone (E.164 format, e.g. +972501234567).",
        }
    payload = {**payload, "emergency_contact_phone": phone, "confirmed": True}
    name = os.getenv("EMERGENCY_CALL_LAMBDA_NAME", "ptsd-emergency-contact-voice-call")
    return _invoke_lambda(name, payload)


def _invoke_lambda(function_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not function_name:
        return {"status": "error", "error": "Lambda function name not configured."}
    try:
        client = _lambda_client()
        resp = client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        )
        raw = resp["Payload"].read().decode("utf-8")
        body = json.loads(raw) if raw else {}
        if isinstance(body, dict) and "body" in body and isinstance(body["body"], str):
            try:
                body = json.loads(body["body"])
            except json.JSONDecodeError:
                pass
        return body if isinstance(body, dict) else {"status": "success", "raw": body}
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        logger.error("[tools] Lambda invoke failed (%s): %s", function_name, exc)
        return {"status": "error", "error": f"Lambda invoke failed ({code}): {exc}"}
    except Exception as exc:  # noqa: BLE001
        logger.error("[tools] Lambda invoke error: %s", exc)
        return {"status": "error", "error": str(exc)}


def build_weekly_snapshot_payload(tasks: list[dict], language: str = "he") -> dict[str, Any]:
    completed = [t.get("title", "") for t in tasks if t.get("status") == "done"]
    open_tasks = [t.get("title", "") for t in tasks if t.get("status") == "open"]
    topics = list({t.get("category", "") for t in tasks if t.get("category")})[:8]
    return {
        "completed_tasks": completed[:20],
        "open_tasks": open_tasks[:20],
        "recent_topics": topics,
        "language": language,
    }
