"""
Lightweight Bedrock Runtime helper for non-chat features (e.g. task extraction).

NOT used by /api/chat — chat goes through Bedrock Agent (agent_engine.py).
"""

from __future__ import annotations

import os
import time

import boto3
from botocore.exceptions import ClientError


def _region() -> str:
    return os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))


def _model_ids() -> list[str]:
    primary = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0").strip()
    fallbacks = os.getenv(
        "BEDROCK_MODEL_FALLBACKS",
        "amazon.nova-micro-v1:0,anthropic.claude-3-haiku-20240307-v1:0",
    )
    ids = [primary] + [m.strip() for m in fallbacks.split(",") if m.strip()]
    seen: set[str] = set()
    return [m for m in ids if m and not (m in seen or seen.add(m))]


def converse(user_message: str, extra_system: str = "") -> tuple[str, str]:
    """Call Bedrock Runtime converse (for auxiliary features only)."""
    client = boto3.client("bedrock-runtime", region_name=_region())
    system_blocks = [{"text": extra_system}] if extra_system else []
    messages = [{"role": "user", "content": [{"text": user_message}]}]
    config = {
        "maxTokens": int(os.getenv("BEDROCK_MAX_TOKENS", "1200")),
        "temperature": float(os.getenv("BEDROCK_TEMPERATURE", "0.3")),
    }
    last_error = None
    for model_id in _model_ids():
        try:
            kwargs = {
                "modelId": model_id,
                "messages": messages,
                "inferenceConfig": config,
            }
            if system_blocks:
                kwargs["system"] = system_blocks
            resp = client.converse(**kwargs)
            text = resp["output"]["message"]["content"][0]["text"].strip()
            return text, model_id
        except ClientError as exc:
            last_error = exc
            code = exc.response.get("Error", {}).get("Code", "")
            if code in ("AccessDeniedException", "ValidationException", "ResourceNotFoundException"):
                continue
            if code in ("ThrottlingException", "TooManyRequestsException"):
                time.sleep(2)
                continue
            raise
    if last_error:
        raise last_error
    raise RuntimeError("No Bedrock model available.")
