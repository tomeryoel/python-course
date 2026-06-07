"""Tests for agent_engine configuration and response parsing."""

import pytest

from agent_engine import (
    AGENT_CONFIG_ERROR,
    build_agent_session_id,
    is_agent_configured,
    parse_agent_response,
    require_agent_config,
)
from agent_engine import AgentConfigError


def test_agent_not_configured_by_default(monkeypatch):
    monkeypatch.delenv("BEDROCK_AGENT_ID", raising=False)
    monkeypatch.delenv("BEDROCK_AGENT_ALIAS_ID", raising=False)
    assert is_agent_configured() is False
    with pytest.raises(AgentConfigError):
        require_agent_config()


def test_agent_configured_when_env_set(monkeypatch):
    monkeypatch.setenv("BEDROCK_AGENT_ID", "AGENT123")
    monkeypatch.setenv("BEDROCK_AGENT_ALIAS_ID", "ALIAS456")
    assert is_agent_configured() is True
    assert require_agent_config() == ("AGENT123", "ALIAS456")


def test_build_agent_session_id_stable():
    sid = build_agent_session_id("conv_abc", "stored-session-1")
    assert sid == "stored-session-1"


def test_parse_agent_response_chunks():
    response = {
        "completion": [
            {"chunk": {"bytes": b"Hello "}},
            {"chunk": {"bytes": b"world"}},
        ]
    }
    parsed = parse_agent_response(response)
    assert parsed["answer"] == "Hello world"
    assert parsed["sources"] == []


def test_agent_config_error_message():
    assert "BEDROCK_AGENT_ID" in AGENT_CONFIG_ERROR
