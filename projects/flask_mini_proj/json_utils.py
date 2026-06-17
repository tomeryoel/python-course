"""
JSON-safe conversion helpers for Flask API responses and Agent trace parsing.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any


def json_safe(value: Any) -> Any:
    """Recursively convert values to JSON-serializable primitives."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def dumps_json_safe(obj: Any, **kwargs: Any) -> str:
    """json.dumps wrapper that sanitizes datetime and nested objects first."""
    return json.dumps(json_safe(obj), **kwargs)
