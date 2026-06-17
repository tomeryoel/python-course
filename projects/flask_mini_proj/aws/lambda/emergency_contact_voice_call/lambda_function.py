"""
Emergency Contact Voice Call — Bedrock Agent Action Group tool (Lambda).

Triggers an outbound call via Amazon Connect to a predefined emergency contact.
REQUIRES confirmed=true — never calls without explicit user confirmation.

NOT a medical emergency service. Educational demo only.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

E164 = re.compile(r"^\+[1-9]\d{7,14}$")


def _unwrap_event(event: dict) -> dict:
    if "requestBody" in event:
        content = event.get("requestBody", {}).get("content", {})
        for block in content.values():
            body = block.get("body", "")
            if isinstance(body, str):
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    return {}
    if "body" in event and isinstance(event["body"], str):
        try:
            return json.loads(event["body"])
        except json.JSONDecodeError:
            pass
    return event if isinstance(event, dict) else {}


def _mask_phone(phone: str) -> str:
    if len(phone) < 6:
        return "***"
    return phone[:4] + "****" + phone[-2:]


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


def _start_connect_call(data: dict) -> dict[str, Any]:
    if not data.get("confirmed"):
        return {
            "status": "confirmation_required",
            "message": "Emergency contact call requires explicit user confirmation.",
        }

    phone = (data.get("emergency_contact_phone") or os.getenv("EMERGENCY_CONTACT_PHONE", "")).strip()
    if not E164.match(phone):
        return {"status": "failed", "error": "Missing or invalid emergency_contact_phone (E.164)."}

    instance_id = os.getenv("CONNECT_INSTANCE_ID", "").strip()
    flow_id = os.getenv("CONNECT_CONTACT_FLOW_ID", "").strip()
    source_phone = os.getenv("CONNECT_SOURCE_PHONE_NUMBER", "").strip()

    if not all([instance_id, flow_id, source_phone]):
        return {
            "status": "failed",
            "error": (
                "Amazon Connect not configured. Set CONNECT_INSTANCE_ID, "
                "CONNECT_CONTACT_FLOW_ID, CONNECT_SOURCE_PHONE_NUMBER on the Lambda."
            ),
        }

    import boto3

    connect = boto3.client("connect")
    attrs = {
        "user_display_name": str(data.get("user_display_name", "User")),
        "trigger_reason": str(data.get("trigger_reason", "Wellness companion support")),
        "language": str(data.get("language", "he")),
    }

    logger.info("Starting outbound call to %s", _mask_phone(phone))

    try:
        resp = connect.start_outbound_voice_contact(
            InstanceId=instance_id,
            ContactFlowId=flow_id,
            DestinationPhoneNumber=phone,
            SourcePhoneNumber=source_phone,
            Attributes=attrs,
        )
        contact_id = resp.get("ContactId", "")
        return {
            "status": "call_started",
            "contact_id": contact_id,
            "message": "Emergency contact call was triggered successfully.",
        }
    except Exception as exc:  # noqa: BLE001
        logger.error("Connect call failed: %s", exc)
        return {"status": "failed", "error": str(exc)}


def lambda_handler(event, context):
    data = _unwrap_event(event)
    result = _start_connect_call(data)

    if "actionGroup" in event or "agent" in event:
        ag = event.get("actionGroup", "EmergencyContactCall")
        fn = event.get("function", "emergency_contact_voice_call")
        return _agent_response(ag, fn, result)

    return {"statusCode": 200, "body": json.dumps(result, ensure_ascii=False)}
