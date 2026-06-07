"""
Bedrock Agent runtime — primary AI orchestration layer.

Architecture:
    Flask → boto3 bedrock-agent-runtime.invoke_agent()
         → Bedrock Agent
         → Knowledge Base (RAG from S3-indexed documents)
         → Lambda Action Groups (MCP-style tools)
         → final response

This module is the ONLY path for /api/chat. It does NOT call local FAISS or
Bedrock Runtime converse directly.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

logger = logging.getLogger("ptsd.agent")

AGENT_CONFIG_ERROR = (
    "Bedrock Agent is not configured. Please set BEDROCK_AGENT_ID and "
    "BEDROCK_AGENT_ALIAS_ID in your .env file."
)


class AgentConfigError(ValueError):
    """Raised when required Agent environment variables are missing."""


def _region() -> str:
    return os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))


def get_agent_client():
    return boto3.client("bedrock-agent-runtime", region_name=_region())


def require_agent_config() -> tuple[str, str]:
    agent_id = os.getenv("BEDROCK_AGENT_ID", "").strip()
    alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID", "").strip()
    if not agent_id or not alias_id:
        raise AgentConfigError(AGENT_CONFIG_ERROR)
    return agent_id, alias_id


def is_agent_configured() -> bool:
    try:
        require_agent_config()
        return True
    except AgentConfigError:
        return False


def build_agent_session_id(conversation_id: str, stored_session_id: str | None = None) -> str:
    if stored_session_id:
        return stored_session_id
    safe = re.sub(r"[^a-zA-Z0-9._:-]", "-", conversation_id)[:64]
    return f"ptsd-{safe}"


def _friendly_aws_error(exc: Exception) -> str:
    if isinstance(exc, (NoCredentialsError, PartialCredentialsError)):
        return (
            "לא נמצאו פרטי התחברות ל-AWS. הגדר AWS_ACCESS_KEY_ID, "
            "AWS_SECRET_ACCESS_KEY ו-AWS_REGION בקובץ .env."
        )
    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code", "")
        msg = exc.response.get("Error", {}).get("Message", str(exc))
        if code in ("AccessDeniedException", "AccessDenied"):
            return f"אין הרשאה לגשת ל-Bedrock Agent. בדוק IAM: bedrock:InvokeAgent. ({msg})"
        if code in ("ResourceNotFoundException", "ValidationException"):
            return f"Bedrock Agent לא נמצא או לא תקין. בדוק BEDROCK_AGENT_ID / ALIAS. ({msg})"
        if code in ("ThrottlingException", "TooManyRequestsException"):
            return "המערכת עמוסה. נסה שוב בעוד כמה שניות."
        return f"שגיאת AWS ({code}): {msg}"
    return f"שגיאה בחיבור ל-Bedrock Agent: {exc}"


def _extract_citations_from_trace(trace: dict) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    try:
        orch = trace.get("trace", {}).get("orchestrationTrace", {})
        obs = orch.get("observation", {})
        kb = obs.get("knowledgeBaseLookupOutput", {})
        for ref in kb.get("retrievedReferences", []) or []:
            content = ref.get("content", {}) or {}
            text = (content.get("text") or "")[:280]
            loc = ref.get("location", {}) or {}
            s3 = loc.get("s3Location", {}) or {}
            sources.append({
                "text_preview": text + ("…" if len(content.get("text", "")) > 280 else ""),
                "uri": s3.get("uri", ""),
                "type": loc.get("type", "S3"),
            })
    except (TypeError, KeyError):
        pass
    return sources


def _extract_tool_calls_from_trace(trace: dict) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    try:
        orch = trace.get("trace", {}).get("orchestrationTrace", {})
        inv = orch.get("invocationInput", {})
        action = inv.get("actionGroupInvocationInput", {})
        if action:
            tools.append({
                "action_group": action.get("actionGroupName", ""),
                "function": action.get("function", ""),
                "parameters": action.get("parameters", []),
            })
    except (TypeError, KeyError):
        pass
    return tools


def parse_agent_response(response: dict) -> dict[str, Any]:
    """Parse streaming invoke_agent completion + trace events."""
    answer_parts: list[str] = []
    sources: list[dict[str, Any]] = []
    tool_calls: list[dict[str, Any]] = []
    trace_summary: list[str] = []

    for event in response.get("completion", []):
        if "chunk" in event:
            chunk = event["chunk"]
            if "bytes" in chunk:
                answer_parts.append(chunk["bytes"].decode("utf-8", errors="replace"))
            if "attribution" in chunk:
                for cite in chunk["attribution"].get("citations", []) or []:
                    for ref in cite.get("retrievedReferences", []) or []:
                        content = ref.get("content", {}) or {}
                        text = (content.get("text") or "")[:280]
                        sources.append({"text_preview": text, "source": "attribution"})
        if "trace" in event:
            trace = event["trace"]
            trace_summary.append(json.dumps(trace, ensure_ascii=False)[:200])
            sources.extend(_extract_citations_from_trace(trace))
            tool_calls.extend(_extract_tool_calls_from_trace(trace))

    # Deduplicate sources by preview text
    seen: set[str] = set()
    unique_sources = []
    for s in sources:
        key = s.get("text_preview", "") or s.get("uri", "")
        if key and key not in seen:
            seen.add(key)
            unique_sources.append(s)

    return {
        "answer": "".join(answer_parts).strip(),
        "sources": unique_sources,
        "tool_calls": tool_calls,
        "trace_summary": trace_summary[:5],
    }


def invoke_bedrock_agent(
    message: str,
    session_id: str,
    memory_context: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    agent_id, alias_id = require_agent_config()
    client = get_agent_client()

    # Optional: prepend recent app memory as context (Agent also keeps sessionId state).
    input_text = message
    if memory_context:
        history_lines = [
            f"{m.get('role', 'user')}: {m.get('content', '')}" for m in memory_context[-4:]
        ]
        if history_lines:
            input_text = (
                "היסטוריית שיחה אחרונה:\n"
                + "\n".join(history_lines)
                + f"\n\nשאלת המשתמש:\n{message}"
            )

    logger.info(
        "[agent] invoke_agent agent=%s alias=%s session=%s msg_len=%d",
        agent_id[:8], alias_id[:8], session_id[:20], len(message),
    )

    try:
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_id,
            sessionId=session_id,
            inputText=input_text,
            enableTrace=True,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("[agent] invoke_agent failed: %s", exc)
        raise

    parsed = parse_agent_response(response)
    logger.info(
        "[agent] response len=%d sources=%d tools=%d",
        len(parsed["answer"]), len(parsed["sources"]), len(parsed["tool_calls"]),
    )
    return parsed


def answer_with_agent(
    message: str,
    conversation_id: str | None = None,
    user_id: str | None = None,
    memory_context: list[dict[str, str]] | None = None,
    agent_session_id: str | None = None,
) -> dict[str, Any]:
    """Main entry point for /api/chat."""
    _ = user_id  # reserved for future multi-user support
    if not message.strip():
        return {"status": "error", "message": "נא להזין הודעה."}

    try:
        require_agent_config()
    except AgentConfigError as exc:
        return {"status": "error", "message": str(exc)}

    session_id = build_agent_session_id(conversation_id or "default", agent_session_id)

    try:
        parsed = invoke_bedrock_agent(message, session_id, memory_context)
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "message": _friendly_aws_error(exc),
            "conversation_id": conversation_id,
            "agent_session_id": session_id,
        }

    if not parsed["answer"]:
        parsed["answer"] = "לא התקבלה תשובה מה-Agent. בדוק את הגדרות ה-Agent ב-AWS Console."

    return {
        "status": "success",
        "answer": parsed["answer"],
        "conversation_id": conversation_id,
        "agent_session_id": session_id,
        "sources": parsed["sources"],
        "tool_calls": parsed["tool_calls"],
        "trace_summary": parsed["trace_summary"],
        "memory_summary": {
            "recent_turns": len(memory_context or []),
        },
    }
